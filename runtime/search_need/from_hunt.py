"""Build SearchNeeds from unresolved local Search Hunt Sessions."""

from typing import Any, Mapping

from runtime.search_hunt import build_hunt_exhaustion_report

from .records import SearchNeed, SearchNeedDesiredOutcome, SearchNeedKind
from .validation import validate_need_creation_from_hunt


def build_search_need_from_hunt(runtime: Any, hunt_id: str, *, operator_label: str | None = None) -> SearchNeed:
    hunt = runtime.search_hunt.get_session(hunt_id)
    report = runtime.search_hunt.get_latest_exhaustion_report(hunt_id) if hunt is not None else None
    if hunt is not None and report is None:
        generated = build_hunt_exhaustion_report(runtime, hunt_id, operator_label=operator_label)
        report = runtime.search_hunt.attach_exhaustion_report(hunt_id, generated)
    validate_need_creation_from_hunt(hunt, report)
    report_payload = report.to_dict()
    result_state = _mapping(report_payload.get("result_state"))
    query_summary = _mapping(report_payload.get("query_summary"))
    return SearchNeed.new(
        hunt_id=hunt.id,
        exhaustion_report_id=report.report_id,
        query=hunt.query,
        need_title=derive_need_title(hunt, report_payload),
        need_summary=derive_need_summary(hunt, report_payload),
        need_kind=derive_need_kind(hunt, report_payload),
        desired_outcome=derive_desired_outcome(hunt, report_payload),
        local_result_state=str(result_state.get("confidence_class", "local_not_evaluated")),
        checked_layers=tuple(_layer_names(report_payload.get("checked_layers"))),
        deferred_layers=tuple(_layer_names(report_payload.get("unchecked_or_deferred_layers"))),
        recommended_future_work=build_recommended_future_work(report_payload),
        priority=derive_priority(query_summary, result_state),
        warnings=tuple(str(item) for item in report_payload.get("warnings", []) if item),
    )


def derive_need_kind(hunt: Any, exhaustion_report: Mapping[str, Any]) -> SearchNeedKind:
    result_state = _mapping(exhaustion_report.get("result_state"))
    confidence = str(result_state.get("confidence_class", ""))
    if confidence == "local_blocked":
        return SearchNeedKind.POLICY_BLOCKED_NEED
    if confidence == "local_absent":
        return SearchNeedKind.IMPROVE_ABSENCE_REPORT
    if confidence == "local_weak_hit":
        return SearchNeedKind.IMPROVE_RANKING_OR_IDENTITY
    if "source" in str(getattr(hunt, "query", "")).lower():
        return SearchNeedKind.FIND_SOURCE_OR_MIRROR
    return SearchNeedKind.FIND_EXACT_ARTIFACT


def derive_desired_outcome(hunt: Any, exhaustion_report: Mapping[str, Any]) -> SearchNeedDesiredOutcome:
    result_state = _mapping(exhaustion_report.get("result_state"))
    confidence = str(result_state.get("confidence_class", ""))
    if confidence in {"local_absent", "local_not_evaluated"}:
        return SearchNeedDesiredOutcome.IMPROVE_INDEX
    if confidence == "local_blocked":
        return SearchNeedDesiredOutcome.VERIFY_ONLY
    return SearchNeedDesiredOutcome.CITE_OR_REFERENCE


def build_recommended_future_work(exhaustion_report: Mapping[str, Any]) -> tuple[str, ...]:
    actions = []
    for item in _sequence(exhaustion_report.get("recommended_next_actions")):
        value = _mapping(item)
        action = str(value.get("action", ""))
        if action:
            actions.append(action)
    return tuple(actions)


def derive_need_title(hunt: Any, exhaustion_report: Mapping[str, Any]) -> str:
    query = str(getattr(hunt, "query", "")).strip()
    return f"Investigate unresolved local search: {query}"[:160]


def derive_need_summary(hunt: Any, exhaustion_report: Mapping[str, Any]) -> str:
    result_state = _mapping(exhaustion_report.get("result_state"))
    confidence = str(result_state.get("confidence_class", "local_not_evaluated"))
    absence = str(result_state.get("absence_state", "local_current_index_not_evaluated"))
    return (
        "Local SearchNeed created from a Search Hunt exhaustion report. "
        f"Current local result state is {confidence}; absence state is {absence}. "
        "Future work must remain policy gated and cannot mutate reviewed indexes directly."
    )


def derive_priority(query_summary: Mapping[str, Any], result_state: Mapping[str, Any]) -> int:
    confidence = str(result_state.get("confidence_class", ""))
    if confidence in {"local_absent", "local_blocked"}:
        return 70
    if confidence == "local_weak_hit":
        return 55
    return 50


def _layer_names(value: Any) -> list[str]:
    names = []
    for item in _sequence(value):
        payload = _mapping(item)
        name = str(payload.get("layer", payload.get("name", "")))
        if name:
            names.append(name)
    return names


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return ()
