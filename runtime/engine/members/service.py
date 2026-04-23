from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import PurePosixPath
import zipfile

from runtime.engine.acquisition.acquisition_result import AcquisitionResult
from runtime.engine.decomposition.member_summary import DecompositionResult, MemberSummary
from runtime.engine.interfaces.public.acquisition import AcquisitionRequest
from runtime.engine.interfaces.public.decomposition import DecompositionRequest
from runtime.engine.interfaces.public.member_access import MemberAccessRequest
from runtime.engine.interfaces.public.resolution import Notice
from runtime.engine.interfaces.service.acquisition_service import AcquisitionService
from runtime.engine.interfaces.service.decomposition_service import DecompositionService
from runtime.engine.interfaces.service.member_access_service import MemberAccessService
from runtime.engine.members.member_access import MemberAccessResult


_TEXT_CONTENT_TYPES = frozenset(
    {
        "application/json",
        "application/ld+json",
        "application/x-yaml",
        "application/yaml",
    }
)
_MAX_TEXT_PREVIEW_CHARS = 400


class DeterministicMemberAccessService(MemberAccessService):
    def __init__(
        self,
        acquisition_service: AcquisitionService,
        decomposition_service: DecompositionService,
    ) -> None:
        self._acquisition_service = acquisition_service
        self._decomposition_service = decomposition_service

    def read_member(self, request: MemberAccessRequest) -> MemberAccessResult:
        decomposition_result = self._decomposition_service.decompose_representation(
            DecompositionRequest.from_parts(request.target_ref, request.representation_id),
        )
        if decomposition_result.decomposition_status != "decomposed":
            return _result_from_decomposition(
                decomposition_result,
                member_path=request.member_path,
                member_access_status=_member_status_from_decomposition(decomposition_result.decomposition_status),
            )

        member_summary = _find_member(decomposition_result.members, request.member_path)
        if member_summary is None:
            return _result_from_decomposition(
                decomposition_result,
                member_path=request.member_path,
                member_access_status="blocked",
                reason_codes=("member_not_found",),
                reason_messages=(
                    f"No bounded member matched member_path '{request.member_path}' for this representation.",
                ),
                notices=(
                    *decomposition_result.notices,
                    Notice(
                        code="member_not_found",
                        severity="warning",
                        message=(
                            f"No bounded member matched member_path '{request.member_path}' "
                            f"for representation '{request.representation_id}'."
                        ),
                    ),
                ),
            )

        if member_summary.member_kind != "file":
            return _result_from_decomposition(
                decomposition_result,
                member_path=request.member_path,
                member_access_status="unavailable",
                member_summary=member_summary,
                reason_codes=("member_not_readable",),
                reason_messages=(
                    "This bounded member is known in the listing, but it is not readable as a file payload in this bootstrap slice.",
                ),
                notices=(
                    *decomposition_result.notices,
                    Notice(
                        code="member_not_readable",
                        severity="warning",
                        message=(
                            f"Member '{request.member_path}' is not readable as a file payload in this bootstrap slice."
                        ),
                    ),
                ),
            )

        acquisition_result = self._acquisition_service.fetch_representation(
            AcquisitionRequest.from_parts(request.target_ref, request.representation_id),
        )
        if acquisition_result.acquisition_status != "fetched" or acquisition_result.payload is None:
            return _result_from_acquisition(
                acquisition_result,
                member_path=request.member_path,
                member_access_status=(
                    "unavailable" if acquisition_result.acquisition_status == "unavailable" else "blocked"
                ),
                member_summary=member_summary,
            )

        try:
            member_bytes = _read_zip_member(acquisition_result.payload, request.member_path)
        except KeyError:
            return _result_from_acquisition(
                acquisition_result,
                member_path=request.member_path,
                member_access_status="blocked",
                member_summary=member_summary,
                reason_codes=("member_not_found",),
                reason_messages=(
                    f"No bounded member matched member_path '{request.member_path}' in the fetched representation payload.",
                ),
                notices=(
                    *acquisition_result.notices,
                    Notice(
                        code="member_not_found_in_payload",
                        severity="warning",
                        message=(
                            f"Member '{request.member_path}' was listed earlier but could not be read from the fetched payload."
                        ),
                    ),
                ),
            )
        except zipfile.BadZipFile:
            return _result_from_acquisition(
                acquisition_result,
                member_path=request.member_path,
                member_access_status="unsupported",
                member_summary=member_summary,
                reason_codes=("representation_format_unsupported",),
                reason_messages=(
                    "This bounded representation is not readable for member access because only ZIP payloads are supported in this bootstrap slice.",
                ),
                notices=(
                    *acquisition_result.notices,
                    Notice(
                        code="representation_format_unsupported",
                        severity="warning",
                        message=(
                            f"Representation '{request.representation_id}' could not be read as a ZIP payload for member access."
                        ),
                    ),
                ),
            )

        text_preview, preview_notices = _build_text_preview(
            member_summary.content_type,
            member_bytes,
        )
        member_sha256 = hashlib.sha256(member_bytes).hexdigest()
        return _result_from_acquisition(
            acquisition_result,
            member_path=request.member_path,
            member_access_status="previewed" if text_preview is not None else "read",
            member_summary=MemberSummary(
                member_path=member_summary.member_path,
                member_kind=member_summary.member_kind,
                byte_length=len(member_bytes),
                content_type=member_summary.content_type,
                sha256=member_sha256,
                text_hint=member_summary.text_hint,
            ),
            reason_codes=(
                ("member_preview_available",) if text_preview is not None else ("member_readback_succeeded",)
            ),
            reason_messages=(
                (
                    "Read the bounded member successfully and produced a compact text preview for inspection."
                    if text_preview is not None
                    else "Read the bounded member successfully without writing it to disk."
                ),
            ),
            notices=(
                *acquisition_result.notices,
                *preview_notices,
            ),
            payload=member_bytes,
            text_preview=text_preview,
        )


def _find_member(members: tuple[MemberSummary, ...], member_path: str) -> MemberSummary | None:
    for member in members:
        if member.member_path == member_path:
            return member
    return None


def _read_zip_member(payload: bytes, member_path: str) -> bytes:
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        info = archive.getinfo(member_path)
        if info.is_dir():
            raise KeyError(member_path)
        return archive.read(member_path)


def _build_text_preview(
    content_type: str | None,
    payload: bytes,
) -> tuple[str | None, tuple[Notice, ...]]:
    if not _is_text_like(content_type):
        return None, ()

    text = payload.decode("utf-8", errors="replace")
    if len(text) <= _MAX_TEXT_PREVIEW_CHARS:
        return text, ()
    return (
        text[:_MAX_TEXT_PREVIEW_CHARS],
        (
            Notice(
                code="member_preview_truncated",
                severity="info",
                message=(
                    f"Text preview was truncated to the first {_MAX_TEXT_PREVIEW_CHARS} characters in this bootstrap slice."
                ),
            ),
        ),
    )


def _is_text_like(content_type: str | None) -> bool:
    if content_type is None:
        return False
    if content_type.startswith("text/"):
        return True
    return content_type in _TEXT_CONTENT_TYPES


def _member_status_from_decomposition(status: str) -> str:
    if status == "unsupported":
        return "unsupported"
    if status == "unavailable":
        return "unavailable"
    return "blocked"


def _result_from_decomposition(
    decomposition_result: DecompositionResult,
    *,
    member_path: str,
    member_access_status: str,
    member_summary: MemberSummary | None = None,
    reason_codes: tuple[str, ...] | None = None,
    reason_messages: tuple[str, ...] | None = None,
    notices: tuple[Notice, ...] | None = None,
) -> MemberAccessResult:
    return MemberAccessResult(
        member_access_status=member_access_status,
        target_ref=decomposition_result.target_ref,
        representation_id=decomposition_result.representation_id,
        member_path=member_path,
        resolved_resource_id=decomposition_result.resolved_resource_id,
        representation_kind=decomposition_result.representation_kind,
        label=decomposition_result.label,
        filename=decomposition_result.filename,
        source_family=decomposition_result.source_family,
        source_label=decomposition_result.source_label,
        source_locator=decomposition_result.source_locator,
        access_kind=decomposition_result.access_kind,
        access_locator=decomposition_result.access_locator,
        member_kind=member_summary.member_kind if member_summary is not None else None,
        content_type=member_summary.content_type if member_summary is not None else None,
        byte_length=member_summary.byte_length if member_summary is not None else None,
        sha256=member_summary.sha256 if member_summary is not None else None,
        reason_codes=reason_codes if reason_codes is not None else decomposition_result.reason_codes,
        reason_messages=reason_messages if reason_messages is not None else decomposition_result.reason_messages,
        notices=notices if notices is not None else decomposition_result.notices,
    )


def _result_from_acquisition(
    acquisition_result: AcquisitionResult,
    *,
    member_path: str,
    member_access_status: str,
    member_summary: MemberSummary | None = None,
    reason_codes: tuple[str, ...] | None = None,
    reason_messages: tuple[str, ...] | None = None,
    notices: tuple[Notice, ...] | None = None,
    payload: bytes | None = None,
    text_preview: str | None = None,
) -> MemberAccessResult:
    return MemberAccessResult(
        member_access_status=member_access_status,
        target_ref=acquisition_result.target_ref,
        representation_id=acquisition_result.representation_id,
        member_path=member_path,
        resolved_resource_id=acquisition_result.resolved_resource_id,
        representation_kind=acquisition_result.representation_kind,
        label=acquisition_result.label,
        filename=acquisition_result.filename,
        source_family=acquisition_result.source_family,
        source_label=acquisition_result.source_label,
        source_locator=acquisition_result.source_locator,
        access_kind=acquisition_result.access_kind,
        access_locator=acquisition_result.access_locator,
        member_kind=member_summary.member_kind if member_summary is not None else None,
        content_type=member_summary.content_type if member_summary is not None else None,
        byte_length=member_summary.byte_length if member_summary is not None else None,
        sha256=member_summary.sha256 if member_summary is not None else None,
        text_preview=text_preview,
        reason_codes=reason_codes if reason_codes is not None else acquisition_result.reason_codes,
        reason_messages=reason_messages if reason_messages is not None else acquisition_result.reason_messages,
        notices=notices if notices is not None else acquisition_result.notices,
        payload=payload,
    )


def member_filename_from_path(member_path: str) -> str:
    candidate = PurePosixPath(member_path).name
    return candidate or "member.bin"
