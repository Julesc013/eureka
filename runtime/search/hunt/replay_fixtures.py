"""Build deterministic replay fixtures from local Search Hunt state."""

from typing import Any, Mapping

from .errors import SearchHuntNotFoundError
from .replay_records import (
    BLOCKED_REPLAY_STEP_KINDS,
    ENABLED_REPLAY_STEP_KINDS,
    HuntReplayFixture,
    HuntReplayStep,
    HuntReplayStepStatus,
    utc_now,
)
from .replay_validation import validate_replay_fixture


def build_replay_fixture_from_hunt(runtime: Any, hunt_id: str) -> HuntReplayFixture:
    hunt = runtime.search_hunt.get_session(hunt_id)
    if hunt is None:
        raise SearchHuntNotFoundError(f"Search Hunt session not found: {hunt_id}")
    expected_outputs = expected_output_summary(runtime, hunt_id)
    fixture = HuntReplayFixture(
        replay_source="local_search_hunt_record",
        hunt_id=hunt.id,
        query=hunt.query,
        instance_schema_version=str(getattr(getattr(runtime, "instance_ref", None), "instance_schema_version", "")),
        index_snapshot_id=str(hunt.index_snapshot_id or "local_current_index"),
        expected_steps=tuple(
            HuntReplayStep.new(kind, HuntReplayStepStatus.PLANNED, label=kind.value.replace("_", " "))
            for kind in ENABLED_REPLAY_STEP_KINDS
        ),
        blocked_steps=tuple(
            HuntReplayStep.new(
                kind,
                HuntReplayStepStatus.BLOCKED,
                label=kind.value.replace("_", " "),
                limitations=("blocked future actions are listed but not replayed",),
            )
            for kind in BLOCKED_REPLAY_STEP_KINDS
        ),
        expected_outputs=expected_outputs,
        warnings=(),
        limitations=(
            "replay uses local instance state only",
            "blocked future actions remain blocked",
            "replay does not prove truth or broad absence",
        ),
        created_at=utc_now(),
    )
    return validate_replay_fixture(fixture)


def expected_output_summary(runtime: Any, hunt_id: str) -> dict[str, Any]:
    hunt = runtime.search_hunt.get_session(hunt_id)
    if hunt is None:
        raise SearchHuntNotFoundError(f"Search Hunt session not found: {hunt_id}")
    return {
        "query": hunt.query,
        "normalized_query": hunt.normalized_query,
        "enabled_step_kinds": [item.value for item in ENABLED_REPLAY_STEP_KINDS],
        "blocked_step_kinds": [item.value for item in BLOCKED_REPLAY_STEP_KINDS],
        "exhaustion_report_present": True,
        "search_need_created": True,
        "workunit_plan_present": True,
        "workunits_created": True,
        "safe_worker_run_recorded": True,
        "agent_research_task_drafted": True,
        "blocked_source_probe_remained_blocked": True,
        "blocked_extraction_remained_blocked": True,
        "blocked_ai_model_remained_blocked": True,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def collect_existing_replay_summary(runtime: Any, hunt_id: str) -> dict[str, Any]:
    hunt = runtime.search_hunt.get_session(hunt_id)
    if hunt is None:
        raise SearchHuntNotFoundError(f"Search Hunt session not found: {hunt_id}")
    return {
        "query": hunt.query,
        "normalized_query": hunt.normalized_query,
        "enabled_step_kinds": [item.value for item in ENABLED_REPLAY_STEP_KINDS],
        "blocked_step_kinds": [item.value for item in BLOCKED_REPLAY_STEP_KINDS],
        "exhaustion_report_present": runtime.search_hunt.get_latest_exhaustion_report(hunt_id) is not None,
        "search_need_created": bool(runtime.search_need.list_needs_for_hunt(hunt_id, limit=1)),
        "workunit_plan_present": True,
        "workunits_created": bool(_hunt_workunits(runtime, hunt_id)),
        "safe_worker_run_recorded": bool(runtime.search_hunt.list_background_hunt_runs(hunt_id=hunt_id, limit=1)),
        "agent_research_task_drafted": bool(runtime.agent_research.list_tasks(hunt_id=hunt_id, limit=1)),
        "blocked_source_probe_remained_blocked": True,
        "blocked_extraction_remained_blocked": True,
        "blocked_ai_model_remained_blocked": True,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _hunt_workunits(runtime: Any, hunt_id: str) -> list[Mapping[str, Any]]:
    rows = []
    for workunit in runtime.workunit_queue.list_workunits(limit=500):
        payload = getattr(workunit, "payload", {})
        if isinstance(payload, Mapping) and str(payload.get("search_hunt_id") or "") == str(hunt_id):
            rows.append(workunit.to_dict())
    return rows
