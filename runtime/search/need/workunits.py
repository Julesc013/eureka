"""Create and inspect WorkUnits derived from SearchNeeds."""

from typing import Any

from runtime.worker.workunit_queue.records import WorkUnit, WorkUnitState

from .workunit_plan import (
    SearchNeedWorkUnitCreationResult,
    SearchNeedWorkUnitPlan,
    SearchNeedWorkUnitPolicyState,
    build_workunit_plan_for_need,
    validate_workunit_plan,
)


def create_workunits_from_need(
    runtime: Any,
    need_id: str,
    *,
    operator_label: str | None = None,
    idempotency_key: str | None = None,
) -> SearchNeedWorkUnitCreationResult:
    plan = validate_workunit_plan(build_workunit_plan_for_need(runtime, need_id, operator_label=operator_label))
    created: list[dict[str, Any]] = []
    linked_count = 0
    base_key = idempotency_key or "search_need_workunit:" + plan.need_id
    for item in plan.items:
        key = base_key + ":" + item.plan_item_id
        workunit = WorkUnit.new(
            item.kind,
            item.title,
            payload=item.payload,
            priority=item.priority,
            idempotency_key=key,
            parent_id=plan.need_id,
            warnings=(
                "WorkUnit was created from a local SearchNeed",
                "WorkUnit execution remains disabled",
            ),
            limitations=(
                "source probes, extraction, and model/provider calls remain disabled",
                "reviewed public and master indexes are not mutated by creation",
            ),
        )
        stored = runtime.workunit_queue.create_workunit(workunit)
        if item.policy_state in {
            SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY,
            SearchNeedWorkUnitPolicyState.BLOCKED_UNTIL_EVIDENCE,
        } and stored.state != WorkUnitState.BLOCKED:
            stored = runtime.workunit_queue.block_workunit(stored.id, item.blocked_reason or item.reason)
        linked_count += _record_links(runtime, stored.id, plan)
        created.append(_workunit_payload(stored.to_dict()))
    return SearchNeedWorkUnitCreationResult(
        need_id=plan.need_id,
        search_hunt_id=plan.search_hunt_id,
        exhaustion_report_id=plan.exhaustion_report_id,
        plan=plan,
        workunits=tuple(created),
        created_count=len(created),
        linked_count=linked_count,
        warnings=(),
        limitations=(
            "WorkUnits were created only as local queue records",
            "WorkUnit execution was not performed",
        ),
    )


def list_workunits_for_need(runtime: Any, need_id: str, limit: int = 100) -> list[dict[str, Any]]:
    results = []
    for workunit in runtime.workunit_queue.list_workunits(limit=limit):
        payload = dict(workunit.payload)
        if str(payload.get("search_need_id", "")) == str(need_id):
            results.append(_workunit_payload(workunit.to_dict()))
    return results


def list_workunits_for_hunt(runtime: Any, hunt_id: str, limit: int = 100) -> list[dict[str, Any]]:
    results = []
    for workunit in runtime.workunit_queue.list_workunits(limit=limit):
        payload = dict(workunit.payload)
        if str(payload.get("search_hunt_id", "")) == str(hunt_id):
            results.append(_workunit_payload(workunit.to_dict()))
    return results


def list_runnable_workunits_for_hunt(runtime: Any, hunt_id: str, limit: int = 100) -> list[dict[str, Any]]:
    return [
        item
        for item in list_workunits_for_hunt(runtime, hunt_id, limit=limit)
        if item.get("state") == "queued" and item.get("policy_state") == "queued_local_safe"
    ]


def _record_links(runtime: Any, workunit_id: str, plan: SearchNeedWorkUnitPlan) -> int:
    count = 0
    existing = {
        (str(ref.ref_kind), str(ref.ref_id))
        for ref in runtime.workunit_queue.list_payload_refs(workunit_id, limit=500)
    }
    for ref_kind, ref_id in (
        ("search_need", plan.need_id),
        ("search_hunt", plan.search_hunt_id),
        ("exhaustion_report", plan.exhaustion_report_id),
    ):
        if ref_id and (ref_kind, ref_id) not in existing:
            runtime.workunit_queue.record_payload_ref(workunit_id, ref_kind, ref_id)
            count += 1
    return count


def _workunit_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    work_payload = dict(result.get("payload", {}))
    result["payload"] = work_payload
    result["search_need_id"] = work_payload.get("search_need_id")
    result["search_hunt_id"] = work_payload.get("search_hunt_id")
    result["exhaustion_report_id"] = work_payload.get("exhaustion_report_id")
    result["policy_state"] = work_payload.get("policy_state")
    result["execution_enabled"] = False
    result["source_probe_enabled"] = False
    result["extraction_enabled"] = False
    result["model_provider_enabled"] = False
    return result
