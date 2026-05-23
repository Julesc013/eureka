"""Validation helpers for durable local work records."""

from pathlib import Path
from typing import Any, Mapping

from .errors import WorkUnitValidationError
from .records import WorkUnit, WorkUnitPriority, WorkUnitState, WorkUnitType


ALLOWED_WORKUNIT_TYPES = tuple(item.value for item in WorkUnitType)
ALLOWED_WORKUNIT_STATES = tuple(item.value for item in WorkUnitState)
ALLOWED_WORKUNIT_PRIORITIES = tuple(item.value for item in WorkUnitPriority)


def validate_workunit(workunit: WorkUnit) -> WorkUnit:
    if not workunit.id.strip():
        raise WorkUnitValidationError("workunit id is required")
    if not workunit.title.strip():
        raise WorkUnitValidationError("workunit title is required")
    validate_workunit_kind(workunit.kind)
    validate_workunit_state(workunit.state)
    validate_workunit_priority(workunit.priority)
    if not isinstance(workunit.payload, Mapping):
        raise WorkUnitValidationError("workunit payload must be an object")
    if workunit.blocked_reason and workunit.state != WorkUnitState.BLOCKED:
        raise WorkUnitValidationError("blocked_reason is only valid for blocked work records")
    return workunit


def validate_workunit_kind(value: WorkUnitType | str) -> WorkUnitType:
    try:
        return value if isinstance(value, WorkUnitType) else WorkUnitType(str(value))
    except ValueError as exc:
        raise WorkUnitValidationError(f"unsupported workunit kind: {value}") from exc


def validate_workunit_state(value: WorkUnitState | str) -> WorkUnitState:
    try:
        return value if isinstance(value, WorkUnitState) else WorkUnitState(str(value))
    except ValueError as exc:
        raise WorkUnitValidationError(f"unsupported workunit state: {value}") from exc


def validate_workunit_priority(value: WorkUnitPriority | str) -> WorkUnitPriority:
    try:
        return value if isinstance(value, WorkUnitPriority) else WorkUnitPriority(str(value))
    except ValueError as exc:
        raise WorkUnitValidationError(f"unsupported workunit priority: {value}") from exc


def validate_queue_path(path: str | Path) -> Path:
    if str(path) == ":memory:":
        return Path(":memory:")
    resolved = Path(path).expanduser()
    if not str(resolved).strip():
        raise WorkUnitValidationError("workunit queue path is required")
    if resolved.name.startswith("."):
        raise WorkUnitValidationError("hidden workunit queue file names are forbidden")
    if any(part in {".cache", ".local", "." + "ai" + "de.local", "secrets"} for part in resolved.parts):
        raise WorkUnitValidationError("hidden or private roots are forbidden")
    return resolved


def require_reason(reason: str | None, action: str) -> str:
    text = str(reason or "").strip()
    if not text:
        raise WorkUnitValidationError(f"{action} requires a reason")
    return text


def validate_limit(limit: int | str | None, default: int = 100, maximum: int = 500) -> int:
    try:
        value = int(limit if limit is not None else default)
    except (TypeError, ValueError) as exc:
        raise WorkUnitValidationError("limit must be an integer") from exc
    if value < 1:
        raise WorkUnitValidationError("limit must be positive")
    return min(value, maximum)


def validate_no_execution_flags(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    forbidden_true = (
        "execution_enabled",
        "worker_runner_enabled",
        "source_probe_execution_enabled",
        "review_decision_mutation_enabled",
        "index_rebuild_enabled",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in forbidden_true:
        if payload.get(key) is True:
            raise WorkUnitValidationError(f"{key} must not be true")
    return payload
