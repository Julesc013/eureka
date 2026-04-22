from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.subject_states import SubjectStatesRequest, SubjectStatesResult


class SubjectStatesService(Protocol):
    def list_states(self, request: SubjectStatesRequest) -> SubjectStatesResult:
        """List bounded ordered states for one bootstrap subject key."""
