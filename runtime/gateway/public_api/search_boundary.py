from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import SearchRequest, SearchResponse
from runtime.engine.interfaces.service import SearchService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class SearchCatalogRequest:
    query: str

    @classmethod
    def from_parts(cls, query: str) -> "SearchCatalogRequest":
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must be a non-empty string.")
        return cls(query=normalized_query)

    def to_engine_request(self) -> SearchRequest:
        return SearchRequest.from_parts(self.query)


class SearchPublicApi:
    def __init__(self, search_service: SearchService) -> None:
        self._search_service = search_service

    def search_records(self, request: SearchCatalogRequest) -> PublicApiResponse:
        response = self._search_service.search(request.to_engine_request())
        return PublicApiResponse(
            status_code=200,
            body=search_response_to_public_envelope(response),
        )


def search_response_to_public_envelope(response: SearchResponse) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "query": response.query,
        "result_count": len(response.results),
        "results": [search_result_to_public_entry(result) for result in response.results],
    }
    if response.absence is not None:
        envelope["absence"] = {
            "code": response.absence.code,
            "message": response.absence.message or "No matching records were found.",
        }
    return envelope


def search_result_to_public_entry(result) -> dict[str, Any]:
    entry = {
        "target_ref": result.target_ref,
        "object": result.object_summary.to_dict(),
    }
    if result.result_lanes:
        entry["result_lanes"] = list(result.result_lanes)
    if result.primary_lane is not None:
        entry["primary_lane"] = result.primary_lane
    if result.user_cost_score is not None:
        entry["user_cost_score"] = result.user_cost_score
    if result.user_cost_reasons:
        entry["user_cost_reasons"] = list(result.user_cost_reasons)
    if result.usefulness_summary is not None:
        entry["usefulness_summary"] = result.usefulness_summary
    if result.resolved_resource_id is not None:
        entry["resolved_resource_id"] = result.resolved_resource_id
    if result.source is not None:
        entry["source"] = result.source.to_dict()
    if result.evidence:
        entry["evidence"] = [summary.to_dict() for summary in result.evidence]
    return entry
