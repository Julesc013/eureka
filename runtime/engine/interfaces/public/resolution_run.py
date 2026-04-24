from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public.absence import AbsenceReport
from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.provenance import EvidenceSummary


@dataclass(frozen=True)
class ExactResolutionRunRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "ExactResolutionRunRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)


@dataclass(frozen=True)
class DeterministicSearchRunRequest:
    query: str

    @classmethod
    def from_parts(cls, query: str) -> "DeterministicSearchRunRequest":
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must be a non-empty string.")
        return cls(query=normalized_query)


@dataclass(frozen=True)
class CheckedSourceSummary:
    source_id: str
    name: str
    source_family: str
    status: str
    trust_lane: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "name": self.name,
            "source_family": self.source_family,
            "status": self.status,
            "trust_lane": self.trust_lane,
        }


@dataclass(frozen=True)
class ResolutionRunResultItem:
    target_ref: str
    object_summary: ObjectSummary
    resolved_resource_id: str | None = None
    source: SourceSummary | None = None
    evidence: tuple[EvidenceSummary, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "target_ref": self.target_ref,
            "object": self.object_summary.to_dict(),
        }
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        if self.evidence:
            payload["evidence"] = [summary.to_dict() for summary in self.evidence]
        return payload


@dataclass(frozen=True)
class ResolutionRunResultSummary:
    result_kind: str
    result_count: int
    items: tuple[ResolutionRunResultItem, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_kind": self.result_kind,
            "result_count": self.result_count,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(frozen=True)
class ResolutionRunRecord:
    run_id: str
    run_kind: str
    requested_value: str
    status: str
    started_at: str
    completed_at: str
    checked_source_ids: tuple[str, ...]
    checked_source_families: tuple[str, ...]
    checked_sources: tuple[CheckedSourceSummary, ...] = ()
    result_summary: ResolutionRunResultSummary | None = None
    absence_report: AbsenceReport | None = None
    notices: tuple[Notice, ...] = ()
    created_by_slice: str = "resolution_runs_v0"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "run_id": self.run_id,
            "run_kind": self.run_kind,
            "requested_value": self.requested_value,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "checked_source_ids": list(self.checked_source_ids),
            "checked_source_families": list(self.checked_source_families),
            "checked_sources": [source.to_dict() for source in self.checked_sources],
            "notices": [notice.to_dict() for notice in self.notices],
            "created_by_slice": self.created_by_slice,
        }
        if self.result_summary is not None:
            payload["result_summary"] = self.result_summary.to_dict()
        if self.absence_report is not None:
            payload["absence_report"] = self.absence_report.to_dict()
        return payload
