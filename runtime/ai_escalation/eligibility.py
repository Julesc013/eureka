"""Eligibility evaluation for disabled AI escalation gates."""

from typing import Any, Mapping

from .records import (
    AIEscalationEligibility,
    AIEscalationForbiddenAction,
    AIEscalationGateState,
    AIEscalationInputPacket,
    DEFAULT_LIMITATIONS,
    default_output_schema,
    normalize_query,
)


def evaluate_ai_escalation_eligibility(runtime: Any, hunt_id: str | None = None, need_id: str | None = None) -> AIEscalationEligibility:
    hunt = None
    need = None
    report = None
    task = None
    missing: list[str] = []
    warnings: list[str] = []

    if need_id:
        need = runtime.search_need.get_need(str(need_id))
        if need is None:
            missing.append("search_need")
        else:
            hunt_id = need.hunt_id
    if hunt_id:
        hunt = runtime.search_hunt.get_session(str(hunt_id))
        if hunt is None:
            missing.append("search_hunt")
    if hunt is not None:
        report = runtime.search_hunt.get_latest_exhaustion_report(hunt.id)
        if report is None:
            missing.append("exhaustion_report")
        linked_needs = runtime.search_need.list_needs_for_hunt(hunt.id, limit=1)
        if need is None and linked_needs:
            need = linked_needs[0]
        if need is None:
            missing.append("search_need")
        tasks = runtime.agent_research.list_tasks(hunt_id=hunt.id, need_id=need.id if need else None, limit=1)
        if not tasks and need is not None:
            tasks = runtime.agent_research.list_tasks(need_id=need.id, limit=1)
        task = tasks[0] if tasks else None
        if task is None:
            missing.append("agent_research_task")
    else:
        if "search_hunt" not in missing:
            missing.append("search_hunt")

    state = _state_for_missing(missing)
    eligible = not missing and state == AIEscalationGateState.ELIGIBLE_BUT_DISABLED
    if eligible:
        warnings.append("provider gate is still disabled")
    packet = _build_input_packet(hunt, need, report, task)
    return AIEscalationEligibility(
        state=state,
        eligible=eligible,
        input_packet=packet,
        missing_requirements=tuple(dict.fromkeys(missing)),
        warnings=tuple(warnings),
        limitations=DEFAULT_LIMITATIONS,
    )


def _state_for_missing(missing: list[str]) -> AIEscalationGateState:
    if "exhaustion_report" in missing:
        return AIEscalationGateState.BLOCKED_MISSING_EXHAUSTION_REPORT
    if "search_need" in missing:
        return AIEscalationGateState.BLOCKED_MISSING_SEARCH_NEED
    if missing:
        return AIEscalationGateState.BLOCKED_BY_POLICY
    return AIEscalationGateState.ELIGIBLE_BUT_DISABLED


def _build_input_packet(hunt: Any, need: Any, report: Any, task: Any) -> AIEscalationInputPacket:
    hunt_payload = hunt.to_dict() if hunt is not None else {}
    need_payload = need.to_dict() if need is not None else {}
    report_payload = report.to_dict() if report is not None else {}
    task_payload = task.to_dict() if task is not None else {}
    query = str(need_payload.get("query") or hunt_payload.get("query") or task_payload.get("query") or "")
    return AIEscalationInputPacket(
        search_hunt_id=str(hunt_payload.get("id") or need_payload.get("hunt_id") or task_payload.get("search_hunt_id") or ""),
        search_need_id=str(need_payload.get("id") or task_payload.get("search_need_id") or ""),
        exhaustion_report_id=str(
            need_payload.get("exhaustion_report_id")
            or report_payload.get("report_id")
            or task_payload.get("exhaustion_report_id")
            or ""
        ),
        agent_research_task_id=str(task_payload.get("task_id") or ""),
        query=query,
        normalized_query=str(need_payload.get("normalized_query") or hunt_payload.get("normalized_query") or normalize_query(query)),
        checked_layers=_layer_names(report_payload.get("checked_layers")) or tuple_text(need_payload.get("checked_layers")),
        deferred_layers=_layer_names(report_payload.get("unchecked_or_deferred_layers")) or tuple_text(need_payload.get("deferred_layers")),
        blocked_by_policy=_policy_names(report_payload.get("blocked_by_policy")),
        steering_preferences=tuple_mapping(task_payload.get("steering_preferences")),
        candidate_context=_candidate_context(report_payload, task_payload),
        absence_context=_absence_context(report_payload, need_payload, task_payload),
        forbidden_actions=tuple(AIEscalationForbiddenAction),
        desired_output_schema=default_output_schema(),
        provider_enabled=False,
        execution_enabled=False,
    )


def _candidate_context(report: Mapping[str, Any], task: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    candidates = tuple_mapping(task.get("known_candidates"))
    if candidates:
        return candidates
    result_state = _mapping(report.get("result_state"))
    count = int(result_state.get("reviewed_result_count", 0) or 0)
    if count <= 0:
        return ()
    return ({"candidate_family": "reviewed_local_index", "reviewed_result_count": count, "candidate_only": True},)


def _absence_context(report: Mapping[str, Any], need: Mapping[str, Any], task: Mapping[str, Any]) -> Mapping[str, Any]:
    result_state = _mapping(report.get("result_state"))
    return {
        "absence_state": str(result_state.get("absence_state") or need.get("local_result_state") or task.get("known_absence_state") or ""),
        "local_result_state": str(need.get("local_result_state") or ""),
        "candidate_only": True,
        "review_required": True,
    }


def _layer_names(value: Any) -> tuple[str, ...]:
    names = []
    for item in _sequence(value):
        payload = _mapping(item)
        name = str(payload.get("layer", payload.get("name", "")))
        if name:
            names.append(name)
    return tuple(names)


def _policy_names(value: Any) -> tuple[str, ...]:
    names = []
    for item in _sequence(value):
        payload = _mapping(item)
        name = str(payload.get("policy_id", ""))
        if name:
            names.append(name)
    return tuple(names)


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def tuple_mapping(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(dict(item) for item in value if isinstance(item, Mapping))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return value if isinstance(value, (list, tuple)) else ()
