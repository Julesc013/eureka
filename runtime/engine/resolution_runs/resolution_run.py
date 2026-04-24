from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from runtime.engine.interfaces.public.absence import AbsenceNearMatch, AbsenceReport
from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.interfaces.public.resolution_run import (
    CheckedSourceSummary,
    ResolutionRunRecord,
    ResolutionRunResultItem,
    ResolutionRunResultSummary,
)
from runtime.engine.provenance import EvidenceSummary


class ResolutionRunNotFoundError(LookupError):
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        super().__init__(f"Unknown resolution run '{run_id}'.")


class MalformedResolutionRunRecordError(ValueError):
    def __init__(self, source_path: Path, message: str) -> None:
        self.source_path = source_path
        super().__init__(f"{source_path}: {message}")


def resolution_run_to_dict(run: ResolutionRunRecord) -> dict[str, Any]:
    payload = run.to_dict()
    payload["record_kind"] = "eureka.resolution_run"
    payload["record_version"] = "0.1.0-draft"
    return payload


def resolution_run_from_dict(
    raw_record: Mapping[str, Any],
    *,
    source_path: Path,
) -> ResolutionRunRecord:
    _require_string(raw_record.get("record_kind"), "record_kind", source_path)
    _require_string(raw_record.get("record_version"), "record_version", source_path)
    return ResolutionRunRecord(
        run_id=_require_string(raw_record.get("run_id"), "run_id", source_path),
        run_kind=_require_string(raw_record.get("run_kind"), "run_kind", source_path),
        requested_value=_require_string(raw_record.get("requested_value"), "requested_value", source_path),
        status=_require_string(raw_record.get("status"), "status", source_path),
        started_at=_require_string(raw_record.get("started_at"), "started_at", source_path),
        completed_at=_require_string(raw_record.get("completed_at"), "completed_at", source_path),
        checked_source_ids=_require_string_tuple(
            raw_record.get("checked_source_ids"),
            "checked_source_ids",
            source_path,
        ),
        checked_source_families=_require_string_tuple(
            raw_record.get("checked_source_families"),
            "checked_source_families",
            source_path,
        ),
        checked_sources=_coerce_checked_sources(
            raw_record.get("checked_sources"),
            "checked_sources",
            source_path,
        ),
        result_summary=_coerce_result_summary(
            raw_record.get("result_summary"),
            "result_summary",
            source_path,
        ),
        absence_report=_coerce_absence_report(
            raw_record.get("absence_report"),
            "absence_report",
            source_path,
        ),
        notices=_coerce_notices(raw_record.get("notices"), "notices", source_path),
        created_by_slice=_require_string(
            raw_record.get("created_by_slice"),
            "created_by_slice",
            source_path,
        ),
    )


def _coerce_checked_sources(
    value: Any,
    field_name: str,
    source_path: Path,
) -> tuple[CheckedSourceSummary, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be a list.")
    entries: list[CheckedSourceSummary] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionRunRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be an object.",
            )
        entries.append(
            CheckedSourceSummary(
                source_id=_require_string(item.get("source_id"), f"{field_name}[{index}].source_id", source_path),
                name=_require_string(item.get("name"), f"{field_name}[{index}].name", source_path),
                source_family=_require_string(
                    item.get("source_family"),
                    f"{field_name}[{index}].source_family",
                    source_path,
                ),
                status=_require_string(item.get("status"), f"{field_name}[{index}].status", source_path),
                trust_lane=_require_string(
                    item.get("trust_lane"),
                    f"{field_name}[{index}].trust_lane",
                    source_path,
                ),
            )
        )
    return tuple(entries)


def _coerce_result_summary(
    value: Any,
    field_name: str,
    source_path: Path,
) -> ResolutionRunResultSummary | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be an object.")
    items_value = value.get("items")
    if not isinstance(items_value, list):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}.items' must be a list.")
    items: list[ResolutionRunResultItem] = []
    for index, item in enumerate(items_value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionRunRecordError(
                source_path,
                f"Field '{field_name}.items[{index}]' must be an object.",
            )
        items.append(
            ResolutionRunResultItem(
                target_ref=_require_string(item.get("target_ref"), f"{field_name}.items[{index}].target_ref", source_path),
                object_summary=_coerce_object_summary(
                    item.get("object"),
                    f"{field_name}.items[{index}].object",
                    source_path,
                ),
                resolved_resource_id=_optional_string(
                    item.get("resolved_resource_id"),
                    f"{field_name}.items[{index}].resolved_resource_id",
                    source_path,
                ),
                source=_coerce_source_summary(
                    item.get("source"),
                    f"{field_name}.items[{index}].source",
                    source_path,
                ),
                evidence=_coerce_evidence_list(
                    item.get("evidence"),
                    f"{field_name}.items[{index}].evidence",
                    source_path,
                ),
            )
        )
    return ResolutionRunResultSummary(
        result_kind=_require_string(value.get("result_kind"), f"{field_name}.result_kind", source_path),
        result_count=_require_non_negative_int(value.get("result_count"), f"{field_name}.result_count", source_path),
        items=tuple(items),
    )


def _coerce_absence_report(
    value: Any,
    field_name: str,
    source_path: Path,
) -> AbsenceReport | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be an object.")
    near_matches_value = value.get("near_matches")
    if not isinstance(near_matches_value, list):
        raise MalformedResolutionRunRecordError(
            source_path,
            f"Field '{field_name}.near_matches' must be a list.",
        )
    near_matches: list[AbsenceNearMatch] = []
    for index, item in enumerate(near_matches_value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionRunRecordError(
                source_path,
                f"Field '{field_name}.near_matches[{index}]' must be an object.",
            )
        near_matches.append(
            AbsenceNearMatch(
                match_kind=_require_string(item.get("match_kind"), f"{field_name}.near_matches[{index}].match_kind", source_path),
                target_ref=_require_string(item.get("target_ref"), f"{field_name}.near_matches[{index}].target_ref", source_path),
                resolved_resource_id=_require_string(
                    item.get("resolved_resource_id"),
                    f"{field_name}.near_matches[{index}].resolved_resource_id",
                    source_path,
                ),
                object_summary=_coerce_object_summary(
                    item.get("object"),
                    f"{field_name}.near_matches[{index}].object",
                    source_path,
                ),
                source=_coerce_source_summary(
                    item.get("source"),
                    f"{field_name}.near_matches[{index}].source",
                    source_path,
                ),
                subject_key=_optional_string(
                    item.get("subject_key"),
                    f"{field_name}.near_matches[{index}].subject_key",
                    source_path,
                ),
                version_or_state=_optional_string(
                    item.get("version_or_state"),
                    f"{field_name}.near_matches[{index}].version_or_state",
                    source_path,
                ),
                normalized_version_or_state=_optional_string(
                    item.get("normalized_version_or_state"),
                    f"{field_name}.near_matches[{index}].normalized_version_or_state",
                    source_path,
                ),
                evidence=_coerce_evidence_list(
                    item.get("evidence"),
                    f"{field_name}.near_matches[{index}].evidence",
                    source_path,
                ),
            )
        )
    return AbsenceReport(
        request_kind=_require_string(value.get("request_kind"), f"{field_name}.request_kind", source_path),
        requested_value=_require_string(
            value.get("requested_value"),
            f"{field_name}.requested_value",
            source_path,
        ),
        status=_require_string(value.get("status"), f"{field_name}.status", source_path),
        checked_source_families=_require_string_tuple(
            value.get("checked_source_families"),
            f"{field_name}.checked_source_families",
            source_path,
        ),
        checked_record_count=_require_non_negative_int(
            value.get("checked_record_count"),
            f"{field_name}.checked_record_count",
            source_path,
        ),
        checked_subject_count=_require_non_negative_int(
            value.get("checked_subject_count"),
            f"{field_name}.checked_subject_count",
            source_path,
        ),
        likely_reason_code=_require_string(
            value.get("likely_reason_code"),
            f"{field_name}.likely_reason_code",
            source_path,
        ),
        reason_message=_require_string(
            value.get("reason_message"),
            f"{field_name}.reason_message",
            source_path,
        ),
        near_matches=tuple(near_matches),
        next_steps=_require_string_tuple(value.get("next_steps"), f"{field_name}.next_steps", source_path),
        notices=_coerce_notices(value.get("notices"), f"{field_name}.notices", source_path),
    )


def _coerce_object_summary(value: Any, field_name: str, source_path: Path) -> ObjectSummary:
    if not isinstance(value, Mapping):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be an object.")
    return ObjectSummary(
        id=_require_string(value.get("id"), f"{field_name}.id", source_path),
        kind=_optional_string(value.get("kind"), f"{field_name}.kind", source_path),
        label=_optional_string(value.get("label"), f"{field_name}.label", source_path),
    )


def _coerce_source_summary(
    value: Any,
    field_name: str,
    source_path: Path,
) -> SourceSummary | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be an object.")
    return SourceSummary(
        family=_require_string(value.get("family"), f"{field_name}.family", source_path),
        source_id=_optional_string(value.get("source_id"), f"{field_name}.source_id", source_path),
        label=_optional_string(value.get("label"), f"{field_name}.label", source_path),
        locator=_optional_string(value.get("locator"), f"{field_name}.locator", source_path),
    )


def _coerce_evidence_list(
    value: Any,
    field_name: str,
    source_path: Path,
) -> tuple[EvidenceSummary, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be a list.")
    entries: list[EvidenceSummary] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionRunRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be an object.",
            )
        entries.append(
            EvidenceSummary(
                claim_kind=_require_string(item.get("claim_kind"), f"{field_name}[{index}].claim_kind", source_path),
                claim_value=_require_string(
                    item.get("claim_value"),
                    f"{field_name}[{index}].claim_value",
                    source_path,
                ),
                asserted_by_family=_require_string(
                    item.get("asserted_by_family"),
                    f"{field_name}[{index}].asserted_by_family",
                    source_path,
                ),
                evidence_kind=_require_string(
                    item.get("evidence_kind"),
                    f"{field_name}[{index}].evidence_kind",
                    source_path,
                ),
                evidence_locator=_require_string(
                    item.get("evidence_locator"),
                    f"{field_name}[{index}].evidence_locator",
                    source_path,
                ),
                asserted_by_label=_optional_string(
                    item.get("asserted_by_label"),
                    f"{field_name}[{index}].asserted_by_label",
                    source_path,
                ),
                asserted_at=_optional_string(
                    item.get("asserted_at"),
                    f"{field_name}[{index}].asserted_at",
                    source_path,
                ),
            )
        )
    return tuple(entries)


def _coerce_notices(
    value: Any,
    field_name: str,
    source_path: Path,
) -> tuple[Notice, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be a list.")
    notices: list[Notice] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionRunRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be an object.",
            )
        notices.append(
            Notice(
                code=_require_string(item.get("code"), f"{field_name}[{index}].code", source_path),
                severity=_require_string(item.get("severity"), f"{field_name}[{index}].severity", source_path),
                message=_optional_string(item.get("message"), f"{field_name}[{index}].message", source_path),
            )
        )
    return tuple(notices)


def _require_string(value: Any, field_name: str, source_path: Path) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedResolutionRunRecordError(
            source_path,
            f"Field '{field_name}' must be a non-empty string.",
        )
    return value


def _optional_string(value: Any, field_name: str, source_path: Path) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name, source_path)


def _require_string_tuple(value: Any, field_name: str, source_path: Path) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise MalformedResolutionRunRecordError(source_path, f"Field '{field_name}' must be a list.")
    entries: list[str] = []
    for index, item in enumerate(value):
        entries.append(_require_string(item, f"{field_name}[{index}]", source_path))
    return tuple(entries)


def _require_non_negative_int(value: Any, field_name: str, source_path: Path) -> int:
    if not isinstance(value, int) or value < 0:
        raise MalformedResolutionRunRecordError(
            source_path,
            f"Field '{field_name}' must be a non-negative integer.",
        )
    return value
