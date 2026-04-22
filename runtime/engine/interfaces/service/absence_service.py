from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.absence import (
    AbsenceReport,
    ResolveAbsenceRequest,
    SearchAbsenceRequest,
)


class AbsenceService(Protocol):
    def explain_resolution_miss(self, request: ResolveAbsenceRequest) -> AbsenceReport:
        """Explain a bounded exact-resolution miss without inventing certainty."""

    def explain_search_miss(self, request: SearchAbsenceRequest) -> AbsenceReport:
        """Explain a bounded deterministic search miss without adding ranking or fuzzy retrieval."""
