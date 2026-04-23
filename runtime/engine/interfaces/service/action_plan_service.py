from __future__ import annotations

from typing import Protocol

from runtime.engine.interfaces.public.action_plan import ActionPlanRequest, ActionPlanResult


class ActionPlanService(Protocol):
    def plan_actions(self, request: ActionPlanRequest) -> ActionPlanResult:
        """Return a bounded action plan for one resolved target and optional bootstrap host profile."""
