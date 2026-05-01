#!/usr/bin/env python3
"""Validate Eureka Query Observation v0 examples.

The validator is intentionally structural and stdlib-only. It validates the
P59 contract posture without using telemetry, persistence, network calls,
probe queues, caches, ledgers, candidate indexes, or master-index writes.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "query_observations"
DEFAULT_EXAMPLE_ROOT = EXAMPLES_ROOT / "minimal_query_observation_v0"
OBSERVATION_FILE_NAME = "QUERY_OBSERVATION.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "observation_id",
    "observation_kind",
    "status",
    "created_by_tool",
    "raw_query_policy",
    "normalized_query",
    "query_fingerprint",
    "query_intent",
    "destination",
    "detected_entities",
    "filters",
    "result_summary",
    "checked_scope",
    "index_refs",
    "privacy",
    "retention_policy",
    "probe_policy",
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
    "redacted",
}
ALLOWED_RAW_RETENTION = {
    "not_retained",
    "redacted",
    "local_private_only",
    "public_safe_short_text",
}
ALLOWED_INTENTS = {
    "find_exact_artifact",
    "find_software_version",
    "find_driver",
    "find_manual_or_documentation",
    "find_source_code",
    "find_package_metadata",
    "find_inside_container_member",
    "find_inside_scan_article",
    "compare_versions_or_sources",
    "check_compatibility",
    "explain_absence",
    "unknown",
}
ALLOWED_DESTINATIONS = {
    "read",
    "inspect",
    "cite",
    "compare",
    "preserve",
    "download_or_install_intent_detected_but_actions_disabled",
    "emulate_or_reconstruct_intent_detected_but_actions_disabled",
    "unknown",
}
ALLOWED_ENTITY_KINDS = {
    "product",
    "version",
    "platform",
    "architecture",
    "artifact_type",
    "source_family",
    "file_name",
    "extension",
    "date",
    "vendor",
    "package_name",
    "identifier",
    "unknown",
}
ALLOWED_HIT_STATES = {
    "no_query_executed",
    "no_hits",
    "weak_hits",
    "near_misses",
    "hits",
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
    "probe_enqueued",
    "result_cache_mutated",
    "miss_ledger_mutated",
    "telemetry_exported",
    "external_calls_performed",
}
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[a-zA-Z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d[\d .-]{7,}\d)\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE)),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
)


def validate_query_observation_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_observation(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "query_observation_validator_v0",
        "observation": _repo_relative(path),
        "observation_id": payload.get("observation_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_query_observation_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    observation_path = root / OBSERVATION_FILE_NAME
    if not observation_path.is_file():
        return {
            "status": "invalid",
            "created_by": "query_observation_validator_v0",
            "observation_root": _repo_relative(root),
            "observation_id": None,
            "errors": [f"{OBSERVATION_FILE_NAME}: missing observation file."],
            "warnings": [],
        }
    report = validate_query_observation_file(observation_path, strict=strict, example_root=root)
    report["observation_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/query_observations: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/query_observations: no example roots found.")
        for root in roots:
            result = validate_query_observation_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('observation_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('observation_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "query_observation_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_observation(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("observation_kind") != "query_observation":
        errors.append("observation_kind must be query_observation.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not an allowed query observation status.")

    raw_policy = _require_mapping(payload, "raw_query_policy", errors)
    if raw_policy:
        if raw_policy.get("raw_query_retention_class") not in ALLOWED_RAW_RETENTION:
            errors.append("raw_query_policy.raw_query_retention_class is invalid.")
        if not isinstance(raw_policy.get("raw_query_length"), int) or raw_policy.get("raw_query_length", -1) < 0:
            errors.append("raw_query_policy.raw_query_length must be a non-negative integer.")
        if not isinstance(raw_policy.get("redaction_reasons"), list):
            errors.append("raw_query_policy.redaction_reasons must be a list.")
        if payload.get("status") != "local_private":
            if raw_policy.get("raw_query_retained") is not False:
                errors.append("public-safe observations must not retain raw queries.")
            if raw_policy.get("safe_to_publish_raw_query") is not False:
                errors.append("safe_to_publish_raw_query must be false for P59 examples.")
            if strict and raw_policy.get("raw_query_redacted") is not True:
                errors.append("strict mode requires raw_query_redacted true for non-local examples.")

    normalized = _require_mapping(payload, "normalized_query", errors)
    if normalized:
        text = normalized.get("text")
        if not isinstance(text, str):
            errors.append("normalized_query.text must be a string.")
        if not isinstance(normalized.get("tokens"), list):
            errors.append("normalized_query.tokens must be a list.")
        if not isinstance(normalized.get("normalized_terms"), list):
            errors.append("normalized_query.normalized_terms must be a list.")
        if not isinstance(normalized.get("safe_public_terms"), list):
            errors.append("normalized_query.safe_public_terms must be a list.")

    fingerprint = _require_mapping(payload, "query_fingerprint", errors)
    if fingerprint:
        if fingerprint.get("algorithm") != "sha256":
            errors.append("query_fingerprint.algorithm must be sha256.")
        if not isinstance(fingerprint.get("value"), str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint["value"]):
            errors.append("query_fingerprint.value must be a lowercase sha256 hex string.")
        if fingerprint.get("reversible") is not False:
            errors.append("query_fingerprint.reversible must be false.")
        if fingerprint.get("salt_policy") not in {
            "unsalted_public_aggregate",
            "deployment_secret_salted_future",
            "local_private_salted_future",
        }:
            errors.append("query_fingerprint.salt_policy is invalid.")

    intent = _require_mapping(payload, "query_intent", errors)
    if intent:
        if intent.get("primary_intent") not in ALLOWED_INTENTS:
            errors.append("query_intent.primary_intent is invalid.")
        if intent.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append("query_intent.confidence is invalid.")
        if not isinstance(intent.get("secondary_intents"), list):
            errors.append("query_intent.secondary_intents must be a list.")

    destination = _require_mapping(payload, "destination", errors)
    if destination:
        if destination.get("primary_destination") not in ALLOWED_DESTINATIONS:
            errors.append("destination.primary_destination is invalid.")
        if not isinstance(destination.get("disabled_destination_intent_detected"), bool):
            errors.append("destination.disabled_destination_intent_detected must be boolean.")

    entities = payload.get("detected_entities")
    if not isinstance(entities, list):
        errors.append("detected_entities must be a list.")
    else:
        for index, entity in enumerate(entities):
            if not isinstance(entity, Mapping):
                errors.append(f"detected_entities[{index}] must be an object.")
                continue
            if entity.get("entity_kind") not in ALLOWED_ENTITY_KINDS:
                errors.append(f"detected_entities[{index}].entity_kind is invalid.")
            for key in ("value", "normalized_value", "privacy_classification"):
                if not isinstance(entity.get(key), str):
                    errors.append(f"detected_entities[{index}].{key} must be a string.")

    result_summary = _require_mapping(payload, "result_summary", errors)
    if result_summary:
        for key in ("result_count", "returned_count", "near_miss_count"):
            if not isinstance(result_summary.get(key), int) or result_summary.get(key, -1) < 0:
                errors.append(f"result_summary.{key} must be a non-negative integer.")
        if result_summary.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append("result_summary.confidence is invalid.")
        if result_summary.get("hit_state") not in ALLOWED_HIT_STATES:
            errors.append("result_summary.hit_state is invalid.")
        for key in ("gap_types", "warnings", "limitations"):
            if not isinstance(result_summary.get(key), list):
                errors.append(f"result_summary.{key} must be a list.")

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

    privacy = _require_mapping(payload, "privacy", errors)
    if privacy:
        if privacy.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSIFICATIONS:
            errors.append("privacy.privacy_classification is invalid.")
        for key in (
            "pii_detected",
            "secret_detected",
            "private_path_detected",
            "private_url_detected",
            "credential_detected",
            "local_identifier_detected",
            "publishable",
            "public_aggregate_allowed",
        ):
            if not isinstance(privacy.get(key), bool):
                errors.append(f"privacy.{key} must be boolean.")
        sensitive_flags = (
            privacy.get("pii_detected"),
            privacy.get("secret_detected"),
            privacy.get("private_path_detected"),
            privacy.get("private_url_detected"),
            privacy.get("credential_detected"),
        )
        if any(sensitive_flags) and privacy.get("publishable") is True:
            errors.append("privacy.publishable must be false when sensitive flags are true.")
        if any(sensitive_flags) and privacy.get("public_aggregate_allowed") is True and payload.get("status") != "redacted":
            errors.append("public_aggregate_allowed requires redacted status when sensitive flags are true.")

    retention = _require_mapping(payload, "retention_policy", errors)
    if retention:
        if retention.get("raw_query_retention") not in {"none", "redacted_only", "local_private_future"}:
            errors.append("retention_policy.raw_query_retention is invalid.")
        if payload.get("status") != "local_private" and retention.get("raw_query_retention") != "none":
            errors.append("public-safe P59 examples must use raw_query_retention none.")

    probe_policy = _require_mapping(payload, "probe_policy", errors)
    if probe_policy:
        if probe_policy.get("probe_enqueue_allowed") is not False:
            errors.append("probe_policy.probe_enqueue_allowed must be false.")
        if probe_policy.get("future_only") is not True:
            errors.append("probe_policy.future_only must be true.")

    mutation = _require_mapping(payload, "no_mutation_guarantees", errors)
    if mutation:
        for key in sorted(HARD_FALSE_FIELDS):
            if mutation.get(key) is not False:
                errors.append(f"no_mutation_guarantees.{key} must be false.")

    if payload.get("status") == "public_aggregate_candidate":
        warnings.append("public aggregate candidate status requires future privacy/poisoning review before publication.")


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
    if OBSERVATION_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include QUERY_OBSERVATION.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("observation file is missing.")
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
        "Query Observation validation",
        f"status: {report['status']}",
    ]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("observation_id"):
        lines.append(f"observation_id: {report['observation_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _single_reports_to_summary(reports: Iterable[dict[str, Any]]) -> dict[str, Any]:
    results = list(reports)
    errors: list[str] = []
    warnings: list[str] = []
    for result in results:
        label = result.get("observation") or result.get("observation_root") or "observation"
        errors.extend(f"{label}: {error}" for error in result.get("errors", []))
        warnings.extend(f"{label}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "query_observation_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation", type=Path, help="Validate one QUERY_OBSERVATION.json file.")
    parser.add_argument("--observation-root", type=Path, help="Validate one example root containing QUERY_OBSERVATION.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed query observation examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.observation, args.observation_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --observation, --observation-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.observation_root:
        report = validate_query_observation_root(args.observation_root, strict=args.strict)
    elif args.observation:
        report = validate_query_observation_file(args.observation, strict=args.strict)
    else:  # pragma: no cover - argparse-selected guard
        report = _single_reports_to_summary([])

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
