"""Validation for local Internet Archive metadata fixture replay."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.source.observation.internet_archive_metadata import (
    FORBIDDEN_SIDE_EFFECT_FLAGS,
    IAMetadataCandidateRecord,
    IABoundaryReport,
    OBSERVATION_KINDS,
    SOURCE_ID,
)


REQUIRED_FIXTURE_CLASSES = (
    "metadata_search_small",
    "item_metadata_read",
    "item_file_list_metadata_read",
    "missing_item",
    "malformed_partial",
    "retry_after_429",
    "large_file_list",
    "no_download_proof",
)


def validate_ia_fixture_payload(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("schema_version") != "ia_metadata_fixture.v0":
        errors.append("fixture schema_version must be ia_metadata_fixture.v0")
    if not payload.get("fixture_id"):
        errors.append("fixture_id is required")
    fixture_class = str(payload.get("fixture_class", ""))
    if fixture_class not in REQUIRED_FIXTURE_CLASSES:
        errors.append(f"fixture_class is not supported: {fixture_class}")
    if "payload" not in payload:
        errors.append("payload is required")
    if payload.get("expected", {}).get("download_performed") is not False:
        errors.append("fixture expected download_performed must be false")
    return tuple(errors)


def validate_normalized_ia_record(record: IAMetadataCandidateRecord | Mapping[str, Any]) -> tuple[str, ...]:
    data = record.to_dict() if isinstance(record, IAMetadataCandidateRecord) else dict(record)
    errors: list[str] = []
    if data.get("source_id") != SOURCE_ID:
        errors.append("source_id must be internet_archive_metadata")
    if data.get("observation_kind") not in OBSERVATION_KINDS:
        errors.append("observation_kind is not supported")
    if not data.get("observation_id"):
        errors.append("observation_id is required")
    if data.get("review_required") is not True:
        errors.append("review_required must be true")
    if data.get("accepted_truth") is not False:
        errors.append("accepted_truth must be false")
    for key in (
        "download_performed",
        "source_cache_write_performed",
        "evidence_ledger_write_performed",
        "index_mutation_performed",
    ):
        if data.get(key) is not False:
            errors.append(f"{key} must be false")
    if "rights_clear" in data.get("rights_flags", []):
        errors.append("rights clearance cannot be inferred")
    if "safe" in data.get("risk_flags", []):
        errors.append("safety cannot be inferred")
    return tuple(errors)


def build_boundary_report(
    record: IAMetadataCandidateRecord,
    *,
    network_imports_detected: bool = False,
) -> IABoundaryReport:
    violations = list(validate_normalized_ia_record(record))
    if network_imports_detected:
        violations.append("forbidden network imports detected")
    return IABoundaryReport(
        fixture_id=record.fixture_id,
        observation_id=record.observation_id,
        observation_kind=record.observation_kind,
        passed=not violations,
        violations=tuple(violations),
        network_imports_detected=network_imports_detected,
    )


def validate_boundary_report(report: IABoundaryReport | Mapping[str, Any]) -> tuple[str, ...]:
    data = report.to_dict() if isinstance(report, IABoundaryReport) else dict(report)
    errors: list[str] = []
    if data.get("passed") is not True:
        errors.append("boundary report did not pass")
    if data.get("violations"):
        errors.append("boundary report has violations")
    if data.get("network_imports_detected") is not False:
        errors.append("network imports must not be detected")
    for key in FORBIDDEN_SIDE_EFFECT_FLAGS:
        if data.get(key) is not False:
            errors.append(f"{key} must be false")
    return tuple(errors)
