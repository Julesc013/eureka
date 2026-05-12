"""Source observations derived from explicit metadata responses."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from .ids import SourceId, canonical_json
from .policy import PolicyDecisionStatus, SourcePolicy, evaluate_source_policy
from .records import SourceRecord
from .responses import ResponseFingerprint
from .responses import MetadataResponse
from .ids import stable_digest


@dataclass(frozen=True, slots=True)
class SourceObservation:
    observation_id: str
    source_id: SourceId
    request_id: str
    response_id: str
    observation_kind: str
    observed_fields: Mapping[str, Any]
    response_fingerprint: ResponseFingerprint
    confidence: float
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "source_id": str(self.source_id),
            "request_id": self.request_id,
            "response_id": self.response_id,
            "observation_kind": self.observation_kind,
            "observed_fields": dict(self.observed_fields),
            "response_fingerprint": self.response_fingerprint.to_dict(),
            "confidence": self.confidence,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceObservation":
        return cls(
            observation_id=str(data.get("observation_id", "")),
            source_id=SourceId.from_dict(str(data.get("source_id", ""))),
            request_id=str(data.get("request_id", "")),
            response_id=str(data.get("response_id", "")),
            observation_kind=str(data.get("observation_kind", "")),
            observed_fields=dict(data.get("observed_fields", {}) or {}),
            response_fingerprint=ResponseFingerprint.from_dict(data.get("response_fingerprint", {}) or {}),
            confidence=float(data.get("confidence", 0.0)),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
        )

    @classmethod
    def from_json(cls, text: str) -> "SourceObservation":
        return cls.from_dict(json.loads(text))


def build_source_observation(
    response: MetadataResponse,
    source_record: SourceRecord,
    policy: SourcePolicy | None = None,
    observed_fields: Mapping[str, Any] | None = None,
) -> SourceObservation:
    decision = evaluate_source_policy(
        source_record,
        "metadata_observation",
        {"policy": policy or SourcePolicy()},
    )
    warnings = list(response.warnings)
    if decision.status is not PolicyDecisionStatus.ALLOWED:
        warnings.append(decision.reason)
    fields = dict(observed_fields or {})
    observation_id = "obs_" + stable_digest(
        {
            "source_id": str(response.source_id),
            "request_id": response.request_id,
            "response_id": response.response_id,
            "fingerprint": response.fingerprint.to_dict(),
        }
    )
    return SourceObservation(
        observation_id=observation_id,
        source_id=response.source_id,
        request_id=response.request_id,
        response_id=response.response_id,
        observation_kind=response.payload_format,
        observed_fields=fields,
        response_fingerprint=response.fingerprint,
        confidence=0.7 if decision.status is PolicyDecisionStatus.ALLOWED else 0.3,
        limitations=tuple(source_record.limitations + response.limitations + decision.limitations),
        warnings=tuple(warnings),
    )
