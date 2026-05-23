"""Explicit local review decisions."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .records import ReviewQueueStatus, canonical_json, utc_now


class ReviewDecisionKind(Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    BLOCK = "block"
    SUPERSEDE = "supersede"
    REQUEST_MORE_EVIDENCE = "request_more_evidence"
    NOTE_ONLY = "note_only"


def new_decision_id() -> str:
    return "rvd_" + uuid.uuid4().hex


@dataclass(frozen=True, slots=True)
class ReviewDecision:
    review_item_id: str
    decision_kind: ReviewDecisionKind
    decision_actor: str
    reason: str | None = None
    decision_status: ReviewQueueStatus | None = None
    decision_id: str = field(default_factory=new_decision_id)
    payload: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    def resolved_status(self, current_status: ReviewQueueStatus = ReviewQueueStatus.NEEDS_REVIEW) -> ReviewQueueStatus:
        if self.decision_status is not None:
            return self.decision_status
        return {
            ReviewDecisionKind.ACCEPT: ReviewQueueStatus.ACCEPTED,
            ReviewDecisionKind.REJECT: ReviewQueueStatus.REJECTED,
            ReviewDecisionKind.BLOCK: ReviewQueueStatus.BLOCKED,
            ReviewDecisionKind.SUPERSEDE: ReviewQueueStatus.SUPERSEDED,
            ReviewDecisionKind.REQUEST_MORE_EVIDENCE: ReviewQueueStatus.NEEDS_MORE_EVIDENCE,
            ReviewDecisionKind.NOTE_ONLY: current_status,
        }[self.decision_kind]

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "review_item_id": self.review_item_id,
            "decision_kind": self.decision_kind.value,
            "decision_status": self.decision_status.value if self.decision_status else None,
            "decision_actor": self.decision_actor,
            "reason": self.reason,
            "payload": dict(self.payload),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReviewDecision":
        status = data.get("decision_status")
        return cls(
            decision_id=str(data.get("decision_id", "")) or new_decision_id(),
            review_item_id=str(data.get("review_item_id", "")),
            decision_kind=ReviewDecisionKind(str(data.get("decision_kind", ReviewDecisionKind.NOTE_ONLY.value))),
            decision_status=ReviewQueueStatus(str(status)) if status else None,
            decision_actor=str(data.get("decision_actor", "")),
            reason=data.get("reason"),
            payload=dict(data.get("payload", {}) or {}),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")) or utc_now(),
        )

    @classmethod
    def from_json(cls, text: str) -> "ReviewDecision":
        return cls.from_dict(json.loads(text))
