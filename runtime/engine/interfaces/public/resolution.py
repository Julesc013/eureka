from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


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
    primary_object: ObjectSummary | None = None
    snapshot_manifest_id: str | None = None
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"notices": [notice.to_dict() for notice in self.notices]}
        if self.primary_object is not None:
            payload["primary_object"] = self.primary_object.to_dict()
        if self.snapshot_manifest_id is not None:
            payload["snapshot_manifest_id"] = self.snapshot_manifest_id
        return payload
