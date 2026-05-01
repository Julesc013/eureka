#!/usr/bin/env python3
"""Validate Eureka Search Result Cache Entry v0 examples.

The validator is structural and stdlib-only. It validates the P60 shared
query/result cache contract posture without using telemetry, persistence,
network calls, live probes, cache runtime writes, miss ledgers, search needs,
candidate indexes, or master-index writes.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "query_result_cache"
ENTRY_FILE_NAME = "SEARCH_RESULT_CACHE_ENTRY.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "cache_entry_id",
    "cache_entry_kind",
    "status",
    "created_by_tool",
    "query_ref",
    "cache_key",
    "request_summary",
    "response_summary",
    "result_summaries",
    "absence_summary",
    "checked_scope",
    "index_refs",
    "source_status_summary",
    "freshness",
    "invalidation",
    "privacy",
    "retention_policy",
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
    "expired",
    "invalidated",
}
ALLOWED_HIT_STATES = {
    "no_hits",
    "weak_hits",
    "near_misses",
    "hits",
    "blocked_by_policy",
}
ALLOWED_ABSENCE_STATUSES = {
    "not_absent",
    "no_verified_result",
    "scoped_absence",
    "known_unresolved_need_future",
    "blocked_by_policy",
}
ALLOWED_CONFIDENCE = {"none", "low", "medium", "high"}
ALLOWED_PRIVACY_CLASSIFICATIONS = {
    "public_safe_aggregate",
    "local_private",
    "rejected_sensitive",
    "redacted",
    "unknown",
}
ALLOWED_CHECKED_INDEXES = {
    "master_index",
    "public_index",
    "candidate_index_future",
    "query_intelligence_future",
    "source_cache_future",
}
HARD_FALSE_FIELDS = {
    "master_index_mutated",
    "local_index_mutated",
    "candidate_index_mutated",
    "query_observation_mutated",
    "miss_ledger_mutated",
    "search_need_mutated",
    "probe_enqueued",
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
REQUIRED_INVALIDATION_EVENTS = {
    "public_index_rebuild",
    "source_cache_refresh",
    "contract_version_change",
    "candidate_promotion",
    "rights_policy_change",
    "safety_policy_change",
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


def validate_cache_entry_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
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
        "created_by": "search_result_cache_entry_validator_v0",
        "entry": _repo_relative(path),
        "cache_entry_id": payload.get("cache_entry_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_cache_entry_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    entry_path = root / ENTRY_FILE_NAME
    if not entry_path.is_file():
        return {
            "status": "invalid",
            "created_by": "search_result_cache_entry_validator_v0",
            "entry_root": _repo_relative(root),
            "cache_entry_id": None,
            "errors": [f"{ENTRY_FILE_NAME}: missing cache entry file."],
            "warnings": [],
        }
    report = validate_cache_entry_file(entry_path, strict=strict, example_root=root)
    report["entry_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/query_result_cache: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/query_result_cache: no example roots found.")
        for root in roots:
            result = validate_cache_entry_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('entry_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('entry_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "search_result_cache_entry_validator_v0",
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
    if payload.get("cache_entry_kind") != "search_result_cache_entry":
        errors.append("cache_entry_kind must be search_result_cache_entry.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not an allowed cache entry status.")

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

    cache_key = _require_mapping(payload, "cache_key", errors)
    if cache_key:
        if cache_key.get("key_algorithm") != "sha256":
            errors.append("cache_key.key_algorithm must be sha256.")
        if cache_key.get("key_basis") not in {
            "normalized_query",
            "normalized_query_plus_profile",
            "normalized_query_plus_profile_plus_index_snapshot",
        }:
            errors.append("cache_key.key_basis is invalid.")
        if cache_key.get("mode") != "local_index_only":
            errors.append("cache_key.mode must be local_index_only.")
        for key in ("normalized_query_hash", "value"):
            if not isinstance(cache_key.get(key), str) or not re.fullmatch(r"[a-f0-9]{64}", cache_key[key]):
                errors.append(f"cache_key.{key} must be a lowercase sha256 hex string.")
        if cache_key.get("reversible") is not False:
            errors.append("cache_key.reversible must be false.")
        if cache_key.get("salt_policy") not in {
            "unsalted_public_aggregate",
            "deployment_secret_salted_future",
            "local_private_salted_future",
        }:
            errors.append("cache_key.salt_policy is invalid.")

    request = _require_mapping(payload, "request_summary", errors)
    if request:
        if request.get("mode") != "local_index_only":
            errors.append("request_summary.mode must be local_index_only.")
        if not isinstance(request.get("limit"), int) or request.get("limit", -1) < 0 or request.get("limit", 999) > 20:
            errors.append("request_summary.limit must be an integer between 0 and 20.")
        if request.get("forbidden_parameters_present") is not False:
            errors.append("request_summary.forbidden_parameters_present must be false.")

    response = _require_mapping(payload, "response_summary", errors)
    if response:
        for key in ("result_count", "returned_count", "warning_count", "gap_count", "limitation_count"):
            if not isinstance(response.get(key), int) or response.get(key, -1) < 0:
                errors.append(f"response_summary.{key} must be a non-negative integer.")
        if response.get("hit_state") not in ALLOWED_HIT_STATES:
            errors.append("response_summary.hit_state is invalid.")
        if response.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append("response_summary.confidence is invalid.")

    results = payload.get("result_summaries")
    if not isinstance(results, list):
        errors.append("result_summaries must be a list.")
    else:
        for index, result in enumerate(results):
            _validate_result_summary(result, index, errors)

    absence = _require_mapping(payload, "absence_summary", errors)
    if absence:
        status = absence.get("absence_status")
        if status not in ALLOWED_ABSENCE_STATUSES:
            errors.append("absence_summary.absence_status is invalid.")
        if status in {"scoped_absence", "no_verified_result"}:
            limitations_text = " ".join(str(item) for item in absence.get("limitations", [])).casefold()
            if "scoped" not in limitations_text:
                errors.append("absence_summary scoped/no-result entries must state scoped limitations.")
        for key in ("gap_types", "checked", "not_checked", "next_actions", "limitations"):
            if not isinstance(absence.get(key), list):
                errors.append(f"absence_summary.{key} must be a list.")
        if not isinstance(absence.get("near_miss_count"), int) or absence.get("near_miss_count", -1) < 0:
            errors.append("absence_summary.near_miss_count must be a non-negative integer.")

    checked_scope = _require_mapping(payload, "checked_scope", errors)
    if checked_scope:
        checked_indexes = checked_scope.get("checked_indexes")
        if not isinstance(checked_indexes, list):
            errors.append("checked_scope.checked_indexes must be a list.")
        else:
            invalid = sorted(str(value) for value in checked_indexes if value not in ALLOWED_CHECKED_INDEXES)
            if invalid:
                errors.append(f"checked_scope.checked_indexes contains invalid values: {', '.join(invalid)}")
        if checked_scope.get("live_probes_attempted") is not False:
            errors.append("checked_scope.live_probes_attempted must be false.")
        if checked_scope.get("external_calls_performed") is not False:
            errors.append("checked_scope.external_calls_performed must be false.")

    _validate_index_refs(_require_mapping(payload, "index_refs", errors), errors)
    _validate_source_status(_require_mapping(payload, "source_status_summary", errors), errors)
    _validate_freshness(_require_mapping(payload, "freshness", errors), errors)
    _validate_invalidation(_require_mapping(payload, "invalidation", errors), errors)
    _validate_privacy(_require_mapping(payload, "privacy", errors), errors, payload)
    _validate_retention(_require_mapping(payload, "retention_policy", errors), errors, payload)
    _validate_mutation(_require_mapping(payload, "no_mutation_guarantees", errors), errors)
    _validate_no_global_absence_claim(payload, errors)

    if strict and payload.get("status") == "public_aggregate_candidate":
        warnings.append("public aggregate candidate status requires future privacy/poisoning review before publication.")


def _validate_result_summary(value: Any, index: int, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"result_summaries[{index}] must be an object.")
        return
    required = {
        "result_ref",
        "title",
        "source_id",
        "source_family",
        "result_lane",
        "user_cost",
        "evidence_count",
        "compatibility_summary",
        "action_summary",
        "warning_count",
        "limitation_count",
        "public_safe",
    }
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"result_summaries[{index}] missing fields: {', '.join(missing)}")
    if value.get("public_safe") is not True:
        errors.append(f"result_summaries[{index}].public_safe must be true.")
    for key in ("evidence_count", "warning_count", "limitation_count"):
        if not isinstance(value.get(key), int) or value.get(key, -1) < 0:
            errors.append(f"result_summaries[{index}].{key} must be a non-negative integer.")
    actions = value.get("action_summary")
    if not isinstance(actions, Mapping):
        errors.append(f"result_summaries[{index}].action_summary must be an object.")
        return
    blocked = actions.get("blocked_actions")
    if not isinstance(blocked, list):
        errors.append(f"result_summaries[{index}].action_summary.blocked_actions must be a list.")
    else:
        for action in ("download", "execute", "upload", "live_probe"):
            if action not in blocked:
                errors.append(f"result_summaries[{index}] must block {action}.")


def _validate_fingerprint(value: Mapping[str, Any], errors: list[str], label: str) -> None:
    if not value:
        return
    if value.get("algorithm") != "sha256":
        errors.append(f"{label}.algorithm must be sha256.")
    if not isinstance(value.get("value"), str) or not re.fullmatch(r"[a-f0-9]{64}", value["value"]):
        errors.append(f"{label}.value must be a lowercase sha256 hex string.")
    if value.get("reversible") is not False:
        errors.append(f"{label}.reversible must be false.")


def _validate_index_refs(value: Mapping[str, Any], errors: list[str]) -> None:
    required = {"public_index_build_id", "public_index_manifest_ref", "source_coverage_ref", "index_snapshot_id"}
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"index_refs missing fields: {', '.join(missing)}")


def _validate_source_status(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("live_sources_used") is not False:
        errors.append("source_status_summary.live_sources_used must be false.")
    if not isinstance(value.get("source_count"), int) or value.get("source_count", -1) < 0:
        errors.append("source_status_summary.source_count must be a non-negative integer.")


def _validate_freshness(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("cache_scope") not in {"local_public_index", "hosted_public_index_future", "source_cache_future"}:
        errors.append("freshness.cache_scope is invalid.")
    if value.get("ttl_policy") not in {
        "none_for_example",
        "short_lived_future",
        "until_index_changes",
        "until_source_cache_changes",
    }:
        errors.append("freshness.ttl_policy is invalid.")
    for key in ("stale_if_index_changes", "stale_if_contract_changes", "stale_if_source_status_changes"):
        if value.get(key) is not True:
            errors.append(f"freshness.{key} must be true for examples.")


def _validate_invalidation(value: Mapping[str, Any], errors: list[str]) -> None:
    events = value.get("invalidation_required_on")
    if not isinstance(events, list):
        errors.append("invalidation.invalidation_required_on must be a list.")
    else:
        missing = sorted(REQUIRED_INVALIDATION_EVENTS - set(events))
        if missing:
            errors.append(f"invalidation missing required events: {', '.join(missing)}")
    if value.get("invalidated") is not False:
        errors.append("invalidation.invalidated must be false for examples.")


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


def _validate_retention(value: Mapping[str, Any], errors: list[str], payload: Mapping[str, Any]) -> None:
    if value.get("raw_query_retention") != "none":
        errors.append("retention_policy.raw_query_retention must be none.")
    if value.get("cache_entry_retention") not in {"example_only", "short_lived_future", "until_index_rebuild_future"}:
        errors.append("retention_policy.cache_entry_retention is invalid.")
    if payload.get("status") != "rejected_by_privacy_filter" and value.get("public_aggregate_allowed") is not True:
        errors.append("retention_policy.public_aggregate_allowed should be true for public-safe examples.")


def _validate_mutation(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(HARD_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_mutation_guarantees.{key} must be false.")


def _validate_no_global_absence_claim(payload: Mapping[str, Any], errors: list[str]) -> None:
    absence = payload.get("absence_summary")
    if isinstance(absence, Mapping) and absence.get("absence_status") == "scoped_absence":
        text = "\n".join(_iter_string_values(absence)).casefold()
        if "all sources" in text or "every source" in text or "does not exist globally" in text:
            errors.append("absence_summary must not claim global absence.")
    if payload.get("global_absence_proof") is True:
        errors.append("cache entries must not claim global absence proof.")


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
        errors.append("CHECKSUMS.SHA256 must include SEARCH_RESULT_CACHE_ENTRY.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("cache entry file is missing.")
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
        "Search Result Cache Entry validation",
        f"status: {report['status']}",
    ]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("cache_entry_id"):
        lines.append(f"cache_entry_id: {report['cache_entry_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", type=Path, help="Validate one SEARCH_RESULT_CACHE_ENTRY.json file.")
    parser.add_argument("--entry-root", type=Path, help="Validate one example root containing SEARCH_RESULT_CACHE_ENTRY.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed search result cache examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.entry, args.entry_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --entry, --entry-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.entry_root:
        report = validate_cache_entry_root(args.entry_root, strict=args.strict)
    elif args.entry:
        report = validate_cache_entry_file(args.entry, strict=args.strict)
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
