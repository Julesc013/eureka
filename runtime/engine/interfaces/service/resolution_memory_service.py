from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.resolution_memory import (
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
    ResolutionMemoryRecord,
)


class ResolutionMemoryNotFoundError(LookupError):
    def __init__(self, memory_id: str) -> None:
        self.memory_id = memory_id
        super().__init__(f"Unknown resolution memory '{memory_id}'.")


class ResolutionMemorySourceRunNotFoundError(LookupError):
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        super().__init__(f"Unknown source resolution run '{run_id}'.")


class ResolutionMemoryService(Protocol):
    def create_memory_from_run(
        self,
        request: ResolutionMemoryCreateRequest,
    ) -> ResolutionMemoryRecord:
        """Build, persist, and return one explicit local memory record from one existing run."""

    def get_memory(self, request: ResolutionMemoryReadRequest) -> ResolutionMemoryRecord:
        """Read one persisted local resolution memory record by memory_id."""

    def list_memories(
        self,
        request: ResolutionMemoryCatalogRequest | None = None,
    ) -> tuple[ResolutionMemoryRecord, ...]:
        """List persisted local resolution memories, optionally filtered by bounded fields."""
