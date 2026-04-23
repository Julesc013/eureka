from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import (
    RepresentationSelectionRequest,
    RepresentationSelectionResult,
)
from runtime.engine.interfaces.service import RepresentationSelectionService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class RepresentationSelectionEvaluationRequest:
    target_ref: str
    host_profile_id: str | None = None
    strategy_id: str | None = None

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        host_profile_id: str | None = None,
        strategy_id: str | None = None,
    ) -> "RepresentationSelectionEvaluationRequest":
        engine_request = RepresentationSelectionRequest.from_parts(
            target_ref,
            host_profile_id,
            strategy_id,
        )
        return cls(
            target_ref=engine_request.target_ref,
            host_profile_id=engine_request.host_profile_id,
            strategy_id=engine_request.strategy_id,
        )

    def to_engine_request(self) -> RepresentationSelectionRequest:
        return RepresentationSelectionRequest.from_parts(
            self.target_ref,
            self.host_profile_id,
            self.strategy_id,
        )


class RepresentationSelectionPublicApi:
    def __init__(
        self,
        representation_selection_service: RepresentationSelectionService,
    ) -> None:
        self._representation_selection_service = representation_selection_service

    def select_representation(
        self,
        request: RepresentationSelectionEvaluationRequest,
    ) -> PublicApiResponse:
        result = self._representation_selection_service.select_representation(
            request.to_engine_request()
        )
        return PublicApiResponse(
            status_code=200 if result.status == "available" else 404,
            body=representation_selection_result_to_public_envelope(result),
        )


def representation_selection_result_to_public_envelope(
    result: RepresentationSelectionResult,
) -> dict[str, Any]:
    return result.to_dict()
