from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import DecompositionRequest
from runtime.engine.interfaces.service import DecompositionService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class DecompositionInspectionRequest:
    target_ref: str
    representation_id: str

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        representation_id: str,
    ) -> "DecompositionInspectionRequest":
        engine_request = DecompositionRequest.from_parts(target_ref, representation_id)
        return cls(
            target_ref=engine_request.target_ref,
            representation_id=engine_request.representation_id,
        )

    def to_engine_request(self) -> DecompositionRequest:
        return DecompositionRequest.from_parts(self.target_ref, self.representation_id)


class DecompositionPublicApi:
    def __init__(self, decomposition_service: DecompositionService) -> None:
        self._decomposition_service = decomposition_service

    def decompose_representation(
        self,
        request: DecompositionInspectionRequest,
    ) -> PublicApiResponse:
        result = self._decomposition_service.decompose_representation(request.to_engine_request())
        return PublicApiResponse(
            status_code=_status_code_for_result(result.decomposition_status),
            body=decomposition_result_to_public_envelope(result),
        )


def decomposition_result_to_public_envelope(result: Any) -> dict[str, Any]:
    return result.to_dict()


def _status_code_for_result(status: str) -> int:
    if status == "decomposed":
        return 200
    if status in {"unsupported", "unavailable"}:
        return 422
    return 404
