"""SQLite row helpers for local Search Hunt sessions."""

import json
from typing import Any, Mapping

from .records import SearchHuntDestination, SearchHuntIntent, SearchHuntSession, SearchHuntState, SearchHuntSummary, SearchHuntTransition


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def decode_json(value: Any, default: Any) -> Any:
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError):
        return default


def row_to_session(row: Mapping[str, Any]) -> SearchHuntSession:
    return SearchHuntSession(
        id=str(row["id"]),
        query=str(row["query"]),
        normalized_query=str(row["normalized_query"]),
        state=SearchHuntState(str(row["state"])),
        intent=SearchHuntIntent(str(row["intent"])),
        destination=SearchHuntDestination(str(row["destination"])),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        index_snapshot_id=optional(row["index_snapshot_id"]),
        reviewed_result_count=int(row["reviewed_result_count"]),
        candidate_result_count=int(row["candidate_result_count"]),
        absence_report_id=optional(row["absence_report_id"]),
        checked_layers=tuple_text(decode_json(row["checked_layers_json"], [])),
        unchecked_layers=tuple_text(decode_json(row["unchecked_layers_json"], [])),
        limitations=tuple_text(decode_json(row["limitations_json"], [])),
        warnings=tuple_text(decode_json(row["warnings_json"], [])),
        idempotency_key=optional(row["idempotency_key"]),
        parent_id=optional(row["parent_id"]),
    )


def row_to_transition(row: Mapping[str, Any]) -> SearchHuntTransition:
    return SearchHuntTransition(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        from_state=str(row["from_state"]),
        to_state=SearchHuntState(str(row["to_state"])),
        reason=optional(row["reason"]),
        created_at=str(row["created_at"]),
    )


def row_to_summary(row: Mapping[str, Any]) -> SearchHuntSummary:
    return SearchHuntSummary(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
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
