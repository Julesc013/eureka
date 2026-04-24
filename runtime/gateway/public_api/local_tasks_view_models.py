from __future__ import annotations

from typing import Any, Mapping


def local_tasks_envelope_to_view_model(envelope: Mapping[str, Any]) -> dict[str, Any]:
    view_model: dict[str, Any] = {
        "status": _require_string(envelope.get("status"), "envelope.status"),
        "task_count": _require_non_negative_int(envelope.get("task_count"), "envelope.task_count"),
        "tasks": _coerce_tasks(envelope.get("tasks"), "envelope.tasks"),
    }
    selected_task_id = envelope.get("selected_task_id")
    if selected_task_id is not None:
        view_model["selected_task_id"] = _require_string(
            selected_task_id,
            "envelope.selected_task_id",
        )
    notices = envelope.get("notices")
    if notices is not None:
        view_model["notices"] = _coerce_notices(notices, "envelope.notices")
    requested_task_kind = envelope.get("requested_task_kind")
    if requested_task_kind is not None:
        view_model["requested_task_kind"] = _require_string(
            requested_task_kind,
            "envelope.requested_task_kind",
        )
    return view_model


def _coerce_tasks(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    tasks: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        task: dict[str, Any] = {
            "task_id": _require_string(item.get("task_id"), f"{field_name}[{index}].task_id"),
            "task_kind": _require_string(item.get("task_kind"), f"{field_name}[{index}].task_kind"),
            "status": _require_string(item.get("status"), f"{field_name}[{index}].status"),
            "requested_inputs": _coerce_json_object(
                item.get("requested_inputs"),
                f"{field_name}[{index}].requested_inputs",
            ),
            "created_at": _require_string(item.get("created_at"), f"{field_name}[{index}].created_at"),
            "notices": _coerce_notices(item.get("notices"), f"{field_name}[{index}].notices"),
            "created_by_slice": _require_string(
                item.get("created_by_slice"),
                f"{field_name}[{index}].created_by_slice",
            ),
        }
        started_at = item.get("started_at")
        if started_at is not None:
            task["started_at"] = _require_string(started_at, f"{field_name}[{index}].started_at")
        completed_at = item.get("completed_at")
        if completed_at is not None:
            task["completed_at"] = _require_string(
                completed_at,
                f"{field_name}[{index}].completed_at",
            )
        result_summary = item.get("result_summary")
        if result_summary is not None:
            task["result_summary"] = _coerce_json_object(
                result_summary,
                f"{field_name}[{index}].result_summary",
            )
        error_summary = item.get("error_summary")
        if error_summary is not None:
            task["error_summary"] = _coerce_json_object(
                error_summary,
                f"{field_name}[{index}].error_summary",
            )
        output_references = item.get("output_references")
        if output_references is not None:
            task["output_references"] = _coerce_json_object(
                output_references,
                f"{field_name}[{index}].output_references",
            )
        tasks.append(task)
    return tasks


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


def _coerce_json_object(value: Any, field_name: str) -> dict[str, Any]:
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


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_non_negative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value
