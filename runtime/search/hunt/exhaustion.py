"""Deterministic local/current-index exhaustion reports for Search Hunt sessions."""

from typing import Any, Mapping, Sequence

from .absence_summary import build_local_absence_summary
from .records import (
    SearchHuntBlockedPolicyReport,
    SearchHuntCheckedLayerReport,
    SearchHuntDeferredLayerReport,
    SearchHuntExhaustionReport,
    SearchHuntExhaustionState,
    SearchHuntRecommendedAction,
    SearchHuntSession,
)
from .search_summary import build_reviewed_index_search_summary


DEFERRED_LAYERS = (
    ("source_probes", "source inspection remains disabled by policy", "future source policy gate"),
    ("WorkUnits", "background work creation is deferred", "future work queue gate"),
    ("extraction", "extraction remains deferred", "future extraction safety gate"),
    ("broader_connectors", "broader connector coverage has not run", "future connector gate"),
    ("synthetic_query_foundry", "synthetic query generation is not active", "future synthetic query gate"),
    ("ranking_identity_merge", "ranking and identity merge have not been evaluated here", "future ranking and identity gate"),
    ("AI_research_escalation", "model/provider escalation is disabled", "future escalation gate"),
    ("federation_packs", "pack or federation exchange has not run", "future pack gate"),
    ("public_hosted_index", "hosted public indexing is not part of this local report", "future public hosting review"),
)

BLOCKED_POLICIES = (
    ("source_probe_disabled", "source probe disabled"),
    ("workunit_creation_disabled", "background work creation disabled until a later pipeline"),
    ("extraction_deferred", "extraction deferred until a later safety gate"),
    ("model_provider_disabled", "AI/model provider disabled"),
    ("external_search_disabled", "external search disabled"),
    ("payload_actions_forbidden", "payload acquisition and runtime actions forbidden"),
    ("index_mutation_forbidden", "public/master index mutation forbidden"),
)

RECOMMENDED_ACTIONS = (
    ("create_search_need_later", "create SearchNeed later in the need pipeline"),
    ("create_work_items_later", "create background work later through the work queue gate"),
    ("source_probe_review_later", "consider source inspection later only after source policy approval"),
    ("extraction_review_later", "consider extraction later only after extraction safety approval"),
    ("run_synthetic_query_eval_later", "run synthetic query/eval later through the synthetic query track"),
    ("run_ai_escalation_later", "run model escalation later only after explicit disabled-by-default gate"),
)

LIMITATIONS = (
    "local reviewed index only",
    "local current-index absence only",
    "not a world-wide absence proof",
    "no source coverage claim",
    "no rights or safety clearance",
    "no production or public launch readiness claim",
)


def build_hunt_exhaustion_report(runtime: Any, hunt_id: str, *, operator_label: str | None = None) -> SearchHuntExhaustionReport:
    hunt = runtime.search_hunt.get_session(hunt_id)
    if hunt is None:
        errors = __import__("runtime.search_hunt.errors", fromlist=["SearchHuntNotFoundError"])
        raise errors.SearchHuntNotFoundError(f"Search Hunt session not found: {hunt_id}")
    search_summary = _latest_summary(runtime, hunt_id, "reviewed_index_search")
    if not search_summary:
        search_summary = build_reviewed_index_search_summary(runtime, hunt.query)
    absence_summary = _latest_summary(runtime, hunt_id, "local_absence")
    if not absence_summary:
        absence_summary = build_local_absence_summary(runtime, hunt.query)
    result_state = build_result_state(hunt, search_summary, absence_summary)
    return SearchHuntExhaustionReport.new(
        hunt.id,
        state=_exhaustion_state(hunt, result_state),
        query_summary={
            "hunt_id": hunt.id,
            "original_query": hunt.query,
            "normalized_query": hunt.normalized_query,
            "intent": hunt.intent.value,
            "destination": hunt.destination.value,
            "hunt_state": hunt.state.value,
        },
        checked_layers=build_checked_layer_reports(runtime, hunt, search_summary, absence_summary),
        result_state=result_state,
        unchecked_or_deferred_layers=build_deferred_layer_reports(runtime, hunt),
        blocked_by_policy=build_blocked_policy_reports(runtime, hunt),
        recommended_next_actions=build_recommended_actions(runtime, hunt),
        limitations=LIMITATIONS,
        warnings=tuple(hunt.warnings),
        operator_label=operator_label,
    )


def build_checked_layer_reports(
    runtime: Any,
    hunt: SearchHuntSession,
    search_summary: Mapping[str, Any] | None = None,
    absence_summary: Mapping[str, Any] | None = None,
) -> tuple[SearchHuntCheckedLayerReport, ...]:
    search_payload = dict(search_summary or build_reviewed_index_search_summary(runtime, hunt.query))
    absence_payload = dict(absence_summary or build_local_absence_summary(runtime, hunt.query))
    transitions = runtime.search_hunt.list_transitions(hunt.id, limit=100)
    steering = runtime.search_hunt.list_steering_preferences(hunt.id, active_only=True)
    return (
        SearchHuntCheckedLayerReport(
            "reviewed_public_index",
            "checked",
            "Reviewed public index searched locally.",
            {"result_count": int(search_payload.get("result_count", 0) or 0)},
        ),
        SearchHuntCheckedLayerReport(
            "local_search_summary",
            "checked",
            "Local reviewed-index search summary is available.",
            _summary_details(search_payload),
        ),
        SearchHuntCheckedLayerReport(
            "local_absence_report",
            "checked",
            "Absence is local/current-index only.",
            _absence_details(absence_payload),
        ),
        SearchHuntCheckedLayerReport(
            "local_hunt_history",
            "checked",
            "Local transition and command history inspected.",
            {
                "transition_count": len(transitions),
                "command_count": len(runtime.search_hunt.list_commands(hunt.id, limit=100)),
            },
        ),
        SearchHuntCheckedLayerReport(
            "local_steering_preferences",
            "checked",
            "Active steering preferences inspected.",
            {"active_steering_count": len(steering)},
        ),
    )


def build_deferred_layer_reports(runtime: Any, hunt: SearchHuntSession) -> tuple[SearchHuntDeferredLayerReport, ...]:
    return tuple(
        SearchHuntDeferredLayerReport(layer=layer, status="unchecked_or_deferred", reason=reason, future_gate=future_gate)
        for layer, reason, future_gate in DEFERRED_LAYERS
    )


def build_blocked_policy_reports(runtime: Any, hunt: SearchHuntSession) -> tuple[SearchHuntBlockedPolicyReport, ...]:
    return tuple(SearchHuntBlockedPolicyReport(policy_id=policy_id, status="blocked", reason=reason) for policy_id, reason in BLOCKED_POLICIES)


def build_recommended_actions(runtime: Any, hunt: SearchHuntSession) -> tuple[SearchHuntRecommendedAction, ...]:
    return tuple(
        SearchHuntRecommendedAction(action=action, status="deferred", reason=reason, enabled_now=False)
        for action, reason in RECOMMENDED_ACTIONS
    )


def build_result_state(
    hunt: SearchHuntSession,
    search_summary: Mapping[str, Any],
    absence_summary: Mapping[str, Any],
) -> dict[str, Any]:
    reviewed_count = int(search_summary.get("result_count", hunt.reviewed_result_count) or 0)
    candidate_count = int(hunt.candidate_result_count or 0)
    absence = _mapping(absence_summary.get("absence"))
    absence_count = int(absence.get("result_count", reviewed_count) or 0)
    if reviewed_count >= 2:
        confidence = "local_hit"
    elif reviewed_count == 1:
        confidence = "local_weak_hit"
    elif hunt.state.value in {"blocked", "waiting_for_policy"}:
        confidence = "local_blocked"
    elif absence_count == 0:
        confidence = "local_absent"
    else:
        confidence = "local_not_evaluated"
    return {
        "reviewed_result_count": reviewed_count,
        "candidate_result_count": candidate_count,
        "near_miss_count": 0,
        "absence_state": "local_current_index_absent" if reviewed_count == 0 else "local_current_index_has_reviewed_result",
        "confidence_class": confidence,
    }


def _exhaustion_state(hunt: SearchHuntSession, result_state: Mapping[str, Any]) -> SearchHuntExhaustionState:
    if hunt.state.value == "waiting_for_user":
        return SearchHuntExhaustionState.WAITING_FOR_USER
    if hunt.state.value == "waiting_for_policy":
        return SearchHuntExhaustionState.WAITING_FOR_POLICY
    if hunt.state.value == "blocked":
        return SearchHuntExhaustionState.BLOCKED_BY_POLICY
    if hunt.state.value == "complete" and int(result_state.get("reviewed_result_count", 0) or 0) > 0:
        return SearchHuntExhaustionState.COMPLETE_ENOUGH_LOCALLY
    if int(result_state.get("reviewed_result_count", 0) or 0) == 0:
        return SearchHuntExhaustionState.INSUFFICIENT_LOCAL_INDEX
    return SearchHuntExhaustionState.INFORMATIVE


def _latest_summary(runtime: Any, hunt_id: str, summary_type: str) -> Mapping[str, Any] | None:
    latest: Mapping[str, Any] | None = None
    for summary in runtime.search_hunt.list_summaries(hunt_id, limit=100):
        if summary.summary_type == summary_type:
            latest = summary.payload
    return latest


def _summary_details(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "query": payload.get("query", ""),
        "normalized_query": payload.get("normalized_query", ""),
        "reviewed_index_only": bool(payload.get("reviewed_index_only", True)),
        "current_index_only": bool(payload.get("current_index_only", True)),
        "result_count": int(payload.get("result_count", 0) or 0),
    }


def _absence_details(payload: Mapping[str, Any]) -> dict[str, Any]:
    absence = _mapping(payload.get("absence"))
    return {
        "query": payload.get("query", ""),
        "normalized_query": payload.get("normalized_query", ""),
        "local_current_index_absence_only": bool(payload.get("local_current_index_absence_only", True)),
        "result_count": int(absence.get("result_count", 0) or 0),
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
