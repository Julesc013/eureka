from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.compatibility import CompatibilityReason, HostProfile
from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary


@dataclass(frozen=True)
class CompatibilityRequest:
    target_ref: str
    host_profile_id: str

    @classmethod
    def from_parts(cls, target_ref: str, host_profile_id: str) -> "CompatibilityRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        normalized_host_profile_id = host_profile_id.strip()
        if not normalized_host_profile_id:
            raise ValueError("host_profile_id must be a non-empty string.")
        return cls(
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
        )


@dataclass(frozen=True)
class CompatibilityResult:
    status: str
    target_ref: str
    host_profile: HostProfile
    compatibility_status: str | None = None
    resolved_resource_id: str | None = None
    primary_object: ObjectSummary | None = None
    source: SourceSummary | None = None
    reasons: tuple[CompatibilityReason, ...] = ()
    next_steps: tuple[str, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "target_ref": self.target_ref,
            "host_profile": self.host_profile.to_dict(),
            "reasons": [reason.to_dict() for reason in self.reasons],
            "next_steps": list(self.next_steps),
            "notices": [notice.to_dict() for notice in self.notices],
        }
        if self.compatibility_status is not None:
            payload["compatibility_status"] = self.compatibility_status
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.primary_object is not None:
            payload["primary_object"] = self.primary_object.to_dict()
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        return payload
