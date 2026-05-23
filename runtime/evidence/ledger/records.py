"""Durable evidence ledger record objects."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from runtime.source.observation import EvidenceCandidate


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class EvidenceReviewStatus(Enum):
    CANDIDATE = "candidate"
    NEEDS_REVIEW = "needs_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    SUPERSEDED = "superseded"


class EvidenceEventKind(Enum):
    CANDIDATE_CREATED = "candidate_created"
    SOURCE_CACHE_LINKED = "source_cache_linked"
    NORMALIZED_OBSERVATION_LINKED = "normalized_observation_linked"
    CONFLICT_DETECTED = "conflict_detected"
    REVIEW_REQUESTED = "review_requested"
    REVIEW_STATUS_CHANGED = "review_status_changed"
    SUPERSEDED = "superseded"
    BLOCKED = "blocked"
    NOTE_ADDED = "note_added"


def new_event_id() -> str:
    return "eve_" + uuid.uuid4().hex


@dataclass(frozen=True, slots=True)
class EvidenceCandidateRecord:
    evidence_id: str
    source_id: str
    observation_id: str
    normalized_observation_id: str
    claim_kind: str
    claim_subject: str
    claim_payload: Mapping[str, Any]
    status: EvidenceReviewStatus = EvidenceReviewStatus.CANDIDATE
    source_cache_entry_id: str | None = None
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "source_cache_entry_id": self.source_cache_entry_id,
            "observation_id": self.observation_id,
            "normalized_observation_id": self.normalized_observation_id,
            "claim_kind": self.claim_kind,
            "claim_subject": self.claim_subject,
            "claim_payload": dict(self.claim_payload),
            "status": self.status.value,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_candidate(
        cls,
        candidate: EvidenceCandidate,
        normalized_observation_id: str = "",
        source_cache_entry_id: str | None = None,
        status: EvidenceReviewStatus = EvidenceReviewStatus.CANDIDATE,
    ) -> "EvidenceCandidateRecord":
        now = utc_now()
        return cls(
            evidence_id=candidate.candidate_id,
            source_id=str(candidate.source_id),
            source_cache_entry_id=source_cache_entry_id,
            observation_id=candidate.observation_id,
            normalized_observation_id=normalized_observation_id,
            claim_kind=candidate.evidence_kind,
            claim_subject=str(candidate.source_id),
            claim_payload=dict(candidate.claim),
            status=status,
            limitations=candidate.limitations,
            warnings=candidate.warnings,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvidenceCandidateRecord":
        return cls(
            evidence_id=str(data.get("evidence_id", "")),
            source_id=str(data.get("source_id", "")),
            source_cache_entry_id=data.get("source_cache_entry_id"),
            observation_id=str(data.get("observation_id", "")),
            normalized_observation_id=str(data.get("normalized_observation_id", "")),
            claim_kind=str(data.get("claim_kind", "")),
            claim_subject=str(data.get("claim_subject", "")),
            claim_payload=dict(data.get("claim_payload", {}) or {}),
            status=EvidenceReviewStatus(str(data.get("status", EvidenceReviewStatus.CANDIDATE.value))),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    @classmethod
    def from_json(cls, text: str) -> "EvidenceCandidateRecord":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class EvidenceEvent:
    evidence_id: str
    event_kind: EvidenceEventKind
    event_payload: Mapping[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=new_event_id)
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "evidence_id": self.evidence_id,
            "event_kind": self.event_kind.value,
            "event_payload": dict(self.event_payload),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvidenceEvent":
        return cls(
            event_id=str(data.get("event_id", "")) or new_event_id(),
            evidence_id=str(data.get("evidence_id", "")),
            event_kind=EvidenceEventKind(str(data.get("event_kind", EvidenceEventKind.NOTE_ADDED.value))),
            event_payload=dict(data.get("event_payload", {}) or {}),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")) or utc_now(),
        )

    @classmethod
    def from_json(cls, text: str) -> "EvidenceEvent":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class EvidenceConflict:
    conflict_id: str
    evidence_id: str
    conflict_kind: str
    conflict_payload: Mapping[str, Any]
    conflicting_evidence_id: str | None = None
    status: EvidenceReviewStatus = EvidenceReviewStatus.NEEDS_REVIEW
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "evidence_id": self.evidence_id,
            "conflicting_evidence_id": self.conflicting_evidence_id,
            "conflict_kind": self.conflict_kind,
            "conflict_payload": dict(self.conflict_payload),
            "status": self.status.value,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvidenceConflict":
        return cls(
            conflict_id=str(data.get("conflict_id", "")),
            evidence_id=str(data.get("evidence_id", "")),
            conflicting_evidence_id=data.get("conflicting_evidence_id"),
            conflict_kind=str(data.get("conflict_kind", "")),
            conflict_payload=dict(data.get("conflict_payload", {}) or {}),
            status=EvidenceReviewStatus(str(data.get("status", EvidenceReviewStatus.NEEDS_REVIEW.value))),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    @classmethod
    def from_json(cls, text: str) -> "EvidenceConflict":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class EvidenceLedgerSummary:
    evidence_candidate_count: int
    evidence_event_count: int
    source_cache_link_count: int
    conflict_count: int
    review_status_count: int
    status_counts: Mapping[str, int]
    claim_kind_counts: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_candidate_count": self.evidence_candidate_count,
            "evidence_event_count": self.evidence_event_count,
            "source_cache_link_count": self.source_cache_link_count,
            "conflict_count": self.conflict_count,
            "review_status_count": self.review_status_count,
            "status_counts": dict(self.status_counts),
            "claim_kind_counts": dict(self.claim_kind_counts),
        }
