from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.search import SearchRequest, SearchResponse


class SearchService(Protocol):
    def search(self, request: SearchRequest) -> SearchResponse:
        """Search a bounded, already-normalized record set."""
