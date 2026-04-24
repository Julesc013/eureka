from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.resolution_run import (
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
    ResolutionRunRecord,
)


class ResolutionRunService(Protocol):
    def run_exact_resolution(self, request: ExactResolutionRunRequest) -> ResolutionRunRecord:
        """Execute one bounded exact-resolution investigation and persist its record."""

    def run_deterministic_search(
        self,
        request: DeterministicSearchRunRequest,
    ) -> ResolutionRunRecord:
        """Execute one bounded deterministic-search investigation and persist its record."""

    def get_run(self, run_id: str) -> ResolutionRunRecord:
        """Read one persisted resolution run by run_id."""

    def list_runs(self) -> tuple[ResolutionRunRecord, ...]:
        """List persisted resolution runs in deterministic order."""
