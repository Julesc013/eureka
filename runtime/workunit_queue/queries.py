"""SQLite row helpers for the durable local work queue."""

import json
from typing import Any, Mapping

from .records import WorkUnit, WorkUnitPayloadRef, WorkUnitPriority, WorkUnitState, WorkUnitTransition, WorkUnitType


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def decode_json(value: Any, default: Any) -> Any:
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError):
        return default


def row_to_workunit(row: Mapping[str, Any]) -> WorkUnit:
    return WorkUnit(
        id=str(row["id"]),
        kind=WorkUnitType(str(row["kind"])),
        state=WorkUnitState(str(row["state"])),
        title=str(row["title"]),
        payload=_mapping(decode_json(row["payload_json"], {})),
        priority=WorkUnitPriority(str(row["priority"])),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        idempotency_key=_optional(row["idempotency_key"]),
        parent_id=_optional(row["parent_id"]),
        blocked_reason=_optional(row["blocked_reason"]),
        warnings=_tuple(decode_json(row["warnings_json"], [])),
        limitations=_tuple(decode_json(row["limitations_json"], [])),
    )


def row_to_transition(row: Mapping[str, Any]) -> WorkUnitTransition:
    return WorkUnitTransition(
        id=str(row["id"]),
        workunit_id=str(row["workunit_id"]),
        from_state=str(row["from_state"]),
        to_state=WorkUnitState(str(row["to_state"])),
        reason=_optional(row["reason"]),
        created_at=str(row["created_at"]),
    )


def row_to_payload_ref(row: Mapping[str, Any]) -> WorkUnitPayloadRef:
    return WorkUnitPayloadRef(
        id=str(row["id"]),
        workunit_id=str(row["workunit_id"]),
        ref_kind=str(row["ref_kind"]),
        ref_id=str(row["ref_id"]),
        created_at=str(row["created_at"]),
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def _optional(value: Any) -> str | None:
    text = str(value) if value is not None else ""
    return text or None
