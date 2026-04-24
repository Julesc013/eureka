from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.local_index import (
    LocalIndexBuildRequest,
    LocalIndexBuildResult,
    LocalIndexQueryRequest,
    LocalIndexQueryResult,
    LocalIndexStatusRequest,
    LocalIndexStatusResult,
)


class LocalIndexService(Protocol):
    def build_index(self, request: LocalIndexBuildRequest) -> LocalIndexBuildResult:
        """Build or replace one bootstrap local SQLite index."""

    def get_index_status(self, request: LocalIndexStatusRequest) -> LocalIndexStatusResult:
        """Read bounded bootstrap local index metadata."""

    def query_index(self, request: LocalIndexQueryRequest) -> LocalIndexQueryResult:
        """Run one bounded text query against the bootstrap local index."""
