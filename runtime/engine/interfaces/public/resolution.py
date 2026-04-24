from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from runtime.engine.provenance import EvidenceSummary
from runtime.engine.representations import RepresentationSummary


@dataclass(frozen=True)
class ResolutionRequest:
    target_ref: str
    requested_outputs: tuple[str, ...] = ()

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        requested_outputs: Sequence[str] | None = None,
    ) -> "ResolutionRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(
            target_ref=normalized_target_ref,
            requested_outputs=tuple(requested_outputs or ()),
        )


@dataclass(frozen=True)
class ObjectSummary:
    id: str
    kind: str | None = None
    label: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"id": self.id}
        if self.kind is not None:
            payload["kind"] = self.kind
        if self.label is not None:
            payload["label"] = self.label
        return payload


@dataclass(frozen=True)
class SourceSummary:
    family: str
    source_id: str | None = None
    label: str | None = None
    locator: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"family": self.family}
        if self.source_id is not None:
            payload["source_id"] = self.source_id
        if self.label is not None:
            payload["label"] = self.label
        if self.locator is not None:
            payload["locator"] = self.locator
        return payload


@dataclass(frozen=True)
class Notice:
    code: str
    severity: str
    message: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"code": self.code, "severity": self.severity}
        if self.message is not None:
            payload["message"] = self.message
        return payload


@dataclass(frozen=True)
class ResolutionResult:
    resolved_resource_id: str | None = None
    primary_object: ObjectSummary | None = None
    source: SourceSummary | None = None
    representations: tuple[RepresentationSummary, ...] = ()
    evidence: tuple[EvidenceSummary, ...] = ()
    snapshot_manifest_id: str | None = None
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"notices": [notice.to_dict() for notice in self.notices]}
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.primary_object is not None:
            payload["primary_object"] = self.primary_object.to_dict()
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        if self.representations:
            payload["representations"] = [summary.to_dict() for summary in self.representations]
        if self.evidence:
            payload["evidence"] = [summary.to_dict() for summary in self.evidence]
        if self.snapshot_manifest_id is not None:
            payload["snapshot_manifest_id"] = self.snapshot_manifest_id
        return payload
