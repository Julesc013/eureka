"""SQLite row helpers for local SearchNeeds."""

from typing import Any, Mapping
import json

from .records import (
    SearchNeed,
    SearchNeedDesiredOutcome,
    SearchNeedKind,
    SearchNeedState,
    SearchNeedSummary,
    SearchNeedTransition,
)


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def decode_json(value: Any, default: Any) -> Any:
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError):
        return default


def row_to_need(row: Mapping[str, Any]) -> SearchNeed:
    return SearchNeed(
        id=str(row["id"]),
        hunt_id=str(row["hunt_id"]),
        exhaustion_report_id=str(row["exhaustion_report_id"]),
        query=str(row["query"]),
        normalized_query=str(row["normalized_query"]),
        need_title=str(row["need_title"]),
        need_summary=str(row["need_summary"]),
        need_kind=SearchNeedKind(str(row["need_kind"])),
        desired_outcome=SearchNeedDesiredOutcome(str(row["desired_outcome"])),
        priority=int(row["priority"]),
        state=SearchNeedState(str(row["state"])),
        local_result_state=str(row["local_result_state"]),
        checked_layers=tuple_text(decode_json(row["checked_layers_json"], [])),
        deferred_layers=tuple_text(decode_json(row["deferred_layers_json"], [])),
        recommended_future_work=tuple_text(decode_json(row["recommended_future_work_json"], [])),
        policy_limitations=tuple_text(decode_json(row["policy_limitations_json"], [])),
        warnings=tuple_text(decode_json(row["warnings_json"], [])),
        public_safe_summary_allowed=bool(int(row["public_safe_summary_allowed"])),
        private_notes_allowed=bool(int(row["private_notes_allowed"])),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        idempotency_key=optional(row["idempotency_key"]),
        superseded_by=optional(row["superseded_by"]),
    )


def row_to_transition(row: Mapping[str, Any]) -> SearchNeedTransition:
    return SearchNeedTransition(
        id=str(row["id"]),
        need_id=str(row["need_id"]),
        from_state=optional(row["from_state"]),
        to_state=SearchNeedState(str(row["to_state"])),
        reason=optional(row["reason"]),
        created_at=str(row["created_at"]),
    )


def row_to_summary(row: Mapping[str, Any]) -> SearchNeedSummary:
    return SearchNeedSummary(
        id=str(row["id"]),
        need_id=str(row["need_id"]),
        summary_type=str(row["summary_type"]),
        payload=dict(decode_json(row["payload_json"], {})),
        created_at=str(row["created_at"]),
    )


def optional(value: Any) -> str | None:
    text = str(value) if value is not None else ""
    return text or None


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)
