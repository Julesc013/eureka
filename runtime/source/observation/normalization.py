"""Normalization for explicit metadata response payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from .ids import SourceId, canonical_json, stable_digest
from .observations import build_source_observation
from .policy import SourcePolicy
from .records import SourceRecord
from .responses import MetadataResponse


@dataclass(frozen=True, slots=True)
class NormalizedObservation:
    normalized_observation_id: str
    source_id: SourceId
    source_family: str
    observation_id: str
    normalized_fields: Mapping[str, Any]
    confidence: float
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "normalized_observation_id": self.normalized_observation_id,
            "source_id": str(self.source_id),
            "source_family": self.source_family,
            "observation_id": self.observation_id,
            "normalized_fields": dict(self.normalized_fields),
            "confidence": self.confidence,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "NormalizedObservation":
        return cls(
            normalized_observation_id=str(data.get("normalized_observation_id", "")),
            source_id=SourceId.from_dict(str(data.get("source_id", ""))),
            source_family=str(data.get("source_family", "")),
            observation_id=str(data.get("observation_id", "")),
            normalized_fields=dict(data.get("normalized_fields", {}) or {}),
            confidence=float(data.get("confidence", 0.0)),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
        )

    @classmethod
    def from_json(cls, text: str) -> "NormalizedObservation":
        return cls.from_dict(json.loads(text))


def normalize_metadata_response(
    response: MetadataResponse,
    source_record: SourceRecord,
    policy: SourcePolicy | None = None,
) -> NormalizedObservation:
    fields = _extract_fields(response)
    observation = build_source_observation(response, source_record, policy=policy, observed_fields=fields)
    normalized_id = "norm_" + stable_digest(observation.to_dict())
    return NormalizedObservation(
        normalized_observation_id=normalized_id,
        source_id=response.source_id,
        source_family=source_record.source_family,
        observation_id=observation.observation_id,
        normalized_fields=fields,
        confidence=observation.confidence,
        limitations=observation.limitations,
        warnings=observation.warnings,
    )


def _extract_fields(response: MetadataResponse) -> dict[str, Any]:
    if response.payload_format == "json":
        try:
            parsed = json.loads(response.payload)
        except json.JSONDecodeError:
            return {"raw_payload": response.payload}
        if isinstance(parsed, Mapping):
            return dict(parsed)
        return {"items": parsed}
    return {"raw_payload": response.payload}
