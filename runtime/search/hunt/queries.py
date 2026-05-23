"""SQLite row helpers for local Search Hunt sessions."""

import json
from typing import Any, Mapping

from .commands import SearchHuntCommand
from .records import (
    SearchHuntDestination,
    SearchHuntExhaustionReport,
    SearchHuntIntent,
    SearchHuntSession,
    SearchHuntState,
    SearchHuntSummary,
    SearchHuntTransition,
)
from .run_records import BackgroundHuntRun
from .replay_records import HuntReplayRecord
from .steering import SearchHuntSteeringPreference


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


def row_to_command(row: Mapping[str, Any]) -> SearchHuntCommand:
    return SearchHuntCommand(
        command_id=str(row["command_id"]),
        hunt_id=str(row["hunt_id"]),
        command_type=str(row["command_type"]),
        value=optional(row["value"]),
        reason=str(row["reason"]),
        operator_label=str(row["operator_label"]),
        previous_state=str(row["previous_state"]),
        resulting_state=str(row["resulting_state"]),
        policy_decision=str(row["policy_decision"]),
        side_effects=dict(decode_json(row["side_effects_json"], {})),
        created_at=str(row["created_at"]),
    )


def row_to_steering_preference(row: Mapping[str, Any]) -> SearchHuntSteeringPreference:
    return SearchHuntSteeringPreference(
        id=str(row["id"]),
        command_id=str(row["command_id"]),
        hunt_id=str(row["hunt_id"]),
        command_type=str(row["command_type"]),
        value=str(row["value"]),
        reason=str(row["reason"]),
        operator_label=str(row["operator_label"]),
        active=bool(int(row["active"])),
        limitations=tuple_text(decode_json(row["limitations_json"], [])),
        warnings=tuple_text(decode_json(row["warnings_json"], [])),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def row_to_exhaustion_report(row: Mapping[str, Any]) -> SearchHuntExhaustionReport:
    payload = dict(decode_json(row["payload_json"], {}))
    payload.setdefault("report_id", str(row["report_id"]))
    payload.setdefault("hunt_id", str(row["hunt_id"]))
    payload.setdefault("schema_version", str(row["report_version"]))
    payload.setdefault("state", str(row["exhaustion_state"]))
    payload.setdefault("created_at", str(row["created_at"]))
    return SearchHuntExhaustionReport.from_dict(payload)


def row_to_background_hunt_run(row: Mapping[str, Any]) -> BackgroundHuntRun:
    payload = dict(decode_json(row["payload_json"], {}))
    payload.setdefault("run_id", str(row["run_id"]))
    payload.setdefault("hunt_id", str(row["hunt_id"]))
    payload.setdefault("status", str(row["status"]))
    payload.setdefault("started_at", str(row["started_at"]))
    payload.setdefault("finished_at", optional(row["finished_at"]))
    return BackgroundHuntRun.from_dict(payload)


def row_to_hunt_replay_record(row: Mapping[str, Any]) -> HuntReplayRecord:
    payload = dict(decode_json(row["payload_json"], {}))
    payload.setdefault("replay_id", str(row["replay_id"]))
    payload.setdefault("hunt_id", str(row["hunt_id"]))
    payload.setdefault("replay_source", str(row["replay_source"]))
    payload.setdefault("status", str(row["status"]))
    payload.setdefault("started_at", str(row["started_at"]))
    payload.setdefault("finished_at", optional(row["finished_at"]))
    return HuntReplayRecord.from_dict(payload)


def optional(value: Any) -> str | None:
    text = str(value) if value is not None else ""
    return text or None


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)
