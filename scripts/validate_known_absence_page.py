#!/usr/bin/env python3
"""Validate Eureka Known Absence Page v0 examples.

This validator is stdlib-only and local. It validates contract/example
artifacts only; it performs no network calls, telemetry, persistence, runtime
known-absence page creation, live probes, source-cache mutation, evidence-ledger
mutation, candidate-index mutation, public-index mutation, local-index mutation,
or master-index mutation.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "known_absence_pages"
PAGE_FILE_NAME = "KNOWN_ABSENCE_PAGE.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "absence_page_id",
    "absence_page_kind",
    "status",
    "created_by_tool",
    "query_context",
    "absence_summary",
    "checked_scope",
    "not_checked_scope",
    "near_misses",
    "weak_hits",
    "gap_explanations",
    "source_status_summary",
    "evidence_context",
    "candidate_context",
    "safe_next_actions",
    "user_facing_sections",
    "api_projection",
    "static_projection",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_global_absence_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "scoped_absence_example",
    "local_private",
    "public_safe_example",
    "rejected_by_privacy_filter",
    "superseded_future",
    "resolved_future",
}
ALLOWED_ABSENCE_STATUS = {
    "no_verified_result",
    "scoped_absence",
    "no_public_index_hit",
    "weak_hits_only",
    "near_misses_only",
    "blocked_by_policy",
    "source_coverage_gap",
    "capability_gap",
    "unknown",
}
ALLOWED_CHECKED_INDEXES = {
    "public_index",
    "local_index_only",
    "result_cache_future",
    "candidate_index_future",
    "source_cache_future",
    "master_index_future",
}
ALLOWED_CHECKED_AT_POLICY = {"example_static", "future_runtime", "unknown"}
ALLOWED_REASONS_NOT_CHECKED = {
    "not_implemented",
    "disabled_by_policy",
    "approval_gated",
    "operator_gated",
    "source_not_available",
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
    "policy_blocked",
    "unknown",
}
ALLOWED_EVIDENCE_STATUS = {"none", "insufficient", "candidate_only", "source_backed", "review_required"}
ALLOWED_CANDIDATE_STATUS = {"none", "candidate_available_future", "review_required", "not_surfaceable"}
ALLOWED_ACTION_TYPES = {
    "refine_query",
    "view_near_misses",
    "view_checked_sources",
    "run_manual_observation_future",
    "submit_source_pack_future",
    "submit_evidence_pack_future",
    "create_search_need_future",
    "enqueue_probe_after_approval_future",
    "enable_live_probe_after_approval_future",
    "deep_extract_container_future",
    "OCR_scan_future",
    "no_action",
}
ALLOWED_ENABLED_NOW_ACTIONS = {"refine_query", "view_near_misses", "view_checked_sources"}
ALLOWED_PRIVACY = {
    "public_safe_example",
    "public_safe_aggregate",
    "local_private",
    "rejected_sensitive",
    "redacted",
    "unknown",
}
ALLOWED_RIGHTS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
ALLOWED_RISK = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}
NO_GLOBAL_FALSE_FIELDS = {
    "global_absence_claimed",
    "exhaustive_search_claimed",
    "live_probes_performed",
    "external_calls_performed",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "arbitrary_url_fetch_enabled",
}
NO_MUTATION_FALSE_FIELDS = {
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "candidate_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "result_cache_mutated",
    "miss_ledger_mutated",
    "search_need_mutated",
    "probe_queue_mutated",
    "telemetry_exported",
}
PRIVACY_FALSE_FIELDS = {
    "contains_raw_query",
    "contains_private_path",
    "contains_secret",
    "contains_private_url",
    "contains_user_identifier",
    "contains_ip_address",
}
RIGHTS_FALSE_FIELDS = {
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
}
PROHIBITED_ACTION_WORDS = re.compile(r"\b(download|install|upload|execute|live fetch|arbitrary url|probe now)\b", re.IGNORECASE)
SCOPED_LANGUAGE = re.compile(r"\b(scoped|checked scope|checked indexes|not global|not proof)\b", re.IGNORECASE)
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d{1,3}[\s.-]+)?(?:\(?\d{2,4}\)?[\s.-]+){2,}\d{2,4}\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\b", re.IGNORECASE)),
)


def validate_page_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_page(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "known_absence_page_validator_v0",
        "page": _repo_relative(path),
        "absence_page_id": payload.get("absence_page_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_page_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    path = root / PAGE_FILE_NAME
    if not path.is_file():
        return {
            "status": "invalid",
            "created_by": "known_absence_page_validator_v0",
            "page_root": _repo_relative(root),
            "absence_page_id": None,
            "errors": [f"{PAGE_FILE_NAME}: missing page file."],
            "warnings": [],
        }
    report = validate_page_file(path, strict=strict, example_root=root)
    report["page_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/known_absence_pages: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/known_absence_pages: no example roots found.")
        for root in roots:
            result = validate_page_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('page_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('page_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "known_absence_page_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_page(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("absence_page_kind") != "known_absence_page":
        errors.append("absence_page_kind must be known_absence_page.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not allowed.")
    if strict and payload.get("status") in {"superseded_future", "resolved_future"}:
        errors.append("resolved/superseded statuses must not be used in P66 examples.")

    _validate_query_context(_require_mapping(payload, "query_context", errors), errors)
    _validate_absence_summary(_require_mapping(payload, "absence_summary", errors), errors)
    _validate_checked_scope(_require_mapping(payload, "checked_scope", errors), errors)
    _validate_not_checked_scope(_require_mapping(payload, "not_checked_scope", errors), errors)
    _validate_near_misses(payload.get("near_misses"), errors)
    _validate_weak_hits(payload.get("weak_hits"), errors)
    _validate_gaps(payload.get("gap_explanations"), errors)
    _validate_source_status(_require_mapping(payload, "source_status_summary", errors), errors)
    _validate_evidence(_require_mapping(payload, "evidence_context", errors), errors)
    _validate_candidate(_require_mapping(payload, "candidate_context", errors), errors)
    _validate_actions(payload.get("safe_next_actions"), errors)
    _validate_user_sections(_require_mapping(payload, "user_facing_sections", errors), errors)
    _validate_api_projection(_require_mapping(payload, "api_projection", errors), errors)
    _validate_static_projection(_require_mapping(payload, "static_projection", errors), errors)
    _validate_privacy(_require_mapping(payload, "privacy", errors), errors)
    _validate_rights_risk(_require_mapping(payload, "rights_and_risk", errors), errors)
    _validate_no_global(_require_mapping(payload, "no_global_absence_guarantees", errors), errors)
    _validate_mutation(_require_mapping(payload, "no_mutation_guarantees", errors), errors)
    if not isinstance(payload.get("limitations"), list) or not payload.get("limitations"):
        errors.append("limitations must be a non-empty list.")
    warnings.append("P66 validates contract/example artifacts only; runtime known absence pages remain deferred.")


def _validate_query_context(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("raw_query_retained") is not False:
        errors.append("query_context.raw_query_retained must be false.")
    fingerprint = value.get("query_fingerprint")
    if not isinstance(fingerprint, str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint):
        errors.append("query_context.query_fingerprint must be a sha256 hex string.")
    if not isinstance(value.get("normalized_query"), str) or not value.get("normalized_query"):
        errors.append("query_context.normalized_query must be a non-empty public-safe string.")


def _validate_absence_summary(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("absence_status") not in ALLOWED_ABSENCE_STATUS:
        errors.append("absence_summary.absence_status is invalid.")
    if value.get("confidence") not in {"low", "medium", "high", "unknown"}:
        errors.append("absence_summary.confidence is invalid.")
    if value.get("global_absence_claimed") is not False:
        errors.append("absence_summary.global_absence_claimed must be false.")
    if value.get("exhaustive_search_claimed") is not False:
        errors.append("absence_summary.exhaustive_search_claimed must be false.")
    summary = value.get("summary_text")
    if not isinstance(summary, str) or not SCOPED_LANGUAGE.search(summary):
        errors.append("absence_summary.summary_text must use scoped, checked, or not-global language.")
    if not isinstance(value.get("scoped_to"), list) or not value.get("scoped_to"):
        errors.append("absence_summary.scoped_to must be a non-empty list.")


def _validate_checked_scope(value: Mapping[str, Any], errors: list[str]) -> None:
    indexes = value.get("checked_indexes")
    if not isinstance(indexes, list) or not indexes:
        errors.append("checked_scope.checked_indexes must be a non-empty list.")
    else:
        for item in indexes:
            if item not in ALLOWED_CHECKED_INDEXES:
                errors.append(f"checked_scope.checked_indexes contains invalid value: {item}")
    if value.get("checked_at_policy") not in ALLOWED_CHECKED_AT_POLICY:
        errors.append("checked_scope.checked_at_policy is invalid.")
    if value.get("live_probes_attempted") is not False:
        errors.append("checked_scope.live_probes_attempted must be false.")
    if value.get("external_calls_performed") is not False:
        errors.append("checked_scope.external_calls_performed must be false.")
    for key in ("checked_sources", "checked_source_families", "checked_capabilities", "checked_index_snapshot_refs"):
        if not isinstance(value.get(key), list):
            errors.append(f"checked_scope.{key} must be a list.")


def _validate_not_checked_scope(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("sources_not_checked", "source_families_not_checked", "capabilities_not_checked", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"not_checked_scope.{key} must be a list.")
    reasons = value.get("reasons_not_checked")
    if not isinstance(reasons, list) or not reasons:
        errors.append("not_checked_scope.reasons_not_checked must be a non-empty list.")
    else:
        for item in reasons:
            if item not in ALLOWED_REASONS_NOT_CHECKED:
                errors.append(f"not_checked_scope.reasons_not_checked contains invalid value: {item}")


def _validate_near_misses(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("near_misses must be a list.")
        return
    for index, item in enumerate(value):
        label = f"near_misses[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        for key in ("result_ref", "title", "source_id", "source_family", "reason", "limitations"):
            if key not in item:
                errors.append(f"{label}.{key} is missing.")
        if item.get("reason") not in ALLOWED_NEAR_MISS_REASONS:
            errors.append(f"{label}.reason is invalid.")
        if item.get("public_safe") is not True:
            errors.append(f"{label}.public_safe must be true.")


def _validate_weak_hits(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("weak_hits must be a list.")
        return
    for index, item in enumerate(value):
        label = f"weak_hits[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        for key in ("result_ref", "title", "source_id", "source_family", "weakness", "limitations"):
            if key not in item:
                errors.append(f"{label}.{key} is missing.")
        if item.get("weakness") not in ALLOWED_WEAKNESSES:
            errors.append(f"{label}.weakness is invalid.")
        if item.get("public_safe") is not True:
            errors.append(f"{label}.public_safe must be true.")


def _validate_gaps(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("gap_explanations must be a non-empty list.")
        return
    for index, gap in enumerate(value):
        label = f"gap_explanations[{index}]"
        if not isinstance(gap, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        if gap.get("gap_type") not in ALLOWED_GAP_TYPES:
            errors.append(f"{label}.gap_type is invalid.")
        if gap.get("user_visible") is not True:
            errors.append(f"{label}.user_visible must be true.")
        if not isinstance(gap.get("explanation"), str) or not gap.get("explanation"):
            errors.append(f"{label}.explanation must be non-empty.")
        if not isinstance(gap.get("limitations"), list):
            errors.append(f"{label}.limitations must be a list.")


def _validate_source_status(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("live_sources_enabled") is not False:
        errors.append("source_status_summary.live_sources_enabled must be false.")
    if value.get("live_sources_disabled") is not True:
        errors.append("source_status_summary.live_sources_disabled must be true.")
    for key in ("checked_source_families", "not_checked_source_families", "placeholder_sources", "fixture_sources", "recorded_sources", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"source_status_summary.{key} must be a list.")


def _validate_evidence(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("evidence_status") not in ALLOWED_EVIDENCE_STATUS:
        errors.append("evidence_context.evidence_status is invalid.")
    if not isinstance(value.get("evidence_refs"), list):
        errors.append("evidence_context.evidence_refs must be a list.")


def _validate_candidate(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("candidate_status") not in ALLOWED_CANDIDATE_STATUS:
        errors.append("candidate_context.candidate_status is invalid.")
    if value.get("candidate_index_runtime_implemented") is not False:
        errors.append("candidate_context.candidate_index_runtime_implemented must be false.")
    if value.get("candidate_promotion_runtime_implemented") is not False:
        errors.append("candidate_context.candidate_promotion_runtime_implemented must be false.")
    if not isinstance(value.get("candidate_refs"), list):
        errors.append("candidate_context.candidate_refs must be a list.")


def _validate_actions(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("safe_next_actions must be a non-empty list.")
        return
    for index, item in enumerate(value):
        label = f"safe_next_actions[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        action_type = item.get("action_type")
        if action_type not in ALLOWED_ACTION_TYPES:
            errors.append(f"{label}.action_type is invalid.")
        enabled = item.get("enabled_now")
        if not isinstance(enabled, bool):
            errors.append(f"{label}.enabled_now must be boolean.")
        if enabled and action_type not in ALLOWED_ENABLED_NOW_ACTIONS:
            errors.append(f"{label}.enabled_now may only be true for informational actions.")
        if str(action_type).endswith("_future") and item.get("future_only") is not True:
            errors.append(f"{label}.future_only must be true for future actions.")
        if enabled and PROHIBITED_ACTION_WORDS.search(" ".join(_iter_string_values(item))):
            errors.append(f"{label} enables a prohibited action label or limitation.")


def _validate_user_sections(value: Mapping[str, Any], errors: list[str]) -> None:
    required = {
        "title",
        "summary",
        "what_was_checked",
        "what_was_not_checked",
        "near_misses_section",
        "gaps_section",
        "safe_next_actions_section",
        "limitations_section",
        "evidence_section",
        "privacy_notice",
        "no_global_absence_notice",
    }
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"user_facing_sections missing: {', '.join(missing)}")
    notice = value.get("no_global_absence_notice")
    if not isinstance(notice, str) or not SCOPED_LANGUAGE.search(notice):
        errors.append("user_facing_sections.no_global_absence_notice must use scoped/not-global language.")
    if not value.get("limitations_section"):
        errors.append("user_facing_sections.limitations_section must be present.")


def _validate_api_projection(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("response_kind") != "known_absence_response":
        errors.append("api_projection.response_kind must be known_absence_response.")
    for key, expected in {
        "compatible_with_search_response": True,
        "error_response": False,
        "ok": True,
        "result_count": 0,
        "gaps_included": True,
        "absence_summary_included": True,
        "near_misses_included": True,
        "limitations_included": True,
    }.items():
        if value.get(key) != expected:
            errors.append(f"api_projection.{key} must be {expected!r}.")


def _validate_static_projection(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("static_demo_available", "generated_static_artifact"):
        if value.get(key) is not False:
            errors.append(f"static_projection.{key} must be false for P66 examples.")
    for key in ("no_js_required", "base_path_safe", "old_client_safe"):
        if value.get(key) is not True:
            errors.append(f"static_projection.{key} must be true.")


def _validate_privacy(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("privacy_classification") not in ALLOWED_PRIVACY:
        errors.append("privacy.privacy_classification is invalid.")
    for key in sorted(PRIVACY_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"privacy.{key} must be false for public-safe P66 examples.")
    if any(value.get(key) for key in PRIVACY_FALSE_FIELDS) and value.get("publishable") is True:
        errors.append("privacy.publishable must be false when sensitive flags are true.")
    if not isinstance(value.get("reasons"), list):
        errors.append("privacy.reasons must be a list.")


def _validate_rights_risk(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("rights_classification") not in ALLOWED_RIGHTS:
        errors.append("rights_and_risk.rights_classification is invalid.")
    if value.get("risk_classification") not in ALLOWED_RISK:
        errors.append("rights_and_risk.risk_classification is invalid.")
    for key in sorted(RIGHTS_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"rights_and_risk.{key} must be false.")


def _validate_no_global(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(NO_GLOBAL_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_global_absence_guarantees.{key} must be false.")


def _validate_mutation(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(NO_MUTATION_FALSE_FIELDS):
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
    for filename, expected_digest in sorted(expected.items()):
        path = root / filename
        if not path.is_file():
            errors.append(f"CHECKSUMS.SHA256 references missing file: {filename}.")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_digest:
            errors.append(f"CHECKSUMS.SHA256 mismatch for {filename}.")
    if PAGE_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include KNOWN_ABSENCE_PAGE.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("known absence page file is missing.")
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
    lines = ["Known Absence Page validation", f"status: {report['status']}"]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("absence_page_id"):
        lines.append(f"absence_page_id: {report['absence_page_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", type=Path, help="Validate one KNOWN_ABSENCE_PAGE.json file.")
    parser.add_argument("--page-root", type=Path, help="Validate one example root containing KNOWN_ABSENCE_PAGE.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed known absence examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.page, args.page_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --page, --page-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.page_root:
        report = validate_page_root(args.page_root, strict=args.strict)
    elif args.page:
        report = validate_page_file(args.page, strict=args.strict)
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
