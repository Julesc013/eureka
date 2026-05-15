"""Build disabled agent research task drafts from local hunt context."""

from typing import Any, Mapping

from .records import AgentResearchTask
from .report_schema import build_agent_research_report_schema
from .validation import validate_agent_research_task


def build_agent_research_task_from_hunt(runtime: Any, hunt_id: str) -> AgentResearchTask:
    packet = build_agent_research_input_packet(runtime, hunt_id=hunt_id)
    task = AgentResearchTask.new(
        search_hunt_id=str(packet["search_hunt_id"]),
        search_need_id=str(packet.get("search_need_id", "")),
        exhaustion_report_id=str(packet["exhaustion_report_id"]),
        query=str(packet["query"]),
        intent=str(packet.get("intent", "")),
        destination=str(packet.get("destination", "")),
        checked_layers=tuple(packet.get("checked_layers", ())),
        deferred_layers=tuple(packet.get("deferred_layers", ())),
        blocked_by_policy=tuple(packet.get("blocked_by_policy", ())),
        known_candidates=tuple(packet.get("known_candidates", ())),
        known_absence_state=str(packet.get("known_absence_state", "")),
        steering_preferences=tuple(packet.get("steering_preferences", ())),
        allowed_source_families=tuple(packet.get("allowed_source_families", ())),
        blocked_source_families=tuple(packet.get("blocked_source_families", ())),
        output_schema=build_agent_research_report_schema().to_dict(),
    )
    return validate_agent_research_task(task)


def build_agent_research_task_from_need(runtime: Any, need_id: str) -> AgentResearchTask:
    need = runtime.search_need.get_need(need_id)
    if need is None:
        errors = __import__("runtime.search_need.errors", fromlist=["SearchNeedNotFoundError"])
        raise errors.SearchNeedNotFoundError(f"SearchNeed not found: {need_id}")
    packet = build_agent_research_input_packet(runtime, hunt_id=need.hunt_id, need_id=need.id)
    task = AgentResearchTask.new(
        search_hunt_id=str(packet["search_hunt_id"]),
        search_need_id=need.id,
        exhaustion_report_id=str(packet["exhaustion_report_id"]),
        query=need.query,
        intent=str(packet.get("intent", "")),
        destination=str(packet.get("destination", "")),
        checked_layers=tuple(packet.get("checked_layers", ())),
        deferred_layers=tuple(packet.get("deferred_layers", ())),
        blocked_by_policy=tuple(packet.get("blocked_by_policy", ())),
        known_candidates=tuple(packet.get("known_candidates", ())),
        known_absence_state=str(packet.get("known_absence_state", need.local_result_state)),
        steering_preferences=tuple(packet.get("steering_preferences", ())),
        allowed_source_families=tuple(packet.get("allowed_source_families", ())),
        blocked_source_families=tuple(packet.get("blocked_source_families", ())),
        output_schema=build_agent_research_report_schema().to_dict(),
    )
    return validate_agent_research_task(task)


def build_agent_research_input_packet(runtime: Any, hunt_id: str | None = None, need_id: str | None = None) -> dict[str, Any]:
    if need_id and not hunt_id:
        need = runtime.search_need.get_need(need_id)
        if need is None:
            errors = __import__("runtime.search_need.errors", fromlist=["SearchNeedNotFoundError"])
            raise errors.SearchNeedNotFoundError(f"SearchNeed not found: {need_id}")
        hunt_id = need.hunt_id
    hunt = runtime.search_hunt.get_session(str(hunt_id or ""))
    if hunt is None:
        errors = __import__("runtime.search_hunt.errors", fromlist=["SearchHuntNotFoundError"])
        raise errors.SearchHuntNotFoundError(f"Search Hunt session not found: {hunt_id}")
    report = runtime.search_hunt.get_latest_exhaustion_report(hunt.id)
    if report is None:
        raise ValueError("agent research task draft requires an existing exhaustion report")
    report_payload = report.to_dict()
    steering = [item.to_dict() for item in runtime.search_hunt.list_steering_preferences(hunt.id, active_only=True)]
    linked_needs = runtime.search_need.list_needs_for_hunt(hunt.id, limit=1)
    chosen_need_id = str(need_id or (linked_needs[0].id if linked_needs else ""))
    return {
        "schema_version": "agent_research_input_packet.v0",
        "search_hunt_id": hunt.id,
        "search_need_id": chosen_need_id,
        "exhaustion_report_id": report.report_id,
        "query": hunt.query,
        "normalized_query": hunt.normalized_query,
        "intent": hunt.intent.value,
        "destination": hunt.destination.value,
        "checked_layers": _layer_names(report_payload.get("checked_layers")),
        "deferred_layers": _layer_names(report_payload.get("unchecked_or_deferred_layers")),
        "blocked_by_policy": _policy_names(report_payload.get("blocked_by_policy")),
        "known_candidates": _known_candidates(report_payload),
        "known_absence_state": str(_mapping(report_payload.get("result_state")).get("absence_state", "")),
        "steering_preferences": steering,
        "allowed_source_families": _source_families(steering, "include_source_family"),
        "blocked_source_families": _source_families(steering, "exclude_source_family"),
        "provider_enabled": False,
        "execution_enabled": False,
        "source_probe_enabled": False,
    }


def _known_candidates(report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    result_state = _mapping(report.get("result_state"))
    count = int(result_state.get("reviewed_result_count", 0) or 0)
    if count <= 0:
        return ()
    return ({"candidate_family": "reviewed_local_index", "reviewed_result_count": count, "candidate_only": True},)


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


def _source_families(steering: list[Mapping[str, Any]], command_type: str) -> tuple[str, ...]:
    return tuple(str(item.get("value", "")) for item in steering if item.get("command_type") == command_type and item.get("value"))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    return value if isinstance(value, (list, tuple)) else ()
