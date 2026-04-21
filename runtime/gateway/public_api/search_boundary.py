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
    if result.resolved_resource_id is not None:
        entry["resolved_resource_id"] = result.resolved_resource_id
    return entry
