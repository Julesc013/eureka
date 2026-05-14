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


def coerce_state(value: SearchHuntState | str) -> SearchHuntState:
    return value if isinstance(value, SearchHuntState) else SearchHuntState(str(value))


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
