#!/usr/bin/env python3
"""Emit a hypothetical Query Guard Decision v0 to stdout only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any, Sequence, TextIO


PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE),
)
SECRET_PATTERN = re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key)\b|\b(?:secret|credential)\s*[:=]", re.IGNORECASE)
PRIVATE_URL_PATTERN = re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)
FETCH_PATTERN = re.compile(r"\b(?:fetch|crawl|scrape|open url|arbitrary url)\b", re.IGNORECASE)
LIVE_PROBE_PATTERN = re.compile(r"\b(?:live probe|wayback|internet archive|github api|pypi api|wikidata api)\b", re.IGNORECASE)
UNSAFE_ACTION_PATTERN = re.compile(r"\b(?:download|install|execute|upload)\b", re.IGNORECASE)


def build_decision(query: str) -> dict[str, Any]:
    normalized = _normalize(query)
    privacy_risks: list[dict[str, Any]] = []
    poisoning_risks: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    redaction_tokens: list[str] = []
    redaction_strategy = "none"
    redaction_applied = False
    status = "dry_run_validated"
    public_search_allowed = True
    public_status = "allowed"
    public_error = None
    aggregate_allowed = True
    public_safe_context = True
    required_reviews: list[str] = []

    if any(pattern.search(query) for pattern in PRIVATE_PATH_PATTERNS):
        normalized = "<redacted-private-path>"
        privacy_risks.append(_privacy("private_path_detected", "high", True, True, True, "Private path-like input is redacted and rejected."))
        actions.extend([
            _action("reject_sensitive", "applied_in_example", "Private paths are rejected from public aggregate learning."),
            _action("exclude_from_public_aggregate", "applied_in_example", "Private path inputs must not influence aggregate learning."),
        ])
        redaction_tokens.append("<redacted-private-path>")
        redaction_strategy = "replace_private_path"
        redaction_applied = True
        status = "rejected_sensitive"
        public_search_allowed = False
        public_status = "blocked_by_policy"
        public_error = "query_privacy_rejected"
        aggregate_allowed = False
        public_safe_context = False
        required_reviews.append("privacy_review")

    if SECRET_PATTERN.search(query):
        normalized = "<redacted-secret>"
        privacy_risks.append(_privacy("credential_detected", "critical", True, True, True, "Credential-like input is redacted and rejected."))
        actions.extend([
            _action("reject_sensitive", "applied_in_example", "Credentials are rejected from public aggregate learning."),
            _action("exclude_from_public_aggregate", "applied_in_example", "Credential-like inputs must not count as demand."),
        ])
        redaction_tokens.append("<redacted-secret>")
        redaction_strategy = "replace_secret"
        redaction_applied = True
        status = "rejected_sensitive"
        public_search_allowed = False
        public_status = "blocked_by_policy"
        public_error = "query_privacy_rejected"
        aggregate_allowed = False
        public_safe_context = False
        required_reviews.extend(["privacy_review", "security_review"])

    if PRIVATE_URL_PATTERN.search(query):
        normalized = "<redacted-private-url>"
        privacy_risks.append(_privacy("private_url_detected", "high", True, True, True, "Private URL-like input is redacted and rejected."))
        actions.extend([
            _action("reject_sensitive", "applied_in_example", "Private URLs are rejected from public aggregate learning."),
            _action("exclude_from_public_aggregate", "applied_in_example", "Private URL inputs must not influence aggregate learning."),
        ])
        redaction_tokens.append("<redacted-private-url>")
        redaction_strategy = "replace_private_url"
        redaction_applied = True
        status = "rejected_sensitive"
        public_search_allowed = False
        public_status = "blocked_by_policy"
        public_error = "query_privacy_rejected"
        aggregate_allowed = False
        public_safe_context = False
        required_reviews.append("privacy_review")

    if FETCH_PATTERN.search(query):
        poisoning_risks.append(_poison("arbitrary_url_fetch_attempt", "high", True, True, False, True, "Input appears to request arbitrary URL fetching."))
        actions.extend([
            _action("quarantine_for_review", "applied_in_example", "Arbitrary fetch forcing is quarantined."),
            _action("exclude_from_public_aggregate", "applied_in_example", "Fetch-forcing input is excluded from public aggregate learning."),
        ])
        status = "quarantined_poisoning_risk" if status == "dry_run_validated" else status
        aggregate_allowed = False
        required_reviews.append("poisoning_review")

    if LIVE_PROBE_PATTERN.search(query):
        poisoning_risks.append(_poison("live_probe_forcing_attempt", "high", True, True, False, True, "Input appears to force live source probing."))
        actions.extend([
            _action("quarantine_for_review", "applied_in_example", "Live-probe forcing is quarantined."),
            _action("exclude_from_probe_queue_future", "future_only", "No future probe queue item should be created without review."),
        ])
        status = "quarantined_poisoning_risk" if status == "dry_run_validated" else status
        aggregate_allowed = False
        required_reviews.append("poisoning_review")

    if UNSAFE_ACTION_PATTERN.search(query):
        poisoning_risks.append(_poison("download_install_execute_forcing_attempt", "high", True, True, False, True, "Input appears to request download/install/execute/upload behavior."))
        actions.extend([
            _action("quarantine_for_review", "applied_in_example", "Unsafe action forcing is quarantined."),
            _action("exclude_from_public_aggregate", "applied_in_example", "Unsafe action forcing is excluded from aggregate learning."),
        ])
        status = "quarantined_poisoning_risk" if status == "dry_run_validated" else status
        aggregate_allowed = False
        required_reviews.append("security_review")

    if len(query) > 240 and aggregate_allowed:
        privacy_risks.append(_privacy("long_sensitive_text_detected", "medium", True, True, False, "Long input is redacted from raw retention and requires review."))
        actions.append(_action("allow_redacted", "applied_in_example", "Long input is allowed only as a redacted decision projection."))
        redaction_strategy = "truncate_long_text"
        redaction_applied = True
        status = "allowed_redacted"
        public_status = "allowed_with_redaction"
        required_reviews.append("privacy_review")

    if not privacy_risks:
        privacy_risks.append(_privacy("none_detected", "none", False, False, False, "No private data indicators were detected."))
    if not poisoning_risks:
        poisoning_risks.append(_poison("none_detected", "none", False, False, False, False, "No poisoning indicators were detected."))
    if not actions:
        actions.append(_action("allow_public_safe", "applied_in_example", "Public-safe dry-run input is allowed for future aggregate learning."))

    fingerprint = hashlib.sha256(f"query_guard:v0:{normalized}".encode("utf-8")).hexdigest()
    return {
        "schema_version": "0.1.0",
        "guard_decision_id": f"dry_run.query_guard.{fingerprint[:16]}",
        "guard_decision_kind": "query_guard_decision",
        "status": status,
        "created_by_tool": "dry_run_query_guard_v0",
        "input_context": {
            "input_kind": "raw_query",
            "raw_query_retained": False,
            "raw_query_redacted": redaction_applied,
            "normalized_query": normalized,
            "query_fingerprint": fingerprint,
            "source_object_ref": None,
            "public_safe_context": public_safe_context,
            "limitations": ["Stdout-only dry run; no query log, guard store, telemetry, or derived object is written."],
        },
        "privacy_risks": privacy_risks,
        "poisoning_risks": poisoning_risks,
        "policy_actions": actions,
        "redaction": {
            "redaction_applied": redaction_applied,
            "redaction_strategy": redaction_strategy,
            "redacted_fields": ["input_context.normalized_query"] if redaction_applied else [],
            "redaction_tokens": sorted(set(redaction_tokens)),
            "residual_risk": "blocked from aggregate" if not aggregate_allowed else "none detected in dry-run input",
            "safe_to_publish_after_redaction": public_safe_context and aggregate_allowed,
            "limitations": ["Redaction is a dry-run decision projection only."],
        },
        "aggregate_eligibility": {
            "public_aggregate_allowed": aggregate_allowed,
            "allowed_aggregate_fields": [
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
            ] if aggregate_allowed else [],
            "disallowed_aggregate_fields": [
                "raw_query",
                "IP_address",
                "account_identifier",
                "private_path",
                "secret",
                "private_url",
                "local_identifier",
                "user_file_name",
            ],
            "reason": "Allowed by dry-run classifier." if aggregate_allowed else "Blocked by privacy or poisoning risk.",
            "limitations": ["No demand count or aggregate store is updated."],
        },
        "retention_policy": {
            "raw_query_retention": "none",
            "guard_decision_retention": "example_only",
            "deletion_supported_future": True,
            "notes": ["Dry-run output is stdout only and not persisted."],
        },
        "query_intelligence_eligibility": {
            "query_observation_allowed_future": aggregate_allowed,
            "result_cache_allowed_future": aggregate_allowed,
            "miss_ledger_allowed_future": aggregate_allowed,
            "search_need_allowed_future": aggregate_allowed,
            "probe_queue_allowed_future": aggregate_allowed,
            "candidate_index_allowed_future": aggregate_allowed,
            "known_absence_allowed_future": aggregate_allowed or redaction_applied,
            "public_aggregate_allowed": aggregate_allowed,
            "required_redactions": sorted(set(redaction_tokens)),
            "review_required": bool(required_reviews),
            "limitations": ["Eligibility flags are future-only and do not mutate any query-intelligence object."],
        },
        "public_search_effect": {
            "public_search_allowed": public_search_allowed,
            "public_search_error_code": public_error,
            "response_redaction_required": redaction_applied,
            "status": public_status,
            "limitations": ["Policy projection only; public search runtime is not called or changed."],
        },
        "review_requirements": {
            "required_review_kinds": sorted(set(required_reviews)),
            "reviews_completed": [],
            "reviews_missing": sorted(set(required_reviews)),
            "automatic_acceptance_allowed": False,
            "limitations": ["No automatic acceptance, source trust, rights clearance, malware safety, or candidate promotion decision is made."],
        },
        "limitations": ["Dry-run helper emits JSON to stdout only and writes no files."],
        "no_runtime_guarantees": {
            "runtime_guard_implemented": False,
            "persistent_guard_store_implemented": False,
            "telemetry_exported": False,
            "account_tracking_performed": False,
            "ip_tracking_performed": False,
            "public_query_logging_enabled": False,
        },
        "no_mutation_guarantees": {
            "query_observation_mutated": False,
            "result_cache_mutated": False,
            "miss_ledger_mutated": False,
            "search_need_mutated": False,
            "probe_queue_mutated": False,
            "candidate_index_mutated": False,
            "known_absence_mutated": False,
            "public_index_mutated": False,
            "local_index_mutated": False,
            "master_index_mutated": False,
            "external_calls_performed": False,
            "live_source_called": False,
        },
        "notes": ["Privacy before learning; poisoning defense before aggregation."],
    }


def _privacy(risk_type: str, severity: str, detected: bool, redaction_required: bool, rejection_required: bool, reason: str) -> dict[str, Any]:
    return {
        "risk_type": risk_type,
        "severity": severity,
        "detected": detected,
        "redaction_required": redaction_required,
        "rejection_required": rejection_required,
        "reason": reason,
        "field_refs": ["input_context.normalized_query"] if detected else [],
        "limitations": ["Dry-run classifier is conservative and not production moderation."],
    }


def _poison(risk_type: str, severity: str, detected: bool, quarantine: bool, throttle: bool, exclude: bool, reason: str) -> dict[str, Any]:
    return {
        "risk_type": risk_type,
        "severity": severity,
        "detected": detected,
        "quarantine_required": quarantine,
        "throttling_required_future": throttle,
        "aggregate_exclusion_required": exclude,
        "reason": reason,
        "limitations": ["Dry-run classifier does not implement runtime throttling, bot detection, or source trust."],
    }


def _action(action_type: str, action_status: str, reason: str) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "action_status": action_status,
        "reason": reason,
        "affects_public_search_response": action_type in {"reject_sensitive", "allow_redacted", "keep_local_private"},
        "affects_query_intelligence": action_type != "no_action",
        "limitations": ["Decision output only; no persistent state is written."],
    }


def _normalize(value: str) -> str:
    return " ".join(value.strip().split())[:160] or "unknown query"


def _format_plain(decision: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Query Guard dry run",
            f"status: {decision['status']}",
            f"guard_decision_id: {decision['guard_decision_id']}",
            f"public_aggregate_allowed: {str(decision['aggregate_eligibility']['public_aggregate_allowed']).lower()}",
            "files_written: false",
        ]
    ) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Query text for a hypothetical guard decision.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    decision = build_decision(args.query)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(decision, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
