from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from runtime.engine.interfaces.public.absence import AbsenceNearMatch, AbsenceReport
from runtime.engine.interfaces.public.query_plan import ResolutionTask
from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.interfaces.public.resolution_memory import (
    ResolutionMemoryRecord,
    ResolutionMemoryResultSummary,
)
from runtime.engine.interfaces.public.resolution_run import CheckedSourceSummary
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.query_planner.resolution_task import resolution_task_from_dict


class MalformedResolutionMemoryRecordError(ValueError):
    def __init__(self, source_path: Path, message: str) -> None:
        self.source_path = source_path
        super().__init__(f"{source_path}: {message}")


def resolution_memory_to_dict(memory: ResolutionMemoryRecord) -> dict[str, Any]:
    payload = memory.to_dict()
    payload["record_kind"] = "eureka.resolution_memory"
    payload["record_version"] = "0.1.0-draft"
    return payload


def resolution_memory_from_dict(
    raw_record: Mapping[str, Any],
    *,
    source_path: Path,
) -> ResolutionMemoryRecord:
    _require_string(raw_record.get("record_kind"), "record_kind", source_path)
    _require_string(raw_record.get("record_version"), "record_version", source_path)
    return ResolutionMemoryRecord(
        memory_id=_require_string(raw_record.get("memory_id"), "memory_id", source_path),
        memory_kind=_require_string(raw_record.get("memory_kind"), "memory_kind", source_path),
        source_run_id=_require_string(raw_record.get("source_run_id"), "source_run_id", source_path),
        created_at=_require_string(raw_record.get("created_at"), "created_at", source_path),
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
        raw_query=_optional_string(raw_record.get("raw_query"), "raw_query", source_path),
        task_kind=_optional_string(raw_record.get("task_kind"), "task_kind", source_path),
        requested_value=_optional_string(
            raw_record.get("requested_value"),
            "requested_value",
            source_path,
        ),
        resolution_task=_coerce_resolution_task(
            raw_record.get("resolution_task"),
            "resolution_task",
            source_path,
        ),
        result_summaries=_coerce_result_summaries(
            raw_record.get("result_summaries"),
            "result_summaries",
            source_path,
        ),
        absence_report=_coerce_absence_report(
            raw_record.get("absence_report"),
            "absence_report",
            source_path,
        ),
        useful_source_ids=_require_string_tuple(
            raw_record.get("useful_source_ids"),
            "useful_source_ids",
            source_path,
        ),
        primary_resolved_resource_id=_optional_string(
            raw_record.get("primary_resolved_resource_id"),
            "primary_resolved_resource_id",
            source_path,
        ),
        evidence_summary=_coerce_evidence_list(
            raw_record.get("evidence_summary"),
            "evidence_summary",
            source_path,
        ),
        notices=_coerce_notices(raw_record.get("notices"), "notices", source_path),
        created_by_slice=_require_string(
            raw_record.get("created_by_slice"),
            "created_by_slice",
            source_path,
        ),
        invalidation_hints=_coerce_optional_json_object(
            raw_record.get("invalidation_hints"),
            "invalidation_hints",
            source_path,
        ),
    )


def _coerce_resolution_task(
    value: Any,
    field_name: str,
    source_path: Path,
) -> ResolutionTask | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise MalformedResolutionMemoryRecordError(
            source_path,
            f"Field '{field_name}' must be an object.",
        )
    return resolution_task_from_dict(value, source_path=source_path)


def _coerce_checked_sources(
    value: Any,
    field_name: str,
    source_path: Path,
) -> tuple[CheckedSourceSummary, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be a list.")
    entries: list[CheckedSourceSummary] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionMemoryRecordError(
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


def _coerce_result_summaries(
    value: Any,
    field_name: str,
    source_path: Path,
) -> tuple[ResolutionMemoryResultSummary, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be a list.")
    summaries: list[ResolutionMemoryResultSummary] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionMemoryRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be an object.",
            )
        summaries.append(
            ResolutionMemoryResultSummary(
                target_ref=_require_string(item.get("target_ref"), f"{field_name}[{index}].target_ref", source_path),
                object_summary=_coerce_object_summary(
                    item.get("object"),
                    f"{field_name}[{index}].object",
                    source_path,
                ),
                resolved_resource_id=_optional_string(
                    item.get("resolved_resource_id"),
                    f"{field_name}[{index}].resolved_resource_id",
                    source_path,
                ),
                source=_coerce_source_summary(
                    item.get("source"),
                    f"{field_name}[{index}].source",
                    source_path,
                ),
            )
        )
    return tuple(summaries)


def _coerce_absence_report(
    value: Any,
    field_name: str,
    source_path: Path,
) -> AbsenceReport | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be an object.")
    near_matches_value = value.get("near_matches")
    if not isinstance(near_matches_value, list):
        raise MalformedResolutionMemoryRecordError(
            source_path,
            f"Field '{field_name}.near_matches' must be a list.",
        )
    near_matches: list[AbsenceNearMatch] = []
    for index, item in enumerate(near_matches_value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionMemoryRecordError(
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
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be an object.")
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
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be an object.")
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
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be a list.")
    evidence_summaries: list[EvidenceSummary] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionMemoryRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be an object.",
            )
        evidence_summaries.append(
            EvidenceSummary(
                claim_kind=_require_string(item.get("claim_kind"), f"{field_name}[{index}].claim_kind", source_path),
                claim_value=_require_string(item.get("claim_value"), f"{field_name}[{index}].claim_value", source_path),
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
    return tuple(evidence_summaries)


def _coerce_notices(value: Any, field_name: str, source_path: Path) -> tuple[Notice, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be a list.")
    notices: list[Notice] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise MalformedResolutionMemoryRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be an object.",
            )
        notices.append(
            Notice(
                code=_require_string(item.get("code"), f"{field_name}[{index}].code", source_path),
                severity=_require_string(
                    item.get("severity"),
                    f"{field_name}[{index}].severity",
                    source_path,
                ),
                message=_optional_string(
                    item.get("message"),
                    f"{field_name}[{index}].message",
                    source_path,
                ),
            )
        )
    return tuple(notices)


def _coerce_optional_json_object(
    value: Any,
    field_name: str,
    source_path: Path,
) -> dict[str, Any] | None:
    if value is None:
        return None
    return _coerce_json_object(value, field_name, source_path)


def _coerce_json_object(value: Any, field_name: str, source_path: Path) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be an object.")
    return _clone_json_like(value, field_name, source_path)


def _clone_json_like(value: Any, field_name: str, source_path: Path) -> Any:
    if isinstance(value, Mapping):
        payload: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise MalformedResolutionMemoryRecordError(
                    source_path,
                    f"Field '{field_name}' keys must be non-empty strings.",
                )
            payload[key] = _clone_json_like(item, f"{field_name}.{key}", source_path)
        return payload
    if isinstance(value, list):
        return [_clone_json_like(item, f"{field_name}[]", source_path) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise MalformedResolutionMemoryRecordError(
        source_path,
        f"Field '{field_name}' must contain only JSON-compatible values.",
    )


def _require_string_tuple(value: Any, field_name: str, source_path: Path) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise MalformedResolutionMemoryRecordError(source_path, f"Field '{field_name}' must be a list.")
    entries: list[str] = []
    for index, item in enumerate(value):
        entries.append(_require_string(item, f"{field_name}[{index}]", source_path))
    return tuple(entries)


def _require_string(value: Any, field_name: str, source_path: Path) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedResolutionMemoryRecordError(
            source_path,
            f"Field '{field_name}' must be a non-empty string.",
        )
    return value


def _optional_string(value: Any, field_name: str, source_path: Path) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name, source_path)


def _require_non_negative_int(value: Any, field_name: str, source_path: Path) -> int:
    if not isinstance(value, int) or value < 0:
        raise MalformedResolutionMemoryRecordError(
            source_path,
            f"Field '{field_name}' must be a non-negative integer.",
        )
    return value
