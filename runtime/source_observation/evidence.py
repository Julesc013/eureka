"""Evidence candidates derived from normalized observations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from .ids import SourceId, canonical_json, stable_digest
from .normalization import NormalizedObservation


@dataclass(frozen=True, slots=True)
class EvidenceCandidate:
    candidate_id: str
    source_id: SourceId
    observation_id: str
    evidence_kind: str
    claim: Mapping[str, Any]
    confidence: float
    accepted: bool = False
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": str(self.source_id),
            "observation_id": self.observation_id,
            "evidence_kind": self.evidence_kind,
            "claim": dict(self.claim),
            "confidence": self.confidence,
            "accepted": self.accepted,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvidenceCandidate":
        return cls(
            candidate_id=str(data.get("candidate_id", "")),
            source_id=SourceId.from_dict(str(data.get("source_id", ""))),
            observation_id=str(data.get("observation_id", "")),
            evidence_kind=str(data.get("evidence_kind", "")),
            claim=dict(data.get("claim", {}) or {}),
            confidence=float(data.get("confidence", 0.0)),
            accepted=bool(data.get("accepted", False)),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
        )

    @classmethod
    def from_json(cls, text: str) -> "EvidenceCandidate":
        return cls.from_dict(json.loads(text))


def build_evidence_candidate(observation: NormalizedObservation) -> EvidenceCandidate:
    claim = {
        "source_family": observation.source_family,
        "fields": dict(observation.normalized_fields),
    }
    candidate_id = "evc_" + stable_digest(
        {
            "source_id": str(observation.source_id),
            "observation_id": observation.observation_id,
            "claim": claim,
        }
    )
    return EvidenceCandidate(
        candidate_id=candidate_id,
        source_id=observation.source_id,
        observation_id=observation.observation_id,
        evidence_kind="metadata",
        claim=claim,
        confidence=observation.confidence,
        accepted=False,
        limitations=observation.limitations,
        warnings=observation.warnings,
    )
