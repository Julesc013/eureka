#!/usr/bin/env python3
"""Validate Eureka Source Sync Worker Job v0 examples.

This validator is stdlib-only and local. It validates contract/example
artifacts only; it performs no network calls, telemetry, persistence,
credentials use, source sync execution, live source calls, source-cache
mutation, evidence-ledger mutation, candidate-index mutation, public-index
mutation, local-index mutation, master-index mutation, or probe execution.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "source_sync"
JOB_FILE_NAME = "SOURCE_SYNC_WORKER_JOB.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "source_sync_job_id",
    "source_sync_job_kind",
    "status",
    "created_by_tool",
    "job_identity",
    "job_kind",
    "source_target",
    "source_policy",
    "approval_gates",
    "scheduling",
    "retry_timeout_rate_limit",
    "user_agent_and_terms",
    "input_refs",
    "expected_outputs",
    "safety_requirements",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_execution_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "approval_required",
    "operator_required",
    "blocked_by_policy",
    "disabled",
    "scheduled_future",
    "running_future",
    "completed_future",
    "failed_future",
    "cancelled_future",
}
ALLOWED_JOB_KINDS = {
    "manual_source_review",
    "source_metadata_sync",
    "source_identifier_lookup",
    "source_availability_check",
    "source_cache_refresh",
    "source_record_normalization",
    "connector_health_check",
    "rate_limit_policy_check",
    "deep_extraction_request",
    "package_metadata_sync",
    "repository_release_sync",
    "wayback_availability_sync",
    "internet_archive_metadata_sync",
    "software_heritage_metadata_sync",
    "wikidata_identity_sync",
    "unknown",
}
ALLOWED_EXECUTION_CLASSES = {
    "human_operated_future",
    "scheduled_worker_future",
    "approval_gated_live_sync_future",
    "local_offline_normalization_future",
    "no_execution_v0",
}
ALLOWED_SOURCE_FAMILIES = {
    "internet_archive",
    "wayback",
    "github_releases",
    "pypi",
    "npm",
    "software_heritage",
    "wikidata_open_library",
    "sourceforge",
    "manual_source_pack",
    "local_fixture",
    "recorded_fixture",
    "unknown",
}
ALLOWED_SOURCE_STATUSES = {"active_fixture", "active_recorded_fixture", "placeholder", "future", "disabled", "approval_required", "unknown"}
ALLOWED_TARGET_SCOPES = {"single_identifier", "bounded_query", "bounded_source_family", "fixture_only", "manual_review", "unknown"}
ALLOWED_SOURCE_POLICY_KINDS = {
    "no_source_call",
    "manual_only",
    "fixture_only",
    "recorded_fixture_only",
    "source_cache_only_future",
    "live_metadata_sync_after_approval",
    "local_offline_normalization_after_approval",
    "unknown",
}
ALLOWED_GATE_TYPES = {
    "source_policy_review",
    "rights_review",
    "risk_review",
    "operator_approval",
    "human_approval",
    "rate_limit_review",
    "user_agent_review",
    "circuit_breaker_review",
    "cache_policy_review",
    "evidence_output_review",
    "connector_contract_review",
    "credential_policy_review",
}
LIVE_REQUIRED_GATES = {
    "source_policy_review",
    "rate_limit_review",
    "user_agent_review",
    "circuit_breaker_review",
    "cache_policy_review",
}
ALLOWED_GATE_STATUSES = {"passed", "failed", "review_required", "future_required", "not_applicable"}
ALLOWED_SCHEDULE_STATUSES = {"not_scheduled_v0", "future_manual", "future_scheduled_worker", "future_after_approval", "blocked"}
ALLOWED_EARLIEST_RUN = {"not_applicable_v0", "after_human_approval_future", "after_operator_setup_future", "after_source_policy_review_future"}
ALLOWED_RECURRENCE = {"none_v0", "future_bounded_schedule"}
ALLOWED_RETRY = {"none_v0", "future_bounded_retry"}
ALLOWED_TIMEOUT = {"none_v0", "future_bounded_timeout"}
ALLOWED_RATE_LIMIT = {"none_v0", "source_policy_required_future", "future_bounded_rate_limit"}
ALLOWED_CIRCUIT = {"none_v0", "future_required"}
ALLOWED_OUTPUT_KINDS = {
    "source_cache_record_future",
    "evidence_ledger_record_future",
    "candidate_index_record_future",
    "connector_health_record_future",
    "source_coverage_update_future",
    "absence_evidence_future",
    "manual_report_future",
    "no_output_v0",
}
ALLOWED_OUTPUT_DESTINATIONS = {
    "no_output_v0",
    "source_cache_future",
    "evidence_ledger_future",
    "candidate_index_future",
    "connector_health_future",
    "manual_report_future",
}
ALLOWED_PRIVACY_CLASSES = {"public_safe_example", "public_safe_aggregate", "local_private", "rejected_sensitive", "redacted", "unknown"}
ALLOWED_RIGHTS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
ALLOWED_RISK = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}
NO_EXECUTION_FALSE_FIELDS = {
    "worker_runtime_implemented",
    "job_executed",
    "live_source_called",
    "external_calls_performed",
    "telemetry_exported",
    "credentials_used",
}
NO_MUTATION_FALSE_FIELDS = {
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "probe_queue_mutated",
    "search_need_mutated",
    "result_cache_mutated",
}
SAFETY_TRUE_FIELDS = {
    "no_public_query_fanout",
    "no_arbitrary_url_fetch",
    "no_downloads",
    "no_installs",
    "no_execution",
    "no_uploads",
    "no_private_paths",
    "no_credentials_in_examples",
    "no_raw_payload_dump",
    "source_cache_required_before_public_use",
    "evidence_attribution_required",
    "bounded_result_count_required_future",
    "timeout_required_future",
    "rate_limit_required_future",
    "circuit_breaker_required_future",
    "rights_review_required",
    "risk_review_required",
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


def validate_job_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_job(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_sync_worker_job_validator_v0",
        "job": _repo_relative(path),
        "source_sync_job_id": payload.get("source_sync_job_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_job_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    path = root / JOB_FILE_NAME
    if not path.is_file():
        return {
            "status": "invalid",
            "created_by": "source_sync_worker_job_validator_v0",
            "job_root": _repo_relative(root),
            "source_sync_job_id": None,
            "errors": [f"{JOB_FILE_NAME}: missing job file."],
            "warnings": [],
        }
    report = validate_job_file(path, strict=strict, example_root=root)
    report["job_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir()) if EXAMPLES_ROOT.is_dir() else []
    if not roots:
        errors.append("examples/source_sync: no example roots found.")
    for root in roots:
        report = validate_job_root(root, strict=strict)
        results.append(report)
        errors.extend(f"{report.get('job_root')}: {error}" for error in report.get("errors", []))
        warnings.extend(f"{report.get('job_root')}: {warning}" for warning in report.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_sync_worker_job_validator_v0",
        "example_count": len(roots),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_job(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - payload.keys())
    if missing:
        errors.append(f"missing required top-level fields: {', '.join(missing)}")
    if payload.get("source_sync_job_kind") != "source_sync_worker_job":
        errors.append("source_sync_job_kind must be source_sync_worker_job.")
    _enum(payload.get("status"), ALLOWED_STATUSES, "status", errors)
    if strict and payload.get("status") in {"running_future", "completed_future"}:
        errors.append("committed v0 examples must not imply running or completed sync.")

    _validate_job_identity(payload.get("job_identity"), errors)
    job_kind = _require_mapping(payload.get("job_kind"), "job_kind", errors)
    live_network = False
    if job_kind:
        _enum(job_kind.get("kind"), ALLOWED_JOB_KINDS, "job_kind.kind", errors)
        _enum(job_kind.get("execution_class"), ALLOWED_EXECUTION_CLASSES, "job_kind.execution_class", errors)
        live_network = job_kind.get("live_network_required_future") is True
        if live_network and job_kind.get("approval_required") is not True:
            errors.append("job_kind.approval_required must be true when live_network_required_future is true.")
        if job_kind.get("execution_class") == "approval_gated_live_sync_future" and not live_network:
            errors.append("approval_gated_live_sync_future jobs must set live_network_required_future true.")

    target = _require_mapping(payload.get("source_target"), "source_target", errors)
    if target:
        _enum(target.get("source_family"), ALLOWED_SOURCE_FAMILIES, "source_target.source_family", errors)
        _enum(target.get("source_status"), ALLOWED_SOURCE_STATUSES, "source_target.source_status", errors)
        _enum(target.get("target_scope"), ALLOWED_TARGET_SCOPES, "source_target.target_scope", errors)
        if target.get("arbitrary_url_allowed") is not False:
            errors.append("source_target.arbitrary_url_allowed must be false.")

    source_policy = _require_mapping(payload.get("source_policy"), "source_policy", errors)
    if source_policy:
        _enum(source_policy.get("source_policy_kind"), ALLOWED_SOURCE_POLICY_KINDS, "source_policy.source_policy_kind", errors)
        if source_policy.get("live_source_enabled_now") is not False:
            errors.append("source_policy.live_source_enabled_now must be false.")
        for field in (
            "source_terms_review_required",
            "robots_or_source_policy_review_required",
            "rate_limit_required_future",
            "retry_backoff_required_future",
            "circuit_breaker_required_future",
            "cache_required_before_public_use",
            "evidence_attribution_required",
        ):
            if source_policy.get(field) is not True:
                errors.append(f"source_policy.{field} must be true.")

    _validate_gates(payload.get("approval_gates"), errors, live_network=live_network)
    _validate_scheduling(payload.get("scheduling"), errors)
    _validate_retry(payload.get("retry_timeout_rate_limit"), errors)
    _validate_user_agent(payload.get("user_agent_and_terms"), errors, live_network=live_network)
    _validate_input_refs(payload.get("input_refs"), errors)
    _validate_outputs(payload.get("expected_outputs"), errors)
    _validate_safety(payload.get("safety_requirements"), errors)
    _validate_privacy(payload.get("privacy"), errors)
    _validate_rights(payload.get("rights_and_risk"), errors)
    _validate_false_fields(payload.get("no_execution_guarantees"), NO_EXECUTION_FALSE_FIELDS, "no_execution_guarantees", errors)
    _validate_false_fields(payload.get("no_mutation_guarantees"), NO_MUTATION_FALSE_FIELDS, "no_mutation_guarantees", errors)
    if strict and payload.get("expected_outputs", {}).get("output_destination_policy") == "candidate_index_future":
        warnings.append("candidate_index_future output is future-only and must remain review-gated.")


def _validate_job_identity(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "job_identity", errors)
    if not mapping:
        return
    fingerprint = _require_mapping(mapping.get("job_fingerprint"), "job_identity.job_fingerprint", errors)
    if fingerprint:
        if fingerprint.get("algorithm") != "sha256":
            errors.append("job_identity.job_fingerprint.algorithm must be sha256.")
        if fingerprint.get("reversible") is not False:
            errors.append("job_identity.job_fingerprint.reversible must be false.")
        if not fingerprint.get("value"):
            errors.append("job_identity.job_fingerprint.value is required.")
    if not mapping.get("canonical_job_label"):
        errors.append("job_identity.canonical_job_label is required.")


def _validate_gates(value: Any, errors: list[str], *, live_network: bool) -> None:
    if not isinstance(value, list) or not value:
        errors.append("approval_gates must be a non-empty list.")
        return
    required_present: set[str] = set()
    for idx, item in enumerate(value):
        prefix = f"approval_gates[{idx}]"
        mapping = _require_mapping(item, prefix, errors)
        if not mapping:
            continue
        gate_type = mapping.get("gate_type")
        _enum(gate_type, ALLOWED_GATE_TYPES, f"{prefix}.gate_type", errors)
        _enum(mapping.get("status"), ALLOWED_GATE_STATUSES, f"{prefix}.status", errors)
        if mapping.get("required") is True:
            required_present.add(gate_type)
            if mapping.get("status") not in {"review_required", "future_required", "passed"}:
                errors.append(f"{prefix}.status must require or pass review when gate is required.")
    if live_network:
        missing = sorted(LIVE_REQUIRED_GATES - required_present)
        if missing:
            errors.append(f"future live/network source jobs require approval gates: {', '.join(missing)}")


def _validate_scheduling(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "scheduling", errors)
    if not mapping:
        return
    _enum(mapping.get("schedule_status"), ALLOWED_SCHEDULE_STATUSES, "scheduling.schedule_status", errors)
    _enum(mapping.get("earliest_run_policy"), ALLOWED_EARLIEST_RUN, "scheduling.earliest_run_policy", errors)
    _enum(mapping.get("recurrence_policy"), ALLOWED_RECURRENCE, "scheduling.recurrence_policy", errors)
    if mapping.get("schedule_status") != "not_scheduled_v0":
        errors.append("P69 examples must not create a real schedule.")


def _validate_retry(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "retry_timeout_rate_limit", errors)
    if not mapping:
        return
    _enum(mapping.get("retry_policy"), ALLOWED_RETRY, "retry_timeout_rate_limit.retry_policy", errors)
    _enum(mapping.get("timeout_policy"), ALLOWED_TIMEOUT, "retry_timeout_rate_limit.timeout_policy", errors)
    _enum(mapping.get("rate_limit_policy"), ALLOWED_RATE_LIMIT, "retry_timeout_rate_limit.rate_limit_policy", errors)
    _enum(mapping.get("circuit_breaker_policy"), ALLOWED_CIRCUIT, "retry_timeout_rate_limit.circuit_breaker_policy", errors)


def _validate_user_agent(value: Any, errors: list[str], *, live_network: bool) -> None:
    mapping = _require_mapping(value, "user_agent_and_terms", errors)
    if not mapping:
        return
    if mapping.get("user_agent_value_current") is not None:
        errors.append("user_agent_and_terms.user_agent_value_current must be null in P69 examples.")
    if live_network:
        for field in (
            "user_agent_required_future",
            "descriptive_user_agent_required_future",
            "contact_url_or_email_required_future",
            "source_terms_review_required",
            "robots_or_source_policy_review_required",
            "retry_after_respect_required_future",
        ):
            if mapping.get(field) is not True:
                errors.append(f"user_agent_and_terms.{field} must be true for future live sync jobs.")


def _validate_input_refs(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "input_refs", errors)
    if not mapping:
        return
    for field in (
        "query_observation_refs",
        "search_result_cache_refs",
        "search_miss_ledger_refs",
        "search_need_refs",
        "probe_queue_refs",
        "demand_dashboard_refs",
        "source_inventory_refs",
    ):
        if not isinstance(mapping.get(field), list):
            errors.append(f"input_refs.{field} must be a list.")


def _validate_outputs(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "expected_outputs", errors)
    if not mapping:
        return
    kinds = mapping.get("expected_output_kinds")
    if not isinstance(kinds, list) or not kinds:
        errors.append("expected_outputs.expected_output_kinds must be a non-empty list.")
    else:
        for kind in kinds:
            _enum(kind, ALLOWED_OUTPUT_KINDS, "expected_outputs.expected_output_kinds[]", errors)
    _enum(mapping.get("output_destination_policy"), ALLOWED_OUTPUT_DESTINATIONS, "expected_outputs.output_destination_policy", errors)
    if mapping.get("output_destination_policy") != "no_output_v0":
        if mapping.get("requires_validation") is not True:
            errors.append("future output destinations require expected_outputs.requires_validation true.")
        if mapping.get("requires_review") is not True:
            errors.append("future output destinations require expected_outputs.requires_review true.")


def _validate_safety(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "safety_requirements", errors)
    if not mapping:
        return
    for field in SAFETY_TRUE_FIELDS:
        if mapping.get(field) is not True:
            errors.append(f"safety_requirements.{field} must be true.")


def _validate_privacy(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "privacy", errors)
    if not mapping:
        return
    _enum(mapping.get("privacy_classification"), ALLOWED_PRIVACY_CLASSES, "privacy.privacy_classification", errors)
    for field in PRIVACY_FALSE_FIELDS:
        if mapping.get(field) is not False:
            errors.append(f"privacy.{field} must be false in public-safe examples.")
    if mapping.get("publishable") is not True:
        errors.append("privacy.publishable must be true for committed public-safe examples.")


def _validate_rights(value: Any, errors: list[str]) -> None:
    mapping = _require_mapping(value, "rights_and_risk", errors)
    if not mapping:
        return
    _enum(mapping.get("rights_classification"), ALLOWED_RIGHTS, "rights_and_risk.rights_classification", errors)
    _enum(mapping.get("risk_classification"), ALLOWED_RISK, "rights_and_risk.risk_classification", errors)
    for field in ("rights_clearance_claimed", "malware_safety_claimed", "downloads_enabled", "installs_enabled", "execution_enabled"):
        if mapping.get(field) is not False:
            errors.append(f"rights_and_risk.{field} must be false.")


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
            errors.append(f"source sync job contains prohibited private/sensitive data pattern: {label}")


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
    parser = argparse.ArgumentParser(description="Validate Source Sync Worker Job v0 examples.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--job", type=Path, help="Path to a SOURCE_SYNC_WORKER_JOB.json file.")
    group.add_argument("--job-root", type=Path, help="Path to an example root containing SOURCE_SYNC_WORKER_JOB.json.")
    group.add_argument("--all-examples", action="store_true", help="Validate all committed source sync examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply committed-example strictness.")
    args = parser.parse_args(argv)
    if args.job:
        report = validate_job_file(args.job, strict=args.strict)
    elif args.job_root:
        report = validate_job_root(args.job_root, strict=args.strict)
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
