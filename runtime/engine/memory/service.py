from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable

from runtime.engine.interfaces.public import (
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
    ResolutionMemoryRecord,
)
from runtime.engine.interfaces.service import (
    ResolutionMemoryService,
    ResolutionMemorySourceRunNotFoundError,
    ResolutionRunService,
)
from runtime.engine.memory.memory_builder import ResolutionMemoryBuilder
from runtime.engine.memory.memory_store import LocalResolutionMemoryStore
from runtime.engine.resolution_runs import ResolutionRunNotFoundError


@dataclass(frozen=True)
class LocalResolutionMemoryService(ResolutionMemoryService):
    memory_store: LocalResolutionMemoryStore
    memory_builder: ResolutionMemoryBuilder
    run_service: ResolutionRunService | None = None
    created_by_slice: str = "resolution_memory_v0"
    timestamp_factory: Callable[[], datetime | str] | None = None

    def create_memory_from_run(
        self,
        request: ResolutionMemoryCreateRequest,
    ) -> ResolutionMemoryRecord:
        if self.run_service is None:
            raise ValueError(
                "Resolution Memory v0 creation requires a configured run store/service. "
                "Provide a bootstrap run_store_root."
            )
        try:
            run = self.run_service.get_run(request.run_id)
        except ResolutionRunNotFoundError as error:
            raise ResolutionMemorySourceRunNotFoundError(request.run_id) from error
        memory_id = self.memory_store.allocate_memory_id(
            self._memory_kind_from_run(run),
        )
        created_at = self._timestamp()
        memory = self.memory_builder.build_from_run(
            memory_id=memory_id,
            run=run,
            created_at=created_at,
        )
        return self.memory_store.save_memory(memory)

    def get_memory(self, request: ResolutionMemoryReadRequest) -> ResolutionMemoryRecord:
        return self.memory_store.get_memory(request.memory_id)

    def list_memories(
        self,
        request: ResolutionMemoryCatalogRequest | None = None,
    ) -> tuple[ResolutionMemoryRecord, ...]:
        return self.memory_store.list_memories(request)

    def _timestamp(self) -> str:
        factory = self.timestamp_factory or _default_timestamp
        value = factory()
        if isinstance(value, datetime):
            return value.astimezone(UTC).isoformat(timespec="seconds")
        return str(value)

    def _memory_kind_from_run(self, run) -> str:
        if run.absence_report is not None:
            return "absence_finding"
        if run.run_kind == "exact_resolution":
            return "successful_resolution"
        return "successful_search"


def _default_timestamp() -> datetime:
    return datetime.now(tz=UTC)
