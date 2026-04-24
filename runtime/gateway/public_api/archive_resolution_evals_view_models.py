from __future__ import annotations

from typing import Any, Mapping


def archive_resolution_evals_envelope_to_view_model(
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "envelope.status"),
        "eval_suite": _coerce_suite(envelope.get("eval_suite"), "envelope.eval_suite"),
    }
    notices = envelope.get("notices")
    if notices is not None:
        view_model["notices"] = _coerce_notices(notices, "envelope.notices")
    return view_model


def _coerce_suite(value: Any, field_name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object or null.")
    return {
        "total_task_count": _require_non_negative_int(
            value.get("total_task_count"),
            f"{field_name}.total_task_count",
        ),
        "status_counts": _coerce_int_mapping(
            value.get("status_counts"),
            f"{field_name}.status_counts",
        ),
        "task_summaries": _coerce_task_summaries(
            value.get("task_summaries"),
            f"{field_name}.task_summaries",
        ),
        "tasks": _coerce_tasks(value.get("tasks"), f"{field_name}.tasks"),
        "created_at": _require_string(value.get("created_at"), f"{field_name}.created_at"),
        "created_by_slice": _require_string(
            value.get("created_by_slice"),
            f"{field_name}.created_by_slice",
        ),
        "load_errors": _coerce_load_errors(
            value.get("load_errors"),
            f"{field_name}.load_errors",
        ),
        "notices": _coerce_notices(value.get("notices"), f"{field_name}.notices"),
    }


def _coerce_task_summaries(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    summaries: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        summaries.append(_clone_json_mapping(item, f"{field_name}[{index}]"))
    return summaries


def _coerce_tasks(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    tasks: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        task = _clone_json_mapping(item, f"{field_name}[{index}]")
        _require_string(task.get("task_id"), f"{field_name}[{index}].task_id")
        _require_string(task.get("overall_status"), f"{field_name}[{index}].overall_status")
        _require_string(task.get("planner_status"), f"{field_name}[{index}].planner_status")
        tasks.append(task)
    return tasks


def _coerce_int_mapping(value: Any, field_name: str) -> dict[str, int]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    payload: dict[str, int] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{field_name} keys must be non-empty strings.")
        payload[key] = _require_non_negative_int(item, f"{field_name}.{key}")
    return payload


def _coerce_load_errors(value: Any, field_name: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    errors: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        errors.append(
            {
                "source_path": _require_string(
                    item.get("source_path"),
                    f"{field_name}[{index}].source_path",
                ),
                "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
                "message": _require_string(
                    item.get("message"),
                    f"{field_name}[{index}].message",
                ),
            }
        )
    return errors


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


def _clone_json_mapping(value: Mapping[str, Any], field_name: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{field_name} keys must be non-empty strings.")
        payload[key] = _clone_json_like(item, f"{field_name}.{key}")
    return payload


def _clone_json_like(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        return _clone_json_mapping(value, field_name)
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]") for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(f"{field_name} must contain only JSON-compatible values.")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value
