"""Review item candidates for source observations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .evidence import EvidenceCandidate
from .ids import SourceId, canonical_json, stable_digest


class ReviewStatus(Enum):
    CANDIDATE = "candidate"
    NEEDS_REVIEW = "needs_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    SUPERSEDED = "superseded"


@dataclass(frozen=True, slots=True)
class ReviewItem:
    review_item_id: str
    candidate_id: str
    source_id: SourceId
    review_status: ReviewStatus
    summary: str
    decision: str | None = None
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_item_id": self.review_item_id,
            "candidate_id": self.candidate_id,
            "source_id": str(self.source_id),
            "review_status": self.review_status.value,
            "summary": self.summary,
            "decision": self.decision,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReviewItem":
        return cls(
            review_item_id=str(data.get("review_item_id", "")),
            candidate_id=str(data.get("candidate_id", "")),
            source_id=SourceId.from_dict(str(data.get("source_id", ""))),
            review_status=ReviewStatus(str(data.get("review_status", ReviewStatus.CANDIDATE.value))),
            summary=str(data.get("summary", "")),
            decision=data.get("decision"),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
        )

    @classmethod
    def from_json(cls, text: str) -> "ReviewItem":
        return cls.from_dict(json.loads(text))


def build_review_item(candidate: EvidenceCandidate) -> ReviewItem:
    review_item_id = "rev_" + stable_digest(
        {
            "candidate_id": candidate.candidate_id,
            "source_id": str(candidate.source_id),
            "claim": candidate.claim,
        }
    )
    return ReviewItem(
        review_item_id=review_item_id,
        candidate_id=candidate.candidate_id,
        source_id=candidate.source_id,
        review_status=ReviewStatus.NEEDS_REVIEW,
        summary="metadata evidence candidate requires review",
        decision=None,
        limitations=candidate.limitations,
        warnings=candidate.warnings,
    )
