from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import (
    ResolveAbsenceRequest,
    SearchAbsenceRequest,
)
from runtime.engine.interfaces.service import AbsenceService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class ExplainResolveMissRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "ExplainResolveMissRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)

    def to_engine_request(self) -> ResolveAbsenceRequest:
        return ResolveAbsenceRequest.from_parts(self.target_ref)


@dataclass(frozen=True)
class ExplainSearchMissRequest:
    query: str

    @classmethod
    def from_parts(cls, query: str) -> "ExplainSearchMissRequest":
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must be a non-empty string.")
        return cls(query=normalized_query)

    def to_engine_request(self) -> SearchAbsenceRequest:
        return SearchAbsenceRequest.from_parts(self.query)


class AbsencePublicApi:
    def __init__(self, absence_service: AbsenceService) -> None:
        self._absence_service = absence_service

    def explain_resolution_miss(self, request: ExplainResolveMissRequest) -> PublicApiResponse:
        report = self._absence_service.explain_resolution_miss(request.to_engine_request())
        return PublicApiResponse(status_code=200, body=absence_report_to_public_envelope(report))

    def explain_search_miss(self, request: ExplainSearchMissRequest) -> PublicApiResponse:
        report = self._absence_service.explain_search_miss(request.to_engine_request())
        return PublicApiResponse(status_code=200, body=absence_report_to_public_envelope(report))


def absence_report_to_public_envelope(report) -> dict[str, Any]:
    return report.to_dict()
