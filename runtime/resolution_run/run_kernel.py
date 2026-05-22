"""Headless resolution-run kernel over existing Hunt, WorkUnit, and lane seams."""

from __future__ import annotations

from typing import Any, Mapping

from .command_handler import handle_run_command
from .event_log import InMemoryRunEventLog
from .lane_projector import build_run_lane_snapshot
from .policy_gate import DEFAULT_RUN_POLICY, evaluate_run_policy
from .run_store import FIXED_CREATED_AT, InMemoryRunStore, stable_id
from .workunit_scheduler import schedule_ia_hunt_workunits


BLOCKED_ACTIONS = (
    "run_live_source_probe",
    "run_live_ia_metadata",
    "download",
    "upload",
    "extract",
    "execute",
    "call_model_provider",
    "mutate_operator_instance",
    "mutate_master_index",
    "deploy",
    "promote_reviewed_record",
)


def create_resolution_run(
    query: str,
    *,
    projection_profile: str = "operator_workbench",
    policy: Mapping[str, Any] | None = None,
    store: InMemoryRunStore | None = None,
    event_log: InMemoryRunEventLog | None = None,
) -> dict[str, Any]:
    """Create a headless run packet without scheduling or executing sources."""
    if not str(query).strip():
        raise ValueError("query is required")
    store = store or InMemoryRunStore()
    event_log = event_log or InMemoryRunEventLog()
    run = store.create(str(query).strip(), projection_profile)
    event_log.append(run["run_id"], "run_created", {"query": run["query"]})
    event_log.append(run["run_id"], "query_compiled", {"compiled_query_id": run["compiled_query_id"]})
    decision = evaluate_run_policy("project_lanes", policy or DEFAULT_RUN_POLICY)
    run["policy_decision"] = decision
    return {
        "schema_version": "resolution_run_kernel_create_result.v0",
        "run": run,
        "events": event_log.list_events(run["run_id"]),
        "policy_decision": decision,
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "store_mutation_performed": False,
    }


def run_resolution_dry_run(
    query: str,
    *,
    projection_profile: str = "operator_workbench",
    include_ia_hunt: bool = True,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the foundation orchestration proof in dry-run mode."""
    store = InMemoryRunStore()
    event_log = InMemoryRunEventLog()
    created = create_resolution_run(
        query,
        projection_profile=projection_profile,
        policy=policy,
        store=store,
        event_log=event_log,
    )
    run = dict(created["run"])
    run = handle_run_command(run, {"command_type": "start"}, event_log, policy)
    workunit_schedule = schedule_ia_hunt_workunits(query, policy or DEFAULT_RUN_POLICY) if include_ia_hunt else {}
    if workunit_schedule:
        event_log.append(run["run_id"], "workunits_scheduled", {"workunit_count": workunit_schedule["workunit_count"]})
    lane_snapshot = build_run_lane_snapshot(
        run,
        workunit_schedule,
        projection_profile=projection_profile,
        run_ia_dry_run=include_ia_hunt,
    )
    run["active_lanes"] = [str(lane.get("lane_kind", "")) for lane in lane_snapshot["lane_page"].get("lanes", []) if lane.get("visible")]
    run["state"] = "completed"
    run["state_history"] = list(run.get("state_history", [])) + [
        {"state": "completed", "at": FIXED_CREATED_AT, "reason": "dry-run orchestration completed"}
    ]
    store.update(run)
    event_log.append(run["run_id"], "lane_snapshot_built", {"snapshot_id": lane_snapshot["snapshot_id"]})
    coverage_report = build_run_coverage_report(run, workunit_schedule, lane_snapshot)
    event_log.append(run["run_id"], "coverage_report_built", {"coverage_report_id": coverage_report["coverage_report_id"]})
    return {
        "schema_version": "resolution_run_kernel_result.v0",
        "run": run,
        "events": event_log.list_events(run["run_id"]),
        "workunit_schedule": workunit_schedule,
        "lane_snapshot": lane_snapshot,
        "coverage_report": coverage_report,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "boundaries": _boundary_report(),
    }


def build_run_coverage_report(
    run: Mapping[str, Any],
    workunit_schedule: Mapping[str, Any],
    lane_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a coverage report for one dry-run resolution run."""
    return {
        "schema_version": "run_coverage_report.v0",
        "coverage_report_id": str(run.get("coverage_report_id") or stable_id("coverage", run.get("run_id"))),
        "run_id": str(run.get("run_id")),
        "created_at": FIXED_CREATED_AT,
        "checked_layers": [
            "headless_run_created",
            "query_compiled",
            "local_lane_projection",
            "ia_hunt_workunit_dry_run",
            "blocked_action_posture",
        ],
        "unchecked_layers": [
            "live_source_metadata",
            "downloads",
            "extraction",
            "review_promote_apply",
            "operator_instance_apply",
            "public_fanout",
        ],
        "workunit_count": int(workunit_schedule.get("workunit_count", 0) or 0),
        "lane_count": int(lane_snapshot.get("lane_count", 0) or 0),
        "accepted_truth": False,
        "review_required": True,
        "limitations": [
            "Coverage is scoped to committed fixtures and dry-run WorkUnit planning.",
            "Live IA metadata and browser apply flows remain future governed work.",
        ],
    }


def _boundary_report() -> dict[str, Any]:
    return {
        "schema_version": "resolution_run_boundary_report.v0",
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "candidate_index_mutated": False,
        "review_queue_mutated": False,
        "reviewed_index_mutated": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
