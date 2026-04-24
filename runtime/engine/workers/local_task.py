from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from runtime.engine.interfaces.public.local_task import LocalTaskRecord
from runtime.engine.interfaces.public.resolution import Notice
from runtime.engine.interfaces.service.local_task_service import LocalTaskNotFoundError


class MalformedLocalTaskRecordError(ValueError):
    def __init__(self, source_path: Path, message: str) -> None:
        self.source_path = source_path
        super().__init__(f"{source_path}: {message}")


def local_task_to_dict(task: LocalTaskRecord) -> dict[str, Any]:
    payload = task.to_dict()
    payload["record_kind"] = "eureka.local_task"
    payload["record_version"] = "0.1.0-draft"
    return payload


def local_task_from_dict(
    raw_record: Mapping[str, Any],
    *,
    source_path: Path,
) -> LocalTaskRecord:
    _require_string(raw_record.get("record_kind"), "record_kind", source_path)
    _require_string(raw_record.get("record_version"), "record_version", source_path)
    return LocalTaskRecord(
        task_id=_require_string(raw_record.get("task_id"), "task_id", source_path),
        task_kind=_require_string(raw_record.get("task_kind"), "task_kind", source_path),
        status=_require_string(raw_record.get("status"), "status", source_path),
        requested_inputs=_coerce_json_object(
            raw_record.get("requested_inputs"),
            "requested_inputs",
            source_path,
        ),
        created_at=_require_string(raw_record.get("created_at"), "created_at", source_path),
        started_at=_optional_string(raw_record.get("started_at"), "started_at", source_path),
        completed_at=_optional_string(raw_record.get("completed_at"), "completed_at", source_path),
        result_summary=_coerce_optional_json_object(
            raw_record.get("result_summary"),
            "result_summary",
            source_path,
        ),
        error_summary=_coerce_optional_json_object(
            raw_record.get("error_summary"),
            "error_summary",
            source_path,
        ),
        output_references=_coerce_optional_json_object(
            raw_record.get("output_references"),
            "output_references",
            source_path,
        ),
        notices=_coerce_notices(raw_record.get("notices"), "notices", source_path),
        created_by_slice=_require_string(
            raw_record.get("created_by_slice"),
            "created_by_slice",
            source_path,
        ),
    )


def _coerce_notices(value: Any, field_name: str, source_path: Path) -> tuple[Notice, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise MalformedLocalTaskRecordError(source_path, f"Field '{field_name}' must be a list.")
    notices: list[Notice] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedLocalTaskRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be an object.",
            )
        notices.append(
            Notice(
                code=_require_string(item.get("code"), f"{field_name}[{index}].code", source_path),
                severity=_require_string(
                    item.get("severity"),
                    f"{field_name}[{index}].severity",
                    source_path,
                ),
                message=_optional_string(
                    item.get("message"),
                    f"{field_name}[{index}].message",
                    source_path,
                ),
            )
        )
    return tuple(notices)


def _coerce_optional_json_object(
    value: Any,
    field_name: str,
    source_path: Path,
) -> dict[str, Any] | None:
    if value is None:
        return None
    return _coerce_json_object(value, field_name, source_path)


def _coerce_json_object(value: Any, field_name: str, source_path: Path) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise MalformedLocalTaskRecordError(source_path, f"Field '{field_name}' must be an object.")
    return _clone_json_like(value, field_name, source_path)


def _clone_json_like(value: Any, field_name: str, source_path: Path) -> Any:
    if isinstance(value, Mapping):
        payload: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise MalformedLocalTaskRecordError(
                    source_path,
                    f"Field '{field_name}' keys must be non-empty strings.",
                )
            payload[key] = _clone_json_like(item, f"{field_name}.{key}", source_path)
        return payload
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]", source_path) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise MalformedLocalTaskRecordError(
        source_path,
        f"Field '{field_name}' must contain only JSON-compatible values.",
    )


def _require_string(value: Any, field_name: str, source_path: Path) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedLocalTaskRecordError(
            source_path,
            f"Field '{field_name}' must be a non-empty string.",
        )
    return value


def _optional_string(value: Any, field_name: str, source_path: Path) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name, source_path)
