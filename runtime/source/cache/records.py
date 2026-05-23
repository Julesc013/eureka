"""Durable source cache record objects."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class SourceCacheStatus(Enum):
    CACHED = "cached"
    STALE = "stale"
    SUPERSEDED = "superseded"
    BLOCKED = "blocked"
    INVALID = "invalid"
    NOT_EVALUABLE = "not_evaluable"


@dataclass(frozen=True, slots=True)
class SourceCacheEntry:
    entry_id: str
    source_id: str
    source_family: str
    trust_lane: str
    request_id: str
    response_id: str
    observation_id: str
    normalized_observation_id: str
    response_fingerprint: str
    status: SourceCacheStatus
    payload: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "source_id": self.source_id,
            "source_family": self.source_family,
            "trust_lane": self.trust_lane,
            "request_id": self.request_id,
            "response_id": self.response_id,
            "observation_id": self.observation_id,
            "normalized_observation_id": self.normalized_observation_id,
            "response_fingerprint": self.response_fingerprint,
            "status": self.status.value,
            "payload": dict(self.payload),
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceCacheEntry":
        return cls(
            entry_id=str(data.get("entry_id", "")),
            source_id=str(data.get("source_id", "")),
            source_family=str(data.get("source_family", "")),
            trust_lane=str(data.get("trust_lane", "")),
            request_id=str(data.get("request_id", "")),
            response_id=str(data.get("response_id", "")),
            observation_id=str(data.get("observation_id", "")),
            normalized_observation_id=str(data.get("normalized_observation_id", "")),
            response_fingerprint=str(data.get("response_fingerprint", "")),
            status=SourceCacheStatus(str(data.get("status", SourceCacheStatus.NOT_EVALUABLE.value))),
            payload=dict(data.get("payload", {}) or {}),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    @classmethod
    def from_json(cls, text: str) -> "SourceCacheEntry":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class SourceCacheWrite:
    table: str
    record_id: str
    status: str
    row_count: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "table": self.table,
            "record_id": self.record_id,
            "status": self.status,
            "row_count": self.row_count,
        }


@dataclass(frozen=True, slots=True)
class SourceCacheRead:
    found: bool
    record_id: str
    payload: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "found": self.found,
            "record_id": self.record_id,
            "payload": dict(self.payload or {}),
        }


@dataclass(frozen=True, slots=True)
class SourceCacheSummary:
    source_record_count: int
    metadata_response_count: int
    source_observation_count: int
    normalized_observation_count: int
    cache_entry_count: int
    status_counts: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_record_count": self.source_record_count,
            "metadata_response_count": self.metadata_response_count,
            "source_observation_count": self.source_observation_count,
            "normalized_observation_count": self.normalized_observation_count,
            "cache_entry_count": self.cache_entry_count,
            "status_counts": dict(self.status_counts),
        }
