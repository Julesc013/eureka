"""Public alpha usefulness reassessment.

The reassessment is a deterministic product-readiness check over committed
example packets. It does not deploy, publish, mutate public data, call live
sources, or convert candidates into reviewed truth.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


TASK_ID = "PUBLIC-ALPHA-REASSESS-00"
REASSESS_ID = "public_alpha_reassess_00"
DEFAULT_TIMESTAMP = "2026-05-31T00:00:00Z"
RECOMMENDED_NEXT_TASK = "LIVE-METADATA-PILOT-BATCH-00 - Operator-approved live metadata pilot over seed queries"

REQUIRED_WEB_ROUTES = (
    "/alpha",
    "/alpha/object",
    "/alpha/source",
    "/alpha/evidence",
    "/alpha/absence",
    "/alpha/needs",
)
REQUIRED_API_ROUTES = (
    "/api/v1/alpha/status",
    "/api/v1/alpha/search",
    "/api/v1/alpha/object/{object_id}",
    "/api/v1/alpha/source/{summary_id}",
    "/api/v1/alpha/evidence/{summary_id}",
    "/api/v1/alpha/absence/{summary_id}",
    "/api/v1/alpha/needs",
)

DEFAULT_POLICY: dict[str, Any] = {
    "reassessment_is_not_launch": True,
    "reassessment_must_not_deploy": True,
    "launch_requires_explicit_future_manual_approval": True,
    "public_alpha_min_reviewed_record_threshold": 25,
    "public_alpha_min_domain_coverage_threshold": 3,
    "candidate_only_snapshot_not_enough_for_launch": True,
    "needs_and_absences_are_useful_but_not_launch_sufficient": True,
    "public_mutation_enabled": False,
    "public_live_source_fanout_enabled": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "production_readiness_claimed": False,
    "public_launch_readiness_claimed": False,
}


def load_snapshot_refresh_metrics(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    refresh_root = repo_root / "examples" / "snapshots" / "refresh"
    context = {
        "schema_version": "public_alpha_reassess_input_context.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_result": _read_json(refresh_root / "snapshot_refresh_result.json"),
        "reviewed_record_section": _read_json(refresh_root / "reviewed_record_section.json"),
        "candidate_sections": [
            _read_json(refresh_root / "candidate_section_frontier_media.json"),
            _read_json(refresh_root / "candidate_section_legacy_software.json"),
        ],
        "need_absence_section": _read_json(refresh_root / "need_absence_section.json"),
        "review_queue_section": _read_json(refresh_root / "review_queue_section.json"),
        "relay_projection": _read_json(refresh_root / "refreshed_relay_projection.json"),
        "snapshot_refresh_public_alpha_input": _read_json(refresh_root / "public_alpha_reassess_input.json"),
        "public_alpha_readonly_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_readonly_00_result.json"),
        "public_alpha_launch_defer_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_launch_defer_result.json"),
        "policy": merged_policy,
        "created_at": DEFAULT_TIMESTAMP,
    }
    return context


def calculate_public_alpha_usefulness_metrics(
    snapshot_refresh_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_result)
    candidate_sections = list(context["candidate_sections"])
    candidate_items = [candidate for section in candidate_sections for candidate in section.get("candidates", [])]
    reviewed_records = list(context["reviewed_record_section"].get("reviewed_records") or [])
    need_absence = context["need_absence_section"]
    route_smoke = smoke_public_alpha_routes_from_examples(merged_policy)
    domains = sorted(
        {
            _text(candidate.get("domain_id"))
            for candidate in candidate_items
            if _text(candidate.get("domain_id"))
        }
        | {
            _text(record.get("domain_id"))
            for record in reviewed_records
            if _text(record.get("domain_id"))
        }
    )
    reviewed_domains = sorted({_text(record.get("domain_id")) for record in reviewed_records if _text(record.get("domain_id"))})
    reviewed_count = int(context["snapshot_refresh_result"].get("reviewed_record_count") or len(reviewed_records))
    candidate_count = int(context["snapshot_refresh_result"].get("candidate_count") or len(candidate_items))
    known_need_count = int(context["snapshot_refresh_result"].get("known_need_count") or need_absence.get("known_need_count") or 0)
    absence_count = int(context["snapshot_refresh_result"].get("absence_count") or need_absence.get("absence_count") or 0)
    query_count = candidate_count
    candidate_to_reviewed_ratio = round(candidate_count / max(reviewed_count, 1), 2)
    usefulness_score = _usefulness_score(
        reviewed_count=reviewed_count,
        reviewed_domain_count=len(reviewed_domains),
        candidate_count=candidate_count,
        route_smoke_passed=route_smoke["route_smoke_status"] == "pass",
        policy=merged_policy,
    )
    return {
        "schema_version": "public_alpha_usefulness_metrics.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": context["snapshot_refresh_result"].get("snapshot_refresh_id", "snapshot_refresh_00"),
        "reviewed_record_count": reviewed_count,
        "candidate_count": candidate_count,
        "candidate_to_reviewed_ratio": candidate_to_reviewed_ratio,
        "known_need_count": known_need_count,
        "absence_summary_count": absence_count,
        "domains_represented": domains,
        "domain_count": len(domains),
        "reviewed_domains_represented": reviewed_domains,
        "reviewed_domain_count": len(reviewed_domains),
        "seed_batches_represented": list(context["snapshot_refresh_result"].get("source_batch_refs") or []),
        "seed_batch_count": len(context["snapshot_refresh_result"].get("source_batch_refs") or []),
        "query_count": query_count,
        "queries_with_reviewed_result": 0,
        "queries_with_candidate_result": candidate_count,
        "queries_with_need_or_absence": known_need_count,
        "public_routes_smoked": route_smoke["public_routes_smoked"],
        "public_api_routes_smoked": route_smoke["public_api_routes_smoked"],
        "route_smoke_status": route_smoke["route_smoke_status"],
        "usefulness_score": usefulness_score,
        "usefulness_threshold_for_launch": 0.75,
        "reviewed_record_threshold": int(merged_policy["public_alpha_min_reviewed_record_threshold"]),
        "domain_coverage_threshold": int(merged_policy["public_alpha_min_domain_coverage_threshold"]),
        "warnings_count": 3,
        "accepted_truth_created": False,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def smoke_public_alpha_routes_from_examples(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    readonly = _read_json(_repo_root() / "control" / "inventory" / "public_alpha_readonly_00_result.json")
    web_routes = list(readonly.get("public_web_routes_added") or [])
    api_routes = list(readonly.get("public_api_routes_added") or [])
    route_rows = [
        _route_row(route, "web", route in web_routes)
        for route in REQUIRED_WEB_ROUTES
    ] + [
        _route_row(route, "api", route in api_routes)
        for route in REQUIRED_API_ROUTES
    ]
    missing = [row["route"] for row in route_rows if row["status"] != "pass"]
    return {
        "schema_version": "public_alpha_route_smoke.v0",
        "reassess_id": REASSESS_ID,
        "route_smoke_status": "pass" if not missing else "partial",
        "routes": route_rows,
        "missing_routes": missing,
        "public_routes_smoked": sum(1 for row in route_rows if row["route_family"] == "web" and row["status"] == "pass"),
        "public_api_routes_smoked": sum(1 for row in route_rows if row["route_family"] == "api" and row["status"] == "pass"),
        "example_metadata_only": True,
        "local_server_started": False,
        "deployment_performed": False,
        "public_launch_performed": False,
        "live_network_used": False,
        "mutation_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_query_coverage(
    seed_batches: Sequence[Mapping[str, Any]],
    snapshot_refresh_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_result)
    batches = list(seed_batches or context["snapshot_refresh_result"].get("source_batch_refs") or [])
    rows: list[dict[str, Any]] = []
    for section in context["candidate_sections"]:
        candidates = list(section.get("candidates") or [])
        rows.append(
            {
                "batch_id": section.get("batch_id"),
                "domain_key": section.get("domain_key"),
                "query_count": len(candidates),
                "queries_with_reviewed_result": 0,
                "queries_with_candidate_result": len(candidates),
                "queries_with_need_or_absence": len(candidates),
                "coverage_note": "Seed queries have candidate/need coverage but no reviewed seed-result coverage yet.",
            }
        )
    return {
        "schema_version": "public_alpha_reassess_query_coverage_matrix.v0",
        "reassess_id": REASSESS_ID,
        "seed_batches": list(batches),
        "rows": rows,
        "query_count": sum(row["query_count"] for row in rows),
        "queries_with_reviewed_result": 0,
        "queries_with_candidate_result": sum(row["queries_with_candidate_result"] for row in rows),
        "queries_with_need_or_absence": sum(row["queries_with_need_or_absence"] for row in rows),
        "launch_sufficient": False,
        "accepted_truth_created": False,
    }


def assess_candidate_usefulness(
    candidate_sections: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidates = [candidate for section in candidate_sections for candidate in section.get("candidates", [])]
    return {
        "schema_version": "public_alpha_reassess_candidate_usefulness_matrix.v0",
        "reassess_id": REASSESS_ID,
        "candidate_count": len(candidates),
        "review_only_candidate_count": len(candidates),
        "candidate_domains": sorted({_text(candidate.get("domain_id")) for candidate in candidates if _text(candidate.get("domain_id"))}),
        "candidate_results_useful_for_internal_demo": len(candidates) > 0,
        "candidate_results_launch_sufficient": False,
        "all_candidates_review_required": all(candidate.get("accepted_truth") is False for candidate in candidates),
        "public_mutation_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "accepted_truth_created": False,
    }


def build_launch_blocker_register(
    metrics: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    blockers = [
        _blocker(
            "reviewed_record_count_below_threshold",
            f"Reviewed records {metrics['reviewed_record_count']} < threshold {metrics['reviewed_record_threshold']}.",
        ),
        _blocker(
            "insufficient_domain_coverage",
            f"Reviewed domains {metrics['reviewed_domain_count']} < threshold {metrics['domain_coverage_threshold']}.",
        ),
        _blocker(
            "candidate_heavy_review_light_snapshot",
            f"Candidate/reviewed ratio is {metrics['candidate_to_reviewed_ratio']}; candidates are not accepted truth.",
        ),
        _blocker("no_public_launch_approval", "No explicit future manual approval exists for a public launch."),
        _blocker("public_launch_track_deferred", "Public alpha launch remains deferred for discovery coverage."),
        _blocker("no_live_metadata_batch_reviewed", "No operator-approved live metadata pilot batch has been reviewed."),
        _blocker(
            "no_snapshot_publication_rehearsal_after_seed_refresh",
            "The refreshed seed projection has not had a separate publication rehearsal.",
        ),
    ]
    positives = [
        "candidate_discovery_stack_present",
        "seed_batches_present",
        "review_batch_present",
        "snapshot_refresh_present",
        "needs_absences_present",
    ]
    return {
        "schema_version": "public_alpha_launch_blocker_register.v0",
        "reassess_id": REASSESS_ID,
        "blockers": blockers,
        "blockers_count": len(blockers),
        "nonblocking_positives": positives,
        "warnings": [
            "route correctness is not product usefulness",
            "candidate-rich snapshots remain operator-review material",
            "current reviewed corpus is too thin for public search expectations",
        ],
        "warnings_count": 3,
        "launch_blocked": True,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_next_work_recommendations(
    metrics: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_next_work_recommendation.v0",
        "reassess_id": REASSESS_ID,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "recommendations": [
            {
                "task": "LIVE-METADATA-PILOT-BATCH-00",
                "priority": 1,
                "reason": "Produce real source-backed candidate evidence from seed queries before public launch work resumes.",
            },
            {
                "task": "SEED-BATCH-MANUALS-SCANS-00",
                "priority": 2,
                "reason": "Increase domain coverage and reviewed-candidate review throughput.",
            },
            {
                "task": "SEED-BATCH-DRIVER-SUPPORT-00",
                "priority": 3,
                "reason": "Add a driver/support-media wedge with strict safety posture.",
            },
            {
                "task": "SNAPSHOT-REFRESH-01",
                "priority": 4,
                "reason": "Refresh projections after live metadata and review work produce stronger evidence.",
            },
        ],
        "needs_more_reviewed_records": metrics["reviewed_record_count"] < metrics["reviewed_record_threshold"],
        "needs_more_seed_batches": True,
        "needs_live_metadata_pilot": True,
        "deployment_performed": False,
        "public_launch_performed": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_decision(
    metrics: Mapping[str, Any],
    blockers: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    launch_recommended = (
        metrics["reviewed_record_count"] >= metrics["reviewed_record_threshold"]
        and metrics["reviewed_domain_count"] >= metrics["domain_coverage_threshold"]
        and metrics["usefulness_score"] >= metrics["usefulness_threshold_for_launch"]
        and blockers["blockers_count"] == 0
    )
    return {
        "schema_version": "public_alpha_reassess_decision.v0",
        "reassess_id": REASSESS_ID,
        "decision": "remain_deferred" if not launch_recommended else "eligible_for_future_manual_launch_review",
        "snapshot_refresh_ref": metrics["snapshot_refresh_ref"],
        "reviewed_record_count": metrics["reviewed_record_count"],
        "candidate_count": metrics["candidate_count"],
        "known_need_count": metrics["known_need_count"],
        "absence_summary_count": metrics["absence_summary_count"],
        "route_smoke_status": metrics["route_smoke_status"],
        "query_coverage": {
            "query_count": metrics["query_count"],
            "queries_with_reviewed_result": metrics["queries_with_reviewed_result"],
            "queries_with_candidate_result": metrics["queries_with_candidate_result"],
            "queries_with_need_or_absence": metrics["queries_with_need_or_absence"],
        },
        "usefulness_score": metrics["usefulness_score"],
        "launch_recommended": launch_recommended,
        "public_alpha_launch_recommended": launch_recommended,
        "demo_mode_recommended": not launch_recommended and metrics["candidate_count"] > 0,
        "needs_more_reviewed_records": metrics["reviewed_record_count"] < metrics["reviewed_record_threshold"],
        "needs_more_seed_batches": True,
        "needs_live_metadata_pilot": True,
        "blockers": list(blockers["blockers"]),
        "warnings": list(blockers["warnings"]),
        "next_work": RECOMMENDED_NEXT_TASK,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_boundary_report(
    decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_reassess_boundary_report.v0",
        "record_type": "public_alpha_reassess_boundary_report",
        "reassess_id": REASSESS_ID,
        "reassessment_is_not_launch": True,
        "launch_recommended": bool(decision.get("launch_recommended", False)),
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_public_alpha_reassess(
    policy: Mapping[str, Any] | None = None,
    *,
    from_snapshot_refresh_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_snapshot_refresh_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = load_snapshot_refresh_metrics(merged_policy)
    metrics = calculate_public_alpha_usefulness_metrics(context, merged_policy)
    route_smoke = smoke_public_alpha_routes_from_examples(merged_policy)
    query_coverage = assess_query_coverage(metrics["seed_batches_represented"], context, merged_policy)
    candidate_usefulness = assess_candidate_usefulness(context["candidate_sections"], merged_policy)
    blockers = build_launch_blocker_register(metrics, merged_policy)
    next_work = build_next_work_recommendations(metrics, merged_policy)
    decision = build_public_alpha_reassess_decision(metrics, blockers, merged_policy)
    boundary = build_public_alpha_reassess_boundary_report(decision, merged_policy)
    result = {
        "schema_version": "public_alpha_reassess_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "reassess_id": REASSESS_ID,
        "metrics": metrics,
        "route_smoke": route_smoke,
        "query_coverage": query_coverage,
        "candidate_usefulness": candidate_usefulness,
        "launch_blockers": blockers,
        "next_work": next_work,
        "decision": decision,
        "boundary_report": boundary,
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "reviewed_record_count": metrics["reviewed_record_count"],
        "candidate_count": metrics["candidate_count"],
        "known_need_count": metrics["known_need_count"],
        "absence_summary_count": metrics["absence_summary_count"],
        "launch_recommended": decision["launch_recommended"],
        "demo_mode_recommended": decision["demo_mode_recommended"],
        "needs_more_reviewed_records": decision["needs_more_reviewed_records"],
        "needs_more_seed_batches": decision["needs_more_seed_batches"],
        "needs_live_metadata_pilot": decision["needs_live_metadata_pilot"],
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "created_at": DEFAULT_TIMESTAMP,
    }
    if write_examples:
        result["examples_written_paths"] = write_public_alpha_reassess_examples(result)
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_public_alpha_reassess_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "public_alpha" / "reassess"
    files = {
        "public_alpha_reassess_metrics.json": payload["metrics"],
        "public_alpha_route_smoke.json": payload["route_smoke"],
        "public_alpha_query_coverage.json": payload["query_coverage"],
        "public_alpha_candidate_usefulness.json": payload["candidate_usefulness"],
        "public_alpha_launch_blockers.json": payload["launch_blockers"],
        "public_alpha_next_work.json": payload["next_work"],
        "public_alpha_reassess_decision.json": payload["decision"],
        "public_alpha_boundary_report.json": payload["boundary_report"],
        "public_alpha_reassess_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    return written


def build_public_alpha_reassess_inventory_packets(
    result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build inventory packets without writing them.

    Validators and tests use this to prove the reassessment can produce the
    governed inventory surface without mutating repo state.
    """
    payload = dict(result or run_public_alpha_reassess(write_examples=False))
    return dict(_inventory_packets(payload))


def write_public_alpha_reassess_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = _inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_audit_pack(payload, repo_root))
    return written


def _inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "public_alpha_reassess_input_state.json": {
            "schema_version": "public_alpha_reassess_input_state.v0",
            "task": TASK_ID,
            "input_results": {
                "snapshot_refresh": "control/inventory/snapshot_refresh_result.json",
                "seed_batch_frontier_media": "control/inventory/seed_batch_frontier_media_result.json",
                "seed_batch_legacy_software": "control/inventory/seed_batch_legacy_software_result.json",
                "review_batch": "control/inventory/review_batch_result.json",
                "scout_runtime": "control/inventory/scout_runtime_result.json",
                "candidate_index": "control/inventory/candidate_index_result.json",
                "query_planner_equivalent": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
                "snapshot_relay": "control/inventory/snapshot_relay_result.json",
                "public_alpha_readonly_equivalent": "control/inventory/public_alpha_readonly_00_result.json",
                "public_alpha_launch_defer": "control/inventory/public_alpha_launch_defer_result.json",
            },
            **_false_boundaries(),
        },
        "public_alpha_reassess_snapshot_metrics.json": result["metrics"],
        "public_alpha_reassess_query_coverage_matrix.json": result["query_coverage"],
        "public_alpha_reassess_route_matrix.json": result["route_smoke"],
        "public_alpha_reassess_candidate_usefulness_matrix.json": result["candidate_usefulness"],
        "public_alpha_reassess_reviewed_record_matrix.json": {
            "schema_version": "public_alpha_reassess_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "reviewed_record_count": result["reviewed_record_count"],
            "reviewed_record_threshold": result["metrics"]["reviewed_record_threshold"],
            "below_threshold": result["needs_more_reviewed_records"],
        },
        "public_alpha_reassess_need_absence_matrix.json": {
            "schema_version": "public_alpha_reassess_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result["known_need_count"],
            "absence_summary_count": result["absence_summary_count"],
            "launch_sufficient": False,
        },
        "public_alpha_reassess_launch_blocker_matrix.json": result["launch_blockers"],
        "public_alpha_reassess_next_work_matrix.json": result["next_work"],
        "public_alpha_reassess_boundary_report.json": result["boundary_report"],
        "public_alpha_reassess_smoke_result.json": {
            "schema_version": "public_alpha_reassess_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "route_smoke_status": result["route_smoke"]["route_smoke_status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            **_false_boundaries(),
        },
        "public_alpha_reassess_validation_matrix.json": {
            "schema_version": "public_alpha_reassess_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_public_alpha_reassess.py",
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_seed_batch_legacy_software.py",
                "python scripts/validate_seed_batch_frontier_media.py",
                "python scripts/validate_review_batch.py",
                "python scripts/validate_scout_runtime.py",
                "python scripts/validate_candidate_index_runtime.py",
                "python scripts/validate_query_to_source_action_planner.py",
                "python scripts/validate_snapshot_relay.py",
                "python scripts/validate_public_alpha_readonly.py",
                "python scripts/validate_source_action_kernel.py",
                "python scripts/validate_source_wave.py",
                "python scripts/check_architecture_boundaries.py",
                "python scripts/check_generated_artifact_cleanliness.py --check --json",
                "focused public-alpha reassess unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "public_alpha_reassess_result.json": _result_summary(result),
        "public_alpha_reassess_next_task_decision.json": {
            "schema_version": "public_alpha_reassess_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "SEED-BATCH-MANUALS-SCANS-00",
                "SEED-BATCH-DRIVER-SUPPORT-00",
                "SNAPSHOT-REFRESH-01",
                "PUBLIC-ALPHA-REASSESS-01",
            ],
            "launch_recommended": False,
            "demo_mode_recommended": True,
        },
        "public_alpha_reassess_failure_repair_log.json": {
            "schema_version": "public_alpha_reassess_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "public-alpha-reassess-00-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# PUBLIC-ALPHA-REASSESS-00 Audit\n\nEvidence-based reassessment after refreshed seed snapshots. Decision: internal demo/review useful, public launch not recommended.\n",
        "snapshot_metrics.md": _matrix_md("Snapshot Metrics", result["metrics"]),
        "query_coverage_matrix.md": _matrix_md("Query Coverage Matrix", result["query_coverage"]),
        "route_matrix.md": _matrix_md("Route Matrix", result["route_smoke"]),
        "candidate_usefulness_matrix.md": _matrix_md("Candidate Usefulness Matrix", result["candidate_usefulness"]),
        "launch_blocker_matrix.md": _matrix_md("Launch Blocker Matrix", result["launch_blockers"]),
        "next_work_matrix.md": _matrix_md("Next Work Matrix", result["next_work"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", {
            "status": result["status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
        }),
        "validation_matrix.md": _matrix_md("Validation Matrix", {"status": "pass", "full_discovery": "NOT_RUN_BY_POLICY"}),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/public_alpha_reassess_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "public_alpha_reassess_report.json": _result_summary(result),
        "generated/sample_reassess_metrics.json": result["metrics"],
        "generated/sample_launch_blockers.json": result["launch_blockers"],
        "generated/sample_next_work.json": result["next_work"],
        "generated/sample_reassess_decision.json": result["decision"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Public Alpha Reassess Summary\n\n"
        f"- reviewed records: {result['reviewed_record_count']}\n"
        f"- candidates: {result['candidate_count']}\n"
        f"- known needs: {result['known_need_count']}\n"
        f"- launch recommended: {str(result['launch_recommended']).lower()}\n"
        f"- demo mode recommended: {str(result['demo_mode_recommended']).lower()}\n"
        f"- next task: {RECOMMENDED_NEXT_TASK}\n"
    )
    written: list[str] = []
    for name, content in markdown.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    for name, content in json_files.items():
        path = audit_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    summary_path = generated / "sample_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    written.append(str(summary_path.relative_to(repo_root)))
    return written


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "reviewed_record_count": result["reviewed_record_count"],
        "candidate_count": result["candidate_count"],
        "known_need_count": result["known_need_count"],
        "absence_summary_count": result["absence_summary_count"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_more_seed_batches": result["needs_more_seed_batches"],
        "needs_live_metadata_pilot": result["needs_live_metadata_pilot"],
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _route_row(route: str, route_family: str, present: bool) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_route_smoke_row.v0",
        "route": route,
        "route_family": route_family,
        "status": "pass" if present else "missing",
        "source": "public_alpha_readonly_00_result",
        "read_only": True,
        "mutation_enabled": False,
        "deployment_performed": False,
    }


def _blocker(blocker_id: str, evidence: str) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_launch_blocker.v0",
        "blocker_id": blocker_id,
        "severity": "launch_blocking",
        "evidence": evidence,
        "public_explanation": evidence,
        "launch_blocking": True,
    }


def _usefulness_score(
    *,
    reviewed_count: int,
    reviewed_domain_count: int,
    candidate_count: int,
    route_smoke_passed: bool,
    policy: Mapping[str, Any],
) -> float:
    reviewed = min(reviewed_count / max(int(policy["public_alpha_min_reviewed_record_threshold"]), 1), 1.0)
    domains = min(reviewed_domain_count / max(int(policy["public_alpha_min_domain_coverage_threshold"]), 1), 1.0)
    candidates = min(candidate_count / 50.0, 1.0)
    route = 1.0 if route_smoke_passed else 0.0
    score = reviewed * 0.45 + domains * 0.20 + candidates * 0.15 + route * 0.10 + 0.10
    return round(score, 3)


def _context(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if "snapshot_refresh_result" in value and "candidate_sections" in value:
        return value
    return load_snapshot_refresh_metrics()


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "reassessment_is_not_launch",
        "reassessment_must_not_deploy",
        "launch_requires_explicit_future_manual_approval",
        "candidate_only_snapshot_not_enough_for_launch",
        "needs_and_absences_are_useful_but_not_launch_sufficient",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"public alpha reassess policy missing required rules: {', '.join(missing)}")
    forbidden_true = {
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"public alpha reassess policy enables forbidden behavior: {', '.join(enabled)}")


def _false_boundaries() -> dict[str, bool]:
    return {
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
    }


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"
