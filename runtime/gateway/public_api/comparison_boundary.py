from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import ComparisonRequest, ComparisonResult
from runtime.engine.interfaces.service import ComparisonService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class CompareTargetsRequest:
    left_target_ref: str
    right_target_ref: str

    @classmethod
    def from_parts(cls, left_target_ref: str, right_target_ref: str) -> "CompareTargetsRequest":
        left = left_target_ref.strip()
        right = right_target_ref.strip()
        if not left:
            raise ValueError("left_target_ref must be a non-empty string.")
        if not right:
            raise ValueError("right_target_ref must be a non-empty string.")
        return cls(left_target_ref=left, right_target_ref=right)

    def to_engine_request(self) -> ComparisonRequest:
        return ComparisonRequest.from_parts(self.left_target_ref, self.right_target_ref)


class ComparisonPublicApi:
    def __init__(self, comparison_service: ComparisonService) -> None:
        self._comparison_service = comparison_service

    def compare_targets(self, request: CompareTargetsRequest) -> PublicApiResponse:
        result = self._comparison_service.compare(request.to_engine_request())
        return PublicApiResponse(
            status_code=200 if result.status == "compared" else 404,
            body=comparison_result_to_public_envelope(result),
        )


def comparison_result_to_public_envelope(result: ComparisonResult) -> dict[str, Any]:
    return result.to_dict()
