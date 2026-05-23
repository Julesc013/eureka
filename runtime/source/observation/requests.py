"""Metadata request descriptions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from .ids import SourceId, canonical_json, stable_digest, utc_now


@dataclass(frozen=True, slots=True)
class MetadataRequest:
    request_id: str
    source_id: SourceId
    request_kind: str
    target: str
    requested_operation: str = "metadata_observation"
    parameters: Mapping[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def build(
        cls,
        source_id: SourceId,
        request_kind: str,
        target: str,
        requested_operation: str = "metadata_observation",
        parameters: Mapping[str, Any] | None = None,
        created_at: str | None = None,
    ) -> "MetadataRequest":
        params = dict(parameters or {})
        created = created_at or utc_now()
        request_id = "req_" + stable_digest(
            {
                "source_id": str(source_id),
                "request_kind": request_kind,
                "target": target,
                "requested_operation": requested_operation,
                "parameters": params,
                "created_at": created,
            }
        )
        return cls(
            request_id=request_id,
            source_id=source_id,
            request_kind=request_kind,
            target=target,
            requested_operation=requested_operation,
            parameters=params,
            created_at=created,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source_id": str(self.source_id),
            "request_kind": self.request_kind,
            "target": self.target,
            "requested_operation": self.requested_operation,
            "parameters": dict(self.parameters),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MetadataRequest":
        return cls(
            request_id=str(data.get("request_id", "")),
            source_id=SourceId.from_dict(str(data.get("source_id", ""))),
            request_kind=str(data.get("request_kind", "")),
            target=str(data.get("target", "")),
            requested_operation=str(data.get("requested_operation", "metadata_observation")),
            parameters=dict(data.get("parameters", {}) or {}),
            created_at=str(data.get("created_at", "")),
        )

    @classmethod
    def from_json(cls, text: str) -> "MetadataRequest":
        return cls.from_dict(json.loads(text))
