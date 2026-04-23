from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import AcquisitionRequest
from runtime.engine.interfaces.service import AcquisitionService


@dataclass(frozen=True)
class AcquisitionFetchRequest:
    target_ref: str
    representation_id: str

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        representation_id: str,
    ) -> "AcquisitionFetchRequest":
        normalized_target_ref = target_ref.strip()
        normalized_representation_id = representation_id.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        if not normalized_representation_id:
            raise ValueError("representation_id must be a non-empty string.")
        return cls(
            target_ref=normalized_target_ref,
            representation_id=normalized_representation_id,
        )

    def to_engine_request(self) -> AcquisitionRequest:
        return AcquisitionRequest.from_parts(self.target_ref, self.representation_id)


@dataclass(frozen=True)
class PublicAcquisitionResponse:
    status_code: int
    body: dict[str, Any]
    payload: bytes | None = None
    content_type: str | None = None
    filename: str | None = None


class AcquisitionPublicApi:
    def __init__(self, acquisition_service: AcquisitionService) -> None:
        self._acquisition_service = acquisition_service

    def fetch_representation(self, request: AcquisitionFetchRequest) -> PublicAcquisitionResponse:
        result = self._acquisition_service.fetch_representation(request.to_engine_request())
        status_code = _status_code_for_result(result.acquisition_status, result.reason_codes)
        return PublicAcquisitionResponse(
            status_code=status_code,
            body=acquisition_result_to_public_envelope(result),
            payload=result.payload if result.acquisition_status == "fetched" else None,
            content_type=(
                (result.content_type or "application/octet-stream")
                if result.acquisition_status == "fetched"
                else None
            ),
            filename=result.filename,
        )


def acquisition_result_to_public_envelope(result: Any) -> dict[str, Any]:
    return result.to_dict()


def _status_code_for_result(acquisition_status: str, reason_codes: tuple[str, ...]) -> int:
    if acquisition_status == "fetched":
        return 200
    if acquisition_status == "unavailable":
        return 422
    if any(
        code in {"acquisition_fixture_missing", "acquisition_fixture_unreadable"}
        for code in reason_codes
    ):
        return 503
    return 404
