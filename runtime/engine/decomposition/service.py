from __future__ import annotations

import hashlib
from io import BytesIO
import mimetypes
import zipfile

from runtime.engine.acquisition.acquisition_result import AcquisitionResult
from runtime.engine.decomposition.member_summary import DecompositionResult, MemberSummary
from runtime.engine.interfaces.public.acquisition import AcquisitionRequest
from runtime.engine.interfaces.public.decomposition import DecompositionRequest
from runtime.engine.interfaces.public.resolution import Notice
from runtime.engine.interfaces.service import AcquisitionService, DecompositionService


_MAX_DECOMPOSED_MEMBERS = 64


class DeterministicDecompositionService(DecompositionService):
    def __init__(self, acquisition_service: AcquisitionService) -> None:
        self._acquisition_service = acquisition_service

    def decompose_representation(self, request: DecompositionRequest) -> DecompositionResult:
        acquisition_result = self._acquisition_service.fetch_representation(
            AcquisitionRequest.from_parts(request.target_ref, request.representation_id),
        )
        if acquisition_result.acquisition_status != "fetched" or acquisition_result.payload is None:
            return _result_from_acquisition(
                acquisition_result,
                decomposition_status=(
                    "unavailable" if acquisition_result.acquisition_status == "unavailable" else "blocked"
                ),
            )

        if not zipfile.is_zipfile(BytesIO(acquisition_result.payload)):
            return _result_from_acquisition(
                acquisition_result,
                decomposition_status="unsupported",
                reason_codes=("representation_format_unsupported",),
                reason_messages=(
                    "This bounded representation was fetched successfully, but its format is not supported for member inspection in this bootstrap slice.",
                ),
                notices=(
                    *acquisition_result.notices,
                    Notice(
                        code="representation_format_unsupported",
                        severity="warning",
                        message=(
                            f"Representation '{request.representation_id}' is fetchable, but Eureka only decomposes ZIP payloads in this bootstrap slice."
                        ),
                    ),
                ),
            )

        members, notices = _zip_members(acquisition_result.payload)
        return _result_from_acquisition(
            acquisition_result,
            decomposition_status="decomposed",
            members=members,
            reason_codes=("representation_decomposed",),
            reason_messages=(
                "Decomposed the bounded ZIP payload into a compact member listing without writing members to disk.",
            ),
            notices=(
                *acquisition_result.notices,
                *notices,
            ),
        )


def _zip_members(payload: bytes) -> tuple[tuple[MemberSummary, ...], tuple[Notice, ...]]:
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        zip_infos = sorted(archive.infolist(), key=lambda item: item.filename.casefold())
        truncated = len(zip_infos) > _MAX_DECOMPOSED_MEMBERS
        selected_infos = zip_infos[:_MAX_DECOMPOSED_MEMBERS]
        members: list[MemberSummary] = []
        for info in selected_infos:
            if info.is_dir():
                members.append(
                    MemberSummary(
                        member_path=info.filename,
                        member_kind="directory",
                        byte_length=0,
                    )
                )
                continue
            member_bytes = archive.read(info.filename)
            content_type = mimetypes.guess_type(info.filename)[0]
            members.append(
                MemberSummary(
                    member_path=info.filename,
                    member_kind="file",
                    byte_length=len(member_bytes),
                    content_type=content_type,
                    sha256=hashlib.sha256(member_bytes).hexdigest(),
                )
            )
    notices: tuple[Notice, ...] = ()
    if truncated:
        notices = (
            Notice(
                code="decomposition_member_list_truncated",
                severity="warning",
                message=(
                    f"Member listing was truncated to the first {_MAX_DECOMPOSED_MEMBERS} archive entries in this bootstrap slice."
                ),
            ),
        )
    return tuple(members), notices


def _result_from_acquisition(
    acquisition_result: AcquisitionResult,
    *,
    decomposition_status: str,
    members: tuple[MemberSummary, ...] = (),
    reason_codes: tuple[str, ...] | None = None,
    reason_messages: tuple[str, ...] | None = None,
    notices: tuple[Notice, ...] | None = None,
) -> DecompositionResult:
    return DecompositionResult(
        decomposition_status=decomposition_status,
        target_ref=acquisition_result.target_ref,
        representation_id=acquisition_result.representation_id,
        resolved_resource_id=acquisition_result.resolved_resource_id,
        representation_kind=acquisition_result.representation_kind,
        label=acquisition_result.label,
        filename=acquisition_result.filename,
        content_type=acquisition_result.content_type,
        byte_length=acquisition_result.byte_length,
        source_family=acquisition_result.source_family,
        source_label=acquisition_result.source_label,
        source_locator=acquisition_result.source_locator,
        access_kind=acquisition_result.access_kind,
        access_locator=acquisition_result.access_locator,
        members=members,
        reason_codes=reason_codes if reason_codes is not None else acquisition_result.reason_codes,
        reason_messages=reason_messages if reason_messages is not None else acquisition_result.reason_messages,
        notices=notices if notices is not None else acquisition_result.notices,
    )
