from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public.absence import AbsenceReport
from runtime.engine.interfaces.public.query_plan import ResolutionTask
from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.interfaces.public.resolution_run import CheckedSourceSummary
from runtime.engine.provenance import EvidenceSummary


@dataclass(frozen=True)
class ResolutionMemoryCreateRequest:
    run_id: str

    @classmethod
    def from_parts(cls, run_id: str) -> "ResolutionMemoryCreateRequest":
        normalized_run_id = run_id.strip()
        if not normalized_run_id:
            raise ValueError("run_id must be a non-empty string.")
        return cls(run_id=normalized_run_id)


@dataclass(frozen=True)
class ResolutionMemoryReadRequest:
    memory_id: str

    @classmethod
    def from_parts(cls, memory_id: str) -> "ResolutionMemoryReadRequest":
        normalized_memory_id = memory_id.strip()
        if not normalized_memory_id:
            raise ValueError("memory_id must be a non-empty string.")
        return cls(memory_id=normalized_memory_id)


@dataclass(frozen=True)
class ResolutionMemoryCatalogRequest:
    memory_kind: str | None = None
    source_run_id: str | None = None
    task_kind: str | None = None
    checked_source_id: str | None = None

    @classmethod
    def from_parts(
        cls,
        *,
        memory_kind: str | None = None,
        source_run_id: str | None = None,
        task_kind: str | None = None,
        checked_source_id: str | None = None,
    ) -> "ResolutionMemoryCatalogRequest":
        return cls(
            memory_kind=_normalize_optional_string(memory_kind),
            source_run_id=_normalize_optional_string(source_run_id),
            task_kind=_normalize_optional_string(task_kind),
            checked_source_id=_normalize_optional_string(checked_source_id),
        )


@dataclass(frozen=True)
class ResolutionMemoryResultSummary:
    target_ref: str
    object_summary: ObjectSummary
    resolved_resource_id: str | None = None
    source: SourceSummary | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "target_ref": self.target_ref,
            "object": self.object_summary.to_dict(),
        }
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        return payload


@dataclass(frozen=True)
class ResolutionMemoryRecord:
    memory_id: str
    memory_kind: str
    source_run_id: str
    created_at: str
    checked_source_ids: tuple[str, ...]
    checked_source_families: tuple[str, ...]
    checked_sources: tuple[CheckedSourceSummary, ...] = ()
    raw_query: str | None = None
    task_kind: str | None = None
    requested_value: str | None = None
    resolution_task: ResolutionTask | None = None
    result_summaries: tuple[ResolutionMemoryResultSummary, ...] = ()
    absence_report: AbsenceReport | None = None
    useful_source_ids: tuple[str, ...] = ()
    primary_resolved_resource_id: str | None = None
    evidence_summary: tuple[EvidenceSummary, ...] = ()
    notices: tuple[Notice, ...] = ()
    created_by_slice: str = "resolution_memory_v0"
    invalidation_hints: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "memory_id": self.memory_id,
            "memory_kind": self.memory_kind,
            "source_run_id": self.source_run_id,
            "created_at": self.created_at,
            "checked_source_ids": list(self.checked_source_ids),
            "checked_source_families": list(self.checked_source_families),
            "checked_sources": [source.to_dict() for source in self.checked_sources],
            "result_summaries": [summary.to_dict() for summary in self.result_summaries],
            "useful_source_ids": list(self.useful_source_ids),
            "evidence_summary": [summary.to_dict() for summary in self.evidence_summary],
            "notices": [notice.to_dict() for notice in self.notices],
            "created_by_slice": self.created_by_slice,
        }
        if self.raw_query is not None:
            payload["raw_query"] = self.raw_query
        if self.task_kind is not None:
            payload["task_kind"] = self.task_kind
        if self.requested_value is not None:
            payload["requested_value"] = self.requested_value
        if self.resolution_task is not None:
            payload["resolution_task"] = self.resolution_task.to_dict()
        if self.absence_report is not None:
            payload["absence_report"] = self.absence_report.to_dict()
        if self.primary_resolved_resource_id is not None:
            payload["primary_resolved_resource_id"] = self.primary_resolved_resource_id
        if self.invalidation_hints is not None:
            payload["invalidation_hints"] = _clone_json_like(self.invalidation_hints)
        return payload


def _normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None


def _clone_json_like(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _clone_json_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clone_json_like(item) for item in value]
    if isinstance(value, tuple):
        return [_clone_json_like(item) for item in value]
    return value
