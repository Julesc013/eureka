from __future__ import annotations

from runtime.engine.interfaces.public.query_plan import QueryPlanRequest, ResolutionTask
from runtime.engine.query_planner.rules import plan_query_by_rules


class DeterministicQueryPlannerService:
    def plan_query(self, request: QueryPlanRequest) -> ResolutionTask:
        return plan_query(request.raw_query)


def plan_query(raw_query: str) -> ResolutionTask:
    normalized_query = raw_query.strip()
    if not normalized_query:
        raise ValueError("raw_query must be a non-empty string.")
    return plan_query_by_rules(normalized_query)


def derive_search_query_from_task(task: ResolutionTask) -> str:
    product_hint = task.constraints.get("product_hint")
    if isinstance(product_hint, str) and product_hint:
        return product_hint
    hardware_hint = task.constraints.get("hardware_hint")
    if isinstance(hardware_hint, str) and hardware_hint:
        return hardware_hint
    function_hint = task.constraints.get("function_hint")
    if isinstance(function_hint, str) and function_hint and task.task_kind == "browse_software":
        platform = task.constraints.get("platform")
        if isinstance(platform, dict):
            marketing_alias = platform.get("marketing_alias")
            if isinstance(marketing_alias, str) and marketing_alias:
                return f"{marketing_alias} {function_hint}"
        return function_hint
    return task.raw_query
