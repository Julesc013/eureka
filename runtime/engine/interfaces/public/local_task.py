from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from runtime.engine.interfaces.public.resolution import Notice


@dataclass(frozen=True)
class LocalTaskRunRequest:
    task_kind: str
    requested_inputs: dict[str, Any]

    @classmethod
    def from_parts(
        cls,
        task_kind: str,
        requested_inputs: Mapping[str, Any] | None = None,
    ) -> "LocalTaskRunRequest":
        normalized_task_kind = task_kind.strip()
        if not normalized_task_kind:
            raise ValueError("task_kind must be a non-empty string.")
        return cls(
            task_kind=normalized_task_kind,
            requested_inputs=_clone_json_object(requested_inputs or {}),
        )


@dataclass(frozen=True)
class LocalTaskReadRequest:
    task_id: str

    @classmethod
    def from_parts(cls, task_id: str) -> "LocalTaskReadRequest":
        normalized_task_id = task_id.strip()
        if not normalized_task_id:
            raise ValueError("task_id must be a non-empty string.")
        return cls(task_id=normalized_task_id)


@dataclass(frozen=True)
class LocalTaskRecord:
    task_id: str
    task_kind: str
    status: str
    requested_inputs: dict[str, Any]
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    result_summary: dict[str, Any] | None = None
    error_summary: dict[str, Any] | None = None
    output_references: dict[str, Any] | None = None
    notices: tuple[Notice, ...] = ()
    created_by_slice: str = "local_worker_task_model_v0"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "task_id": self.task_id,
            "task_kind": self.task_kind,
            "status": self.status,
            "requested_inputs": _clone_json_object(self.requested_inputs),
            "created_at": self.created_at,
            "notices": [notice.to_dict() for notice in self.notices],
            "created_by_slice": self.created_by_slice,
        }
        if self.started_at is not None:
            payload["started_at"] = self.started_at
        if self.completed_at is not None:
            payload["completed_at"] = self.completed_at
        if self.result_summary is not None:
            payload["result_summary"] = _clone_json_object(self.result_summary)
        if self.error_summary is not None:
            payload["error_summary"] = _clone_json_object(self.error_summary)
        if self.output_references is not None:
            payload["output_references"] = _clone_json_object(self.output_references)
        return payload


def _clone_json_object(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clone_json_object(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clone_json_object(item) for item in value]
    if isinstance(value, tuple):
        return [_clone_json_object(item) for item in value]
    return value
