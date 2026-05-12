"""Connector health summary objects."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from .ids import SourceId, canonical_json, utc_now


@dataclass(frozen=True, slots=True)
class ConnectorHealth:
    source_id: SourceId
    status: str
    checked_at: str = ""
    observations_seen: int = 0
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.checked_at:
            object.__setattr__(self, "checked_at", utc_now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": str(self.source_id),
            "status": self.status,
            "checked_at": self.checked_at,
            "observations_seen": self.observations_seen,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ConnectorHealth":
        return cls(
            source_id=SourceId.from_dict(str(data.get("source_id", ""))),
            status=str(data.get("status", "")),
            checked_at=str(data.get("checked_at", "")),
            observations_seen=int(data.get("observations_seen", 0)),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            errors=tuple(str(item) for item in data.get("errors", []) or []),
        )

    @classmethod
    def from_json(cls, text: str) -> "ConnectorHealth":
        return cls.from_dict(json.loads(text))
