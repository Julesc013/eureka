"""Record models for the durable local work queue."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class WorkUnitType(str, Enum):
    SEARCH_NEED = "search_need"
    SOURCE_PROBE = "source_probe"
    EVIDENCE_REVIEW = "evidence_review"
    INDEX_REBUILD = "index_rebuild"
    REGRESSION_TEST = "regression_test"
    EXTRACTION_TASK = "extraction_task"
    DELEGATED_OPERATOR = "ag" + "ent_task"


class WorkUnitState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkUnitPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass(frozen=True)
class WorkUnit:
    id: str
    kind: WorkUnitType
    state: WorkUnitState
    title: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    priority: WorkUnitPriority = WorkUnitPriority.NORMAL
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    idempotency_key: str | None = None
    parent_id: str | None = None
    blocked_reason: str | None = None
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @classmethod
    def new(
        cls,
        kind: WorkUnitType | str,
        title: str,
        *,
        payload: Mapping[str, Any] | None = None,
        priority: WorkUnitPriority | str = WorkUnitPriority.NORMAL,
        idempotency_key: str | None = None,
        parent_id: str | None = None,
        warnings: Sequence[str] = (),
        limitations: Sequence[str] = (),
    ) -> "WorkUnit":
        now = utc_now()
        return cls(
            id="wku_" + uuid.uuid4().hex,
            kind=kind if isinstance(kind, WorkUnitType) else WorkUnitType(str(kind)),
            state=WorkUnitState.QUEUED,
            title=title,
            payload=dict(payload or {}),
            priority=priority if isinstance(priority, WorkUnitPriority) else WorkUnitPriority(str(priority)),
            created_at=now,
            updated_at=now,
            idempotency_key=idempotency_key,
            parent_id=parent_id,
            warnings=tuple(str(item) for item in warnings),
            limitations=tuple(str(item) for item in limitations),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "state": self.state.value,
            "title": self.title,
            "payload": dict(self.payload),
            "priority": self.priority.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "idempotency_key": self.idempotency_key,
            "parent_id": self.parent_id,
            "blocked_reason": self.blocked_reason,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "WorkUnit":
        return cls(
            id=str(payload.get("id") or ""),
            kind=WorkUnitType(str(payload.get("kind") or "")),
            state=WorkUnitState(str(payload.get("state") or "")),
            title=str(payload.get("title") or ""),
            payload=_mapping(payload.get("payload")),
            priority=WorkUnitPriority(str(payload.get("priority") or WorkUnitPriority.NORMAL.value)),
            created_at=str(payload.get("created_at") or utc_now()),
            updated_at=str(payload.get("updated_at") or utc_now()),
            idempotency_key=_optional_text(payload.get("idempotency_key")),
            parent_id=_optional_text(payload.get("parent_id")),
            blocked_reason=_optional_text(payload.get("blocked_reason")),
            warnings=_tuple(payload.get("warnings")),
            limitations=_tuple(payload.get("limitations")),
        )


@dataclass(frozen=True)
class WorkUnitTransition:
    id: str
    workunit_id: str
    from_state: str
    to_state: WorkUnitState
    reason: str | None
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def new(
        cls,
        workunit_id: str,
        from_state: WorkUnitState | str | None,
        to_state: WorkUnitState | str,
        reason: str | None = None,
    ) -> "WorkUnitTransition":
        return cls(
            id="wut_" + uuid.uuid4().hex,
            workunit_id=workunit_id,
            from_state=_state_text(from_state),
            to_state=to_state if isinstance(to_state, WorkUnitState) else WorkUnitState(str(to_state)),
            reason=reason,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "workunit_id": self.workunit_id,
            "from_state": self.from_state,
            "to_state": self.to_state.value,
            "reason": self.reason,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class WorkUnitSummary:
    total: int
    by_state: Mapping[str, int]
    by_kind: Mapping[str, int]
    execution_enabled: bool = False
    worker_runner_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "workunit_queue_summary.v0",
            "total": self.total,
            "by_state": dict(self.by_state),
            "by_kind": dict(self.by_kind),
            "execution_enabled": self.execution_enabled,
            "worker_runner_enabled": self.worker_runner_enabled,
        }


@dataclass(frozen=True)
class WorkUnitSummaryRow:
    key: str
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "count": self.count}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def _optional_text(value: Any) -> str | None:
    text = str(value) if value is not None else ""
    return text or None


def _state_text(value: WorkUnitState | str | None) -> str:
    if value is None:
        return ""
    return value.value if isinstance(value, WorkUnitState) else str(value)
