"""SQLite row helpers for disabled agent research task records."""

from typing import Any, Mapping
import json

from .records import AgentResearchTask


def encode_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def decode_json(value: Any, default: Any) -> Any:
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError):
        return default


def row_to_task(row: Mapping[str, Any]) -> AgentResearchTask:
    return AgentResearchTask.from_dict(
        {
            "task_id": str(row["task_id"]),
            "search_hunt_id": str(row["search_hunt_id"]),
            "search_need_id": str(row["search_need_id"]),
            "exhaustion_report_id": str(row["exhaustion_report_id"]),
            "query": str(row["query"]),
            "normalized_query": str(row["normalized_query"]),
            "intent": str(row["intent"]),
            "destination": str(row["destination"]),
            "checked_layers": decode_json(row["checked_layers_json"], []),
            "deferred_layers": decode_json(row["deferred_layers_json"], []),
            "blocked_by_policy": decode_json(row["blocked_by_policy_json"], []),
            "known_candidates": decode_json(row["known_candidates_json"], []),
            "known_absence_state": str(row["known_absence_state"]),
            "steering_preferences": decode_json(row["steering_preferences_json"], []),
            "allowed_source_families": decode_json(row["allowed_source_families_json"], []),
            "blocked_source_families": decode_json(row["blocked_source_families_json"], []),
            "research_goals": decode_json(row["research_goals_json"], []),
            "forbidden_actions": decode_json(row["forbidden_actions_json"], []),
            "output_schema": decode_json(row["output_schema_json"], {}),
            "provider_enabled": bool(int(row["provider_enabled"])),
            "execution_enabled": bool(int(row["execution_enabled"])),
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
            "state": str(row["state"]),
            "warnings": decode_json(row["warnings_json"], []),
            "limitations": decode_json(row["limitations_json"], []),
        }
    )


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def tuple_mapping(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(dict(item) for item in value if isinstance(item, Mapping))
