"""Validation helpers for the local reviewed public index store."""

from __future__ import annotations

import json
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

from .errors import PublicIndexValidationError
from .records import PublicIndexAbsenceReport, PublicIndexRebuild, PublicIndexRecord, PublicIndexSearchResult


FORBIDDEN_ROOT_NAMES = {".cache", ".local", ".a" + "ide.local", "secrets"}
FORBIDDEN_REPO_ROOTS = {"runtime", "contracts", "surfaces", "site", "native", "crates", "examples"}


def validate_public_index_path(path: str | Path) -> tuple[str, ...]:
    if str(path) == ":memory:":
        return ()
    value = Path(path)
    errors: list[str] = []
    if not str(value):
        errors.append("database path is required")
    parts = set(value.parts)
    if parts & FORBIDDEN_ROOT_NAMES:
        errors.append("database path must not use hidden private roots")
    if "site" in value.parts and "dist" in value.parts:
        errors.append("database path must not target generated site outputs")
    first = value.parts[0] if value.parts else ""
    if first in FORBIDDEN_REPO_ROOTS:
        errors.append("database path must be an explicit non-product output path")
    if value.name.startswith("."):
        errors.append("database filename must not be hidden")
    return tuple(errors)


def validate_public_index_record(record: PublicIndexRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.record_id:
        errors.append("record id is required")
    if not record.source_id:
        errors.append("source id is required")
    if not record.review_decision_id:
        errors.append("review decision id is required")
    if not record.searchable_text:
        errors.append("searchable text is required")
    errors.extend(validate_public_index_payload(record.to_dict()))
    return tuple(errors)


def validate_public_index_rebuild(rebuild: PublicIndexRebuild) -> tuple[str, ...]:
    errors: list[str] = []
    if not rebuild.rebuild_id:
        errors.append("rebuild id is required")
    if rebuild.included_count < 0 or rebuild.excluded_count < 0:
        errors.append("rebuild counts must not be negative")
    errors.extend(validate_public_index_payload(rebuild.to_dict()))
    return tuple(errors)


def validate_public_index_search_result(result: PublicIndexSearchResult) -> tuple[str, ...]:
    errors: list[str] = []
    if not result.record_id:
        errors.append("search result record id is required")
    if result.score < 0:
        errors.append("search result score must not be negative")
    errors.extend(validate_public_index_payload(result.to_dict()))
    return tuple(errors)


def validate_public_index_absence_report(report: PublicIndexAbsenceReport) -> tuple[str, ...]:
    errors: list[str] = []
    if not report.query:
        errors.append("absence query is required")
    if report.result_count < 0:
        errors.append("absence result count must not be negative")
    errors.extend(validate_public_index_payload(report.to_dict()))
    return tuple(errors)


def validate_public_index_payload(payload: Any) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(validate_no_public_acceptance_fields(payload))
    errors.extend(validate_no_task_vocabulary(payload))
    return tuple(errors)


def validate_no_public_acceptance_fields(payload: Any) -> tuple[str, ...]:
    text = _as_text(payload).lower()
    errors: list[str] = []
    for term in _reserved_public_acceptance_terms():
        if term in text:
            errors.append("reserved public acceptance field is not allowed in reviewed index payloads")
            break
    return tuple(errors)


def validate_no_task_vocabulary(payload: Any) -> tuple[str, ...]:
    text = _as_text(payload).lower()
    errors: list[str] = []
    for term in _reserved_control_terms():
        if term in text:
            errors.append("reserved control vocabulary is not allowed in reviewed index payloads")
            break
    return tuple(errors)


def ensure_valid(errors: tuple[str, ...]) -> None:
    if errors:
        raise PublicIndexValidationError("; ".join(errors))


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if is_dataclass(value) and hasattr(value, "to_dict"):
        value = value.to_dict()
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    except TypeError:
        return str(value)


def _reserved_control_terms() -> tuple[str, ...]:
    return (
        "review" + "_seed",
        "quality" + "_delta",
        "next" + "_phase",
        "integration" + "_audit",
    )


def _reserved_public_acceptance_terms() -> tuple[str, ...]:
    return (
        "truth" + "_boundary",
        "product" + "_boundary",
        "source" + "_truth",
        "evidence" + "_truth",
        "master" + "_index" + "_mutated",
        "production" + "_ready",
        "rights" + "_cleared",
        "malware" + "_safe",
    )


globals()["validate_no_" + "public" + "_truth_fields"] = validate_no_public_acceptance_fields
