from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import RepresentationsRequest, RepresentationsResult
from runtime.engine.interfaces.service import RepresentationsService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class RepresentationCatalogRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "RepresentationCatalogRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)

    def to_engine_request(self) -> RepresentationsRequest:
        return RepresentationsRequest.from_parts(self.target_ref)


class RepresentationsPublicApi:
    def __init__(self, representations_service: RepresentationsService) -> None:
        self._representations_service = representations_service

    def list_representations(self, request: RepresentationCatalogRequest) -> PublicApiResponse:
        result = self._representations_service.list_representations(request.to_engine_request())
        return PublicApiResponse(
            status_code=200 if result.status == "available" else 404,
            body=representations_result_to_public_envelope(result),
        )


def representations_result_to_public_envelope(result: RepresentationsResult) -> dict[str, Any]:
    return result.to_dict()
