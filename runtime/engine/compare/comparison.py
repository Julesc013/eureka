from __future__ import annotations

import re

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public import (
    ComparisonAgreement,
    ComparisonDisagreement,
    ComparisonRequest,
    ComparisonResult,
    ComparisonSide,
    Notice,
    ResolutionRequest,
)
from runtime.engine.interfaces.service import ComparisonService, ResolutionService
from runtime.engine.resolve import ExactMatchResolutionService


class DeterministicComparisonService(ComparisonService):
    def __init__(
        self,
        catalog: NormalizedCatalog,
        resolution_service: ResolutionService | None = None,
    ) -> None:
        self._catalog = catalog
        self._resolution_service = resolution_service or ExactMatchResolutionService(catalog)

    def compare(self, request: ComparisonRequest) -> ComparisonResult:
        left_side = self._build_side(request.left_target_ref)
        right_side = self._build_side(request.right_target_ref)

        if left_side.status != "completed" or right_side.status != "completed":
            return ComparisonResult(
                status="blocked",
                left=left_side,
                right=right_side,
                notices=self._blocked_notices(left_side, right_side),
            )

        agreements = self._agreements(left_side, right_side)
        disagreements = self._disagreements(left_side, right_side)
        return ComparisonResult(
            status="compared",
            left=left_side,
            right=right_side,
            agreements=agreements,
            disagreements=disagreements,
        )

    def _build_side(self, target_ref: str) -> ComparisonSide:
        outcome = self._resolution_service.resolve(ResolutionRequest.from_parts(target_ref))
        if outcome.status != "completed" or outcome.result is None:
            return ComparisonSide(
                target_ref=target_ref,
                status="blocked",
                notices=outcome.notices,
            )

        record = self._catalog.find_by_target_ref(target_ref)
        version_or_state = _version_or_state_for_target_ref(target_ref)
        if record is not None and version_or_state is None:
            version_or_state = record.state_kind

        return ComparisonSide(
            target_ref=target_ref,
            status="completed",
            resolved_resource_id=outcome.result.resolved_resource_id,
            primary_object=outcome.result.primary_object,
            source=outcome.result.source,
            version_or_state=version_or_state,
            evidence=outcome.result.evidence,
            notices=outcome.result.notices,
        )

    def _agreements(
        self,
        left_side: ComparisonSide,
        right_side: ComparisonSide,
    ) -> tuple[ComparisonAgreement, ...]:
        agreements: list[ComparisonAgreement] = []
        for category, left_value, right_value in (
            ("subject_key", _subject_key(left_side.target_ref), _subject_key(right_side.target_ref)),
            (
                "object_kind",
                _object_kind(left_side),
                _object_kind(right_side),
            ),
            (
                "normalized_version_or_state",
                _normalized_version_or_state(left_side.version_or_state),
                _normalized_version_or_state(right_side.version_or_state),
            ),
        ):
            if left_value is not None and right_value is not None and left_value == right_value:
                agreements.append(ComparisonAgreement(category=category, value=left_value))
        return tuple(agreements)

    def _disagreements(
        self,
        left_side: ComparisonSide,
        right_side: ComparisonSide,
    ) -> tuple[ComparisonDisagreement, ...]:
        disagreements: list[ComparisonDisagreement] = []
        for category, left_value, right_value in (
            ("object_label", _object_label(left_side), _object_label(right_side)),
            ("version_or_state", left_side.version_or_state, right_side.version_or_state),
            ("source_family", _source_family(left_side), _source_family(right_side)),
            ("source_locator", _source_locator(left_side), _source_locator(right_side)),
        ):
            if left_value is None or right_value is None or left_value == right_value:
                continue
            disagreements.append(
                ComparisonDisagreement(
                    category=category,
                    left_value=left_value,
                    right_value=right_value,
                )
            )
        return tuple(disagreements)

    def _blocked_notices(
        self,
        left_side: ComparisonSide,
        right_side: ComparisonSide,
    ) -> tuple[Notice, ...]:
        notices: list[Notice] = []
        if left_side.status != "completed":
            notices.append(
                Notice(
                    code="comparison_left_unresolved",
                    severity="warning",
                    message=f"Left target '{left_side.target_ref}' could not be resolved for comparison.",
                )
            )
        if right_side.status != "completed":
            notices.append(
                Notice(
                    code="comparison_right_unresolved",
                    severity="warning",
                    message=f"Right target '{right_side.target_ref}' could not be resolved for comparison.",
                )
            )
        return tuple(notices)


def _object_kind(side: ComparisonSide) -> str | None:
    if side.primary_object is None:
        return None
    return side.primary_object.kind


def _object_label(side: ComparisonSide) -> str | None:
    if side.primary_object is None:
        return None
    return side.primary_object.label or side.primary_object.id


def _source_family(side: ComparisonSide) -> str | None:
    if side.source is None:
        return None
    return side.source.family


def _source_locator(side: ComparisonSide) -> str | None:
    if side.source is None:
        return None
    return side.source.locator


def _subject_key(target_ref: str) -> str | None:
    _, _, subject_with_version = target_ref.partition(":")
    if not subject_with_version:
        return None
    subject, _, _version = subject_with_version.partition("@")
    if not subject:
        return None
    tail = subject.split("/")[-1].strip()
    return tail.casefold() or None


def _version_or_state_for_target_ref(target_ref: str) -> str | None:
    _prefix, separator, version_or_state = target_ref.partition("@")
    if not separator or not version_or_state:
        return None
    return version_or_state


def _normalized_version_or_state(value: str | None) -> str | None:
    if value is None:
        return None
    version = value.strip()
    if not version:
        return None
    if re.fullmatch(r"v\d+(?:\.\d+){1,3}", version, flags=re.IGNORECASE):
        return version[1:]
    return version.casefold()
