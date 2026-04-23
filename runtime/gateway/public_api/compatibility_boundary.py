from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.compatibility import bootstrap_host_profiles
from runtime.engine.interfaces.public import CompatibilityRequest, CompatibilityResult
from runtime.engine.interfaces.service import CompatibilityService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


BOOTSTRAP_HOST_PROFILE_PRESETS: tuple[dict[str, Any], ...] = tuple(
    profile.to_dict() for profile in bootstrap_host_profiles()
)


@dataclass(frozen=True)
class CompatibilityEvaluationRequest:
    target_ref: str
    host_profile_id: str

    @classmethod
    def from_parts(cls, target_ref: str, host_profile_id: str) -> "CompatibilityEvaluationRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        normalized_host_profile_id = host_profile_id.strip()
        if not normalized_host_profile_id:
            raise ValueError("host_profile_id must be a non-empty string.")
        return cls(
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
        )

    def to_engine_request(self) -> CompatibilityRequest:
        return CompatibilityRequest.from_parts(self.target_ref, self.host_profile_id)


class CompatibilityPublicApi:
    def __init__(self, compatibility_service: CompatibilityService) -> None:
        self._compatibility_service = compatibility_service

    def evaluate_compatibility(self, request: CompatibilityEvaluationRequest) -> PublicApiResponse:
        result = self._compatibility_service.evaluate_compatibility(request.to_engine_request())
        return PublicApiResponse(
            status_code=200 if result.status == "evaluated" else 404,
            body=compatibility_result_to_public_envelope(result),
        )


def compatibility_result_to_public_envelope(result: CompatibilityResult) -> dict[str, Any]:
    return result.to_dict()
