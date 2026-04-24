from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public.resolution import Notice


@dataclass(frozen=True)
class LocalIndexBuildRequest:
    index_path: str

    @classmethod
    def from_parts(cls, index_path: str) -> "LocalIndexBuildRequest":
        normalized_index_path = index_path.strip()
        if not normalized_index_path:
            raise ValueError("index_path must be a non-empty string.")
        return cls(index_path=normalized_index_path)


@dataclass(frozen=True)
class LocalIndexStatusRequest:
    index_path: str

    @classmethod
    def from_parts(cls, index_path: str) -> "LocalIndexStatusRequest":
        normalized_index_path = index_path.strip()
        if not normalized_index_path:
            raise ValueError("index_path must be a non-empty string.")
        return cls(index_path=normalized_index_path)


@dataclass(frozen=True)
class LocalIndexQueryRequest:
    index_path: str
    query: str

    @classmethod
    def from_parts(cls, index_path: str, query: str) -> "LocalIndexQueryRequest":
        normalized_index_path = index_path.strip()
        normalized_query = query.strip()
        if not normalized_index_path:
            raise ValueError("index_path must be a non-empty string.")
        if not normalized_query:
            raise ValueError("query must be a non-empty string.")
        return cls(index_path=normalized_index_path, query=normalized_query)


@dataclass(frozen=True)
class LocalIndexRecordSummary:
    index_record_id: str
    record_kind: str
    label: str
    summary: str | None = None
    target_ref: str | None = None
    resolved_resource_id: str | None = None
    source_id: str | None = None
    source_family: str | None = None
    source_label: str | None = None
    subject_key: str | None = None
    version_or_state: str | None = None
    representation_id: str | None = None
    member_path: str | None = None
    evidence: tuple[str, ...] = ()
    route_hints: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "index_record_id": self.index_record_id,
            "record_kind": self.record_kind,
            "label": self.label,
            "evidence": list(self.evidence),
            "route_hints": _clone_json_like(self.route_hints or {}),
        }
        if self.summary is not None:
            payload["summary"] = self.summary
        if self.target_ref is not None:
            payload["target_ref"] = self.target_ref
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.source_id is not None:
            payload["source_id"] = self.source_id
        if self.source_family is not None:
            payload["source_family"] = self.source_family
        if self.source_label is not None:
            payload["source_label"] = self.source_label
        if self.subject_key is not None:
            payload["subject_key"] = self.subject_key
        if self.version_or_state is not None:
            payload["version_or_state"] = self.version_or_state
        if self.representation_id is not None:
            payload["representation_id"] = self.representation_id
        if self.member_path is not None:
            payload["member_path"] = self.member_path
        return payload


@dataclass(frozen=True)
class LocalIndexMetadata:
    index_path: str
    fts_mode: str
    record_count: int
    record_kind_counts: dict[str, int]
    index_path_kind: str = "bootstrap_local_path"

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_path_kind": self.index_path_kind,
            "index_path": self.index_path,
            "fts_mode": self.fts_mode,
            "record_count": self.record_count,
            "record_kind_counts": dict(self.record_kind_counts),
        }


@dataclass(frozen=True)
class LocalIndexBuildResult:
    status: str
    metadata: LocalIndexMetadata
    notices: tuple[Notice, ...] = ()


@dataclass(frozen=True)
class LocalIndexStatusResult:
    status: str
    metadata: LocalIndexMetadata
    notices: tuple[Notice, ...] = ()


@dataclass(frozen=True)
class LocalIndexQueryResult:
    query: str
    status: str
    metadata: LocalIndexMetadata
    results: tuple[LocalIndexRecordSummary, ...] = ()
    notices: tuple[Notice, ...] = ()


def _clone_json_like(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _clone_json_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clone_json_like(item) for item in value]
    if isinstance(value, tuple):
        return [_clone_json_like(item) for item in value]
    return value
