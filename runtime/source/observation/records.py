"""Source records and capabilities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from .ids import SourceId, canonical_json


@dataclass(frozen=True, slots=True)
class SourceLocator:
    kind: str
    value: str
    label: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "value": self.value,
            "label": self.label,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceLocator":
        return cls(
            kind=str(data.get("kind", "")),
            value=str(data.get("value", "")),
            label=str(data.get("label", "")),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True, slots=True)
class SourceCapability:
    name: str
    operations: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "operations": list(self.operations),
            "limitations": list(self.limitations),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceCapability":
        return cls(
            name=str(data.get("name", "")),
            operations=tuple(str(item) for item in data.get("operations", []) or []),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
        )


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_id: SourceId
    source_family: str
    trust_lane: str
    label: str
    locators: tuple[SourceLocator, ...] = ()
    capabilities: tuple[SourceCapability, ...] = ()
    limitations: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.source_id),
            "source_family": self.source_family,
            "trust_lane": self.trust_lane,
            "label": self.label,
            "locators": [locator.to_dict() for locator in self.locators],
            "capabilities": [capability.to_dict() for capability in self.capabilities],
            "limitations": list(self.limitations),
            "metadata": dict(self.metadata),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceRecord":
        return cls(
            source_id=SourceId.from_dict(str(data.get("id", ""))),
            source_family=str(data.get("source_family", "")),
            trust_lane=str(data.get("trust_lane", "")),
            label=str(data.get("label", "")),
            locators=tuple(SourceLocator.from_dict(item) for item in data.get("locators", []) or []),
            capabilities=tuple(SourceCapability.from_dict(item) for item in data.get("capabilities", []) or []),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            metadata=dict(data.get("metadata", {}) or {}),
        )

    @classmethod
    def from_json(cls, text: str) -> "SourceRecord":
        return cls.from_dict(json.loads(text))
