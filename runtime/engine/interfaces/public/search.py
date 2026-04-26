from __future__ import annotations

from dataclasses import dataclass

from runtime.engine.provenance import EvidenceSummary
from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary


@dataclass(frozen=True)
class SearchRequest:
    query: str

    @classmethod
    def from_parts(cls, query: str) -> "SearchRequest":
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must be a non-empty string.")
        return cls(query=normalized_query)


@dataclass(frozen=True)
class SearchResultEntry:
    target_ref: str
    object_summary: ObjectSummary
    resolved_resource_id: str | None = None
    source: SourceSummary | None = None
    evidence: tuple[EvidenceSummary, ...] = ()
    result_lanes: tuple[str, ...] = ()
    primary_lane: str | None = None
    user_cost_score: int | None = None
    user_cost_reasons: tuple[str, ...] = ()
    usefulness_summary: str | None = None


@dataclass(frozen=True)
class SearchResponse:
    query: str
    results: tuple[SearchResultEntry, ...] = ()
    absence: Notice | None = None
