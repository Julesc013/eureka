#!/usr/bin/env python3
"""Validate Eureka Search Need Record v0 examples.

The validator is structural and stdlib-only. It validates P62 search need
examples without using telemetry, persistence, network calls, live probes,
need-store writes, probe queue mutation, candidate-index mutation, result cache
mutation, miss ledger mutation, local-index mutation, or master-index writes.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "search_needs"
RECORD_FILE_NAME = "SEARCH_NEED_RECORD.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "search_need_id",
    "search_need_kind",
    "status",
    "created_by_tool",
    "need_identity",
    "target_object",
    "originating_inputs",
    "aggregate_summary",
    "source_and_capability_gaps",
    "checked_scope",
    "not_checked_scope",
    "evidence_and_result_context",
    "suggested_next_steps",
    "priority",
    "privacy",
    "retention_policy",
    "aggregation_policy",
    "limitations",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "unresolved",
    "local_private",
    "public_aggregate_candidate",
    "rejected_by_privacy_filter",
    "merged_future",
    "superseded_future",
    "resolved_future",
}
ALLOWED_OBJECT_KINDS = {
    "software",
    "software_version",
    "driver",
    "manual_or_documentation",
    "source_code_release",
    "package_metadata",
    "web_capture",
    "article_or_scan_segment",
    "file_inside_container",
    "compatibility_evidence",
    "source_identity",
    "unknown",
}
ALLOWED_DESIRED_ACTIONS = {
    "inspect",
    "compare",
    "cite",
    "preserve",
    "locate_download_disabled",
    "install_intent_detected_but_disabled",
    "emulate_intent_detected_but_disabled",
    "unknown",
}
ALLOWED_GAP_TYPES = {
    "source_coverage_gap",
    "capability_gap",
    "compatibility_evidence_gap",
    "member_access_gap",
    "representation_gap",
    "query_interpretation_gap",
    "live_probe_disabled",
    "external_baseline_pending",
    "deep_extraction_missing",
    "OCR_missing",
    "source_cache_missing",
    "unknown",
}
ALLOWED_RESOLUTIONS = {
    "add_source_pack",
    "add_evidence_pack",
    "run_manual_observation",
    "enable_live_probe_after_approval",
    "deep_extract_container",
    "OCR_scan",
    "improve_query_parser",
    "add_connector_after_approval",
    "unknown",
}
ALLOWED_NOT_CHECKED_REASONS = {"not_implemented", "disabled_by_policy", "approval_gated", "operator_gated", "unknown"}
ALLOWED_PRIVACY_CLASSIFICATIONS = {"public_safe_aggregate", "local_private", "rejected_sensitive", "redacted", "unknown"}
ALLOWED_STEP_TYPES = {
    "run_manual_observation",
    "create_probe_job_future",
    "add_source_pack_future",
    "add_evidence_pack_future",
    "add_index_pack_future",
    "request_contribution_future",
    "enable_live_probe_after_approval",
    "add_source_connector_after_approval",
    "deep_extract_container_future",
    "OCR_scan_future",
    "improve_query_parser_future",
    "review_candidate_identity_future",
    "no_action",
}
HARD_FALSE_FIELDS = {
    "master_index_mutated",
    "local_index_mutated",
    "candidate_index_mutated",
    "probe_enqueued",
    "result_cache_mutated",
    "miss_ledger_mutated",
    "query_observation_mutated",
    "telemetry_exported",
    "external_calls_performed",
    "public_need_runtime_created",
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
    ("windows_absolute_path", re.compile(r"\b[a-zA-Z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d[\d .-]{7,}\d)\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\b", re.IGNORECASE)),
)


def validate_search_need_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_record(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "search_need_record_validator_v0",
        "record": _repo_relative(path),
        "search_need_id": payload.get("search_need_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_search_need_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    record_path = root / RECORD_FILE_NAME
    if not record_path.is_file():
        return {
            "status": "invalid",
            "created_by": "search_need_record_validator_v0",
            "record_root": _repo_relative(root),
            "search_need_id": None,
            "errors": [f"{RECORD_FILE_NAME}: missing search need record file."],
            "warnings": [],
        }
    report = validate_search_need_file(record_path, strict=strict, example_root=root)
    report["record_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/search_needs: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/search_needs: no example roots found.")
        for root in roots:
            result = validate_search_need_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('record_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('record_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "search_need_record_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_record(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("search_need_kind") != "search_need_record":
        errors.append("search_need_kind must be search_need_record.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not an allowed search need status.")

    _validate_need_identity(_require_mapping(payload, "need_identity", errors), errors)
    _validate_target_object(_require_mapping(payload, "target_object", errors), errors)
    _validate_originating_inputs(_require_mapping(payload, "originating_inputs", errors), errors)
    _validate_aggregate_summary(_require_mapping(payload, "aggregate_summary", errors), errors)
    _validate_gaps(payload.get("source_and_capability_gaps"), errors)
    _validate_checked_scope(_require_mapping(payload, "checked_scope", errors), errors)
    _validate_not_checked_scope(_require_mapping(payload, "not_checked_scope", errors), errors)
    _validate_evidence_context(_require_mapping(payload, "evidence_and_result_context", errors), errors)
    _validate_suggested_next_steps(payload.get("suggested_next_steps"), errors)
    _validate_priority(_require_mapping(payload, "priority", errors), errors)
    _validate_privacy(_require_mapping(payload, "privacy", errors), errors, payload)
    _validate_retention(_require_mapping(payload, "retention_policy", errors), errors)
    _validate_aggregation(_require_mapping(payload, "aggregation_policy", errors), errors)
    _validate_mutation(_require_mapping(payload, "no_mutation_guarantees", errors), errors)
    _validate_no_absence_overclaim(payload, errors)

    if strict and payload.get("status") == "public_aggregate_candidate":
        warnings.append("public aggregate candidate status requires future privacy and poisoning review before publication.")


def _validate_need_identity(value: Mapping[str, Any], errors: list[str]) -> None:
    fingerprint = _require_mapping(value, "need_fingerprint", errors)
    if fingerprint:
        if fingerprint.get("algorithm") != "sha256":
            errors.append("need_identity.need_fingerprint.algorithm must be sha256.")
        if not isinstance(fingerprint.get("value"), str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint["value"]):
            errors.append("need_identity.need_fingerprint.value must be a lowercase sha256 hex string.")
        if fingerprint.get("reversible") is not False:
            errors.append("need_identity.need_fingerprint.reversible must be false.")
        if fingerprint.get("salt_policy") not in {"unsalted_public_aggregate", "deployment_secret_salted_future", "local_private_salted_future"}:
            errors.append("need_identity.need_fingerprint.salt_policy is invalid.")
    if not isinstance(value.get("canonical_need_label"), str) or not value.get("canonical_need_label"):
        errors.append("need_identity.canonical_need_label must be a non-empty string.")
    for key in ("normalized_need_terms", "disambiguation_terms", "equivalence_keys", "alias_terms"):
        if not isinstance(value.get(key), list):
            errors.append(f"need_identity.{key} must be a list.")


def _validate_target_object(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("object_kind") not in ALLOWED_OBJECT_KINDS:
        errors.append("target_object.object_kind is invalid.")
    if value.get("desired_action") not in ALLOWED_DESIRED_ACTIONS:
        errors.append("target_object.desired_action is invalid.")
    if not value.get("product_name") and value.get("object_kind") not in {"unknown", "source_identity"}:
        errors.append("target_object.product_name must be present for concrete example needs.")


def _validate_originating_inputs(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("query_observation_refs", "search_miss_ledger_refs", "search_result_cache_refs"):
        refs = value.get(key)
        if not isinstance(refs, list):
            errors.append(f"originating_inputs.{key} must be a list.")
            continue
        for index, ref in enumerate(refs):
            _validate_input_ref(ref, errors, f"originating_inputs.{key}[{index}]")
    miss_refs = value.get("search_miss_ledger_refs")
    if not isinstance(miss_refs, list) or not miss_refs:
        errors.append("originating_inputs.search_miss_ledger_refs must include at least one synthetic or future miss ref.")
    for optional in ("manual_observation_refs", "source_pack_refs", "evidence_pack_refs"):
        if optional in value and not isinstance(value.get(optional), list):
            errors.append(f"originating_inputs.{optional} must be a list.")


def _validate_input_ref(ref: Any, errors: list[str], label: str) -> None:
    if not isinstance(ref, Mapping):
        errors.append(f"{label} must be an object.")
        return
    for key in ("ref_id", "ref_kind", "status", "privacy_classification", "limitations"):
        if key not in ref:
            errors.append(f"{label}.{key} is missing.")
    if ref.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSIFICATIONS:
        errors.append(f"{label}.privacy_classification is invalid.")
    if not isinstance(ref.get("limitations"), list):
        errors.append(f"{label}.limitations must be a list.")


def _validate_aggregate_summary(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("occurrence_count", "distinct_query_fingerprint_count", "distinct_normalized_need_count"):
        if not isinstance(value.get(key), int) or value.get(key, -1) < 0:
            errors.append(f"aggregate_summary.{key} must be a non-negative integer.")
    if value.get("first_seen_policy") not in {"not_tracked_in_v0_example", "future_local_private", "future_public_aggregate"}:
        errors.append("aggregate_summary.first_seen_policy is invalid.")
    if value.get("last_seen_policy") not in {"not_tracked_in_v0_example", "future_local_private", "future_public_aggregate"}:
        errors.append("aggregate_summary.last_seen_policy is invalid.")
    if value.get("confidence") not in {"low", "medium", "high"}:
        errors.append("aggregate_summary.confidence is invalid.")
    if value.get("demand_classification") not in {"single_example", "repeated_future", "high_demand_future", "unknown"}:
        errors.append("aggregate_summary.demand_classification is invalid.")
    if value.get("demand_classification") in {"repeated_future", "high_demand_future"} and value.get("occurrence_count") == 1:
        errors.append("single examples must not claim repeated or high demand.")
    for key in ("representative_intents", "representative_platforms", "representative_artifact_types"):
        if not isinstance(value.get(key), list):
            errors.append(f"aggregate_summary.{key} must be a list.")


def _validate_gaps(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("source_and_capability_gaps must be a non-empty list.")
        return
    for index, gap in enumerate(value):
        if not isinstance(gap, Mapping):
            errors.append(f"source_and_capability_gaps[{index}] must be an object.")
            continue
        if gap.get("gap_type") not in ALLOWED_GAP_TYPES:
            errors.append(f"source_and_capability_gaps[{index}].gap_type is invalid.")
        if not isinstance(gap.get("explanation"), str) or not gap.get("explanation"):
            errors.append(f"source_and_capability_gaps[{index}].explanation must be a non-empty string.")
        if not isinstance(gap.get("blocking"), bool):
            errors.append(f"source_and_capability_gaps[{index}].blocking must be boolean.")
        if gap.get("suggested_resolution_future") not in ALLOWED_RESOLUTIONS:
            errors.append(f"source_and_capability_gaps[{index}].suggested_resolution_future is invalid.")


def _validate_checked_scope(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("checked_indexes", "checked_sources", "checked_source_families", "checked_capabilities", "checked_index_snapshot_refs"):
        if not isinstance(value.get(key), list):
            errors.append(f"checked_scope.{key} must be a list.")
    if not value.get("checked_indexes"):
        errors.append("checked_scope.checked_indexes must not be empty.")
    if value.get("live_probes_attempted") is not False:
        errors.append("checked_scope.live_probes_attempted must be false.")
    if value.get("external_calls_performed") is not False:
        errors.append("checked_scope.external_calls_performed must be false.")


def _validate_not_checked_scope(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("sources_not_checked", "source_families_not_checked", "capabilities_not_checked", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"not_checked_scope.{key} must be a list.")
    reasons = value.get("reasons_not_checked")
    if not isinstance(reasons, list) or not reasons:
        errors.append("not_checked_scope.reasons_not_checked must be a non-empty list.")
    else:
        invalid = sorted(str(item) for item in reasons if item not in ALLOWED_NOT_CHECKED_REASONS)
        if invalid:
            errors.append(f"not_checked_scope.reasons_not_checked contains invalid values: {', '.join(invalid)}")


def _validate_evidence_context(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("best_known_result_refs", "near_miss_refs", "weak_hit_refs", "absence_refs", "relevant_source_refs", "relevant_evidence_refs", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"evidence_and_result_context.{key} must be a list.")
    if value.get("confidence") not in {"low", "medium", "high"}:
        errors.append("evidence_and_result_context.confidence is invalid.")


def _validate_suggested_next_steps(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("suggested_next_steps must be a list.")
        return
    for index, step in enumerate(value):
        if not isinstance(step, Mapping):
            errors.append(f"suggested_next_steps[{index}] must be an object.")
            continue
        if step.get("step_type") not in ALLOWED_STEP_TYPES:
            errors.append(f"suggested_next_steps[{index}].step_type is invalid.")
        if step.get("future_only") is not True:
            errors.append(f"suggested_next_steps[{index}].future_only must be true.")


def _validate_priority(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("priority_class") not in {"example_only", "low", "medium", "high", "unknown"}:
        errors.append("priority.priority_class is invalid.")
    if value.get("priority_basis") not in {"single_miss_example", "repeated_miss_future", "source_gap_future", "capability_gap_future", "manual_priority_future", "safety_priority_future", "unknown"}:
        errors.append("priority.priority_basis is invalid.")
    if value.get("demand_count_claimed") is not False:
        errors.append("priority.demand_count_claimed must be false for P62 examples.")
    if not isinstance(value.get("notes"), list):
        errors.append("priority.notes must be a list.")


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
    if value.get("need_record_retention") not in {"example_only", "until_resolved_future", "review_required_future"}:
        errors.append("retention_policy.need_record_retention is invalid.")


def _validate_aggregation(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("raw_query_aggregation_allowed") is not False:
        errors.append("aggregation_policy.raw_query_aggregation_allowed must be false.")
    if value.get("private_identifier_aggregation_allowed") is not False:
        errors.append("aggregation_policy.private_identifier_aggregation_allowed must be false.")
    if not isinstance(value.get("aggregate_fields_allowed"), list):
        errors.append("aggregation_policy.aggregate_fields_allowed must be a list.")


def _validate_mutation(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(HARD_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_mutation_guarantees.{key} must be false.")


def _validate_no_absence_overclaim(payload: Mapping[str, Any], errors: list[str]) -> None:
    text = "\n".join(_iter_string_values(payload)).casefold()
    forbidden = (
        "all sources were checked",
        "every source was checked",
        "does not exist globally",
        "global non-existence",
        "globally absent",
        "global absence proof",
    )
    if any(phrase in text for phrase in forbidden):
        errors.append("search need records must not claim absence outside checked scope.")
    if payload.get("global_absence_claimed") is True:
        errors.append("search need records must not claim absence outside checked scope.")


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
    if RECORD_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include SEARCH_NEED_RECORD.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("search need record file is missing.")
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
        "Search Need Record validation",
        f"status: {report['status']}",
    ]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("search_need_id"):
        lines.append(f"search_need_id: {report['search_need_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, help="Validate one SEARCH_NEED_RECORD.json file.")
    parser.add_argument("--record-root", type=Path, help="Validate one example root containing SEARCH_NEED_RECORD.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed search need examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.record, args.record_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --record, --record-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.record_root:
        report = validate_search_need_root(args.record_root, strict=args.strict)
    elif args.record:
        report = validate_search_need_file(args.record, strict=args.strict)
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
