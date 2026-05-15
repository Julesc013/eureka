"""Record models for durable local Search Hunt sessions."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_query(query: str) -> str:
    return " ".join(str(query).strip().lower().split())


class SearchHuntState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_POLICY = "waiting_for_policy"
    BLOCKED = "blocked"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchHuntIntent(str, Enum):
    UNKNOWN = "unknown"
    FIND_RECORD = "find_record"
    EXPLAIN_ABSENCE = "explain_absence"
    COMPARE_CANDIDATES = "compare_candidates"
    IDENTIFY_SOURCE = "identify_source"


class SearchHuntDestination(str, Enum):
    UNKNOWN = "unknown"
    LOCAL_REVIEWED_INDEX = "local_reviewed_index"
    NEED_CANDIDATE = "need_candidate"
    WORK_CANDIDATE = "work_candidate"
    OPERATOR_REVIEW = "operator_review"


class SearchHuntCheckedLayer(str, Enum):
    REVIEWED_PUBLIC_INDEX = "reviewed_public_index"
    LOCAL_CANDIDATE_SUMMARY = "local_candidate_summary"
    LOCAL_ABSENCE_REPORT = "local_absence_report"


class SearchHuntUncheckedLayer(str, Enum):
    SOURCE_PROBES = "source_probes"
    WORKUNITS = "WorkUnits"
    EXTRACTION = "extraction"
    BROADER_CONNECTORS = "broader_connectors"
    SYNTHETIC_QUERY_FOUNDRY = "synthetic_query_foundry"
    AI_RESEARCH_ESCALATION = "AI_research_escalation"


class SearchHuntExhaustionState(str, Enum):
    INFORMATIVE = "informative"
    INSUFFICIENT_LOCAL_INDEX = "insufficient_local_index"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_POLICY = "waiting_for_policy"
    COMPLETE_ENOUGH_LOCALLY = "complete_enough_locally"
    FAILED_REPORT_GENERATION = "failed_report_generation"


@dataclass(frozen=True)
class SearchHuntSession:
    id: str
    query: str
    normalized_query: str
    state: SearchHuntState
    intent: SearchHuntIntent
    destination: SearchHuntDestination
    created_at: str
    updated_at: str
    index_snapshot_id: str | None = None
    reviewed_result_count: int = 0
    candidate_result_count: int = 0
    absence_report_id: str | None = None
    checked_layers: tuple[str, ...] = ()
    unchecked_layers: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    idempotency_key: str | None = None
    parent_id: str | None = None

    @classmethod
    def new(
        cls,
        query: str,
        *,
        intent: SearchHuntIntent | str = SearchHuntIntent.UNKNOWN,
        destination: SearchHuntDestination | str = SearchHuntDestination.UNKNOWN,
        reviewed_result_count: int = 0,
        candidate_result_count: int = 0,
        idempotency_key: str | None = None,
        parent_id: str | None = None,
        limitations: Sequence[str] = (),
        warnings: Sequence[str] = (),
    ) -> "SearchHuntSession":
        now = utc_now()
        return cls(
            id="shs_" + uuid.uuid4().hex,
            query=str(query).strip(),
            normalized_query=normalize_query(query),
            state=SearchHuntState.CREATED,
            intent=coerce_intent(intent),
            destination=coerce_destination(destination),
            created_at=now,
            updated_at=now,
            reviewed_result_count=int(reviewed_result_count),
            candidate_result_count=int(candidate_result_count),
            checked_layers=tuple(item.value for item in SearchHuntCheckedLayer),
            unchecked_layers=tuple(item.value for item in SearchHuntUncheckedLayer),
            limitations=tuple(limitations)
            or (
                "local reviewed-index investigation state only",
                "external source inspection has not run",
            ),
            warnings=tuple(str(item) for item in warnings),
            idempotency_key=idempotency_key,
            parent_id=parent_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "normalized_query": self.normalized_query,
            "state": self.state.value,
            "intent": self.intent.value,
            "destination": self.destination.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "index_snapshot_id": self.index_snapshot_id,
            "reviewed_result_count": self.reviewed_result_count,
            "candidate_result_count": self.candidate_result_count,
            "absence_report_id": self.absence_report_id,
            "checked_layers": list(self.checked_layers),
            "unchecked_layers": list(self.unchecked_layers),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "idempotency_key": self.idempotency_key,
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SearchHuntSession":
        return cls(
            id=str(payload.get("id") or ""),
            query=str(payload.get("query") or ""),
            normalized_query=str(payload.get("normalized_query") or normalize_query(str(payload.get("query") or ""))),
            state=coerce_state(payload.get("state") or SearchHuntState.CREATED.value),
            intent=coerce_intent(payload.get("intent") or SearchHuntIntent.UNKNOWN.value),
            destination=coerce_destination(payload.get("destination") or SearchHuntDestination.UNKNOWN.value),
            created_at=str(payload.get("created_at") or utc_now()),
            updated_at=str(payload.get("updated_at") or utc_now()),
            index_snapshot_id=optional_text(payload.get("index_snapshot_id")),
            reviewed_result_count=int(payload.get("reviewed_result_count") or 0),
            candidate_result_count=int(payload.get("candidate_result_count") or 0),
            absence_report_id=optional_text(payload.get("absence_report_id")),
            checked_layers=tuple_text(payload.get("checked_layers")),
            unchecked_layers=tuple_text(payload.get("unchecked_layers")),
            limitations=tuple_text(payload.get("limitations")),
            warnings=tuple_text(payload.get("warnings")),
            idempotency_key=optional_text(payload.get("idempotency_key")),
            parent_id=optional_text(payload.get("parent_id")),
        )


@dataclass(frozen=True)
class SearchHuntTransition:
    id: str
    session_id: str
    from_state: str
    to_state: SearchHuntState
    reason: str | None
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def new(
        cls,
        session_id: str,
        from_state: SearchHuntState | str | None,
        to_state: SearchHuntState | str,
        reason: str | None = None,
    ) -> "SearchHuntTransition":
        return cls(
            id="sht_" + uuid.uuid4().hex,
            session_id=session_id,
            from_state=state_text(from_state),
            to_state=coerce_state(to_state),
            reason=reason,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "from_state": self.from_state,
            "to_state": self.to_state.value,
            "reason": self.reason,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class SearchHuntSummary:
    id: str
    session_id: str
    summary_type: str
    payload: Mapping[str, Any]
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def new(cls, session_id: str, summary_type: str, payload: Mapping[str, Any]) -> "SearchHuntSummary":
        return cls(
            id="shm_" + uuid.uuid4().hex,
            session_id=session_id,
            summary_type=str(summary_type),
            payload=dict(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "summary_type": self.summary_type,
            "payload": dict(self.payload),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class SearchHuntCheckedLayerReport:
    layer: str
    status: str
    summary: str
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "status": self.status,
            "summary": self.summary,
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class SearchHuntDeferredLayerReport:
    layer: str
    status: str
    reason: str
    future_gate: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "status": self.status,
            "reason": self.reason,
            "future_gate": self.future_gate,
        }


@dataclass(frozen=True)
class SearchHuntBlockedPolicyReport:
    policy_id: str
    status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "status": self.status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class SearchHuntRecommendedAction:
    action: str
    status: str
    reason: str
    enabled_now: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "status": self.status,
            "reason": self.reason,
            "enabled_now": self.enabled_now,
        }


@dataclass(frozen=True)
class SearchHuntNonClaim:
    claim: str
    allowed: bool
    wording: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "allowed": self.allowed,
            "wording": self.wording,
        }


@dataclass(frozen=True)
class SearchHuntExhaustionReport:
    report_id: str
    hunt_id: str
    report_version: str
    created_at: str
    state: SearchHuntExhaustionState
    query_summary: Mapping[str, Any]
    checked_layers: tuple[SearchHuntCheckedLayerReport, ...]
    result_state: Mapping[str, Any]
    unchecked_or_deferred_layers: tuple[SearchHuntDeferredLayerReport, ...]
    blocked_by_policy: tuple[SearchHuntBlockedPolicyReport, ...]
    recommended_next_actions: tuple[SearchHuntRecommendedAction, ...]
    limitations: tuple[str, ...]
    warnings: tuple[str, ...]
    non_claims: tuple[SearchHuntNonClaim, ...]
    operator_label: str = "local_operator"

    @classmethod
    def new(
        cls,
        hunt_id: str,
        *,
        state: SearchHuntExhaustionState | str,
        query_summary: Mapping[str, Any],
        checked_layers: Sequence[SearchHuntCheckedLayerReport],
        result_state: Mapping[str, Any],
        unchecked_or_deferred_layers: Sequence[SearchHuntDeferredLayerReport],
        blocked_by_policy: Sequence[SearchHuntBlockedPolicyReport],
        recommended_next_actions: Sequence[SearchHuntRecommendedAction],
        limitations: Sequence[str],
        warnings: Sequence[str] = (),
        non_claims: Sequence[SearchHuntNonClaim] = (),
        operator_label: str | None = None,
    ) -> "SearchHuntExhaustionReport":
        return cls(
            report_id="she_" + uuid.uuid4().hex,
            hunt_id=str(hunt_id),
            report_version="search_hunt_exhaustion_report.v0",
            created_at=utc_now(),
            state=coerce_exhaustion_state(state),
            query_summary=dict(query_summary),
            checked_layers=tuple(checked_layers),
            result_state=dict(result_state),
            unchecked_or_deferred_layers=tuple(unchecked_or_deferred_layers),
            blocked_by_policy=tuple(blocked_by_policy),
            recommended_next_actions=tuple(recommended_next_actions),
            limitations=tuple(str(item) for item in limitations),
            warnings=tuple(str(item) for item in warnings),
            non_claims=tuple(non_claims) or default_exhaustion_non_claims(),
            operator_label=str(operator_label or "local_operator"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.report_version,
            "report_id": self.report_id,
            "hunt_id": self.hunt_id,
            "created_at": self.created_at,
            "state": self.state.value,
            "query_summary": dict(self.query_summary),
            "checked_layers": [item.to_dict() for item in self.checked_layers],
            "result_state": dict(self.result_state),
            "unchecked_or_deferred_layers": [item.to_dict() for item in self.unchecked_or_deferred_layers],
            "blocked_by_policy": [item.to_dict() for item in self.blocked_by_policy],
            "recommended_next_actions": [item.to_dict() for item in self.recommended_next_actions],
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "non_claims": [item.to_dict() for item in self.non_claims],
            "operator_label": self.operator_label,
            "workunit_creation_performed": False,
            "source_probe_executed": False,
            "external_network_used": False,
            "model_provider_used": False,
            "review_mutation_performed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SearchHuntExhaustionReport":
        return cls(
            report_id=str(payload.get("report_id") or ""),
            hunt_id=str(payload.get("hunt_id") or ""),
            report_version=str(payload.get("schema_version") or "search_hunt_exhaustion_report.v0"),
            created_at=str(payload.get("created_at") or utc_now()),
            state=coerce_exhaustion_state(payload.get("state") or SearchHuntExhaustionState.INFORMATIVE.value),
            query_summary=_mapping(payload.get("query_summary")),
            checked_layers=tuple(_checked_layer_report(item) for item in _sequence(payload.get("checked_layers"))),
            result_state=_mapping(payload.get("result_state")),
            unchecked_or_deferred_layers=tuple(_deferred_layer_report(item) for item in _sequence(payload.get("unchecked_or_deferred_layers"))),
            blocked_by_policy=tuple(_blocked_policy_report(item) for item in _sequence(payload.get("blocked_by_policy"))),
            recommended_next_actions=tuple(_recommended_action(item) for item in _sequence(payload.get("recommended_next_actions"))),
            limitations=tuple_text(payload.get("limitations")),
            warnings=tuple_text(payload.get("warnings")),
            non_claims=tuple(_non_claim(item) for item in _sequence(payload.get("non_claims"))),
            operator_label=str(payload.get("operator_label") or "local_operator"),
        )


def coerce_state(value: SearchHuntState | str) -> SearchHuntState:
    return value if isinstance(value, SearchHuntState) else SearchHuntState(str(value))


def coerce_exhaustion_state(value: SearchHuntExhaustionState | str) -> SearchHuntExhaustionState:
    return value if isinstance(value, SearchHuntExhaustionState) else SearchHuntExhaustionState(str(value))


def coerce_intent(value: SearchHuntIntent | str) -> SearchHuntIntent:
    return value if isinstance(value, SearchHuntIntent) else SearchHuntIntent(str(value))


def coerce_destination(value: SearchHuntDestination | str) -> SearchHuntDestination:
    return value if isinstance(value, SearchHuntDestination) else SearchHuntDestination(str(value))


def state_text(value: SearchHuntState | str | None) -> str:
    if value is None:
        return ""
    return value.value if isinstance(value, SearchHuntState) else str(value)


def optional_text(value: Any) -> str | None:
    text = str(value) if value is not None else ""
    return text or None


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def default_exhaustion_non_claims() -> tuple[SearchHuntNonClaim, ...]:
    return (
        SearchHuntNonClaim("artifact_does_not_exist", False, "Report does not prove an artifact does not exist."),
        SearchHuntNonClaim("world_wide_absence", False, "Report is limited to local current-index state."),
        SearchHuntNonClaim("all_sources_checked", False, "Deferred layers remain unchecked."),
        SearchHuntNonClaim("evidence_truth_accepted", False, "Report does not accept evidence or candidate truth."),
        SearchHuntNonClaim("rights_or_safety_cleared", False, "Report does not clear rights or safety."),
        SearchHuntNonClaim("production_or_public_launch_ready", False, "Report makes no production or public launch readiness claim."),
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, (list, tuple)) else ()


def _checked_layer_report(value: Any) -> SearchHuntCheckedLayerReport:
    item = _mapping(value)
    return SearchHuntCheckedLayerReport(
        layer=str(item.get("layer") or ""),
        status=str(item.get("status") or ""),
        summary=str(item.get("summary") or ""),
        details=_mapping(item.get("details")),
    )


def _deferred_layer_report(value: Any) -> SearchHuntDeferredLayerReport:
    item = _mapping(value)
    return SearchHuntDeferredLayerReport(
        layer=str(item.get("layer") or ""),
        status=str(item.get("status") or ""),
        reason=str(item.get("reason") or ""),
        future_gate=str(item.get("future_gate") or ""),
    )


def _blocked_policy_report(value: Any) -> SearchHuntBlockedPolicyReport:
    item = _mapping(value)
    return SearchHuntBlockedPolicyReport(
        policy_id=str(item.get("policy_id") or ""),
        status=str(item.get("status") or ""),
        reason=str(item.get("reason") or ""),
    )


def _recommended_action(value: Any) -> SearchHuntRecommendedAction:
    item = _mapping(value)
    return SearchHuntRecommendedAction(
        action=str(item.get("action") or ""),
        status=str(item.get("status") or ""),
        reason=str(item.get("reason") or ""),
        enabled_now=bool(item.get("enabled_now", False)),
    )


def _non_claim(value: Any) -> SearchHuntNonClaim:
    item = _mapping(value)
    return SearchHuntNonClaim(
        claim=str(item.get("claim") or ""),
        allowed=bool(item.get("allowed", False)),
        wording=str(item.get("wording") or ""),
    )
