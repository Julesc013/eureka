"""Search hunt WorkUnit selection for deterministic local workers."""

from typing import Any, Mapping

from runtime.local.worker import BLOCKED_WORKER_KINDS, ENABLED_WORKER_KINDS, LocalWorkerRunner
from runtime.local.worker.policy import evaluate_worker_policy
from runtime.worker.workunit_queue import WorkUnitState

from .errors import SearchHuntNotFoundError
from .run_records import BackgroundHuntPlan, BackgroundHuntPlanItem, BackgroundHuntWorkerPolicyDecision
from .validation import validate_limit


MAX_BACKGROUND_HUNT_BATCH = 10
DEFAULT_BACKGROUND_HUNT_LIMIT = 1


def build_background_hunt_plan(
    runtime: Any,
    hunt_id: str,
    *,
    limit: int = MAX_BACKGROUND_HUNT_BATCH,
    operator_context: Mapping[str, Any] | None = None,
) -> BackgroundHuntPlan:
    if runtime.search_hunt.get_session(hunt_id) is None:
        raise SearchHuntNotFoundError(f"Search Hunt session not found: {hunt_id}")
    bounded_limit = min(validate_limit(limit), MAX_BACKGROUND_HUNT_BATCH)
    runner = LocalWorkerRunner(runtime)
    items = []
    for workunit in _hunt_workunits(runtime, hunt_id, limit=500):
        if len(items) >= bounded_limit:
            break
        items.append(_plan_item(runtime, runner, workunit, hunt_id, operator_context))
    return BackgroundHuntPlan(hunt_id=str(hunt_id), items=tuple(items))


def select_runnable_hunt_workunits(plan: BackgroundHuntPlan, *, limit: int = DEFAULT_BACKGROUND_HUNT_LIMIT) -> tuple[BackgroundHuntPlanItem, ...]:
    bounded = max(1, min(int(limit or DEFAULT_BACKGROUND_HUNT_LIMIT), MAX_BACKGROUND_HUNT_BATCH))
    return plan.runnable_items[:bounded]


def _hunt_workunits(runtime: Any, hunt_id: str, *, limit: int) -> list[Any]:
    results = []
    for workunit in runtime.workunit_queue.list_workunits(limit=limit):
        payload = _mapping(getattr(workunit, "payload", {}))
        if str(payload.get("search_hunt_id") or "") == str(hunt_id):
            results.append(workunit)
    return results


def _plan_item(
    runtime: Any,
    runner: LocalWorkerRunner,
    workunit: Any,
    hunt_id: str,
    operator_context: Mapping[str, Any] | None,
) -> BackgroundHuntPlanItem:
    payload = _mapping(getattr(workunit, "payload", {}))
    worker_kind = runner._resolve_worker_kind(workunit, None)
    policy_payload = evaluate_worker_policy(workunit, worker_kind, operator_context)
    policy = BackgroundHuntWorkerPolicyDecision.from_mapping(policy_payload, getattr(workunit, "id", ""))
    state = getattr(getattr(workunit, "state", ""), "value", str(getattr(workunit, "state", "")))
    policy_state = str(payload.get("policy_state") or "")
    disabled_kind = worker_kind in BLOCKED_WORKER_KINDS or worker_kind not in ENABLED_WORKER_KINDS
    queued = state == WorkUnitState.QUEUED.value
    runnable = queued and bool(policy.allowed) and not disabled_kind
    blocked_reason = _blocked_reason(workunit, policy, disabled_kind, queued)
    return BackgroundHuntPlanItem(
        workunit_id=str(getattr(workunit, "id", "")),
        search_need_id=str(payload.get("search_need_id") or ""),
        hunt_id=str(payload.get("search_hunt_id") or hunt_id),
        exhaustion_report_id=str(payload.get("exhaustion_report_id") or ""),
        workunit_kind=getattr(getattr(workunit, "kind", ""), "value", str(getattr(workunit, "kind", ""))),
        worker_kind=worker_kind,
        state=state,
        title=str(getattr(workunit, "title", "")),
        policy_state=policy_state,
        runnable=runnable,
        blocked_reason=blocked_reason,
        policy_decision=policy,
    )


def _blocked_reason(workunit: Any, policy: BackgroundHuntWorkerPolicyDecision, disabled_kind: bool, queued: bool) -> str:
    if queued and policy.allowed and not disabled_kind:
        return ""
    stored_reason = str(getattr(workunit, "blocked_reason", "") or "")
    if stored_reason:
        return stored_reason
    if disabled_kind:
        return "worker kind is disabled by background hunt policy"
    if not queued:
        state = getattr(getattr(workunit, "state", ""), "value", str(getattr(workunit, "state", "")))
        return f"workunit state is {state}"
    return policy.reason or "worker is blocked by policy"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
