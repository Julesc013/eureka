from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.provenance import EvidenceSummary


@dataclass(frozen=True)
class SubjectStatesRequest:
    subject_key: str

    @classmethod
    def from_parts(cls, subject_key: str) -> "SubjectStatesRequest":
        normalized_subject_key = subject_key.strip().casefold()
        if not normalized_subject_key:
            raise ValueError("subject_key must be a non-empty string.")
        return cls(subject_key=normalized_subject_key)


@dataclass(frozen=True)
class SubjectSummary:
    subject_key: str
    subject_label: str
    state_count: int
    source_family_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "subject_key": self.subject_key,
            "subject_label": self.subject_label,
            "state_count": self.state_count,
        }
        if self.source_family_hint is not None:
            payload["source_family_hint"] = self.source_family_hint
        return payload


@dataclass(frozen=True)
class SubjectStateSummary:
    target_ref: str
    resolved_resource_id: str
    object_summary: ObjectSummary
    version_or_state: str | None = None
    normalized_version_or_state: str | None = None
    source: SourceSummary | None = None
    evidence: tuple[EvidenceSummary, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "target_ref": self.target_ref,
            "resolved_resource_id": self.resolved_resource_id,
            "object": self.object_summary.to_dict(),
        }
        if self.version_or_state is not None:
            payload["version_or_state"] = self.version_or_state
        if self.normalized_version_or_state is not None:
            payload["normalized_version_or_state"] = self.normalized_version_or_state
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        if self.evidence:
            payload["evidence"] = [summary.to_dict() for summary in self.evidence]
        return payload


@dataclass(frozen=True)
class SubjectStatesResult:
    status: str
    requested_subject_key: str
    subject: SubjectSummary | None = None
    states: tuple[SubjectStateSummary, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "requested_subject_key": self.requested_subject_key,
            "states": [state.to_dict() for state in self.states],
            "notices": [notice.to_dict() for notice in self.notices],
        }
        if self.subject is not None:
            payload["subject"] = self.subject.to_dict()
        return payload
