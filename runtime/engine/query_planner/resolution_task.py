from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from runtime.engine.interfaces.public.query_plan import ResolutionTask


class MalformedResolutionTaskError(ValueError):
    def __init__(self, source_path: Path, message: str) -> None:
        self.source_path = source_path
        super().__init__(f"{source_path}: {message}")


def resolution_task_to_dict(task: ResolutionTask) -> dict[str, Any]:
    return task.to_dict()


def resolution_task_from_dict(
    raw_task: Mapping[str, Any],
    *,
    source_path: Path,
) -> ResolutionTask:
    constraints = raw_task.get("constraints")
    if not isinstance(constraints, Mapping):
        raise MalformedResolutionTaskError(source_path, "Field 'constraints' must be an object.")
    return ResolutionTask(
        raw_query=_require_string(raw_task.get("raw_query"), "raw_query", source_path),
        task_kind=_require_string(raw_task.get("task_kind"), "task_kind", source_path),
        object_type=_require_string(raw_task.get("object_type"), "object_type", source_path),
        constraints=_clone_mapping(constraints, source_path, "constraints"),
        prefer=_require_string_tuple(raw_task.get("prefer"), "prefer", source_path),
        exclude=_require_string_tuple(raw_task.get("exclude"), "exclude", source_path),
        action_hints=_require_string_tuple(raw_task.get("action_hints"), "action_hints", source_path),
        source_hints=_require_string_tuple(raw_task.get("source_hints"), "source_hints", source_path),
        planner_confidence=_require_string(
            raw_task.get("planner_confidence"),
            "planner_confidence",
            source_path,
        ),
        planner_notes=_require_string_tuple(raw_task.get("planner_notes"), "planner_notes", source_path),
    )


def _clone_mapping(
    value: Mapping[str, Any],
    source_path: Path,
    field_name: str,
) -> dict[str, Any]:
    cloned: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise MalformedResolutionTaskError(
                source_path,
                f"Field '{field_name}' keys must be non-empty strings.",
            )
        cloned[key] = _clone_json_like(item, source_path, f"{field_name}.{key}")
    return cloned


def _clone_json_like(value: Any, source_path: Path, field_name: str) -> Any:
    if isinstance(value, Mapping):
        return _clone_mapping(value, source_path, field_name)
    if isinstance(value, list):
        return [_clone_json_like(item, source_path, f"{field_name}[]") for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise MalformedResolutionTaskError(
        source_path,
        f"Field '{field_name}' contains a non-JSON-compatible value.",
    )


def _require_string(value: Any, field_name: str, source_path: Path) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedResolutionTaskError(
            source_path,
            f"Field '{field_name}' must be a non-empty string.",
        )
    return value


def _require_string_tuple(value: Any, field_name: str, source_path: Path) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise MalformedResolutionTaskError(source_path, f"Field '{field_name}' must be a list.")
    values: list[str] = []
    for index, item in enumerate(value):
        values.append(_require_string(item, f"{field_name}[{index}]", source_path))
    return tuple(values)
