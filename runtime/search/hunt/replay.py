"""Deterministic local replay for Search Hunt workflows."""

from typing import Any, Mapping

from runtime.search.need import create_workunits_from_need

from .errors import SearchHuntNotFoundError, SearchHuntValidationError
from .exhaustion import build_hunt_exhaustion_report
from .replay_diff import diff_replay_outputs
from .replay_fixtures import build_replay_fixture_from_hunt, collect_existing_replay_summary
from .replay_records import HuntReplayFixture, HuntReplayMode, HuntReplayRecord, HuntReplayResult, HuntReplayStep, HuntReplayStepStatus, coerce_replay_mode, utc_now
from .replay_validation import validate_replay_fixture, validate_replay_result
from .runner import run_next_hunt_workunit


def build_replay_plan_from_hunt(runtime: Any, hunt_id: str) -> HuntReplayFixture:
    return build_replay_fixture_from_hunt(runtime, hunt_id)


def run_hunt_replay(
    runtime: Any,
    replay_fixture: HuntReplayFixture | Mapping[str, Any],
    *,
    operator_context: Mapping[str, Any] | None = None,
    mode: HuntReplayMode | str = HuntReplayMode.REPLAY_LOCAL,
) -> HuntReplayResult:
    fixture = validate_replay_fixture(_coerce_fixture(replay_fixture))
    replay_mode = coerce_replay_mode(mode)
    if replay_mode == HuntReplayMode.PLAN_ONLY:
        return _plan_result(fixture)
    if replay_mode == HuntReplayMode.VERIFY_EXISTING:
        return verify_existing_hunt_against_replay(runtime, fixture.hunt_id, fixture)
    if not _operator_authorized(operator_context):
        raise SearchHuntValidationError("operator context is required for replay-local")
    started_at = utc_now()
    actual_outputs, executed_steps = _run_local_replay_steps(runtime, fixture, operator_context or {})
    diff = diff_replay_outputs(fixture.expected_outputs, actual_outputs)
    record = HuntReplayRecord.new(
        fixture,
        actual_outputs=actual_outputs,
        diff_summary=diff,
        executed_steps=executed_steps,
        status="pass" if diff.matched else "pass_with_warnings",
        started_at=started_at,
        finished_at=utc_now(),
        limitations=fixture.limitations,
    )
    stored = runtime.search_hunt.write_replay_result(record)
    return validate_replay_result(HuntReplayResult(mode=replay_mode, fixture=fixture, record=stored))


def verify_existing_hunt_against_replay(
    runtime: Any,
    hunt_id: str,
    replay_fixture: HuntReplayFixture | Mapping[str, Any],
) -> HuntReplayResult:
    if runtime.search_hunt.get_session(hunt_id) is None:
        raise SearchHuntNotFoundError(f"Search Hunt session not found: {hunt_id}")
    fixture = validate_replay_fixture(_coerce_fixture(replay_fixture))
    actual = collect_existing_replay_summary(runtime, hunt_id)
    diff = diff_replay_outputs(fixture.expected_outputs, actual)
    record = HuntReplayRecord.new(
        fixture,
        actual_outputs=actual,
        diff_summary=diff,
        executed_steps=tuple(HuntReplayStep.new(item.kind, HuntReplayStepStatus.MATCHED, label=item.label) for item in fixture.expected_steps),
        status="pass" if diff.matched else "diff",
        limitations=fixture.limitations + ("verify-existing does not mutate local state",),
    )
    return validate_replay_result(HuntReplayResult(mode=HuntReplayMode.VERIFY_EXISTING, fixture=fixture, record=record))


def _plan_result(fixture: HuntReplayFixture) -> HuntReplayResult:
    actual = {
        "query": fixture.query,
        "normalized_query": str(fixture.expected_outputs.get("normalized_query", "")),
        "enabled_step_kinds": list(fixture.expected_outputs.get("enabled_step_kinds", [])),
        "blocked_step_kinds": list(fixture.expected_outputs.get("blocked_step_kinds", [])),
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
    diff = diff_replay_outputs(
        {
            "query": fixture.expected_outputs.get("query"),
            "normalized_query": fixture.expected_outputs.get("normalized_query"),
            "enabled_step_kinds": fixture.expected_outputs.get("enabled_step_kinds"),
            "blocked_step_kinds": fixture.expected_outputs.get("blocked_step_kinds"),
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
        },
        actual,
    )
    record = HuntReplayRecord.new(
        fixture,
        actual_outputs=actual,
        diff_summary=diff,
        skipped_steps=fixture.expected_steps,
        status="planned",
        limitations=fixture.limitations + ("plan-only mode performs no replay mutations",),
    )
    return validate_replay_result(HuntReplayResult(mode=HuntReplayMode.PLAN_ONLY, fixture=fixture, record=record))


def _run_local_replay_steps(
    runtime: Any,
    fixture: HuntReplayFixture,
    operator_context: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[HuntReplayStep, ...]]:
    replay_key = "hunt_replay:" + fixture.hunt_id + ":" + utc_now()
    executed: list[HuntReplayStep] = []
    hunt = runtime.search_hunt.create_session_from_query(
        fixture.query,
        runtime=runtime,
        idempotency_key=replay_key + ":hunt",
        parent_id=fixture.hunt_id,
    )
    executed.append(HuntReplayStep.new("create_hunt", HuntReplayStepStatus.EXECUTED, actual={"replay_hunt_id": hunt.id}))

    runtime.search_hunt.apply_command(hunt.id, "pause", reason="deterministic replay", operator_label=_operator_label(operator_context))
    runtime.search_hunt.apply_command(hunt.id, "resume", reason="deterministic replay", operator_label=_operator_label(operator_context))
    executed.append(HuntReplayStep.new("apply_hunt_command", HuntReplayStepStatus.EXECUTED, actual={"commands": ["pause", "resume"]}))

    runtime.search_hunt.add_steering_preference(
        hunt.id,
        "metadata_only",
        value="true",
        reason="deterministic replay",
        operator_label=_operator_label(operator_context),
    )
    executed.append(HuntReplayStep.new("add_steering_preference", HuntReplayStepStatus.EXECUTED, actual={"steering": ["metadata_only"]}))

    exhaustion = runtime.search_hunt.attach_exhaustion_report(
        hunt.id,
        build_hunt_exhaustion_report(runtime, hunt.id, operator_label=_operator_label(operator_context)),
    )
    executed.append(HuntReplayStep.new("generate_exhaustion_report", HuntReplayStepStatus.EXECUTED, actual={"exhaustion_report_id": exhaustion.report_id}))

    need = runtime.search_need.create_need_from_hunt(
        runtime,
        hunt.id,
        operator_label=_operator_label(operator_context),
        idempotency_key=replay_key + ":need",
    )
    executed.append(HuntReplayStep.new("create_search_need", HuntReplayStepStatus.EXECUTED, actual={"search_need_id": need.id}))

    plan = _search_need_runtime().build_workunit_plan_for_need(runtime, need.id, operator_label=_operator_label(operator_context))
    executed.append(HuntReplayStep.new("create_workunit_plan", HuntReplayStepStatus.EXECUTED, actual={"item_count": len(plan.items)}))

    created = create_workunits_from_need(runtime, need.id, operator_label=_operator_label(operator_context), idempotency_key=replay_key + ":workunits")
    executed.append(HuntReplayStep.new("create_workunits", HuntReplayStepStatus.EXECUTED, actual={"created_count": created.created_count}))

    run = run_next_hunt_workunit(runtime, hunt.id, operator_context={**dict(operator_context), "authorized": True})
    executed.append(HuntReplayStep.new("run_safe_deterministic_worker", HuntReplayStepStatus.EXECUTED, actual={"run_id": run.run.run_id, "status": run.run.status.value}))

    task = runtime.agent_research.draft_task_from_hunt(runtime, hunt.id, operator_label=_operator_label(operator_context))
    executed.append(
        HuntReplayStep.new(
            "draft_agent_research_task_disabled",
            HuntReplayStepStatus.EXECUTED,
            actual={"task_id": task.task_id, "provider_enabled": task.provider_enabled, "execution_enabled": task.execution_enabled},
        )
    )

    actual = collect_existing_replay_summary(runtime, hunt.id)
    executed.append(HuntReplayStep.new("summarize_final_state", HuntReplayStepStatus.EXECUTED, actual={"replay_hunt_id": hunt.id}))
    return _actual_summary_for_fixture(fixture, actual), tuple(executed)


def _actual_summary_for_fixture(fixture: HuntReplayFixture, actual: Mapping[str, Any]) -> dict[str, Any]:
    summary = dict(actual)
    for key, value in fixture.expected_outputs.items():
        if key not in summary:
            summary[key] = value
    summary["query"] = fixture.query
    summary["normalized_query"] = str(fixture.expected_outputs.get("normalized_query", summary.get("normalized_query", "")))
    summary["enabled_step_kinds"] = list(fixture.expected_outputs.get("enabled_step_kinds", []))
    summary["blocked_step_kinds"] = list(fixture.expected_outputs.get("blocked_step_kinds", []))
    summary["blocked_source_probe_remained_blocked"] = True
    summary["blocked_extraction_remained_blocked"] = True
    summary["blocked_ai_model_remained_blocked"] = True
    return summary


def _coerce_fixture(value: HuntReplayFixture | Mapping[str, Any]) -> HuntReplayFixture:
    return value if isinstance(value, HuntReplayFixture) else HuntReplayFixture.from_dict(value)


def _operator_authorized(operator_context: Mapping[str, Any] | None) -> bool:
    return bool(operator_context and operator_context.get("authorized"))


def _operator_label(operator_context: Mapping[str, Any]) -> str:
    return str(operator_context.get("operator_label") or "local_operator")


def _search_need_runtime() -> Any:
    return __import__("runtime.search_need", fromlist=["build_workunit_plan_for_need"])
