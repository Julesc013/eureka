from __future__ import annotations

from pathlib import Path

from runtime.engine.acquisition.acquisition_result import AcquisitionResult
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public.acquisition import AcquisitionRequest
from runtime.engine.interfaces.public.resolution import Notice, ResolutionRequest
from runtime.engine.interfaces.service import AcquisitionService, ResolutionService
from runtime.engine.representations import RepresentationSummary
from runtime.engine.resolve import ExactMatchResolutionService


_REPO_ROOT = Path(__file__).resolve().parents[3]


class DeterministicAcquisitionService(AcquisitionService):
    def __init__(
        self,
        catalog: NormalizedCatalog,
        *,
        resolution_service: ResolutionService | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self._catalog = catalog
        self._resolution_service = resolution_service or ExactMatchResolutionService(catalog)
        self._repo_root = (repo_root or _REPO_ROOT).resolve()

    def fetch_representation(self, request: AcquisitionRequest) -> AcquisitionResult:
        outcome = self._resolution_service.resolve(ResolutionRequest.from_parts(request.target_ref))
        if outcome.status != "completed" or outcome.result is None:
            primary_notice = outcome.notices[0] if outcome.notices else Notice(
                code="target_ref_not_found",
                severity="warning",
                message=f"No bounded record matched target_ref '{request.target_ref}'.",
            )
            return AcquisitionResult(
                acquisition_status="blocked",
                target_ref=request.target_ref,
                representation_id=request.representation_id,
                reason_codes=("target_unresolved",),
                reason_messages=(primary_notice.message or "The requested target could not be resolved.",),
                notices=outcome.notices,
            )

        record = self._catalog.find_by_target_ref(request.target_ref)
        if record is None:
            return AcquisitionResult(
                acquisition_status="blocked",
                target_ref=request.target_ref,
                representation_id=request.representation_id,
                reason_codes=("target_record_missing",),
                reason_messages=("The resolved target did not map back to a bounded normalized record.",),
            )

        representation = _find_representation(record.representations, request.representation_id)
        if representation is None:
            return AcquisitionResult(
                acquisition_status="blocked",
                target_ref=request.target_ref,
                representation_id=request.representation_id,
                resolved_resource_id=outcome.result.resolved_resource_id,
                reason_codes=("representation_not_found",),
                reason_messages=(
                    f"No bounded representation matched representation_id '{request.representation_id}' for this target.",
                ),
                notices=(
                    Notice(
                        code="representation_not_found",
                        severity="warning",
                        message=(
                            f"No bounded representation matched representation_id '{request.representation_id}' "
                            f"for target_ref '{request.target_ref}'."
                        ),
                    ),
                ),
            )

        if not representation.is_fetchable or representation.fetch_locator is None:
            return _result_from_representation(
                acquisition_status="unavailable",
                target_ref=request.target_ref,
                resolved_resource_id=outcome.result.resolved_resource_id,
                representation=representation,
                byte_length=representation.byte_length,
                reason_codes=("representation_not_fetchable",),
                reason_messages=(
                    "This bounded representation is known for inspection or review, but it does not expose a fixture-backed payload for retrieval.",
                ),
                notices=(
                    Notice(
                        code="representation_not_fetchable",
                        severity="warning",
                        message=(
                            f"Representation '{request.representation_id}' is not fetchable in this bounded bootstrap slice."
                        ),
                    ),
                ),
            )

        fetch_path = self._resolve_fetch_path(representation.fetch_locator)
        if fetch_path is None or not fetch_path.is_file():
            return _result_from_representation(
                acquisition_status="blocked",
                target_ref=request.target_ref,
                resolved_resource_id=outcome.result.resolved_resource_id,
                representation=representation,
                byte_length=representation.byte_length,
                reason_codes=("acquisition_fixture_missing",),
                reason_messages=(
                    "The bounded local payload fixture for this representation is missing or outside the repo root.",
                ),
                notices=(
                    Notice(
                        code="acquisition_fixture_missing",
                        severity="error",
                        message=(
                            f"The bounded local payload fixture '{representation.fetch_locator}' is unavailable."
                        ),
                    ),
                ),
            )

        try:
            payload = fetch_path.read_bytes()
        except OSError as exc:
            return _result_from_representation(
                acquisition_status="blocked",
                target_ref=request.target_ref,
                resolved_resource_id=outcome.result.resolved_resource_id,
                representation=representation,
                byte_length=representation.byte_length,
                reason_codes=("acquisition_fixture_unreadable",),
                reason_messages=(
                    "The bounded local payload fixture could not be read for retrieval.",
                ),
                notices=(
                    Notice(
                        code="acquisition_fixture_unreadable",
                        severity="error",
                        message=(
                            f"The bounded local payload fixture '{representation.fetch_locator}' could not be read: {exc}."
                        ),
                    ),
                ),
            )

        return _result_from_representation(
            acquisition_status="fetched",
            target_ref=request.target_ref,
            resolved_resource_id=outcome.result.resolved_resource_id,
            representation=representation,
            byte_length=len(payload),
            reason_codes=("representation_fetched",),
            reason_messages=(
                "Fetched the bounded local payload fixture for the selected representation.",
            ),
            notices=(
                Notice(
                    code="representation_fetched_from_local_fixture",
                    severity="info",
                    message="Retrieved bytes from a bounded local fixture without live network access.",
                ),
            ),
            payload=payload,
        )

    def _resolve_fetch_path(self, fetch_locator: str) -> Path | None:
        candidate = (self._repo_root / fetch_locator).resolve()
        try:
            candidate.relative_to(self._repo_root)
        except ValueError:
            return None
        return candidate


def _find_representation(
    representations: tuple[RepresentationSummary, ...],
    representation_id: str,
) -> RepresentationSummary | None:
    for representation in representations:
        if representation.representation_id == representation_id:
            return representation
    return None


def _result_from_representation(
    *,
    acquisition_status: str,
    target_ref: str,
    resolved_resource_id: str | None,
    representation: RepresentationSummary,
    byte_length: int | None,
    reason_codes: tuple[str, ...],
    reason_messages: tuple[str, ...],
    notices: tuple[Notice, ...],
    payload: bytes | None = None,
) -> AcquisitionResult:
    return AcquisitionResult(
        acquisition_status=acquisition_status,
        target_ref=target_ref,
        representation_id=representation.representation_id,
        resolved_resource_id=resolved_resource_id,
        representation_kind=representation.representation_kind,
        label=representation.label,
        filename=representation.filename,
        content_type=representation.content_type,
        byte_length=byte_length,
        source_family=representation.source_family,
        source_label=representation.source_label,
        source_locator=representation.source_locator,
        access_kind=representation.access_kind,
        access_locator=representation.access_locator,
        reason_codes=reason_codes,
        reason_messages=reason_messages,
        notices=notices,
        payload=payload,
    )
