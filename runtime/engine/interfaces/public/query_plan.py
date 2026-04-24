from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QueryPlanRequest:
    raw_query: str

    @classmethod
    def from_parts(cls, raw_query: str) -> "QueryPlanRequest":
        normalized_query = raw_query.strip()
        if not normalized_query:
            raise ValueError("raw_query must be a non-empty string.")
        return cls(raw_query=normalized_query)


@dataclass(frozen=True)
class ResolutionTask:
    raw_query: str
    task_kind: str
    object_type: str
    constraints: dict[str, Any]
    prefer: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    action_hints: tuple[str, ...] = ()
    source_hints: tuple[str, ...] = ()
    planner_confidence: str = "low"
    planner_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_query": self.raw_query,
            "task_kind": self.task_kind,
            "object_type": self.object_type,
            "constraints": _clone_json_like(self.constraints),
            "prefer": list(self.prefer),
            "exclude": list(self.exclude),
            "action_hints": list(self.action_hints),
            "source_hints": list(self.source_hints),
            "planner_confidence": self.planner_confidence,
            "planner_notes": list(self.planner_notes),
        }


def _clone_json_like(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _clone_json_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clone_json_like(item) for item in value]
    if isinstance(value, tuple):
        return [_clone_json_like(item) for item in value]
    return value
