from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.query_plan import QueryPlanRequest, ResolutionTask


class QueryPlannerService(Protocol):
    def plan_query(self, request: QueryPlanRequest) -> ResolutionTask:
        """Compile one raw query into a bounded deterministic ResolutionTask."""
