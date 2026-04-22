from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.comparison import ComparisonRequest, ComparisonResult


class ComparisonService(Protocol):
    def compare(self, request: ComparisonRequest) -> ComparisonResult:
        """Compare two bounded resolved targets without merging them into one answer."""

