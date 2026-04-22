from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.provenance import EvidenceSummary


@dataclass(frozen=True)
class ResolveAbsenceRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "ResolveAbsenceRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)


@dataclass(frozen=True)
class SearchAbsenceRequest:
    query: str

    @classmethod
    def from_parts(cls, query: str) -> "SearchAbsenceRequest":
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must be a non-empty string.")
        return cls(query=normalized_query)


@dataclass(frozen=True)
class AbsenceNearMatch:
    match_kind: str
    target_ref: str
    resolved_resource_id: str
    object_summary: ObjectSummary
    source: SourceSummary | None = None
    subject_key: str | None = None
    version_or_state: str | None = None
    normalized_version_or_state: str | None = None
    evidence: tuple[EvidenceSummary, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "match_kind": self.match_kind,
            "target_ref": self.target_ref,
            "resolved_resource_id": self.resolved_resource_id,
            "object": self.object_summary.to_dict(),
        }
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        if self.subject_key is not None:
            payload["subject_key"] = self.subject_key
        if self.version_or_state is not None:
            payload["version_or_state"] = self.version_or_state
        if self.normalized_version_or_state is not None:
            payload["normalized_version_or_state"] = self.normalized_version_or_state
        if self.evidence:
            payload["evidence"] = [summary.to_dict() for summary in self.evidence]
        return payload


@dataclass(frozen=True)
class AbsenceReport:
    request_kind: str
    requested_value: str
    status: str
    checked_source_families: tuple[str, ...]
    checked_record_count: int
    checked_subject_count: int
    likely_reason_code: str
    reason_message: str
    near_matches: tuple[AbsenceNearMatch, ...] = ()
    next_steps: tuple[str, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "request_kind": self.request_kind,
            "requested_value": self.requested_value,
            "status": self.status,
            "checked_source_families": list(self.checked_source_families),
            "checked_record_count": self.checked_record_count,
            "checked_subject_count": self.checked_subject_count,
            "likely_reason_code": self.likely_reason_code,
            "reason_message": self.reason_message,
            "near_matches": [match.to_dict() for match in self.near_matches],
            "next_steps": list(self.next_steps),
            "notices": [notice.to_dict() for notice in self.notices],
        }
        return payload
