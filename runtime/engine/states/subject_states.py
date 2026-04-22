from __future__ import annotations

import re

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import (
    Notice,
    SubjectStateSummary,
    SubjectStatesRequest,
    SubjectStatesResult,
    SubjectSummary,
)
from runtime.engine.interfaces.service import SubjectStatesService
from runtime.engine.resolve.object_summary import normalized_record_to_object_summary
from runtime.engine.resolve.resolved_resource_identity import resolved_resource_id_for_record
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary


_VERSION_PATTERN = re.compile(r"^\d+(?:\.\d+){1,3}$")


class DeterministicSubjectStatesService(SubjectStatesService):
    def __init__(self, catalog: NormalizedCatalog) -> None:
        self._catalog = catalog

    def list_states(self, request: SubjectStatesRequest) -> SubjectStatesResult:
        subject_key = request.subject_key
        matching_records = tuple(
            record
            for record in self._catalog.records
            if subject_key_for_target_ref(record.target_ref) == subject_key
        )
        if not matching_records:
            return SubjectStatesResult(
                status="blocked",
                requested_subject_key=subject_key,
                notices=(
                    Notice(
                        code="subject_not_found",
                        severity="warning",
                        message=f"No bounded states were found for subject '{subject_key}'.",
                    ),
                ),
            )

        ordered_records = _order_records(matching_records)
        return SubjectStatesResult(
            status="listed",
            requested_subject_key=subject_key,
            subject=SubjectSummary(
                subject_key=subject_key,
                subject_label=_subject_label_for_record(ordered_records[0], subject_key),
                state_count=len(ordered_records),
                source_family_hint=_source_family_hint(ordered_records),
            ),
            states=tuple(_state_summary_for_record(record) for record in ordered_records),
        )


def subject_key_for_target_ref(target_ref: str) -> str | None:
    _prefix, separator, subject_with_version = target_ref.partition(":")
    if not separator or not subject_with_version:
        return None
    subject_path, _at, _version_or_state = subject_with_version.partition("@")
    if not subject_path:
        return None
    tail = subject_path.split("/")[-1].strip()
    if not tail:
        return None
    return tail.casefold()


def version_or_state_for_target_ref(target_ref: str) -> str | None:
    _prefix, separator, version_or_state = target_ref.partition("@")
    if not separator or not version_or_state:
        return None
    normalized = version_or_state.strip()
    return normalized or None


def normalized_version_or_state_for_target_ref(target_ref: str) -> str | None:
    return normalized_version_or_state(version_or_state_for_target_ref(target_ref))


def normalized_version_or_state(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    version_candidate = normalized[1:] if normalized[:1].casefold() == "v" else normalized
    if _VERSION_PATTERN.fullmatch(version_candidate):
        return version_candidate
    return normalized.casefold()


def _state_summary_for_record(record: NormalizedResolutionRecord) -> SubjectStateSummary:
    return SubjectStateSummary(
        target_ref=record.target_ref,
        resolved_resource_id=resolved_resource_id_for_record(record),
        object_summary=normalized_record_to_object_summary(record),
        version_or_state=version_or_state_for_target_ref(record.target_ref),
        normalized_version_or_state=normalized_version_or_state_for_target_ref(record.target_ref),
        source=normalized_record_to_source_summary(record),
        evidence=record.evidence,
    )


def _order_records(
    records: tuple[NormalizedResolutionRecord, ...],
) -> tuple[NormalizedResolutionRecord, ...]:
    lexical = sorted(records, key=lambda record: record.target_ref)
    ordered = sorted(lexical, key=_record_order_key, reverse=True)
    return tuple(ordered)


def _record_order_key(record: NormalizedResolutionRecord) -> tuple[int, tuple[int, ...], str]:
    normalized = normalized_version_or_state_for_target_ref(record.target_ref) or ""
    version_tuple = _parsed_version_tuple(normalized)
    if version_tuple is not None:
        return (1, version_tuple, normalized)
    return (0, (), normalized)


def _parsed_version_tuple(value: str) -> tuple[int, ...] | None:
    if not value or _VERSION_PATTERN.fullmatch(value) is None:
        return None
    return tuple(int(part) for part in value.split("."))


def _subject_label_for_record(record: NormalizedResolutionRecord, fallback_subject_key: str) -> str:
    candidate = (record.object_label or record.object_id or fallback_subject_key).strip()
    stripped = re.sub(r"\s+v?\d+(?:\.\d+){1,3}$", "", candidate, flags=re.IGNORECASE).strip()
    return stripped or candidate


def _source_family_hint(records: tuple[NormalizedResolutionRecord, ...]) -> str | None:
    families = {record.source_family for record in records if record.source_family}
    if not families:
        return None
    if len(families) == 1:
        return next(iter(families))
    return "mixed"
