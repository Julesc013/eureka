from __future__ import annotations

from typing import Protocol

from runtime.engine.decomposition.member_summary import DecompositionResult
from runtime.engine.interfaces.public.decomposition import DecompositionRequest


class DecompositionService(Protocol):
    def decompose_representation(self, request: DecompositionRequest) -> DecompositionResult:
        """Inspect a bounded fetched representation into a compact member listing."""
