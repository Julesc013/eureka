from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from runtime.engine.interfaces.public.resolution import Notice, ResolutionRequest, ResolutionResult


@dataclass(frozen=True)
class ResolutionOutcome:
    status: str
    result: ResolutionResult | None = None
    notices: tuple[Notice, ...] = ()


class ResolutionService(Protocol):
    def resolve(self, request: ResolutionRequest) -> ResolutionOutcome:
        """Resolve a bounded target reference against the engine's current data sources."""

