from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.compatibility import CompatibilityRequest, CompatibilityResult


class CompatibilityService(Protocol):
    def evaluate_compatibility(self, request: CompatibilityRequest) -> CompatibilityResult:
        """Evaluate a bounded compatibility verdict for one resolved target and one bootstrap host profile."""
