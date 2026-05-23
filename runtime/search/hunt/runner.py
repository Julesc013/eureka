"""Background Search Hunt runner over deterministic local workers."""

from typing import Any, Mapping

from runtime.local.worker import LocalWorkerRunner

from .run_records import BackgroundHuntRun, BackgroundHuntRunResult, BackgroundHuntRunStatus, utc_now
from .workunit_runner import DEFAULT_BACKGROUND_HUNT_LIMIT, MAX_BACKGROUND_HUNT_BATCH, build_background_hunt_plan, select_runnable_hunt_workunits


def run_next_hunt_workunit(
    runtime: Any,
    hunt_id: str,
    *,
    operator_context: Mapping[str, Any] | None = None,
) -> BackgroundHuntRunResult:
    return run_background_hunt_batch(runtime, hunt_id, limit=DEFAULT_BACKGROUND_HUNT_LIMIT, operator_context=operator_context, mode="run_next")


def run_background_hunt_batch(
    runtime: Any,
    hunt_id: str,
    *,
    limit: int = DEFAULT_BACKGROUND_HUNT_LIMIT,
    operator_context: Mapping[str, Any] | None = None,
    mode: str = "run_batch",
) -> BackgroundHuntRunResult:
    bounded = max(1, min(int(limit or DEFAULT_BACKGROUND_HUNT_LIMIT), MAX_BACKGROUND_HUNT_BATCH))
    plan = build_background_hunt_plan(runtime, hunt_id, limit=MAX_BACKGROUND_HUNT_BATCH, operator_context=operator_context)
    selected = select_runnable_hunt_workunits(plan, limit=bounded)
    started_at = utc_now()
    worker_results = []
    runner = LocalWorkerRunner(runtime)
    for item in selected:
        worker_results.append(runner.run_one(item.workunit_id, worker_kind=item.worker_kind, operator_context=operator_context).to_dict())
    status = _run_status(worker_results, selected)
    search_need_ids = tuple(sorted({item.search_need_id for item in selected if item.search_need_id} | {item.search_need_id for item in plan.blocked_items if item.search_need_id}))
    workunit_ids = tuple(item.workunit_id for item in selected)
    worker_kinds = tuple(item.worker_kind for item in selected)
    run = BackgroundHuntRun.new(
        hunt_id,
        status=status,
        search_need_ids=search_need_ids,
        workunit_ids=workunit_ids,
        worker_kinds=worker_kinds,
        started_at=started_at,
        finished_at=utc_now(),
        policy_decision={
            "schema_version": "background_hunt_policy_decision.v0",
            "status": "allowed" if selected else "skipped",
            "allowed": bool(selected),
            "reason": "safe deterministic WorkUnits selected" if selected else "no runnable WorkUnits were available",
            "source_probe_execution_enabled": False,
            "extraction_execution_enabled": False,
            "model_provider_enabled": False,
            "external_network_enabled": False,
        },
        worker_results=tuple(worker_results),
        blocked_workunits=tuple(item.to_dict() for item in plan.blocked_items),
        warnings=(),
        limitations=(
            "background runner only uses deterministic local workers",
            "policy-blocked WorkUnits remain blocked",
        ),
    )
    runtime.search_hunt.record_background_hunt_run(run)
    return BackgroundHuntRunResult(hunt_id=str(hunt_id), mode=mode, plan=plan, run=run)


def list_background_hunt_runs(runtime: Any, hunt_id: str | None = None, limit: int = 100) -> list[BackgroundHuntRun]:
    return runtime.search_hunt.list_background_hunt_runs(hunt_id=hunt_id, limit=limit)


def summarize_background_hunt(runtime: Any, hunt_id: str) -> dict[str, Any]:
    plan = build_background_hunt_plan(runtime, hunt_id, limit=MAX_BACKGROUND_HUNT_BATCH)
    runs = [item.to_dict() for item in list_background_hunt_runs(runtime, hunt_id=hunt_id, limit=20)]
    return {
        "schema_version": "background_hunt_summary.v0",
        "status": "pass",
        "hunt_id": str(hunt_id),
        "plan": plan.to_dict(),
        "latest_run": runs[0] if runs else None,
        "runs": runs,
        "run_count": len(runs),
        "runnable_count": len(plan.runnable_items),
        "blocked_count": len(plan.blocked_items),
        "safe_runnable_count": len(plan.runnable_items),
        "blocked_workunit_count": len(plan.blocked_items),
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "deployment_performed": False,
    }


def _run_status(worker_results: list[Mapping[str, Any]], selected: tuple[Any, ...]) -> BackgroundHuntRunStatus:
    if not selected:
        return BackgroundHuntRunStatus.SKIPPED
    statuses = {str(item.get("status") or "") for item in worker_results}
    if "failed" in statuses:
        return BackgroundHuntRunStatus.FAILED
    if "blocked" in statuses:
        return BackgroundHuntRunStatus.BLOCKED
    return BackgroundHuntRunStatus.COMPLETE
