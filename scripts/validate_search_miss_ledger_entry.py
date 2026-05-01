#!/usr/bin/env python3
"""Validate Eureka Search Miss Ledger Entry v0 examples.

The validator is structural and stdlib-only. It validates P61 miss ledger
examples without using telemetry, persistence, network calls, live probes,
ledger runtime writes, search need creation, probe queue mutation, result cache
mutation, candidate index mutation, or master-index writes.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "search_miss_ledger"
ENTRY_FILE_NAME = "SEARCH_MISS_LEDGER_ENTRY.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "miss_entry_id",
    "miss_entry_kind",
    "status",
    "created_by_tool",
    "query_ref",
    "miss_classification",
    "miss_causes",
    "checked_scope",
    "not_checked_scope",
    "near_misses",
    "weak_hits",
    "result_summary",
    "absence_summary",
    "suggested_next_steps",
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
    "local_private",
    "public_aggregate_candidate",
    "rejected_by_privacy_filter",
    "superseded",
    "resolved_future",
}
ALLOWED_MISS_TYPES = {
    "no_hits",
    "weak_hits",
    "near_miss_only",
    "blocked_by_policy",
    "source_coverage_gap",
    "capability_gap",
    "compatibility_evidence_gap",
    "member_access_gap",
    "representation_gap",
    "query_interpretation_gap",
    "live_probe_disabled",
    "external_baseline_pending",
    "unknown",
}
ALLOWED_CAUSE_TYPES = {
    "no_public_index_hit",
    "low_score_result",
    "result_shape_mismatch",
    "source_not_covered",
    "source_placeholder_only",
    "live_probe_disabled",
    "connector_missing",
    "deep_extraction_missing",
    "OCR_missing",
    "member_enumeration_missing",
    "compatibility_evidence_missing",
    "exact_version_missing",
    "platform_unsupported_or_unknown",
    "rights_or_access_unknown",
    "query_too_ambiguous",
    "query_blocked_by_policy",
    "external_baseline_pending",
    "unknown",
}
ALLOWED_CHECKED_INDEXES = {
    "public_index",
    "local_index_only",
    "candidate_index_future",
    "query_result_cache_future",
    "source_cache_future",
    "master_index_future",
}
ALLOWED_NOT_CHECKED_REASONS = {
    "not_implemented",
    "disabled_by_policy",
    "approval_gated",
    "operator_gated",
    "unknown",
}
ALLOWED_NEAR_MISS_REASONS = {
    "wrong_version",
    "wrong_platform",
    "wrong_artifact_type",
    "parent_bundle_only",
    "documentation_only",
    "weak_identity_match",
    "no_member_evidence",
    "no_compatibility_evidence",
    "source_unverified",
    "unknown",
}
ALLOWED_WEAKNESSES = {
    "low_score",
    "insufficient_evidence",
    "wrong_lane",
    "vague_identity",
    "missing_version",
    "missing_platform",
    "missing_member",
    "missing_actionability",
    "unknown",
}
ALLOWED_HIT_STATES = {"no_hits", "weak_hits", "near_misses", "blocked_by_policy"}
ALLOWED_ABSENCE_STATUSES = {"not_absent", "scoped_absence", "no_verified_result", "blocked_by_policy", "unknown"}
ALLOWED_PRIVACY_CLASSIFICATIONS = {"public_safe_aggregate", "local_private", "rejected_sensitive", "redacted", "unknown"}
ALLOWED_STEP_TYPES = {
    "create_search_need_future",
    "check_source_cache_future",
    "add_source_pack_future",
    "add_evidence_pack_future",
    "run_manual_observation",
    "enable_live_probe_after_approval",
    "deep_extract_container_future",
    "OCR_scan_future",
    "refine_query",
    "no_action",
}
HARD_FALSE_FIELDS = {
    "master_index_mutated",
    "local_index_mutated",
    "candidate_index_mutated",
    "search_need_created",
    "probe_enqueued",
    "result_cache_mutated",
    "query_observation_mutated",
    "telemetry_exported",
    "external_calls_performed",
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


def validate_miss_entry_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_entry(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "search_miss_ledger_entry_validator_v0",
        "entry": _repo_relative(path),
        "miss_entry_id": payload.get("miss_entry_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_miss_entry_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    entry_path = root / ENTRY_FILE_NAME
    if not entry_path.is_file():
        return {
            "status": "invalid",
            "created_by": "search_miss_ledger_entry_validator_v0",
            "entry_root": _repo_relative(root),
            "miss_entry_id": None,
            "errors": [f"{ENTRY_FILE_NAME}: missing miss entry file."],
            "warnings": [],
        }
    report = validate_miss_entry_file(entry_path, strict=strict, example_root=root)
    report["entry_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/search_miss_ledger: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/search_miss_ledger: no example roots found.")
        for root in roots:
            result = validate_miss_entry_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('entry_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('entry_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "search_miss_ledger_entry_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_entry(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("miss_entry_kind") != "search_miss_ledger_entry":
        errors.append("miss_entry_kind must be search_miss_ledger_entry.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not an allowed miss entry status.")

    query_ref = _require_mapping(payload, "query_ref", errors)
    if query_ref:
        if query_ref.get("raw_query_retained") is not False:
            errors.append("query_ref.raw_query_retained must be false.")
        if payload.get("status") != "local_private" and query_ref.get("raw_query_redacted") is not True:
            errors.append("query_ref.raw_query_redacted must be true for public-safe examples.")
        if query_ref.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSIFICATIONS:
            errors.append("query_ref.privacy_classification is invalid.")
        _validate_fingerprint(_require_mapping(query_ref, "query_fingerprint", errors), errors, "query_ref.query_fingerprint")
        normalized = _require_mapping(query_ref, "normalized_query", errors)
        if normalized:
            if not isinstance(normalized.get("text"), str):
                errors.append("query_ref.normalized_query.text must be a string.")
            if not isinstance(normalized.get("safe_public_terms"), list):
                errors.append("query_ref.normalized_query.safe_public_terms must be a list.")

    classification = _require_mapping(payload, "miss_classification", errors)
    if classification:
        if classification.get("miss_type") not in ALLOWED_MISS_TYPES:
            errors.append("miss_classification.miss_type is invalid.")
        if classification.get("severity") not in {"info", "low", "medium", "high"}:
            errors.append("miss_classification.severity is invalid.")
        if classification.get("confidence") not in {"low", "medium", "high"}:
            errors.append("miss_classification.confidence is invalid.")
        if classification.get("global_absence_claimed") is not False:
            errors.append("miss_classification.global_absence_claimed must be false.")

    causes = payload.get("miss_causes")
    if not isinstance(causes, list) or not causes:
        errors.append("miss_causes must be a non-empty list.")
    elif causes:
        for index, cause in enumerate(causes):
            if not isinstance(cause, Mapping):
                errors.append(f"miss_causes[{index}] must be an object.")
                continue
            if cause.get("cause_type") not in ALLOWED_CAUSE_TYPES:
                errors.append(f"miss_causes[{index}].cause_type is invalid.")
            if not isinstance(cause.get("explanation"), str) or not cause.get("explanation"):
                errors.append(f"miss_causes[{index}].explanation must be a non-empty string.")
            if not isinstance(cause.get("limitations"), list):
                errors.append(f"miss_causes[{index}].limitations must be a list.")

    _validate_checked_scope(_require_mapping(payload, "checked_scope", errors), errors)
    _validate_not_checked_scope(_require_mapping(payload, "not_checked_scope", errors), errors)
    _validate_near_misses(payload.get("near_misses"), errors)
    _validate_weak_hits(payload.get("weak_hits"), errors)
    _validate_result_summary(_require_mapping(payload, "result_summary", errors), errors)
    _validate_absence_summary(_require_mapping(payload, "absence_summary", errors), errors)
    _validate_suggested_next_steps(payload.get("suggested_next_steps"), errors)
    _validate_privacy(_require_mapping(payload, "privacy", errors), errors, payload)
    _validate_retention(_require_mapping(payload, "retention_policy", errors), errors)
    _validate_aggregation(_require_mapping(payload, "aggregation_policy", errors), errors)
    _validate_mutation(_require_mapping(payload, "no_mutation_guarantees", errors), errors)
    _validate_no_global_absence_claim(payload, errors)

    if strict and payload.get("status") == "public_aggregate_candidate":
        warnings.append("public aggregate candidate status requires future privacy/poisoning review before publication.")


def _validate_fingerprint(value: Mapping[str, Any], errors: list[str], label: str) -> None:
    if not value:
        return
    if value.get("algorithm") != "sha256":
        errors.append(f"{label}.algorithm must be sha256.")
    if not isinstance(value.get("value"), str) or not re.fullmatch(r"[a-f0-9]{64}", value["value"]):
        errors.append(f"{label}.value must be a lowercase sha256 hex string.")
    if value.get("reversible") is not False:
        errors.append(f"{label}.reversible must be false.")


def _validate_checked_scope(value: Mapping[str, Any], errors: list[str]) -> None:
    checked_indexes = value.get("checked_indexes")
    if not isinstance(checked_indexes, list) or not checked_indexes:
        errors.append("checked_scope.checked_indexes must be a non-empty list.")
    else:
        invalid = sorted(str(item) for item in checked_indexes if item not in ALLOWED_CHECKED_INDEXES)
        if invalid:
            errors.append(f"checked_scope.checked_indexes contains invalid values: {', '.join(invalid)}")
    for key in ("checked_sources", "checked_source_families", "checked_capabilities", "checked_index_snapshot_refs"):
        if not isinstance(value.get(key), list):
            errors.append(f"checked_scope.{key} must be a list.")
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


def _validate_near_misses(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("near_misses must be a list.")
        return
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"near_misses[{index}] must be an object.")
            continue
        _validate_summary_item(item, index, errors, label="near_misses", enum_key="reason", allowed=ALLOWED_NEAR_MISS_REASONS)


def _validate_weak_hits(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("weak_hits must be a list.")
        return
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"weak_hits[{index}] must be an object.")
            continue
        _validate_summary_item(item, index, errors, label="weak_hits", enum_key="weakness", allowed=ALLOWED_WEAKNESSES)


def _validate_summary_item(item: Mapping[str, Any], index: int, errors: list[str], *, label: str, enum_key: str, allowed: set[str]) -> None:
    for key in ("result_ref", "title", "source_id", "source_family"):
        if not isinstance(item.get(key), str) or not item.get(key):
            errors.append(f"{label}[{index}].{key} must be a non-empty string.")
    if item.get(enum_key) not in allowed:
        errors.append(f"{label}[{index}].{enum_key} is invalid.")
    if not isinstance(item.get("limitations"), list):
        errors.append(f"{label}[{index}].limitations must be a list.")


def _validate_result_summary(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("result_count", "returned_count", "gap_count", "warning_count", "limitation_count"):
        if not isinstance(value.get(key), int) or value.get(key, -1) < 0:
            errors.append(f"result_summary.{key} must be a non-negative integer.")
    if value.get("hit_state") not in ALLOWED_HIT_STATES:
        errors.append("result_summary.hit_state is invalid.")


def _validate_absence_summary(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("absence_status") not in ALLOWED_ABSENCE_STATUSES:
        errors.append("absence_summary.absence_status is invalid.")
    if value.get("global_absence_claimed") is not False:
        errors.append("absence_summary.global_absence_claimed must be false.")
    for key in ("scoped_to", "checked", "not_checked", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"absence_summary.{key} must be a list.")
    if value.get("absence_status") in {"scoped_absence", "no_verified_result"}:
        text = " ".join(str(item) for item in value.get("limitations", [])).casefold()
        if "scoped" not in text:
            errors.append("absence_summary scoped/no-verified-result entries must state scoped limitations.")


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
    if value.get("miss_entry_retention") not in {"example_only", "short_lived_future", "until_resolved_future"}:
        errors.append("retention_policy.miss_entry_retention is invalid.")


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


def _validate_no_global_absence_claim(payload: Mapping[str, Any], errors: list[str]) -> None:
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
        errors.append("miss entries must not claim global absence.")
    if payload.get("global_absence_proof") is True:
        errors.append("miss entries must not claim global absence proof.")


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
    if ENTRY_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include SEARCH_MISS_LEDGER_ENTRY.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("miss entry file is missing.")
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
        "Search Miss Ledger Entry validation",
        f"status: {report['status']}",
    ]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("miss_entry_id"):
        lines.append(f"miss_entry_id: {report['miss_entry_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", type=Path, help="Validate one SEARCH_MISS_LEDGER_ENTRY.json file.")
    parser.add_argument("--entry-root", type=Path, help="Validate one example root containing SEARCH_MISS_LEDGER_ENTRY.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed search miss ledger examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.entry, args.entry_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --entry, --entry-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.entry_root:
        report = validate_miss_entry_root(args.entry_root, strict=args.strict)
    elif args.entry:
        report = validate_miss_entry_file(args.entry, strict=args.strict)
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
