from __future__ import annotations

from typing import Any

from runtime.engine.interfaces.public import QueryPlanRequest, ResolutionTask
from runtime.engine.interfaces.service import QueryPlannerService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


class QueryPlannerPublicApi:
    def __init__(self, planner_service: QueryPlannerService) -> None:
        self._planner_service = planner_service

    def plan_query(self, request: QueryPlanRequest) -> PublicApiResponse:
        task = self._planner_service.plan_query(request)
        return PublicApiResponse(
            status_code=200,
            body=query_plan_to_public_envelope(task),
        )

    def plan_query_text(self, raw_query: str) -> PublicApiResponse:
        normalized_query = raw_query.strip()
        if not normalized_query:
            return PublicApiResponse(
                status_code=400,
                body=query_plan_bad_request_envelope(
                    raw_query,
                    code="raw_query_required",
                    message="raw_query must be a non-empty string.",
                ),
            )
        return self.plan_query(QueryPlanRequest.from_parts(normalized_query))


def query_plan_to_public_envelope(task: ResolutionTask) -> dict[str, Any]:
    return {
        "status": "planned",
        "query_plan": task.to_dict(),
    }


def query_plan_bad_request_envelope(
    raw_query: str,
    *,
    code: str,
    message: str,
) -> dict[str, Any]:
    return {
        "status": "blocked",
        "query_plan": None,
        "notices": [
            {
                "code": code,
                "severity": "warning",
                "message": message,
            }
        ],
        "raw_query": raw_query,
    }
