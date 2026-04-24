from __future__ import annotations

from typing import Any, Mapping


def query_plan_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "envelope.status"),
        "query_plan": _coerce_query_plan(envelope.get("query_plan"), "envelope.query_plan"),
    }
    notices = envelope.get("notices")
    if notices is not None:
        view_model["notices"] = _coerce_notices(notices, "envelope.notices")
    raw_query = envelope.get("raw_query")
    if raw_query is not None:
        view_model["raw_query"] = _require_string(raw_query, "envelope.raw_query")
    return view_model


def _coerce_query_plan(value: Any, field_name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object or null.")
    return {
        "raw_query": _require_string(value.get("raw_query"), f"{field_name}.raw_query"),
        "task_kind": _require_string(value.get("task_kind"), f"{field_name}.task_kind"),
        "object_type": _require_string(value.get("object_type"), f"{field_name}.object_type"),
        "constraints": _coerce_constraints(value.get("constraints"), f"{field_name}.constraints"),
        "prefer": _coerce_string_list(value.get("prefer"), f"{field_name}.prefer"),
        "exclude": _coerce_string_list(value.get("exclude"), f"{field_name}.exclude"),
        "action_hints": _coerce_string_list(
            value.get("action_hints"),
            f"{field_name}.action_hints",
        ),
        "source_hints": _coerce_string_list(
            value.get("source_hints"),
            f"{field_name}.source_hints",
        ),
        "planner_confidence": _require_string(
            value.get("planner_confidence"),
            f"{field_name}.planner_confidence",
        ),
        "planner_notes": _coerce_string_list(
            value.get("planner_notes"),
            f"{field_name}.planner_notes",
        ),
    }


def _coerce_constraints(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return _clone_json_like(value, field_name)


def _clone_json_like(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        payload: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"{field_name} keys must be non-empty strings.")
            payload[key] = _clone_json_like(item, f"{field_name}.{key}")
        return payload
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]") for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(f"{field_name} must contain only JSON-compatible values.")


def _coerce_notices(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    notices: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        notice: dict[str, str] = {
            "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
            "severity": _require_string(item.get("severity"), f"{field_name}[{index}].severity"),
        }
        message = item.get("message")
        if message is not None:
            notice["message"] = _require_string(message, f"{field_name}[{index}].message")
        notices.append(notice)
    return notices


def _coerce_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    values: list[str] = []
    for index, item in enumerate(value):
        values.append(_require_string(item, f"{field_name}[{index}]"))
    return values


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value
