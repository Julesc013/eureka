from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from runtime.engine.core import NormalizedCatalog
from runtime.engine.index.index_builder import build_index_records
from runtime.engine.index.sqlite_index import LocalIndexSqliteStore
from runtime.engine.interfaces.public import Notice
from runtime.engine.interfaces.public.local_index import (
    LocalIndexBuildRequest,
    LocalIndexBuildResult,
    LocalIndexQueryRequest,
    LocalIndexQueryResult,
    LocalIndexStatusRequest,
    LocalIndexStatusResult,
)
from runtime.engine.interfaces.service import LocalIndexService
from runtime.source_registry import SourceRegistry


@dataclass(frozen=True)
class LocalIndexEngineService(LocalIndexService):
    catalog: NormalizedCatalog
    source_registry: SourceRegistry
    sqlite_store: LocalIndexSqliteStore
    created_by_slice: str = "local_index_v0"

    def build_index(self, request: LocalIndexBuildRequest) -> LocalIndexBuildResult:
        records = build_index_records(self.catalog, self.source_registry)
        metadata = self.sqlite_store.build(Path(request.index_path), records)
        return LocalIndexBuildResult(
            status="built",
            metadata=metadata,
            notices=(
                Notice(
                    code="local_index_built",
                    severity="info",
                    message=(
                        "Built Local Index v0 from the current bounded corpus. "
                        "This is a synchronous bootstrap local index, not a live sync or incremental indexer."
                    ),
                ),
            ),
        )

    def get_index_status(self, request: LocalIndexStatusRequest) -> LocalIndexStatusResult:
        metadata = self.sqlite_store.read_metadata(Path(request.index_path))
        return LocalIndexStatusResult(status="available", metadata=metadata)

    def query_index(self, request: LocalIndexQueryRequest) -> LocalIndexQueryResult:
        metadata, results, notices = self.sqlite_store.query(
            Path(request.index_path),
            request.query,
        )
        return LocalIndexQueryResult(
            query=request.query,
            status="queried",
            metadata=metadata,
            results=results,
            notices=notices,
        )
