"""Durable local SearchNeed record types."""

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


DEFAULT_CHECKED_LAYERS = (
    "reviewed_public_index",
    "local_search_summary",
    "local_absence_report",
    "local_hunt_history",
    "local_steering_preferences",
)
DEFAULT_DEFERRED_LAYERS = (
    "source_probes",
    "WorkUnits",
    "extraction",
    "broader_connectors",
    "synthetic_query_foundry",
    "ranking_identity_merge",
    "AI_research_escalation",
)
DEFAULT_POLICY_LIMITATIONS = (
    "SearchNeed is local demand state only",
    "SearchNeed is not evidence",
    "SearchNeed is not source approval",
    "SearchNeed is not global absence proof",
    "WorkUnit creation is disabled",
    "source probes are disabled",
    "model/provider calls are disabled",
    "public/master index mutation is disabled",
)


class SearchNeedState(str, Enum):
    PROPOSED = "proposed"
    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_POLICY = "waiting_for_policy"
    BLOCKED = "blocked"
    SATISFIED_LOCALLY = "satisfied_locally"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


class SearchNeedKind(str, Enum):
    FIND_EXACT_ARTIFACT = "find_exact_artifact"
    FIND_COMPATIBLE_VERSION = "find_compatible_version"
    FIND_SOURCE_OR_MIRROR = "find_source_or_mirror"
    IDENTIFY_UNKNOWN_ARTIFACT = "identify_unknown_artifact"
    VERIFY_PROVENANCE = "verify_provenance"
    EXTRACT_HIDDEN_MEMBER = "extract_hidden_member"
    IMPROVE_ABSENCE_REPORT = "improve_absence_report"
    IMPROVE_RANKING_OR_IDENTITY = "improve_ranking_or_identity"
    SOURCE_GAP = "source_gap"
    POLICY_BLOCKED_NEED = "policy_blocked_need"


class SearchNeedDesiredOutcome(str, Enum):
    VIEW_OR_READ = "view_or_read"
    CITE_OR_REFERENCE = "cite_or_reference"
    ACQUIRE_OR_DOWNLOAD_LATER_POLICY_GATED = "acquire_or_download_later_policy_gated"
    INSTALL_OR_EMULATE_LATER_POLICY_GATED = "install_or_emulate_later_policy_gated"
    PRESERVE_OR_MIRROR_LATER_POLICY_GATED = "preserve_or_mirror_later_policy_gated"
    VERIFY_ONLY = "verify_only"
    IMPROVE_INDEX = "improve_index"


@dataclass(frozen=True)
class SearchNeed:
    id: str
    hunt_id: str
    exhaustion_report_id: str
    query: str
    normalized_query: str
    need_title: str
    need_summary: str
    need_kind: SearchNeedKind
    desired_outcome: SearchNeedDesiredOutcome
    priority: int
    state: SearchNeedState
    local_result_state: str
    checked_layers: tuple[str, ...]
    deferred_layers: tuple[str, ...]
    recommended_future_work: tuple[str, ...]
    policy_limitations: tuple[str, ...]
    warnings: tuple[str, ...]
    public_safe_summary_allowed: bool
    private_notes_allowed: bool
    created_at: str
    updated_at: str
    idempotency_key: str | None = None
    superseded_by: str | None = None

    @classmethod
    def new(
        cls,
        *,
        hunt_id: str,
        exhaustion_report_id: str,
        query: str,
        need_title: str,
        need_summary: str,
        need_kind: SearchNeedKind | str,
        desired_outcome: SearchNeedDesiredOutcome | str,
        local_result_state: str,
        checked_layers: Sequence[str] = DEFAULT_CHECKED_LAYERS,
        deferred_layers: Sequence[str] = DEFAULT_DEFERRED_LAYERS,
        recommended_future_work: Sequence[str] = (),
        priority: int = 50,
        warnings: Sequence[str] = (),
        idempotency_key: str | None = None,
    ) -> "SearchNeed":
        now = utc_now()
        return cls(
            id="sn_" + uuid.uuid4().hex,
            hunt_id=str(hunt_id),
            exhaustion_report_id=str(exhaustion_report_id),
            query=str(query),
            normalized_query=normalize_query(query),
            need_title=str(need_title),
            need_summary=str(need_summary),
            need_kind=need_kind if isinstance(need_kind, SearchNeedKind) else SearchNeedKind(str(need_kind)),
            desired_outcome=desired_outcome
            if isinstance(desired_outcome, SearchNeedDesiredOutcome)
            else SearchNeedDesiredOutcome(str(desired_outcome)),
            priority=int(priority),
            state=SearchNeedState.PROPOSED,
            local_result_state=str(local_result_state),
            checked_layers=tuple(str(item) for item in checked_layers),
            deferred_layers=tuple(str(item) for item in deferred_layers),
            recommended_future_work=tuple(str(item) for item in recommended_future_work),
            policy_limitations=DEFAULT_POLICY_LIMITATIONS,
            warnings=tuple(str(item) for item in warnings),
            public_safe_summary_allowed=False,
            private_notes_allowed=True,
            created_at=now,
            updated_at=now,
            idempotency_key=idempotency_key,
            superseded_by=None,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SearchNeed":
        return cls(
            id=str(payload.get("id", "")),
            hunt_id=str(payload.get("hunt_id", "")),
            exhaustion_report_id=str(payload.get("exhaustion_report_id", "")),
            query=str(payload.get("query", "")),
            normalized_query=str(payload.get("normalized_query", "")),
            need_title=str(payload.get("need_title", "")),
            need_summary=str(payload.get("need_summary", "")),
            need_kind=SearchNeedKind(str(payload.get("need_kind", SearchNeedKind.FIND_EXACT_ARTIFACT.value))),
            desired_outcome=SearchNeedDesiredOutcome(str(payload.get("desired_outcome", SearchNeedDesiredOutcome.IMPROVE_INDEX.value))),
            priority=int(payload.get("priority", 50) or 50),
            state=SearchNeedState(str(payload.get("state", SearchNeedState.PROPOSED.value))),
            local_result_state=str(payload.get("local_result_state", "")),
            checked_layers=tuple_text(payload.get("checked_layers")),
            deferred_layers=tuple_text(payload.get("deferred_layers")),
            recommended_future_work=tuple_text(payload.get("recommended_future_work")),
            policy_limitations=tuple_text(payload.get("policy_limitations")),
            warnings=tuple_text(payload.get("warnings")),
            public_safe_summary_allowed=bool(payload.get("public_safe_summary_allowed", False)),
            private_notes_allowed=bool(payload.get("private_notes_allowed", True)),
            created_at=str(payload.get("created_at", "")),
            updated_at=str(payload.get("updated_at", "")),
            idempotency_key=optional(payload.get("idempotency_key")),
            superseded_by=optional(payload.get("superseded_by")),
        )

    def with_state(self, state: SearchNeedState, reason: str | None = None) -> "SearchNeed":
        return replace(self, state=state, updated_at=utc_now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "search_need_record.v0",
            "id": self.id,
            "hunt_id": self.hunt_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "query": self.query,
            "normalized_query": self.normalized_query,
            "need_title": self.need_title,
            "need_summary": self.need_summary,
            "need_kind": self.need_kind.value,
            "desired_outcome": self.desired_outcome.value,
            "priority": self.priority,
            "state": self.state.value,
            "local_result_state": self.local_result_state,
            "checked_layers": list(self.checked_layers),
            "deferred_layers": list(self.deferred_layers),
            "recommended_future_work": list(self.recommended_future_work),
            "policy_limitations": list(self.policy_limitations),
            "warnings": list(self.warnings),
            "public_safe_summary_allowed": self.public_safe_summary_allowed,
            "private_notes_allowed": self.private_notes_allowed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "idempotency_key": self.idempotency_key,
            "superseded_by": self.superseded_by,
            "workunit_creation_enabled": False,
            "source_probe_execution_enabled": False,
            "model_provider_enabled": False,
        }


@dataclass(frozen=True)
class SearchNeedTransition:
    id: str
    need_id: str
    from_state: str | None
    to_state: SearchNeedState
    reason: str | None
    created_at: str

    @classmethod
    def new(
        cls,
        need_id: str,
        from_state: SearchNeedState | str | None,
        to_state: SearchNeedState | str,
        reason: str | None = None,
    ) -> "SearchNeedTransition":
        from_value = from_state.value if isinstance(from_state, SearchNeedState) else (str(from_state) if from_state else None)
        return cls(
            id="snt_" + uuid.uuid4().hex,
            need_id=str(need_id),
            from_state=from_value,
            to_state=to_state if isinstance(to_state, SearchNeedState) else SearchNeedState(str(to_state)),
            reason=str(reason) if reason else None,
            created_at=utc_now(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "need_id": self.need_id,
            "from_state": self.from_state,
            "to_state": self.to_state.value,
            "reason": self.reason,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class SearchNeedSummary:
    id: str
    need_id: str
    summary_type: str
    payload: Mapping[str, Any]
    created_at: str

    @classmethod
    def new(cls, need_id: str, summary_type: str, payload: Mapping[str, Any]) -> "SearchNeedSummary":
        return cls(
            id="sns_" + uuid.uuid4().hex,
            need_id=str(need_id),
            summary_type=str(summary_type),
            payload=dict(payload),
            created_at=utc_now(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "need_id": self.need_id,
            "summary_type": self.summary_type,
            "payload": dict(self.payload),
            "created_at": self.created_at,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_query(query: str) -> str:
    return " ".join(str(query or "").strip().lower().split())


def optional(value: Any) -> str | None:
    text = str(value) if value is not None else ""
    return text or None


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)
