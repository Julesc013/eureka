#!/usr/bin/env python3
"""Validate Eureka Probe Queue Item v0 examples.

The validator is structural and stdlib-only. It validates P63 probe queue
examples without using telemetry, persistence, network calls, live probes,
runtime queues, source cache writes, evidence ledger writes, candidate-index
mutation, local-index mutation, or master-index writes.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "probe_queue"
ITEM_FILE_NAME = "PROBE_QUEUE_ITEM.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "probe_item_id",
    "probe_item_kind",
    "status",
    "created_by_tool",
    "probe_identity",
    "probe_kind",
    "source_policy",
    "input_refs",
    "target",
    "priority",
    "scheduling",
    "expected_outputs",
    "safety_requirements",
    "privacy",
    "retention_policy",
    "aggregation_policy",
    "limitations",
    "no_execution_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "queued_future",
    "local_private",
    "public_aggregate_candidate",
    "rejected_by_privacy_filter",
    "approval_required",
    "operator_required",
    "blocked_by_policy",
    "superseded_future",
    "completed_future",
    "cancelled_future",
}
ALLOWED_PROBE_KINDS = {
    "manual_observation",
    "source_cache_refresh",
    "source_metadata_probe",
    "source_identifier_probe",
    "wayback_availability_probe",
    "package_metadata_probe",
    "repository_release_probe",
    "deep_container_extraction",
    "member_enumeration",
    "OCR_or_scan_extraction",
    "compatibility_evidence_request",
    "source_pack_request",
    "evidence_pack_request",
    "index_pack_request",
    "query_parser_improvement_request",
    "unknown",
}
ALLOWED_EXECUTION_CLASSES = {
    "human_operated_future",
    "scheduled_worker_future",
    "approval_gated_live_probe_future",
    "local_offline_extraction_future",
    "connector_runtime_future",
    "no_execution_v0",
}
ALLOWED_SOURCE_POLICIES = {
    "no_source_call",
    "manual_only",
    "fixture_only",
    "source_cache_only_future",
    "live_metadata_probe_after_approval",
    "local_offline_extraction_after_approval",
    "unknown",
}
ALLOWED_REF_KINDS = {
    "query_observation",
    "search_result_cache",
    "search_miss_ledger",
    "search_need",
    "manual_observation_future",
    "source_pack_future",
    "evidence_pack_future",
}
ALLOWED_TARGET_KINDS = {
    "source_family",
    "source_id",
    "object_identity",
    "software_version",
    "driver",
    "manual_or_documentation",
    "source_code_release",
    "package_metadata",
    "web_capture",
    "article_or_scan_segment",
    "file_inside_container",
    "compatibility_evidence",
    "query_parser_gap",
    "unknown",
}
ALLOWED_OUTPUT_KINDS = {
    "manual_observation",
    "source_cache_record",
    "evidence_record_candidate",
    "candidate_index_record",
    "absence_evidence",
    "source_pack_request",
    "evidence_pack_request",
    "extraction_report",
    "query_parser_issue",
    "unknown",
}
ALLOWED_OUTPUT_POLICIES = {
    "no_output_v0",
    "source_cache_future",
    "evidence_ledger_future",
    "candidate_index_future",
    "manual_report_future",
    "contribution_candidate_future",
}
ALLOWED_PRIVACY_CLASSIFICATIONS = {"public_safe_aggregate", "local_private", "rejected_sensitive", "redacted", "unknown"}
ALLOWED_SCHEDULE_STATUSES = {"not_scheduled_v0", "future_manual", "future_scheduled_worker", "future_after_approval", "blocked"}
ALLOWED_EARLIEST_RUN_POLICIES = {
    "not_applicable_v0",
    "after_human_approval_future",
    "after_operator_setup_future",
    "after_source_policy_review_future",
}
HARD_EXECUTION_FALSE_FIELDS = {
    "probe_executed",
    "live_source_called",
    "external_calls_performed",
}
HARD_MUTATION_FALSE_FIELDS = {
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "master_index_mutated",
    "local_index_mutated",
    "result_cache_mutated",
    "miss_ledger_mutated",
    "search_need_mutated",
    "telemetry_exported",
}
PRIVACY_FALSE_FIELDS = {
    "contains_raw_query",
    "contains_private_path",
    "contains_secret",
    "contains_private_url",
    "contains_user_identifier",
    "contains_ip_address",
    "contains_local_result",
}
SAFETY_TRUE_FIELDS = {
    "no_downloads",
    "no_installs",
    "no_execution",
    "no_uploads",
    "no_private_paths",
    "no_credentials",
    "no_arbitrary_url_fetch",
}
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[a-zA-Z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d[\d .-]{7,}\d)\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\b", re.IGNORECASE)),
)


def validate_probe_queue_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_item(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "probe_queue_item_validator_v0",
        "item": _repo_relative(path),
        "probe_item_id": payload.get("probe_item_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_probe_queue_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    item_path = root / ITEM_FILE_NAME
    if not item_path.is_file():
        return {
            "status": "invalid",
            "created_by": "probe_queue_item_validator_v0",
            "item_root": _repo_relative(root),
            "probe_item_id": None,
            "errors": [f"{ITEM_FILE_NAME}: missing probe queue item file."],
            "warnings": [],
        }
    report = validate_probe_queue_file(item_path, strict=strict, example_root=root)
    report["item_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/probe_queue: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/probe_queue: no example roots found.")
        for root in roots:
            result = validate_probe_queue_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('item_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('item_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "probe_queue_item_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_item(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("probe_item_kind") != "probe_queue_item":
        errors.append("probe_item_kind must be probe_queue_item.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not an allowed probe queue status.")

    probe_kind = _require_mapping(payload, "probe_kind", errors)
    _validate_probe_identity(_require_mapping(payload, "probe_identity", errors), errors)
    _validate_probe_kind(probe_kind, errors)
    _validate_source_policy(_require_mapping(payload, "source_policy", errors), errors, probe_kind)
    _validate_input_refs(_require_mapping(payload, "input_refs", errors), errors)
    _validate_target(_require_mapping(payload, "target", errors), errors)
    _validate_priority(_require_mapping(payload, "priority", errors), errors)
    _validate_scheduling(_require_mapping(payload, "scheduling", errors), errors)
    _validate_expected_outputs(_require_mapping(payload, "expected_outputs", errors), errors)
    _validate_safety(_require_mapping(payload, "safety_requirements", errors), errors, probe_kind)
    _validate_privacy(_require_mapping(payload, "privacy", errors), errors, payload)
    _validate_retention(_require_mapping(payload, "retention_policy", errors), errors)
    _validate_aggregation(_require_mapping(payload, "aggregation_policy", errors), errors)
    _validate_execution_guarantees(_require_mapping(payload, "no_execution_guarantees", errors), errors)
    _validate_mutation_guarantees(_require_mapping(payload, "no_mutation_guarantees", errors), errors)

    if strict and payload.get("status") in {"queued_future", "public_aggregate_candidate"}:
        warnings.append("future queue/public aggregate statuses require later approval and privacy review before use.")


def _validate_probe_identity(value: Mapping[str, Any], errors: list[str]) -> None:
    fingerprint = _require_mapping(value, "probe_fingerprint", errors)
    if fingerprint:
        if fingerprint.get("algorithm") != "sha256":
            errors.append("probe_identity.probe_fingerprint.algorithm must be sha256.")
        if not isinstance(fingerprint.get("value"), str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint["value"]):
            errors.append("probe_identity.probe_fingerprint.value must be a lowercase sha256 hex string.")
        if fingerprint.get("reversible") is not False:
            errors.append("probe_identity.probe_fingerprint.reversible must be false.")
        if fingerprint.get("salt_policy") not in {"unsalted_public_aggregate", "deployment_secret_salted_future", "local_private_salted_future"}:
            errors.append("probe_identity.probe_fingerprint.salt_policy is invalid.")
    if not isinstance(value.get("canonical_probe_label"), str) or not value.get("canonical_probe_label"):
        errors.append("probe_identity.canonical_probe_label must be a non-empty string.")
    if not isinstance(value.get("normalized_probe_terms"), list):
        errors.append("probe_identity.normalized_probe_terms must be a list.")


def _validate_probe_kind(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("kind") not in ALLOWED_PROBE_KINDS:
        errors.append("probe_kind.kind is invalid.")
    if value.get("execution_class") not in ALLOWED_EXECUTION_CLASSES:
        errors.append("probe_kind.execution_class is invalid.")
    for key in ("live_network_required_future", "approval_required", "operator_required", "human_required"):
        if not isinstance(value.get(key), bool):
            errors.append(f"probe_kind.{key} must be boolean.")
    if value.get("live_network_required_future") is True and value.get("approval_required") is not True:
        errors.append("probe_kind.approval_required must be true when live_network_required_future is true.")
    if value.get("execution_class") == "approval_gated_live_probe_future" and value.get("operator_required") is not True:
        errors.append("probe_kind.operator_required must be true for approval_gated_live_probe_future.")


def _validate_source_policy(value: Mapping[str, Any], errors: list[str], probe_kind: Mapping[str, Any]) -> None:
    if value.get("source_policy_kind") not in ALLOWED_SOURCE_POLICIES:
        errors.append("source_policy.source_policy_kind is invalid.")
    for key in ("allowed_source_ids", "allowed_source_families", "prohibited_source_families", "notes"):
        if not isinstance(value.get(key), list):
            errors.append(f"source_policy.{key} must be a list.")
    if value.get("live_probe_enabled") is not False:
        errors.append("source_policy.live_probe_enabled must be false for P63 examples.")
    for key in ("source_terms_review_required", "rights_review_required"):
        if not isinstance(value.get(key), bool):
            errors.append(f"source_policy.{key} must be boolean.")
    if probe_kind.get("live_network_required_future") is True:
        if value.get("source_policy_kind") != "live_metadata_probe_after_approval":
            errors.append("live-network future probes must use live_metadata_probe_after_approval source policy.")
        if value.get("source_terms_review_required") is not True:
            errors.append("live-network future probes require source terms review.")


def _validate_input_refs(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("query_observation_refs", "search_result_cache_refs", "search_miss_ledger_refs", "search_need_refs"):
        refs = value.get(key)
        if not isinstance(refs, list):
            errors.append(f"input_refs.{key} must be a list.")
            continue
        for index, ref in enumerate(refs):
            _validate_input_ref(ref, errors, f"input_refs.{key}[{index}]")
    search_need_refs = value.get("search_need_refs")
    if not isinstance(search_need_refs, list) or not search_need_refs:
        errors.append("input_refs.search_need_refs must include at least one synthetic or future search need ref.")
    for optional in ("manual_observation_refs", "source_pack_refs", "evidence_pack_refs"):
        if optional in value and not isinstance(value.get(optional), list):
            errors.append(f"input_refs.{optional} must be a list.")


def _validate_input_ref(ref: Any, errors: list[str], label: str) -> None:
    if not isinstance(ref, Mapping):
        errors.append(f"{label} must be an object.")
        return
    for key in ("ref_id", "ref_kind", "status", "privacy_classification", "limitations"):
        if key not in ref:
            errors.append(f"{label}.{key} is missing.")
    if ref.get("ref_kind") not in ALLOWED_REF_KINDS:
        errors.append(f"{label}.ref_kind is invalid.")
    if ref.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSIFICATIONS:
        errors.append(f"{label}.privacy_classification is invalid.")
    if not isinstance(ref.get("limitations"), list):
        errors.append(f"{label}.limitations must be a list.")


def _validate_target(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("target_kind") not in ALLOWED_TARGET_KINDS:
        errors.append("target.target_kind is invalid.")
    if not isinstance(value.get("limitations"), list):
        errors.append("target.limitations must be a list.")
    if value.get("target_kind") != "unknown" and not any(value.get(key) for key in ("product_name", "source_family", "source_id", "identifier")):
        errors.append("target must include a public-safe product, source, or identifier hint for concrete examples.")


def _validate_priority(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("priority_class") not in {"example_only", "low", "medium", "high", "unknown"}:
        errors.append("priority.priority_class is invalid.")
    if value.get("priority_basis") not in {"single_need_example", "repeated_need_future", "high_gap_future", "manual_priority_future", "source_policy_priority_future", "safety_priority_future", "unknown"}:
        errors.append("priority.priority_basis is invalid.")
    if value.get("demand_count_claimed") is not False:
        errors.append("priority.demand_count_claimed must be false for P63 examples.")
    if not isinstance(value.get("notes"), list):
        errors.append("priority.notes must be a list.")


def _validate_scheduling(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("schedule_status") not in ALLOWED_SCHEDULE_STATUSES:
        errors.append("scheduling.schedule_status is invalid.")
    if value.get("earliest_run_policy") not in ALLOWED_EARLIEST_RUN_POLICIES:
        errors.append("scheduling.earliest_run_policy is invalid.")
    if value.get("retry_policy") not in {"none_v0", "future_bounded_retry"}:
        errors.append("scheduling.retry_policy is invalid.")
    if value.get("timeout_policy") not in {"none_v0", "future_bounded_timeout"}:
        errors.append("scheduling.timeout_policy is invalid.")
    if not isinstance(value.get("notes"), list):
        errors.append("scheduling.notes must be a list.")


def _validate_expected_outputs(value: Mapping[str, Any], errors: list[str]) -> None:
    kinds = value.get("expected_output_kinds")
    if not isinstance(kinds, list) or not kinds:
        errors.append("expected_outputs.expected_output_kinds must be a non-empty list.")
    else:
        invalid = sorted(str(kind) for kind in kinds if kind not in ALLOWED_OUTPUT_KINDS)
        if invalid:
            errors.append(f"expected_outputs.expected_output_kinds contains invalid values: {', '.join(invalid)}")
    if value.get("output_destination_policy") not in ALLOWED_OUTPUT_POLICIES:
        errors.append("expected_outputs.output_destination_policy is invalid.")
    for key in ("public_output_allowed_after_review", "requires_validation", "requires_review"):
        if not isinstance(value.get(key), bool):
            errors.append(f"expected_outputs.{key} must be boolean.")
    if value.get("output_destination_policy") != "no_output_v0":
        if value.get("requires_validation") is not True or value.get("requires_review") is not True:
            errors.append("future output destinations require validation and review.")
    if not isinstance(value.get("notes"), list):
        errors.append("expected_outputs.notes must be a list.")


def _validate_safety(value: Mapping[str, Any], errors: list[str], probe_kind: Mapping[str, Any]) -> None:
    for key in sorted(SAFETY_TRUE_FIELDS):
        if value.get(key) is not True:
            errors.append(f"safety_requirements.{key} must be true.")
    for key in ("rate_limit_required_future", "retry_backoff_required_future", "circuit_breaker_required_future", "source_terms_review_required", "robots_or_source_policy_review_required", "cache_required_before_public_use"):
        if not isinstance(value.get(key), bool):
            errors.append(f"safety_requirements.{key} must be boolean.")
    if probe_kind.get("live_network_required_future") is True:
        for key in ("rate_limit_required_future", "retry_backoff_required_future", "circuit_breaker_required_future", "source_terms_review_required", "robots_or_source_policy_review_required", "cache_required_before_public_use"):
            if value.get(key) is not True:
                errors.append(f"live-network future probes require safety_requirements.{key} true.")
        if not isinstance(value.get("max_runtime_ms_future"), int):
            errors.append("live-network future probes require max_runtime_ms_future.")


def _validate_privacy(value: Mapping[str, Any], errors: list[str], payload: Mapping[str, Any]) -> None:
    if value.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSIFICATIONS:
        errors.append("privacy.privacy_classification is invalid.")
    for key in sorted(PRIVACY_FALSE_FIELDS):
        if value.get(key) is not False and payload.get("status") != "rejected_by_privacy_filter":
            errors.append(f"privacy.{key} must be false for public-safe examples.")
    sensitive_flags = [value.get(key) for key in PRIVACY_FALSE_FIELDS]
    if any(sensitive_flags) and value.get("publishable") is True:
        errors.append("privacy.publishable must be false when sensitive flags are true.")
    if any(sensitive_flags) and value.get("public_aggregate_allowed") is True and payload.get("status") != "redacted":
        errors.append("privacy.public_aggregate_allowed requires redacted status when sensitive flags are true.")


def _validate_retention(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("raw_query_retention") != "none":
        errors.append("retention_policy.raw_query_retention must be none.")
    if value.get("probe_item_retention") not in {"example_only", "until_completed_future", "until_cancelled_future", "review_required_future"}:
        errors.append("retention_policy.probe_item_retention is invalid.")
    if not isinstance(value.get("notes"), list):
        errors.append("retention_policy.notes must be a list.")


def _validate_aggregation(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("raw_query_aggregation_allowed") is not False:
        errors.append("aggregation_policy.raw_query_aggregation_allowed must be false.")
    if value.get("private_identifier_aggregation_allowed") is not False:
        errors.append("aggregation_policy.private_identifier_aggregation_allowed must be false.")
    if not isinstance(value.get("aggregate_fields_allowed"), list):
        errors.append("aggregation_policy.aggregate_fields_allowed must be a list.")


def _validate_execution_guarantees(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(HARD_EXECUTION_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_execution_guarantees.{key} must be false.")


def _validate_mutation_guarantees(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(HARD_MUTATION_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_mutation_guarantees.{key} must be false.")


def _require_mapping(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object.")
        return {}
    return value


def _validate_no_sensitive_payload(payload: Mapping[str, Any], errors: list[str]) -> None:
    text = "\n".join(_iter_string_values(payload))
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append(f"payload contains prohibited data pattern: {label}.")


def _iter_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for child in value.values():
            yield from _iter_string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_string_values(child)


def _validate_checksums(root: Path, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.is_file():
        errors.append("CHECKSUMS.SHA256: missing checksums file.")
        return
    expected: dict[str, str] = {}
    for line_number, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) != 2:
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: expected '<sha256>  <file>'.")
            continue
        digest, filename = parts
        if not re.fullmatch(r"[a-f0-9]{64}", digest):
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: invalid sha256 digest.")
            continue
        if "/" in filename or "\\" in filename:
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: filename must be local to example root.")
            continue
        expected[filename] = digest
    for filename, digest in sorted(expected.items()):
        file_path = root / filename
        if not file_path.is_file():
            errors.append(f"CHECKSUMS.SHA256 references missing file: {filename}.")
            continue
        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"CHECKSUMS.SHA256 mismatch for {filename}.")
    if ITEM_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include PROBE_QUEUE_ITEM.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("probe queue item file is missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append("top-level JSON must be an object.")
        return {}
    return payload


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Probe Queue Item validation",
        f"status: {report['status']}",
    ]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("probe_item_id"):
        lines.append(f"probe_item_id: {report['probe_item_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--item", type=Path, help="Validate one PROBE_QUEUE_ITEM.json file.")
    parser.add_argument("--item-root", type=Path, help="Validate one example root containing PROBE_QUEUE_ITEM.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed probe queue examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.item, args.item_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --item, --item-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.item_root:
        report = validate_probe_queue_root(args.item_root, strict=args.strict)
    elif args.item:
        report = validate_probe_queue_file(args.item, strict=args.strict)
    else:  # pragma: no cover - argparse-selected guard
        report = {"status": "invalid", "errors": ["no selection"], "warnings": []}

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
