from __future__ import annotations

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public import Notice, SearchRequest, SearchResponse, SearchResultEntry
from runtime.engine.interfaces.service import SearchService
from runtime.engine.resolve.object_summary import normalized_record_to_object_summary
from runtime.engine.resolve.resolved_resource_identity import resolved_resource_id_for_record
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary


class DeterministicSearchService(SearchService):
    def __init__(self, catalog: NormalizedCatalog) -> None:
        self._catalog = catalog

    def search(self, request: SearchRequest) -> SearchResponse:
        query = request.query
        normalized_query = query.casefold()
        results = tuple(
            SearchResultEntry(
                target_ref=record.target_ref,
                object_summary=normalized_record_to_object_summary(record),
                resolved_resource_id=resolved_resource_id_for_record(record),
                source=normalized_record_to_source_summary(record),
                evidence=record.evidence,
            )
            for record in self._catalog.records
            if _record_matches(record.target_ref, record.object_label, normalized_query)
        )

        if results:
            return SearchResponse(query=query, results=results)

        return SearchResponse(
            query=query,
            results=(),
            absence=Notice(
                code="search_no_matches",
                severity="info",
                message=f"No bounded records matched query '{query}'.",
            ),
        )


def _record_matches(target_ref: str, object_label: str | None, normalized_query: str) -> bool:
    candidate_fields = [target_ref.casefold()]
    if object_label is not None:
        candidate_fields.append(object_label.casefold())
    return any(normalized_query in candidate for candidate in candidate_fields)
