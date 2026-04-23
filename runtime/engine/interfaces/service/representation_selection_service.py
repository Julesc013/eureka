from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.representation_selection import (
    RepresentationSelectionRequest,
    RepresentationSelectionResult,
)


class RepresentationSelectionService(Protocol):
    def select_representation(
        self,
        request: RepresentationSelectionRequest,
    ) -> RepresentationSelectionResult:
        """Return a bounded representation-selection and handoff result for one resolved target."""
