from __future__ import annotations

import re

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.interfaces.public import (
    AbsenceNearMatch,
    AbsenceReport,
    ResolveAbsenceRequest,
    ResolutionRequest,
    SearchAbsenceRequest,
    SearchRequest,
)
from runtime.engine.interfaces.service import AbsenceService, ResolutionService, SearchService
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.resolve.object_summary import normalized_record_to_object_summary
from runtime.engine.resolve.resolved_resource_identity import resolved_resource_id_for_record
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary
from runtime.engine.states import (
    normalized_version_or_state_for_target_ref,
    subject_key_for_target_ref,
    version_or_state_for_target_ref,
)


_VERSION_PATTERN = re.compile(r"^\d+(?:\.\d+){1,3}$")
_NEAR_MATCH_LIMIT = 4


class DeterministicAbsenceService(AbsenceService):
    def __init__(
        self,
        catalog: NormalizedCatalog,
        *,
        resolution_service: ResolutionService | None = None,
        search_service: SearchService | None = None,
    ) -> None:
        self._catalog = catalog
        self._resolution_service = resolution_service or ExactMatchResolutionService(catalog)
        self._search_service = search_service or DeterministicSearchService(catalog)

    def explain_resolution_miss(self, request: ResolveAbsenceRequest) -> AbsenceReport:
        outcome = self._resolution_service.resolve(ResolutionRequest.from_parts(request.target_ref))
        if outcome.status == "completed":
            return self._not_absent_report(
                request_kind="resolve",
                requested_value=request.target_ref,
                reason_code="target_ref_resolves",
                reason_message=(
                    f"Target ref '{request.target_ref}' already resolves in the bounded corpus."
                ),
            )

        requested_subject_key = subject_key_for_target_ref(request.target_ref)
        if requested_subject_key is not None:
            same_subject_records = self._records_for_subject(requested_subject_key)
            if same_subject_records:
                near_matches = tuple(
                    self._near_match_for_record(record, match_kind="same_subject_different_state")
                    for record in _order_records(same_subject_records)[:_NEAR_MATCH_LIMIT]
                )
                return self._explained_report(
                    request_kind="resolve",
                    requested_value=request.target_ref,
                    reason_code="known_subject_different_state",
                    reason_message=(
                        f"Subject '{requested_subject_key}' exists in the bounded corpus, but the requested "
                        f"target ref '{request.target_ref}' does not match one of its known states."
                    ),
                    near_matches=near_matches,
                    next_steps=(
                        f"Try one of the known target_ref values already listed for subject '{requested_subject_key}'.",
                        f"List known states for subject '{requested_subject_key}'.",
                        f"Search for subject '{requested_subject_key}' to inspect related bounded records.",
                    ),
                )

        related_records = self._related_records_for_text(request.target_ref)
        if related_records:
            near_matches = tuple(
                self._near_match_for_record(record, match_kind="related_subject")
                for record in related_records[:_NEAR_MATCH_LIMIT]
            )
            return self._explained_report(
                request_kind="resolve",
                requested_value=request.target_ref,
                reason_code="related_subjects_exist",
                reason_message=(
                    f"No exact target ref matched '{request.target_ref}', but related bounded subjects were found."
                ),
                near_matches=near_matches,
                next_steps=(
                    "Try one of the bounded target_ref values shown in the near matches.",
                    "Search with a tighter bounded subject or label query.",
                ),
            )

        return self._explained_report(
            request_kind="resolve",
            requested_value=request.target_ref,
            reason_code="subject_unknown_in_bounded_corpus",
            reason_message=(
                f"No bounded subject or state matching '{request.target_ref}' was found in the current local corpus."
            ),
            next_steps=(
                "Search the current bounded corpus with a broader subject or label term.",
                "Confirm that the target ref belongs to one of the loaded source families.",
            ),
        )

    def explain_search_miss(self, request: SearchAbsenceRequest) -> AbsenceReport:
        response = self._search_service.search(SearchRequest.from_parts(request.query))
        if response.results:
            return self._not_absent_report(
                request_kind="search",
                requested_value=request.query,
                reason_code="search_has_results",
                reason_message=f"Query '{request.query}' already returns bounded search results.",
            )

        related_records = self._related_records_for_text(request.query)
        if related_records:
            near_matches = tuple(
                self._near_match_for_record(record, match_kind="related_subject")
                for record in related_records[:_NEAR_MATCH_LIMIT]
            )
            next_steps = [
                "Retry search with one of the near-match target_ref values or object labels.",
                "Use an existing subject key if you are looking for known states of one bounded subject.",
            ]
            first_subject_key = subject_key_for_target_ref(related_records[0].target_ref)
            if first_subject_key is not None:
                next_steps.append(f"List known states for subject '{first_subject_key}'.")
            return self._explained_report(
                request_kind="search",
                requested_value=request.query,
                reason_code="related_subjects_exist",
                reason_message=(
                    f"No deterministic substring match was found for query '{request.query}', but related bounded "
                    "subjects were found."
                ),
                near_matches=near_matches,
                next_steps=tuple(next_steps),
            )

        return self._explained_report(
            request_kind="search",
            requested_value=request.query,
            reason_code="query_not_present_in_bounded_corpus",
            reason_message=(
                f"No bounded subject or label related to query '{request.query}' was found in the current local corpus."
            ),
            next_steps=(
                "Retry with a different bounded subject, version, or label term.",
                "Confirm that the expected source family is loaded into the current local corpus.",
            ),
        )

    def _explained_report(
        self,
        *,
        request_kind: str,
        requested_value: str,
        reason_code: str,
        reason_message: str,
        near_matches: tuple[AbsenceNearMatch, ...] = (),
        next_steps: tuple[str, ...] = (),
    ) -> AbsenceReport:
        return AbsenceReport(
            request_kind=request_kind,
            requested_value=requested_value,
            status="explained",
            checked_source_families=self._checked_source_families(),
            checked_record_count=len(self._catalog.records),
            checked_subject_count=self._checked_subject_count(),
            likely_reason_code=reason_code,
            reason_message=reason_message,
            near_matches=near_matches,
            next_steps=next_steps,
        )

    def _not_absent_report(
        self,
        *,
        request_kind: str,
        requested_value: str,
        reason_code: str,
        reason_message: str,
    ) -> AbsenceReport:
        return AbsenceReport(
            request_kind=request_kind,
            requested_value=requested_value,
            status="not_absent",
            checked_source_families=self._checked_source_families(),
            checked_record_count=len(self._catalog.records),
            checked_subject_count=self._checked_subject_count(),
            likely_reason_code=reason_code,
            reason_message=reason_message,
        )

    def _checked_source_families(self) -> tuple[str, ...]:
        families: list[str] = []
        for record in self._catalog.records:
            family = record.source_family.strip()
            if family and family not in families:
                families.append(family)
        return tuple(families)

    def _checked_subject_count(self) -> int:
        subject_keys = {
            subject_key
            for record in self._catalog.records
            for subject_key in (subject_key_for_target_ref(record.target_ref),)
            if subject_key is not None
        }
        return len(subject_keys)

    def _records_for_subject(self, subject_key: str) -> tuple[NormalizedResolutionRecord, ...]:
        return tuple(
            record
            for record in self._catalog.records
            if subject_key_for_target_ref(record.target_ref) == subject_key
        )

    def _related_records_for_text(self, text: str) -> tuple[NormalizedResolutionRecord, ...]:
        compact_text = _compact_text(text)
        if not compact_text:
            return ()

        records: list[NormalizedResolutionRecord] = []
        for record in self._catalog.records:
            if _record_is_related(record, compact_text):
                records.append(record)
        return tuple(records)

    def _near_match_for_record(
        self,
        record: NormalizedResolutionRecord,
        *,
        match_kind: str,
    ) -> AbsenceNearMatch:
        return AbsenceNearMatch(
            match_kind=match_kind,
            target_ref=record.target_ref,
            resolved_resource_id=resolved_resource_id_for_record(record),
            object_summary=normalized_record_to_object_summary(record),
            source=normalized_record_to_source_summary(record),
            subject_key=subject_key_for_target_ref(record.target_ref),
            version_or_state=version_or_state_for_target_ref(record.target_ref),
            normalized_version_or_state=normalized_version_or_state_for_target_ref(record.target_ref),
            evidence=record.evidence,
        )


def _record_is_related(record: NormalizedResolutionRecord, compact_text: str) -> bool:
    candidates = {
        _compact_text(record.target_ref),
        _compact_text(record.object_label or ""),
        _compact_text(record.object_id),
    }
    subject_key = subject_key_for_target_ref(record.target_ref)
    if subject_key is not None:
        candidates.add(_compact_text(subject_key))
    for candidate in candidates:
        if not candidate:
            continue
        if compact_text == candidate or compact_text in candidate or candidate in compact_text:
            return True
    return False


def _compact_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


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
