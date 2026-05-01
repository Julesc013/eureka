#!/usr/bin/env python3
"""Validate Eureka Query Privacy and Poisoning Guard Decision v0 examples.

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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "query_guard"
DECISION_FILE_NAME = "QUERY_GUARD_DECISION.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "guard_decision_id",
    "guard_decision_kind",
    "status",
    "created_by_tool",
    "input_context",
    "privacy_risks",
    "poisoning_risks",
    "policy_actions",
    "redaction",
    "aggregate_eligibility",
    "retention_policy",
    "query_intelligence_eligibility",
    "public_search_effect",
    "review_requirements",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "allowed_public_safe",
    "allowed_redacted",
    "local_private_only",
    "rejected_sensitive",
    "quarantined_poisoning_risk",
    "throttled_future",
    "blocked_by_policy",
}
ALLOWED_INPUT_KINDS = {
    "raw_query",
    "normalized_query",
    "query_observation",
    "search_result_cache_entry",
    "search_miss_ledger_entry",
    "search_need_record",
    "probe_queue_item",
    "candidate_index_record",
    "candidate_promotion_assessment",
    "known_absence_page",
    "public_search_request",
    "unknown",
}
ALLOWED_PRIVACY_RISKS = {
    "none_detected",
    "raw_query_retention_risk",
    "private_path_detected",
    "credential_detected",
    "api_key_detected",
    "auth_token_detected",
    "password_detected",
    "private_key_detected",
    "email_detected",
    "phone_detected",
    "ip_address_detected",
    "account_identifier_detected",
    "private_url_detected",
    "local_identifier_detected",
    "user_file_name_detected",
    "long_sensitive_text_detected",
    "copyrighted_text_dump_risk",
    "executable_payload_reference_risk",
    "unknown",
}
ALLOWED_POISONING_RISKS = {
    "none_detected",
    "spam_query",
    "repeated_fake_demand",
    "source_stuffing",
    "candidate_poisoning",
    "malicious_identifier_stuffing",
    "prompt_injection_like_text",
    "policy_bypass_attempt",
    "live_probe_forcing_attempt",
    "arbitrary_url_fetch_attempt",
    "download_install_execute_forcing_attempt",
    "source_reputation_attack",
    "rank_manipulation_attempt",
    "near_duplicate_flood",
    "unsupported_parameter_abuse",
    "bot_like_pattern_future",
    "unknown",
}
ALLOWED_SEVERITIES = {"none", "low", "medium", "high", "critical"}
HIGH_SEVERITIES = {"high", "critical"}
SENSITIVE_PRIVACY_RISKS = {
    "credential_detected",
    "api_key_detected",
    "auth_token_detected",
    "password_detected",
    "private_key_detected",
}
PRIVATE_ONLY_RISKS = {
    "private_path_detected",
    "private_url_detected",
    "email_detected",
    "phone_detected",
    "ip_address_detected",
    "account_identifier_detected",
    "local_identifier_detected",
    "user_file_name_detected",
}
ALLOWED_ACTION_TYPES = {
    "allow_public_safe",
    "allow_redacted",
    "keep_local_private",
    "reject_sensitive",
    "quarantine_for_review",
    "exclude_from_public_aggregate",
    "exclude_from_candidate_generation_future",
    "exclude_from_probe_queue_future",
    "throttle_future",
    "require_human_review",
    "require_policy_review",
    "no_action",
}
ALLOWED_ACTION_STATUSES = {"recommendation_only", "applied_in_example", "future_only"}
ALLOWED_REDACTION_STRATEGIES = {
    "none",
    "remove_raw_query",
    "replace_private_path",
    "replace_secret",
    "replace_private_url",
    "truncate_long_text",
    "hash_identifier",
    "reject_without_redaction",
}
ALLOWED_AGGREGATE_FIELDS = {
    "normalized_query_terms",
    "query_intent",
    "target_object_kind",
    "platform",
    "artifact_type",
    "source_family",
    "miss_type",
    "gap_type",
    "probe_kind",
    "candidate_type",
    "absence_status",
}
REQUIRED_DISALLOWED_AGGREGATE_FIELDS = {
    "raw_query",
    "IP_address",
    "account_identifier",
    "private_path",
    "secret",
    "private_url",
    "local_identifier",
    "user_file_name",
}
ALLOWED_RETENTION = {"none", "redacted_only", "local_private_future"}
ALLOWED_GUARD_RETENTION = {"example_only", "short_lived_future", "review_required_future"}
ALLOWED_EFFECT_STATUSES = {"allowed", "blocked_by_policy", "allowed_with_redaction", "local_private_only"}
ALLOWED_REVIEW_KINDS = {
    "privacy_review",
    "security_review",
    "poisoning_review",
    "policy_review",
    "human_review",
    "operator_review",
}
NO_RUNTIME_FALSE_FIELDS = {
    "runtime_guard_implemented",
    "persistent_guard_store_implemented",
    "telemetry_exported",
    "account_tracking_performed",
    "ip_tracking_performed",
    "public_query_logging_enabled",
}
NO_MUTATION_FALSE_FIELDS = {
    "query_observation_mutated",
    "result_cache_mutated",
    "miss_ledger_mutated",
    "search_need_mutated",
    "probe_queue_mutated",
    "candidate_index_mutated",
    "known_absence_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "external_calls_performed",
    "live_source_called",
}
REDACTED_PLACEHOLDERS = {
    "<redacted-private-path>",
    "<redacted-secret>",
    "<redacted-private-url>",
    "<redacted-email>",
}
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d{1,3}[\s.-]+)?(?:\(?\d{2,4}\)?[\s.-]+){2,}\d{2,4}\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key)\b|\b(?:secret|credential)\s*[:=]", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\s*[:=]", re.IGNORECASE)),
)


def validate_decision_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_decision(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "query_guard_decision_validator_v0",
        "decision": _repo_relative(path),
        "guard_decision_id": payload.get("guard_decision_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_decision_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    path = root / DECISION_FILE_NAME
    if not path.is_file():
        return {
            "status": "invalid",
            "created_by": "query_guard_decision_validator_v0",
            "decision_root": _repo_relative(root),
            "guard_decision_id": None,
            "errors": [f"{DECISION_FILE_NAME}: missing decision file."],
            "warnings": [],
        }
    report = validate_decision_file(path, strict=strict, example_root=root)
    report["decision_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/query_guard: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/query_guard: no example roots found.")
        for root in roots:
            result = validate_decision_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('decision_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('decision_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "query_guard_decision_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_decision(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("guard_decision_kind") != "query_guard_decision":
        errors.append("guard_decision_kind must be query_guard_decision.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not allowed.")
    if strict and payload.get("status") in {"draft_example"}:
        errors.append("draft_example must not be used in strict P67 example validation.")

    input_context = _require_mapping(payload, "input_context", errors)
    privacy_risks = _require_list(payload, "privacy_risks", errors)
    poisoning_risks = _require_list(payload, "poisoning_risks", errors)
    policy_actions = _require_list(payload, "policy_actions", errors)
    redaction = _require_mapping(payload, "redaction", errors)
    aggregate = _require_mapping(payload, "aggregate_eligibility", errors)
    retention = _require_mapping(payload, "retention_policy", errors)
    intelligence = _require_mapping(payload, "query_intelligence_eligibility", errors)
    public_effect = _require_mapping(payload, "public_search_effect", errors)
    review = _require_mapping(payload, "review_requirements", errors)

    _validate_input_context(input_context, errors)
    high_privacy, sensitive_privacy, private_only = _validate_privacy_risks(privacy_risks, errors)
    high_poisoning = _validate_poisoning_risks(poisoning_risks, errors)
    actions = _validate_policy_actions(policy_actions, errors)
    _validate_redaction(redaction, errors)
    _validate_aggregate(aggregate, errors)
    _validate_retention(retention, errors)
    _validate_query_intelligence(intelligence, errors)
    _validate_public_effect(public_effect, errors)
    _validate_review(review, errors)
    _validate_no_runtime(_require_mapping(payload, "no_runtime_guarantees", errors), errors)
    _validate_no_mutation(_require_mapping(payload, "no_mutation_guarantees", errors), errors)

    if high_privacy and aggregate.get("public_aggregate_allowed") is not False:
        errors.append("high or critical privacy risk must disallow public aggregate.")
    if high_poisoning and aggregate.get("public_aggregate_allowed") is not False:
        errors.append("high or critical poisoning risk must disallow public aggregate.")
    if sensitive_privacy and not actions.intersection({"reject_sensitive", "allow_redacted", "keep_local_private"}):
        errors.append("credential/secret privacy risk requires reject, redact, or local-private action.")
    if sensitive_privacy and aggregate.get("public_aggregate_allowed") is not False:
        errors.append("credential/secret privacy risk must not be public aggregate.")
    if private_only and not actions.intersection({"reject_sensitive", "allow_redacted", "keep_local_private"}):
        errors.append("private data risk requires reject, redact, or local-private action.")
    if private_only and aggregate.get("public_aggregate_allowed") is not False:
        errors.append("private data risk must not be public aggregate.")
    if high_poisoning and not actions.intersection({"quarantine_for_review", "exclude_from_public_aggregate", "throttle_future"}):
        errors.append("high poisoning risk requires quarantine, aggregate exclusion, or future throttle action.")
    if aggregate.get("public_aggregate_allowed") is False and intelligence.get("public_aggregate_allowed") is not False:
        errors.append("query_intelligence_eligibility.public_aggregate_allowed must match aggregate block.")
    if not isinstance(payload.get("limitations"), list) or not payload.get("limitations"):
        errors.append("limitations must be a non-empty list.")
    warnings.append("P67 validates contract/example artifacts only; runtime query guard remains deferred.")


def _validate_input_context(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("input_kind") not in ALLOWED_INPUT_KINDS:
        errors.append("input_context.input_kind is invalid.")
    if value.get("raw_query_retained") is not False:
        errors.append("input_context.raw_query_retained must be false.")
    if not isinstance(value.get("raw_query_redacted"), bool):
        errors.append("input_context.raw_query_redacted must be boolean.")
    normalized = value.get("normalized_query")
    if not isinstance(normalized, str) or not normalized:
        errors.append("input_context.normalized_query must be a non-empty string.")
    fingerprint = value.get("query_fingerprint")
    if fingerprint is not None and (not isinstance(fingerprint, str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint)):
        errors.append("input_context.query_fingerprint must be sha256 hex when present.")
    if not isinstance(value.get("public_safe_context"), bool):
        errors.append("input_context.public_safe_context must be boolean.")


def _validate_privacy_risks(value: list[Any], errors: list[str]) -> tuple[bool, bool, bool]:
    if not value:
        errors.append("privacy_risks must be a non-empty list.")
    high = sensitive = private_only = False
    for index, item in enumerate(value):
        label = f"privacy_risks[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        risk_type = item.get("risk_type")
        severity = item.get("severity")
        detected = item.get("detected")
        if risk_type not in ALLOWED_PRIVACY_RISKS:
            errors.append(f"{label}.risk_type is invalid.")
        if severity not in ALLOWED_SEVERITIES:
            errors.append(f"{label}.severity is invalid.")
        if not isinstance(detected, bool):
            errors.append(f"{label}.detected must be boolean.")
        for key in ("redaction_required", "rejection_required"):
            if not isinstance(item.get(key), bool):
                errors.append(f"{label}.{key} must be boolean.")
        if detected and severity in HIGH_SEVERITIES:
            high = True
        if detected and risk_type in SENSITIVE_PRIVACY_RISKS:
            sensitive = True
            if not (item.get("redaction_required") or item.get("rejection_required")):
                errors.append(f"{label} credential/secret risk must require redaction or rejection.")
        if detected and risk_type in PRIVATE_ONLY_RISKS:
            private_only = True
        if not isinstance(item.get("reason"), str) or not item.get("reason"):
            errors.append(f"{label}.reason must be non-empty.")
        if not isinstance(item.get("field_refs"), list):
            errors.append(f"{label}.field_refs must be a list.")
    return high, sensitive, private_only


def _validate_poisoning_risks(value: list[Any], errors: list[str]) -> bool:
    if not value:
        errors.append("poisoning_risks must be a non-empty list.")
    high = False
    for index, item in enumerate(value):
        label = f"poisoning_risks[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        if item.get("risk_type") not in ALLOWED_POISONING_RISKS:
            errors.append(f"{label}.risk_type is invalid.")
        severity = item.get("severity")
        if severity not in ALLOWED_SEVERITIES:
            errors.append(f"{label}.severity is invalid.")
        if item.get("detected") is True and severity in HIGH_SEVERITIES:
            high = True
        for key in ("detected", "quarantine_required", "throttling_required_future", "aggregate_exclusion_required"):
            if not isinstance(item.get(key), bool):
                errors.append(f"{label}.{key} must be boolean.")
        if item.get("detected") is True and severity in HIGH_SEVERITIES and item.get("aggregate_exclusion_required") is not True:
            errors.append(f"{label} high poisoning risk must require aggregate exclusion.")
        if not isinstance(item.get("reason"), str) or not item.get("reason"):
            errors.append(f"{label}.reason must be non-empty.")
    return high


def _validate_policy_actions(value: list[Any], errors: list[str]) -> set[str]:
    if not value:
        errors.append("policy_actions must be a non-empty list.")
    actions: set[str] = set()
    for index, item in enumerate(value):
        label = f"policy_actions[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        action_type = item.get("action_type")
        if action_type not in ALLOWED_ACTION_TYPES:
            errors.append(f"{label}.action_type is invalid.")
        else:
            actions.add(action_type)
        if item.get("action_status") not in ALLOWED_ACTION_STATUSES:
            errors.append(f"{label}.action_status is invalid.")
        for key in ("affects_public_search_response", "affects_query_intelligence"):
            if not isinstance(item.get(key), bool):
                errors.append(f"{label}.{key} must be boolean.")
        if not isinstance(item.get("reason"), str) or not item.get("reason"):
            errors.append(f"{label}.reason must be non-empty.")
    return actions


def _validate_redaction(value: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(value.get("redaction_applied"), bool):
        errors.append("redaction.redaction_applied must be boolean.")
    if value.get("redaction_strategy") not in ALLOWED_REDACTION_STRATEGIES:
        errors.append("redaction.redaction_strategy is invalid.")
    for key in ("redacted_fields", "redaction_tokens", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"redaction.{key} must be a list.")
    tokens = value.get("redaction_tokens", [])
    if isinstance(tokens, list):
        for token in tokens:
            if token not in REDACTED_PLACEHOLDERS:
                errors.append(f"redaction.redaction_tokens contains unsupported token: {token}")
    if not isinstance(value.get("safe_to_publish_after_redaction"), bool):
        errors.append("redaction.safe_to_publish_after_redaction must be boolean.")


def _validate_aggregate(value: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(value.get("public_aggregate_allowed"), bool):
        errors.append("aggregate_eligibility.public_aggregate_allowed must be boolean.")
    allowed = value.get("allowed_aggregate_fields")
    if not isinstance(allowed, list):
        errors.append("aggregate_eligibility.allowed_aggregate_fields must be a list.")
    else:
        for item in allowed:
            if item not in ALLOWED_AGGREGATE_FIELDS:
                errors.append(f"aggregate_eligibility.allowed_aggregate_fields contains invalid value: {item}")
    disallowed = value.get("disallowed_aggregate_fields")
    if not isinstance(disallowed, list):
        errors.append("aggregate_eligibility.disallowed_aggregate_fields must be a list.")
    else:
        missing = sorted(REQUIRED_DISALLOWED_AGGREGATE_FIELDS - set(disallowed))
        if missing:
            errors.append(f"aggregate_eligibility.disallowed_aggregate_fields missing: {', '.join(missing)}")


def _validate_retention(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("raw_query_retention") != "none":
        errors.append("retention_policy.raw_query_retention must be none for P67 examples.")
    if value.get("guard_decision_retention") not in ALLOWED_GUARD_RETENTION:
        errors.append("retention_policy.guard_decision_retention is invalid.")
    if not isinstance(value.get("deletion_supported_future"), bool):
        errors.append("retention_policy.deletion_supported_future must be boolean.")


def _validate_query_intelligence(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in (
        "query_observation_allowed_future",
        "result_cache_allowed_future",
        "miss_ledger_allowed_future",
        "search_need_allowed_future",
        "probe_queue_allowed_future",
        "candidate_index_allowed_future",
        "known_absence_allowed_future",
        "public_aggregate_allowed",
        "review_required",
    ):
        if not isinstance(value.get(key), bool):
            errors.append(f"query_intelligence_eligibility.{key} must be boolean.")
    if not isinstance(value.get("required_redactions"), list):
        errors.append("query_intelligence_eligibility.required_redactions must be a list.")


def _validate_public_effect(value: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(value.get("public_search_allowed"), bool):
        errors.append("public_search_effect.public_search_allowed must be boolean.")
    if not isinstance(value.get("response_redaction_required"), bool):
        errors.append("public_search_effect.response_redaction_required must be boolean.")
    if value.get("status") not in ALLOWED_EFFECT_STATUSES:
        errors.append("public_search_effect.status is invalid.")


def _validate_review(value: Mapping[str, Any], errors: list[str]) -> None:
    required = value.get("required_review_kinds")
    if not isinstance(required, list):
        errors.append("review_requirements.required_review_kinds must be a list.")
    else:
        for item in required:
            if item not in ALLOWED_REVIEW_KINDS:
                errors.append(f"review_requirements.required_review_kinds contains invalid value: {item}")
    for key in ("reviews_completed", "reviews_missing"):
        if not isinstance(value.get(key), list):
            errors.append(f"review_requirements.{key} must be a list.")
    if value.get("automatic_acceptance_allowed") is not False:
        errors.append("review_requirements.automatic_acceptance_allowed must be false.")


def _validate_no_runtime(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(NO_RUNTIME_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_runtime_guarantees.{key} must be false.")


def _validate_no_mutation(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(NO_MUTATION_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_mutation_guarantees.{key} must be false.")


def _require_mapping(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object.")
        return {}
    return value


def _require_list(payload: Mapping[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be a list.")
        return []
    return value


def _validate_no_sensitive_payload(payload: Mapping[str, Any], errors: list[str]) -> None:
    for text in _iter_string_values(payload):
        sanitized = _sanitize_for_sensitive_scan(text)
        for label, pattern in SENSITIVE_PATTERNS:
            if pattern.search(sanitized):
                errors.append(f"payload contains prohibited data pattern: {label}.")


def _sanitize_for_sensitive_scan(text: str) -> str:
    sanitized = text
    for placeholder in REDACTED_PLACEHOLDERS:
        sanitized = sanitized.replace(placeholder, "")
    for safe_enum in (
        "api_key_detected",
        "auth_token_detected",
        "password_detected",
        "private_key_detected",
        "credential_detected",
        "private_path_detected",
        "private_url_detected",
        "ip_address_detected",
        "account_identifier_detected",
        "replace_secret",
        "secret",
        "private_path",
        "private_url",
        "IP_address",
        "account_identifier",
        "user_file_name",
    ):
        sanitized = sanitized.replace(safe_enum, "")
    return sanitized


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
    for filename, expected_digest in sorted(expected.items()):
        path = root / filename
        if not path.is_file():
            errors.append(f"CHECKSUMS.SHA256 references missing file: {filename}.")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_digest:
            errors.append(f"CHECKSUMS.SHA256 mismatch for {filename}.")
    if DECISION_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include QUERY_GUARD_DECISION.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("query guard decision file is missing.")
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
    lines = ["Query Guard Decision validation", f"status: {report['status']}"]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("guard_decision_id"):
        lines.append(f"guard_decision_id: {report['guard_decision_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", type=Path, help="Validate one QUERY_GUARD_DECISION.json file.")
    parser.add_argument("--decision-root", type=Path, help="Validate one example root containing QUERY_GUARD_DECISION.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed query guard examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.decision, args.decision_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --decision, --decision-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.decision_root:
        report = validate_decision_root(args.decision_root, strict=args.strict)
    elif args.decision:
        report = validate_decision_file(args.decision, strict=args.strict)
    else:  # pragma: no cover
        report = {"status": "invalid", "errors": ["no selection"], "warnings": []}

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
