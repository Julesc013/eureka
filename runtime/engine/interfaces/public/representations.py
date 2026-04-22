from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.representations import RepresentationSummary


@dataclass(frozen=True)
class RepresentationsRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "RepresentationsRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)


@dataclass(frozen=True)
class RepresentationsResult:
    status: str
    target_ref: str
    resolved_resource_id: str | None = None
    primary_object: ObjectSummary | None = None
    source: SourceSummary | None = None
    representations: tuple[RepresentationSummary, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "target_ref": self.target_ref,
            "representations": [summary.to_dict() for summary in self.representations],
            "notices": [notice.to_dict() for notice in self.notices],
        }
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.primary_object is not None:
            payload["primary_object"] = self.primary_object.to_dict()
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        return payload
