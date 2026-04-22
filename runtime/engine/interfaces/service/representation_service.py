from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.representations import (
    RepresentationsRequest,
    RepresentationsResult,
)


class RepresentationsService(Protocol):
    def list_representations(self, request: RepresentationsRequest) -> RepresentationsResult:
        """List bounded known representations/access paths for one resolved target."""
