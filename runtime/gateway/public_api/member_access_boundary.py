from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import MemberAccessRequest
from runtime.engine.interfaces.service import MemberAccessService
from runtime.engine.members.service import member_filename_from_path


@dataclass(frozen=True)
class MemberAccessReadRequest:
    target_ref: str
    representation_id: str
    member_path: str

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        representation_id: str,
        member_path: str,
    ) -> "MemberAccessReadRequest":
        engine_request = MemberAccessRequest.from_parts(target_ref, representation_id, member_path)
        return cls(
            target_ref=engine_request.target_ref,
            representation_id=engine_request.representation_id,
            member_path=engine_request.member_path,
        )

    def to_engine_request(self) -> MemberAccessRequest:
        return MemberAccessRequest.from_parts(
            self.target_ref,
            self.representation_id,
            self.member_path,
        )


@dataclass(frozen=True)
class PublicMemberAccessResponse:
    status_code: int
    body: dict[str, Any]
    payload: bytes | None = None
    content_type: str | None = None
    filename: str | None = None


class MemberAccessPublicApi:
    def __init__(self, member_access_service: MemberAccessService) -> None:
        self._member_access_service = member_access_service

    def read_member(self, request: MemberAccessReadRequest) -> PublicMemberAccessResponse:
        result = self._member_access_service.read_member(request.to_engine_request())
        is_success = result.member_access_status in {"read", "previewed"}
        return PublicMemberAccessResponse(
            status_code=_status_code_for_result(result.member_access_status, result.reason_codes),
            body=member_access_result_to_public_envelope(result),
            payload=result.payload if is_success else None,
            content_type=((result.content_type or "application/octet-stream") if is_success else None),
            filename=(member_filename_from_path(result.member_path) if is_success else None),
        )


def member_access_result_to_public_envelope(result: Any) -> dict[str, Any]:
    return result.to_dict()


def _status_code_for_result(member_access_status: str, reason_codes: tuple[str, ...]) -> int:
    if member_access_status in {"read", "previewed"}:
        return 200
    if member_access_status in {"unsupported", "unavailable"}:
        return 422
    if any(
        code in {"acquisition_fixture_missing", "acquisition_fixture_unreadable"}
        for code in reason_codes
    ):
        return 503
    return 404
