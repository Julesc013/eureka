from __future__ import annotations

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public import Notice, SearchRequest, SearchResponse, SearchResultEntry
from runtime.engine.interfaces.service import SearchService
from runtime.engine.ranking import assign_result_usefulness
from runtime.engine.resolve.object_summary import normalized_record_to_object_summary
from runtime.engine.resolve.resolved_resource_identity import resolved_resource_id_for_record
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary


class DeterministicSearchService(SearchService):
    def __init__(self, catalog: NormalizedCatalog) -> None:
        self._catalog = catalog

    def search(self, request: SearchRequest) -> SearchResponse:
        query = request.query
        normalized_query = query.casefold()
        entries: list[SearchResultEntry] = []
        for record in self._catalog.records:
            if not _record_matches(record.target_ref, record.object_label, normalized_query):
                continue
            usefulness = assign_result_usefulness(record)
            entries.append(
                SearchResultEntry(
                    target_ref=record.target_ref,
                    object_summary=normalized_record_to_object_summary(record),
                    resolved_resource_id=resolved_resource_id_for_record(record),
                    source=normalized_record_to_source_summary(record),
                    evidence=record.evidence,
                    result_lanes=usefulness.result_lanes,
                    primary_lane=usefulness.primary_lane,
                    user_cost_score=usefulness.user_cost_score,
                    user_cost_reasons=usefulness.user_cost_reasons,
                    usefulness_summary=usefulness.usefulness_summary,
                )
            )
        results = tuple(
            sorted(
                entries,
                key=lambda item: (
                    item.user_cost_score if item.user_cost_score is not None else 9,
                    (item.object_summary.label or item.target_ref).casefold(),
                    item.target_ref,
                ),
            )
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
