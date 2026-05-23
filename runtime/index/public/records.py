"""Record objects for the local reviewed public index."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from runtime.evidence.ledger import EvidenceCandidateRecord
from runtime.review.queue import ReviewDecision, ReviewItemRecord
from runtime.source.cache import SourceCacheEntry


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class PublicIndexRecord:
    record_id: str
    source_id: str
    source_cache_entry_id: str
    evidence_id: str
    review_item_id: str
    review_decision_id: str
    title: str
    description: str
    normalized_fields: Mapping[str, Any]
    searchable_text: str
    source_family: str
    trust_lane: str
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.record_id,
            "record_id": self.record_id,
            "source_id": self.source_id,
            "source_cache_entry_id": self.source_cache_entry_id,
            "evidence_id": self.evidence_id,
            "review_item_id": self.review_item_id,
            "review_decision_id": self.review_decision_id,
            "title": self.title,
            "description": self.description,
            "normalized_fields": dict(self.normalized_fields),
            "searchable_text": self.searchable_text,
            "source_family": self.source_family,
            "trust_lane": self.trust_lane,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PublicIndexRecord":
        return cls(
            record_id=str(data.get("record_id") or data.get("id") or ""),
            source_id=str(data.get("source_id", "")),
            source_cache_entry_id=str(data.get("source_cache_entry_id", "")),
            evidence_id=str(data.get("evidence_id", "")),
            review_item_id=str(data.get("review_item_id", "")),
            review_decision_id=str(data.get("review_decision_id", "")),
            title=str(data.get("title", "")),
            description=str(data.get("description", "")),
            normalized_fields=dict(data.get("normalized_fields", {}) or {}),
            searchable_text=str(data.get("searchable_text", "")),
            source_family=str(data.get("source_family", "")),
            trust_lane=str(data.get("trust_lane", "")),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")) or utc_now(),
            updated_at=str(data.get("updated_at", "")) or utc_now(),
        )

    @classmethod
    def from_json(cls, text: str) -> "PublicIndexRecord":
        return cls.from_dict(json.loads(text))

    @classmethod
    def from_reviewed_inputs(
        cls,
        cache_entry: SourceCacheEntry,
        evidence: EvidenceCandidateRecord,
        review_item: ReviewItemRecord,
        decision: ReviewDecision,
    ) -> "PublicIndexRecord":
        normalized_fields = _extract_normalized_fields(cache_entry, evidence)
        title = _choose_text(normalized_fields, ("title", "name", "label")) or evidence.claim_subject or cache_entry.source_id
        description = (
            _choose_text(normalized_fields, ("description", "summary", "version"))
            or review_item.summary
            or f"reviewed local record for {cache_entry.source_id}"
        )
        searchable_text = _searchable_text(
            (
                title,
                description,
                cache_entry.source_id,
                cache_entry.source_family,
                evidence.claim_kind,
                evidence.claim_subject,
                normalized_fields,
                evidence.claim_payload,
            )
        )
        now = utc_now()
        record_id = "pir_" + stable_digest(
            {
                "source_cache_entry_id": cache_entry.entry_id,
                "evidence_id": evidence.evidence_id,
                "review_item_id": review_item.review_item_id,
                "review_decision_id": decision.decision_id,
            }
        )
        return cls(
            record_id=record_id,
            source_id=cache_entry.source_id,
            source_cache_entry_id=cache_entry.entry_id,
            evidence_id=evidence.evidence_id,
            review_item_id=review_item.review_item_id,
            review_decision_id=decision.decision_id,
            title=title,
            description=description,
            normalized_fields=normalized_fields,
            searchable_text=searchable_text,
            source_family=cache_entry.source_family,
            trust_lane=cache_entry.trust_lane,
            limitations=tuple(cache_entry.limitations + evidence.limitations + review_item.limitations + decision.limitations),
            warnings=tuple(cache_entry.warnings + evidence.warnings + review_item.warnings + decision.warnings),
            created_at=now,
            updated_at=now,
        )


@dataclass(frozen=True, slots=True)
class PublicIndexRebuild:
    rebuild_id: str
    status: str
    included_count: int
    excluded_count: int
    include_statuses: tuple[str, ...]
    source_cache_db: str
    evidence_ledger_db: str
    review_queue_db: str
    public_index_db: str
    dry_run: bool
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rebuild_id": self.rebuild_id,
            "status": self.status,
            "included_count": self.included_count,
            "excluded_count": self.excluded_count,
            "include_statuses": list(self.include_statuses),
            "source_cache_db": self.source_cache_db,
            "evidence_ledger_db": self.evidence_ledger_db,
            "review_queue_db": self.review_queue_db,
            "public_index_db": self.public_index_db,
            "dry_run": self.dry_run,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PublicIndexRebuild":
        return cls(
            rebuild_id=str(data.get("rebuild_id", "")),
            status=str(data.get("status", "")),
            included_count=int(data.get("included_count", 0)),
            excluded_count=int(data.get("excluded_count", 0)),
            include_statuses=tuple(str(item) for item in data.get("include_statuses", []) or []),
            source_cache_db=str(data.get("source_cache_db", "")),
            evidence_ledger_db=str(data.get("evidence_ledger_db", "")),
            review_queue_db=str(data.get("review_queue_db", "")),
            public_index_db=str(data.get("public_index_db", "")),
            dry_run=bool(data.get("dry_run", False)),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")) or utc_now(),
        )


@dataclass(frozen=True, slots=True)
class PublicIndexSearchResult:
    record_id: str
    title: str
    description: str
    source_id: str
    score: float
    matched_terms: tuple[str, ...]
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "title": self.title,
            "description": self.description,
            "source_id": self.source_id,
            "score": self.score,
            "matched_terms": list(self.matched_terms),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True, slots=True)
class PublicIndexAbsenceReport:
    query: str
    result_count: int
    checked_sources: tuple[str, ...]
    limitations: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "result_count": self.result_count,
            "checked_sources": list(self.checked_sources),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class PublicIndexSummary:
    record_count: int
    rebuild_count: int
    source_ref_count: int
    evidence_ref_count: int
    review_ref_count: int
    source_counts: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_count": self.record_count,
            "rebuild_count": self.rebuild_count,
            "source_ref_count": self.source_ref_count,
            "evidence_ref_count": self.evidence_ref_count,
            "review_ref_count": self.review_ref_count,
            "source_counts": dict(self.source_counts),
        }


def _extract_normalized_fields(cache_entry: SourceCacheEntry, evidence: EvidenceCandidateRecord) -> dict[str, Any]:
    payload = dict(cache_entry.payload or {})
    normalized = payload.get("normalized_observation")
    if isinstance(normalized, Mapping):
        fields = normalized.get("normalized_fields")
        if isinstance(fields, Mapping):
            return dict(fields)
    claim_payload = dict(evidence.claim_payload or {})
    fields = claim_payload.get("normalized_fields")
    if isinstance(fields, Mapping):
        return dict(fields)
    return claim_payload


def _choose_text(fields: Mapping[str, Any], keys: Sequence[str]) -> str:
    lowered = {str(key).lower(): value for key, value in fields.items()}
    for key in keys:
        value = lowered.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _searchable_text(values: Any) -> str:
    parts: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, Mapping):
            for key, item in value.items():
                parts.append(str(key))
                visit(item)
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                visit(item)
            return
        text = str(value).strip()
        if text:
            parts.append(text)

    visit(values)
    return " ".join(parts).lower()
