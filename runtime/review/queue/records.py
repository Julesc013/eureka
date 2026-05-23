"""Durable review queue record objects."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from runtime.evidence.ledger import EvidenceCandidateRecord


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class ReviewQueueStatus(Enum):
    QUEUED = "queued"
    NEEDS_REVIEW = "needs_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    SUPERSEDED = "superseded"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"


class ReviewEventKind(Enum):
    ITEM_CREATED = "item_created"
    EVIDENCE_LINKED = "evidence_linked"
    SOURCE_CACHE_LINKED = "source_cache_linked"
    DECISION_RECORDED = "decision_recorded"
    STATUS_CHANGED = "status_changed"
    BLOCKED = "blocked"
    SUPERSEDED = "superseded"
    NOTE_ADDED = "note_added"


def new_event_id() -> str:
    return "rve_" + uuid.uuid4().hex


@dataclass(frozen=True, slots=True)
class ReviewItemRecord:
    review_item_id: str
    subject_kind: str
    subject_id: str
    queue_status: ReviewQueueStatus = ReviewQueueStatus.QUEUED
    priority: int = 100
    evidence_id: str | None = None
    source_cache_entry_id: str | None = None
    summary: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_item_id": self.review_item_id,
            "subject_kind": self.subject_kind,
            "subject_id": self.subject_id,
            "queue_status": self.queue_status.value,
            "priority": self.priority,
            "evidence_id": self.evidence_id,
            "source_cache_entry_id": self.source_cache_entry_id,
            "summary": self.summary,
            "payload": dict(self.payload),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_evidence(
        cls,
        evidence: EvidenceCandidateRecord,
        source_cache_entry_id: str | None = None,
        status: ReviewQueueStatus = ReviewQueueStatus.NEEDS_REVIEW,
        priority: int = 100,
    ) -> "ReviewItemRecord":
        now = utc_now()
        payload = {
            "claim_kind": evidence.claim_kind,
            "claim_subject": evidence.claim_subject,
            "claim_payload": dict(evidence.claim_payload),
        }
        return cls(
            review_item_id="rvi_" + _stable_digest({"evidence_id": evidence.evidence_id, "subject": evidence.claim_subject}),
            subject_kind="evidence_candidate",
            subject_id=evidence.evidence_id,
            queue_status=status,
            priority=priority,
            evidence_id=evidence.evidence_id,
            source_cache_entry_id=source_cache_entry_id or evidence.source_cache_entry_id,
            summary=f"review evidence candidate {evidence.evidence_id}",
            payload=payload,
            limitations=evidence.limitations,
            warnings=evidence.warnings,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReviewItemRecord":
        return cls(
            review_item_id=str(data.get("review_item_id", "")),
            subject_kind=str(data.get("subject_kind", "")),
            subject_id=str(data.get("subject_id", "")),
            queue_status=ReviewQueueStatus(str(data.get("queue_status", ReviewQueueStatus.QUEUED.value))),
            priority=int(data.get("priority", 100)),
            evidence_id=data.get("evidence_id"),
            source_cache_entry_id=data.get("source_cache_entry_id"),
            summary=str(data.get("summary", "")),
            payload=dict(data.get("payload", {}) or {}),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    @classmethod
    def from_json(cls, text: str) -> "ReviewItemRecord":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class ReviewEvent:
    review_item_id: str
    event_kind: ReviewEventKind
    event_payload: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=new_event_id)
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "review_item_id": self.review_item_id,
            "event_kind": self.event_kind.value,
            "event_payload": dict(self.event_payload),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReviewEvent":
        return cls(
            event_id=str(data.get("event_id", "")) or new_event_id(),
            review_item_id=str(data.get("review_item_id", "")),
            event_kind=ReviewEventKind(str(data.get("event_kind", ReviewEventKind.NOTE_ADDED.value))),
            event_payload=dict(data.get("event_payload", {}) or {}),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")) or utc_now(),
        )

    @classmethod
    def from_json(cls, text: str) -> "ReviewEvent":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class ReviewQueueSummary:
    review_item_count: int
    review_event_count: int
    evidence_link_count: int
    source_cache_link_count: int
    decision_count: int
    status_counts: Mapping[str, int]
    subject_kind_counts: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_item_count": self.review_item_count,
            "review_event_count": self.review_event_count,
            "evidence_link_count": self.evidence_link_count,
            "source_cache_link_count": self.source_cache_link_count,
            "decision_count": self.decision_count,
            "status_counts": dict(self.status_counts),
            "subject_kind_counts": dict(self.subject_kind_counts),
        }


def _stable_digest(value: Mapping[str, Any]) -> str:
    import hashlib

    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:16]
