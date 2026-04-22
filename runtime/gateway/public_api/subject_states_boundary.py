from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import SubjectStatesRequest, SubjectStatesResult
from runtime.engine.interfaces.service import SubjectStatesService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class SubjectStatesCatalogRequest:
    subject_key: str

    @classmethod
    def from_parts(cls, subject_key: str) -> "SubjectStatesCatalogRequest":
        normalized_subject_key = subject_key.strip().casefold()
        if not normalized_subject_key:
            raise ValueError("subject_key must be a non-empty string.")
        return cls(subject_key=normalized_subject_key)

    def to_engine_request(self) -> SubjectStatesRequest:
        return SubjectStatesRequest.from_parts(self.subject_key)


class SubjectStatesPublicApi:
    def __init__(self, subject_states_service: SubjectStatesService) -> None:
        self._subject_states_service = subject_states_service

    def list_subject_states(self, request: SubjectStatesCatalogRequest) -> PublicApiResponse:
        result = self._subject_states_service.list_states(request.to_engine_request())
        return PublicApiResponse(
            status_code=200 if result.status == "listed" else 404,
            body=subject_states_result_to_public_envelope(result),
        )


def subject_states_result_to_public_envelope(result: SubjectStatesResult) -> dict[str, Any]:
    return result.to_dict()
