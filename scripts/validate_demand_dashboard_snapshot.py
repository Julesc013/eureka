#!/usr/bin/env python3
"""Validate Eureka Demand Dashboard Snapshot v0 examples.

This validator is stdlib-only and local. It validates contract/example
artifacts only; it performs no network calls, telemetry, persistence, account
tracking, IP tracking, public query logging, query-intelligence mutation,
public-index mutation, local-index mutation, master-index mutation, external
source calls, or live probes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "demand_dashboard"
SNAPSHOT_FILE_NAME = "DEMAND_DASHBOARD_SNAPSHOT.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "dashboard_snapshot_id",
    "dashboard_snapshot_kind",
    "status",
    "created_by_tool",
    "input_summary",
    "privacy_guard_summary",
    "poisoning_guard_summary",
    "dashboard_scope",
    "aggregate_buckets",
    "demand_signals",
    "source_gap_demand",
    "capability_gap_demand",
    "manual_observation_demand",
    "connector_priorities",
    "deep_extraction_priorities",
    "candidate_review_priorities",
    "known_absence_patterns",
    "priority_summary",
    "public_visibility",
    "freshness_and_invalidation",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "local_private",
    "public_safe_example",
    "rejected_by_privacy_filter",
    "invalidated_future",
}
ALLOWED_INPUT_KINDS = {"synthetic_example", "dry_run_example", "future_guarded_query_intelligence", "unknown"}
ALLOWED_SOURCE_CONTRACTS = {
    "query_observation",
    "search_result_cache",
    "search_miss_ledger",
    "search_need_record",
    "probe_queue",
    "candidate_index",
    "known_absence_page",
    "query_guard_decision",
}
ALLOWED_SCOPE_KINDS = {"synthetic_example", "public_safe_aggregate_future", "local_private_future"}
ALLOWED_TIME_WINDOWS = {"not_applicable_example", "rolling_window_future", "fixed_window_future"}
ALLOWED_BUCKET_TYPES = {
    "object_kind",
    "platform",
    "artifact_type",
    "source_family",
    "source_gap",
    "capability_gap",
    "miss_type",
    "probe_kind",
    "candidate_type",
    "known_absence_status",
    "manual_observation_need",
    "connector_priority",
    "deep_extraction_need",
    "unknown",
}
ALLOWED_COUNT_POLICIES = {"synthetic_example_count", "future_privacy_filtered_count", "count_not_available"}
ALLOWED_EXAMPLE_COUNT_POLICIES = {"synthetic_example_count", "count_not_available"}
ALLOWED_SIGNAL_TYPES = {
    "repeated_need_future",
    "repeated_miss_future",
    "source_gap",
    "capability_gap",
    "compatibility_gap",
    "member_access_gap",
    "known_absence_pattern",
    "manual_observation_needed",
    "connector_needed",
    "deep_extraction_needed",
    "candidate_review_needed",
    "policy_blocked_pattern",
    "unknown",
}
ALLOWED_PRIORITY_CLASSES = {"example_only", "low", "medium", "high", "unknown"}
ALLOWED_SYNTHETIC_OR_REAL = {"synthetic_example", "future_privacy_filtered"}
ALLOWED_SOURCE_GAP_TYPES = {
    "source_not_covered",
    "source_placeholder_only",
    "source_cache_missing",
    "connector_missing",
    "live_probe_disabled",
    "manual_observation_pending",
    "unknown",
}
ALLOWED_SOURCE_GAP_WORK = {
    "source_pack_request",
    "manual_observation_batch",
    "connector_approval_pack",
    "source_sync_worker_contract",
    "source_cache_evidence_ledger",
    "unknown",
}
ALLOWED_CAPABILITIES = {
    "OCR",
    "member_enumeration",
    "deep_extraction",
    "compatibility_evidence",
    "query_parser",
    "identity_resolution",
    "ranking",
    "source_cache",
    "evidence_ledger",
    "live_probe",
    "unknown",
}
ALLOWED_MANUAL_REASONS = {
    "external_baseline_pending",
    "source_gap_validation",
    "search_quality_comparison",
    "connector_priority_validation",
    "unknown",
}
ALLOWED_CONNECTOR_KINDS = {
    "internet_archive_metadata",
    "wayback_cdx_memento",
    "github_releases",
    "pypi_metadata",
    "npm_metadata",
    "software_heritage",
    "wikidata_open_library",
    "sourceforge_metadata",
    "manual_source_pack",
    "unknown",
}
ALLOWED_CONNECTOR_BASIS = {"synthetic_example", "source_gap_future", "repeated_need_future", "manual_priority_future", "external_baseline_future"}
ALLOWED_EXTRACTION_KINDS = {
    "container_member_enumeration",
    "installer_table_extraction",
    "OCR_scan",
    "WARC_capture_extraction",
    "archive_manifest_extraction",
    "source_repo_release_enumeration",
    "unknown",
}
ALLOWED_REVIEW_KINDS = {
    "evidence_review",
    "provenance_review",
    "source_policy_review",
    "rights_review",
    "risk_review",
    "conflict_review",
    "duplicate_review",
    "compatibility_review",
}
ALLOWED_ABSENCE_STATUSES = {
    "scoped_absence",
    "no_verified_result",
    "weak_hits_only",
    "near_misses_only",
    "source_coverage_gap",
    "capability_gap",
    "policy_blocked",
    "unknown",
}
ALLOWED_PRIORITY_BASIS = {"synthetic_example", "future_privacy_filtered_aggregate"}
ALLOWED_VISIBILITY_CLASSES = {"synthetic_example_only", "local_private_future", "public_safe_aggregate_future", "restricted"}
ALLOWED_FRESHNESS = {"example_only", "until_query_intelligence_rebuild_future", "rolling_window_future"}
ALLOWED_INVALIDATION_EVENTS = {
    "query_guard_policy_change",
    "public_index_rebuild",
    "source_cache_refresh",
    "candidate_promotion_policy_change",
    "privacy_policy_change",
    "poisoning_policy_change",
}
NO_RUNTIME_FALSE_FIELDS = {
    "runtime_dashboard_implemented",
    "persistent_dashboard_store_implemented",
    "telemetry_exported",
    "account_tracking_performed",
    "ip_tracking_performed",
    "public_query_logging_enabled",
    "raw_query_retained",
    "real_user_demand_claimed",
}
NO_MUTATION_FALSE_FIELDS = {
    "query_observation_mutated",
    "result_cache_mutated",
    "miss_ledger_mutated",
    "search_need_mutated",
    "probe_queue_mutated",
    "candidate_index_mutated",
    "candidate_promotion_mutated",
    "known_absence_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "external_calls_performed",
    "live_source_called",
}
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("windows_absolute_path_slash", re.compile(r"\b[A-Za-z]:/+(?:users|documents|temp|windows|projects|private|local)/+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d{1,3}[\s.-]+)?(?:\(?\d{2,4}\)?[\s.-]+){2,}\d{2,4}\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key)\b|\b(?:secret|credential)\s*[:=]", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\s*[:=]", re.IGNORECASE)),
)


def validate_snapshot_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_snapshot(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "demand_dashboard_snapshot_validator_v0",
        "snapshot": _repo_relative(path),
        "dashboard_snapshot_id": payload.get("dashboard_snapshot_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_snapshot_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    path = root / SNAPSHOT_FILE_NAME
    if not path.is_file():
        return {
            "status": "invalid",
            "created_by": "demand_dashboard_snapshot_validator_v0",
            "snapshot_root": _repo_relative(root),
            "dashboard_snapshot_id": None,
            "errors": [f"{SNAPSHOT_FILE_NAME}: missing snapshot file."],
            "warnings": [],
        }
    report = validate_snapshot_file(path, strict=strict, example_root=root)
    report["snapshot_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir()) if EXAMPLES_ROOT.is_dir() else []
    if not roots:
        errors.append("examples/demand_dashboard: no example roots found.")
    for root in roots:
        report = validate_snapshot_root(root, strict=strict)
        results.append(report)
        errors.extend(f"{report.get('snapshot_root')}: {error}" for error in report.get("errors", []))
        warnings.extend(f"{report.get('snapshot_root')}: {warning}" for warning in report.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "demand_dashboard_snapshot_validator_v0",
        "example_count": len(roots),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_snapshot(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - payload.keys())
    if missing:
        errors.append(f"missing required top-level fields: {', '.join(missing)}")
    if payload.get("dashboard_snapshot_kind") != "demand_dashboard_snapshot":
        errors.append("dashboard_snapshot_kind must be demand_dashboard_snapshot.")
    _enum(payload.get("status"), ALLOWED_STATUSES, "status", errors)

    _validate_false_fields(payload.get("no_runtime_guarantees"), NO_RUNTIME_FALSE_FIELDS, "no_runtime_guarantees", errors)
    _validate_false_fields(payload.get("no_mutation_guarantees"), NO_MUTATION_FALSE_FIELDS, "no_mutation_guarantees", errors)

    input_summary = _require_mapping(payload.get("input_summary"), "input_summary", errors)
    if input_summary:
        _enum(input_summary.get("input_kind"), ALLOWED_INPUT_KINDS, "input_summary.input_kind", errors)
        for field in ("real_user_data_included", "raw_queries_included", "protected_data_included"):
            if input_summary.get(field) is not False:
                errors.append(f"input_summary.{field} must be false.")
        refs = input_summary.get("source_contracts_referenced")
        if not isinstance(refs, list) or not refs:
            errors.append("input_summary.source_contracts_referenced must be a non-empty list.")
        else:
            for value in refs:
                _enum(value, ALLOWED_SOURCE_CONTRACTS, "input_summary.source_contracts_referenced[]", errors)

    privacy = _require_mapping(payload.get("privacy_guard_summary"), "privacy_guard_summary", errors)
    if privacy:
        for field in (
            "privacy_filter_required",
            "decisions_required_before_aggregation",
            "high_privacy_risk_excluded",
        ):
            if privacy.get(field) is not True:
                errors.append(f"privacy_guard_summary.{field} must be true.")
        for field in (
            "raw_query_aggregation_allowed",
            "private_path_aggregation_allowed",
            "secret_aggregation_allowed",
            "user_identifier_aggregation_allowed",
            "ip_address_aggregation_allowed",
        ):
            if privacy.get(field) is not False:
                errors.append(f"privacy_guard_summary.{field} must be false.")

    poisoning = _require_mapping(payload.get("poisoning_guard_summary"), "poisoning_guard_summary", errors)
    if poisoning:
        for field in (
            "poisoning_filter_required",
            "fake_demand_excluded",
            "spam_excluded",
            "source_stuffing_excluded",
            "candidate_poisoning_excluded",
            "high_poisoning_risk_excluded",
        ):
            if poisoning.get(field) is not True:
                errors.append(f"poisoning_guard_summary.{field} must be true.")
        if poisoning.get("throttling_runtime_implemented") is not False:
            errors.append("poisoning_guard_summary.throttling_runtime_implemented must be false.")

    scope = _require_mapping(payload.get("dashboard_scope"), "dashboard_scope", errors)
    if scope:
        _enum(scope.get("scope_kind"), ALLOWED_SCOPE_KINDS, "dashboard_scope.scope_kind", errors)
        _enum(scope.get("time_window_policy"), ALLOWED_TIME_WINDOWS, "dashboard_scope.time_window_policy", errors)
        for field in ("includes_live_probe_data", "includes_external_calls"):
            if scope.get(field) is not False:
                errors.append(f"dashboard_scope.{field} must be false.")

    _validate_buckets(payload.get("aggregate_buckets"), errors, strict=strict)
    _validate_signals(payload.get("demand_signals"), errors, strict=strict)
    _validate_source_gaps(payload.get("source_gap_demand"), errors)
    _validate_capability_gaps(payload.get("capability_gap_demand"), errors)
    _validate_manual_observation(payload.get("manual_observation_demand"), errors)
    _validate_connectors(payload.get("connector_priorities"), errors)
    _validate_deep_extraction(payload.get("deep_extraction_priorities"), errors)
    _validate_candidate_reviews(payload.get("candidate_review_priorities"), errors)
    _validate_known_absence(payload.get("known_absence_patterns"), errors)
    _validate_priority_summary(payload.get("priority_summary"), errors, strict=strict)
    _validate_public_visibility(payload.get("public_visibility"), errors, strict=strict)
    _validate_freshness(payload.get("freshness_and_invalidation"), errors)

    if strict and payload.get("status") not in {"synthetic_example", "public_safe_example"}:
        warnings.append("strict example validation expects synthetic_example or public_safe_example status.")


def _validate_buckets(value: Any, errors: list[str], *, strict: bool) -> None:
    if not isinstance(value, list) or not value:
        errors.append("aggregate_buckets must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"aggregate_buckets[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if not mapping:
            continue
        _enum(mapping.get("bucket_type"), ALLOWED_BUCKET_TYPES, f"{prefix}.bucket_type", errors)
        _enum(mapping.get("count_policy"), ALLOWED_COUNT_POLICIES, f"{prefix}.count_policy", errors)
        if strict:
            _enum(mapping.get("count_policy"), ALLOWED_EXAMPLE_COUNT_POLICIES, f"{prefix}.count_policy", errors)
        if mapping.get("count_claimed_as_real_user_demand") is not False:
            errors.append(f"{prefix}.count_claimed_as_real_user_demand must be false.")
        if mapping.get("privacy_safe") is not True:
            errors.append(f"{prefix}.privacy_safe must be true.")
        if mapping.get("poisoning_filtered") is not True:
            errors.append(f"{prefix}.poisoning_filtered must be true.")


def _validate_signals(value: Any, errors: list[str], *, strict: bool) -> None:
    if not isinstance(value, list) or not value:
        errors.append("demand_signals must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"demand_signals[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if not mapping:
            continue
        _enum(mapping.get("signal_type"), ALLOWED_SIGNAL_TYPES, f"{prefix}.signal_type", errors)
        _enum(mapping.get("priority_class"), ALLOWED_PRIORITY_CLASSES, f"{prefix}.priority_class", errors)
        _enum(mapping.get("synthetic_or_real"), ALLOWED_SYNTHETIC_OR_REAL, f"{prefix}.synthetic_or_real", errors)
        if strict and mapping.get("synthetic_or_real") != "synthetic_example":
            errors.append(f"{prefix}.synthetic_or_real must be synthetic_example in committed examples.")
        if mapping.get("real_user_demand_claimed") is not False:
            errors.append(f"{prefix}.real_user_demand_claimed must be false.")


def _validate_source_gaps(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("source_gap_demand must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"source_gap_demand[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if not mapping:
            continue
        _enum(mapping.get("gap_type"), ALLOWED_SOURCE_GAP_TYPES, f"{prefix}.gap_type", errors)
        _enum(mapping.get("suggested_future_work"), ALLOWED_SOURCE_GAP_WORK, f"{prefix}.suggested_future_work", errors)
        if mapping.get("approval_required") is not True:
            errors.append(f"{prefix}.approval_required must be true.")


def _validate_capability_gaps(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("capability_gap_demand must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"capability_gap_demand[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if mapping:
            _enum(mapping.get("capability"), ALLOWED_CAPABILITIES, f"{prefix}.capability", errors)
            _enum(mapping.get("priority_class"), ALLOWED_PRIORITY_CLASSES, f"{prefix}.priority_class", errors)


def _validate_manual_observation(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("manual_observation_demand must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"manual_observation_demand[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if not mapping:
            continue
        _enum(mapping.get("reason"), ALLOWED_MANUAL_REASONS, f"{prefix}.reason", errors)
        if mapping.get("human_required") is not True:
            errors.append(f"{prefix}.human_required must be true.")
        if mapping.get("real_observation_count_claimed") is not False:
            errors.append(f"{prefix}.real_observation_count_claimed must be false.")


def _validate_connectors(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("connector_priorities must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"connector_priorities[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if not mapping:
            continue
        _enum(mapping.get("connector_kind"), ALLOWED_CONNECTOR_KINDS, f"{prefix}.connector_kind", errors)
        _enum(mapping.get("priority_class"), ALLOWED_PRIORITY_CLASSES, f"{prefix}.priority_class", errors)
        _enum(mapping.get("basis"), ALLOWED_CONNECTOR_BASIS, f"{prefix}.basis", errors)
        if mapping.get("approval_required") is not True:
            errors.append(f"{prefix}.approval_required must be true.")


def _validate_deep_extraction(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("deep_extraction_priorities must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"deep_extraction_priorities[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if mapping:
            _enum(mapping.get("extraction_kind"), ALLOWED_EXTRACTION_KINDS, f"{prefix}.extraction_kind", errors)
            _enum(mapping.get("priority_class"), ALLOWED_PRIORITY_CLASSES, f"{prefix}.priority_class", errors)


def _validate_candidate_reviews(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("candidate_review_priorities must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"candidate_review_priorities[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if mapping:
            _enum(mapping.get("review_kind"), ALLOWED_REVIEW_KINDS, f"{prefix}.review_kind", errors)
            _enum(mapping.get("priority_class"), ALLOWED_PRIORITY_CLASSES, f"{prefix}.priority_class", errors)


def _validate_known_absence(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("known_absence_patterns must be a non-empty list.")
        return
    for idx, item in enumerate(value):
        prefix = f"known_absence_patterns[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if mapping:
            _enum(mapping.get("absence_status"), ALLOWED_ABSENCE_STATUSES, f"{prefix}.absence_status", errors)
            _enum(mapping.get("priority_class"), ALLOWED_PRIORITY_CLASSES, f"{prefix}.priority_class", errors)


def _validate_priority_summary(value: Any, errors: list[str], *, strict: bool) -> None:
    mapping = _require_mapping(value, "priority_summary", errors)
    if not mapping:
        return
    _enum(mapping.get("priority_basis"), ALLOWED_PRIORITY_BASIS, "priority_summary.priority_basis", errors)
    if strict and mapping.get("priority_basis") != "synthetic_example":
        errors.append("priority_summary.priority_basis must be synthetic_example in committed examples.")
    if mapping.get("real_user_demand_claimed") is not False:
        errors.append("priority_summary.real_user_demand_claimed must be false.")
    for field in (
        "top_source_gaps",
        "top_capability_gaps",
        "top_manual_observation_needs",
        "top_connector_priorities",
        "top_deep_extraction_priorities",
        "top_candidate_review_priorities",
        "top_known_absence_patterns",
    ):
        if not isinstance(mapping.get(field), list):
            errors.append(f"priority_summary.{field} must be a list.")


def _validate_public_visibility(value: Any, errors: list[str], *, strict: bool) -> None:
    mapping = _require_mapping(value, "public_visibility", errors)
    if not mapping:
        return
    _enum(mapping.get("visibility_class"), ALLOWED_VISIBILITY_CLASSES, "public_visibility.visibility_class", errors)
    if strict and mapping.get("public_dashboard_allowed") is not False:
        errors.append("public_visibility.public_dashboard_allowed must be false in v0 examples.")
    for field in ("raw_queries_visible", "private_data_visible", "demand_counts_claimed_as_real"):
        if mapping.get(field) is not False:
            errors.append(f"public_visibility.{field} must be false.")
    if not isinstance(mapping.get("caveats_required"), list) or not mapping.get("caveats_required"):
        errors.append("public_visibility.caveats_required must be a non-empty list.")


def _validate_freshness(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "freshness_and_invalidation", errors)
    if not mapping:
        return
    _enum(mapping.get("snapshot_freshness_policy"), ALLOWED_FRESHNESS, "freshness_and_invalidation.snapshot_freshness_policy", errors)
    if mapping.get("invalidated") is not False:
        errors.append("freshness_and_invalidation.invalidated must be false.")
    events = mapping.get("invalidation_required_on")
    if not isinstance(events, list) or not events:
        errors.append("freshness_and_invalidation.invalidation_required_on must be a non-empty list.")
    else:
        for event in events:
            _enum(event, ALLOWED_INVALIDATION_EVENTS, "freshness_and_invalidation.invalidation_required_on[]", errors)


def _validate_false_fields(value: Any, fields: Iterable[str], section: str, errors: list[str]) -> None:
    mapping = _require_mapping(value, section, errors)
    if not mapping:
        return
    for field in fields:
        if mapping.get(field) is not False:
            errors.append(f"{section}.{field} must be false.")


def _validate_no_sensitive_payload(payload: Mapping[str, Any], errors: list[str]) -> None:
    text = json.dumps(payload, sort_keys=True)
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append(f"snapshot contains prohibited private/sensitive data pattern: {label}")


def _validate_checksums(root: Path, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.is_file():
        errors.append("CHECKSUMS.SHA256 missing.")
        return
    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            errors.append(f"CHECKSUMS.SHA256 has malformed line: {line}")
            continue
        expected[parts[1]] = parts[0]
    for path in sorted(root.iterdir()):
        if path.name == "CHECKSUMS.SHA256" or not path.is_file():
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected.get(path.name) != actual:
            errors.append(f"CHECKSUMS.SHA256 mismatch for {path.name}.")
    for name in sorted(expected):
        if not (root / name).is_file():
            errors.append(f"CHECKSUMS.SHA256 references missing file: {name}.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_repo_relative(path)}: missing file.")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{_repo_relative(path)}: JSON parse error: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{_repo_relative(path)}: top-level JSON value must be an object.")
        return {}
    return value


def _require_mapping(value: Any, label: str, errors: list[str]) -> Mapping[str, Any] | None:
    if not isinstance(value, Mapping):
        errors.append(f"{label} must be an object.")
        return None
    return value


def _enum(value: Any, allowed: set[str], label: str, errors: list[str]) -> None:
    if value not in allowed:
        errors.append(f"{label} has unsupported value {value!r}; allowed: {', '.join(sorted(allowed))}.")


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _print_text(report: Mapping[str, Any], out: TextIO) -> None:
    print(f"status: {report['status']}", file=out)
    if "example_count" in report:
        print(f"example_count: {report['example_count']}", file=out)
    if report.get("errors"):
        print("errors:", file=out)
        for error in report["errors"]:
            print(f"  - {error}", file=out)
    if report.get("warnings"):
        print("warnings:", file=out)
        for warning in report["warnings"]:
            print(f"  - {warning}", file=out)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Demand Dashboard Snapshot v0 examples.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--snapshot", type=Path, help="Path to a DEMAND_DASHBOARD_SNAPSHOT.json file.")
    group.add_argument("--snapshot-root", type=Path, help="Path to an example root containing DEMAND_DASHBOARD_SNAPSHOT.json.")
    group.add_argument("--all-examples", action="store_true", help="Validate all committed demand dashboard examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply committed-example strictness.")
    args = parser.parse_args(argv)

    if args.snapshot:
        report = validate_snapshot_file(args.snapshot, strict=args.strict)
    elif args.snapshot_root:
        report = validate_snapshot_root(args.snapshot_root, strict=args.strict)
    else:
        report = validate_all_examples(strict=args.strict or args.all_examples)

    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        _print_text(report, sys.stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
