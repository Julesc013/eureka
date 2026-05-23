"""Local-only Query Observation runtime helpers.

This module is intentionally standard-library only and side-effect free. It
does not call networks, read browser state, write files, mutate public search,
or mutate index state.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import re
from typing import Any, Mapping


SCHEMA_VERSION = "query_observation_runtime.v0"
REPORT_SCHEMA_VERSION = "query_observation_runtime_report.v0"
BASE_CONTRACT_REF = "contracts/query/query_observation.v0.json"

ALLOWED_STATUSES = {
    "example_only",
    "recorded_local",
    "privacy_filtered",
    "poisoning_guarded",
    "needs_review",
    "approved_for_miss_ledger_future",
    "approved_for_search_need_seed_future",
    "rejected",
    "duplicate",
    "policy_blocked",
    "deferred",
    "not_evaluable",
}
CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "recorded_local",
    "privacy_filtered",
    "poisoning_guarded",
    "needs_review",
    "policy_blocked",
    "not_evaluable",
}
ALLOWED_QUERY_SOURCES = {
    "explicit_test_fixture",
    "local_eval",
    "manual_observation_candidate",
    "public_search_rehearsal_fixture",
    "static_demo_fixture",
    "agent_assisted_candidate",
    "future_public_search_with_privacy_filter",
    "future_node_workunit",
}
CURRENT_ALLOWED_QUERY_SOURCES = {
    "explicit_test_fixture",
    "local_eval",
    "manual_observation_candidate",
    "public_search_rehearsal_fixture",
    "static_demo_fixture",
    "agent_assisted_candidate",
}
ALLOWED_FAILURE_MODES = {
    "none",
    "empty_result",
    "weak_result",
    "ranking_gap",
    "source_gap",
    "extraction_gap",
    "compatibility_gap",
    "representation_gap",
    "identity_gap",
    "temporal_version_gap",
    "policy_blocked",
    "privacy_filtered",
    "poisoning_risk",
    "not_evaluable",
}
ALLOWED_RESULT_QUALITIES = {
    "empty",
    "weak",
    "useful",
    "mixed",
    "blocked",
    "not_evaluable",
}
ALLOWED_OUTPUT_TYPES = {
    "query_observation_record",
    "query_observation_summary",
    "miss_ledger_seed_future",
    "search_need_seed_future",
    "workunit_seed_future",
    "observation_candidate_future",
    "review_item_future",
}
FORBIDDEN_OUTPUT_TYPES = {
    "observed_external_baseline_truth",
    "accepted_evidence_truth",
    "accepted_public_record",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
}
TRUTH_BOUNDARY_FALSE_FIELDS = {
    "query_observation_is_public_truth",
    "query_observation_is_accepted_evidence",
    "query_observation_can_mutate_master_index",
    "query_observation_is_observed_external_baseline",
    "query_observation_claims_global_absence",
}
PRODUCT_BOUNDARY_FALSE_FIELDS = {
    "implemented_public_telemetry",
    "changed_public_search_behavior",
    "created_local_private_state",
    "enabled_network_access",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "enabled_model_provider_calls",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}
PRIVACY_FALSE_FIELDS = {
    "public_telemetry_enabled",
    "accounts_required",
    "raw_public_query_logging_enabled",
    "private_data_allowed",
    "browser_state_collection_allowed",
    "account_identity_collected",
    "location_collected",
}
REVIEW_TRUE_FIELDS = {
    "human_review_required_for_downstream_use",
    "miss_ledger_review_required",
    "search_need_review_required",
    "workunit_review_required",
    "master_index_review_required",
}
POISONING_RISK_TYPES = {
    "repeated_spam_query",
    "suspiciously_long_query",
    "url_injection",
    "local_path_injection",
    "credential_like_content",
    "private_data_content",
    "binary_download_request",
    "executable_install_request",
    "unsupported_live_probe_request",
    "unsupported_scraping_request",
    "unsupported_account_upload_request",
    "source_manipulation_attempt",
    "result_rank_manipulation_attempt",
    "automated_bulk_pattern_future",
}
CLAIM_PHRASES = {
    "whole web was searched",
    "globally absent",
    "global absence proof",
    "accepted public truth",
    "accepted evidence truth",
    "telemetry enabled",
    "telemetry is enabled",
    "hosted query capture enabled",
    "public user was tracked",
    "hosted user was tracked",
    "master-index mutation is allowed",
    "rights clearance",
    "malware safe",
    "malware safety",
    "verified installability",
    "exhaustive global search",
    "production readiness",
}

TOKEN_RE = re.compile(r"[a-z0-9_.-]+", re.IGNORECASE)
PRIVACY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("local_path_injection", re.compile(r"\b[a-zA-Z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("local_path_injection", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("private_data_content", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("private_data_content", re.compile(r"\b(?:\+?\d[\d .-]{7,}\d)\b")),
    ("credential_like_content", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE)),
)
POISONING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("url_injection", re.compile(r"\bhttps?://", re.IGNORECASE)),
    ("binary_download_request", re.compile(r"\b(?:download|binary|exe|zip|installer payload)\b", re.IGNORECASE)),
    ("executable_install_request", re.compile(r"\b(?:install|execute|run installer|run executable)\b", re.IGNORECASE)),
    ("unsupported_live_probe_request", re.compile(r"\b(?:live[_ -]?probe|live source|fetch now|query live)\b", re.IGNORECASE)),
    ("unsupported_scraping_request", re.compile(r"\b(?:scrape|crawl|google results|forum crawl|reddit ingestion)\b", re.IGNORECASE)),
    ("unsupported_account_upload_request", re.compile(r"\b(?:account|login|upload|cookie|session)\b", re.IGNORECASE)),
    ("source_manipulation_attempt", re.compile(r"\b(?:force source|only rank this source|ignore source policy)\b", re.IGNORECASE)),
    ("result_rank_manipulation_attempt", re.compile(r"\b(?:force rank|boost result|hide result|rank manipulation)\b", re.IGNORECASE)),
    ("automated_bulk_pattern_future", re.compile(r"\b(?:bulk|thousands of queries|mass query|automated batch)\b", re.IGNORECASE)),
)


def default_policy() -> dict[str, Any]:
    return {
        "allowed_input_sources": sorted(ALLOWED_QUERY_SOURCES),
        "current_allowed_input_sources": sorted(CURRENT_ALLOWED_QUERY_SOURCES),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "current_allowed_statuses": sorted(CURRENT_ALLOWED_STATUSES),
        "allowed_failure_modes": sorted(ALLOWED_FAILURE_MODES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "max_query_length": 160,
        "review_required_before_downstream_use": True,
        "privacy": {
            "raw_query_allowed_for_synthetic_fixtures": True,
            "raw_public_query_logging_enabled": False,
            "public_telemetry_enabled": False,
            "private_data_allowed": False,
            "browser_state_collection_allowed": False,
        },
    }


def build_query_observation(input_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build or normalize a local query observation record from explicit input."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(input_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        record = source
    else:
        record = _build_from_input_model(source)

    record.setdefault("schema_version", SCHEMA_VERSION)
    record.setdefault("query_observation_id", _observation_id(record))
    record.setdefault("base_contract_ref", BASE_CONTRACT_REF)
    record.setdefault("observation_status", "recorded_local")
    record.setdefault("query_id_optional", None)
    record.setdefault("query_context", "local explicit input")
    record.setdefault("submitted_via", "explicit_json_input")
    record.setdefault("search_mode", "local_only")
    record.setdefault("local_index_mode", "fixture_or_report_only")
    record.setdefault("top_result_refs", [])
    record.setdefault("failure_modes", [])
    record.setdefault("limitations", [])
    record.setdefault("notes", [])
    record.setdefault("review_gates", _default_review_gates())
    record.setdefault("truth_boundary", _default_truth_boundary())
    record.setdefault("product_boundary", _default_product_boundary())
    record.setdefault("output_candidates", _default_output_candidates())

    record = redact_or_hash_query_if_required(record, active_policy)
    record["poisoning_guard_posture"] = detect_poisoning_risks(record, active_policy)
    record["outcome_classification"] = classify_query_outcome(record)
    return record


def validate_query_observation(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a query observation record."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required = {
        "schema_version",
        "query_observation_id",
        "observation_status",
        "query_text",
        "query_source",
        "search_mode",
        "local_index_mode",
        "result_count",
        "top_result_refs",
        "result_quality",
        "first_useful_result_rank",
        "failure_modes",
        "limitations",
        "privacy_posture",
        "poisoning_guard_posture",
        "review_gates",
        "truth_boundary",
        "product_boundary",
        "notes",
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if record.get("observation_status") not in ALLOWED_STATUSES:
        errors.append("observation_status is not allowed")
    if record.get("observation_status") not in CURRENT_ALLOWED_STATUSES:
        errors.append("current observation_status is not allowed")
    if record.get("query_source") not in ALLOWED_QUERY_SOURCES:
        errors.append("query_source is not allowed")
    if record.get("query_source") not in CURRENT_ALLOWED_QUERY_SOURCES:
        errors.append("current runtime cannot accept future query_source")
    if not isinstance(record.get("result_count"), int) or record.get("result_count", -1) < 0:
        errors.append("result_count must be a non-negative integer")
    if record.get("result_quality") not in ALLOWED_RESULT_QUALITIES:
        errors.append("result_quality is not allowed")
    rank = record.get("first_useful_result_rank")
    if rank is not None and (not isinstance(rank, int) or rank < 1):
        errors.append("first_useful_result_rank must be null or a positive integer")
    if not isinstance(record.get("top_result_refs"), list):
        errors.append("top_result_refs must be a list")

    failure_modes = record.get("failure_modes", [])
    if not isinstance(failure_modes, list):
        errors.append("failure_modes must be a list")
    else:
        unknown = sorted(str(mode) for mode in failure_modes if mode not in ALLOWED_FAILURE_MODES)
        if unknown:
            errors.append(f"failure_modes contains unknown values: {', '.join(unknown)}")

    privacy = record.get("privacy_posture", {})
    if not isinstance(privacy, Mapping):
        errors.append("privacy_posture must be an object")
    else:
        for key in sorted(PRIVACY_FALSE_FIELDS):
            if privacy.get(key) is not False:
                errors.append(f"privacy_posture.{key} must be false")
        detected = _privacy_risk_flags(record)
        declared = set(privacy.get("privacy_risks", []))
        missing_risks = sorted(detected - declared)
        if missing_risks:
            errors.append(f"privacy_posture missing detected risks: {', '.join(missing_risks)}")

    poisoning = record.get("poisoning_guard_posture", {})
    if not isinstance(poisoning, Mapping):
        errors.append("poisoning_guard_posture must be an object")
    elif poisoning.get("poisoning_guarded") is not True:
        errors.append("poisoning_guard_posture.poisoning_guarded must be true")

    for output in record.get("output_candidates", []):
        output_type = output.get("output_type") if isinstance(output, Mapping) else None
        if output_type in FORBIDDEN_OUTPUT_TYPES:
            errors.append(f"forbidden output candidate: {output_type}")
        if output_type not in ALLOWED_OUTPUT_TYPES:
            errors.append(f"unknown output candidate: {output_type}")
        if isinstance(output, Mapping) and output.get("requires_review") is not True:
            errors.append(f"output candidate {output_type} must require review")

    errors.extend(_check_true_map(record.get("review_gates", {}), REVIEW_TRUE_FIELDS, "review_gates"))
    errors.extend(_check_false_map(record.get("truth_boundary", {}), TRUTH_BOUNDARY_FALSE_FIELDS, "truth_boundary"))
    if isinstance(record.get("truth_boundary"), Mapping):
        if record["truth_boundary"].get("human_review_required_for_downstream_use") is not True:
            errors.append("truth_boundary.human_review_required_for_downstream_use must be true")
    errors.extend(_check_false_map(record.get("product_boundary", {}), PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    errors.extend(_scan_for_forbidden_claims(record))

    max_length = int(active_policy.get("max_query_length", 160))
    query_text = str(record.get("query_text", ""))
    if len(query_text) > max_length and "suspiciously_long_query" not in set(record.get("poisoning_guard_posture", {}).get("risk_flags", [])):
        errors.append("suspiciously long query must be flagged")

    return sorted(errors)


def summarize_query_observation(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "query_observation_id": record.get("query_observation_id"),
        "observation_status": record.get("observation_status"),
        "query_source": record.get("query_source"),
        "outcome_classification": classify_query_outcome(record),
        "result_count": record.get("result_count"),
        "result_quality": record.get("result_quality"),
        "first_useful_result_rank": record.get("first_useful_result_rank"),
        "failure_modes": list(record.get("failure_modes", [])),
        "privacy_risks": list(record.get("privacy_posture", {}).get("privacy_risks", [])),
        "poisoning_risks": list(record.get("poisoning_guard_posture", {}).get("risk_flags", [])),
        "review_required": record.get("truth_boundary", {}).get("human_review_required_for_downstream_use") is True,
        "truth_boundary": {
            "query_observation_is_public_truth": False,
            "query_observation_is_accepted_evidence": False,
            "query_observation_can_mutate_master_index": False,
        },
    }


def classify_query_outcome(record: Mapping[str, Any]) -> str:
    status = record.get("observation_status")
    quality = record.get("result_quality")
    result_count = record.get("result_count")
    first_useful_rank = record.get("first_useful_result_rank")
    if status == "policy_blocked" or quality == "blocked" or "policy_blocked" in record.get("failure_modes", []):
        return "policy_blocked"
    if status == "not_evaluable" or quality == "not_evaluable":
        return "not_evaluable"
    if result_count == 0 or quality == "empty":
        return "empty_result"
    if isinstance(first_useful_rank, int) or quality == "useful":
        return "useful_result"
    if quality in {"weak", "mixed"} or "weak_result" in record.get("failure_modes", []):
        return "weak_result"
    return "unknown"


def redact_or_hash_query_if_required(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_policy = policy or default_policy()
    updated = deepcopy(dict(record))
    query_text = str(updated.get("query_text", ""))
    normalized = normalize_query(query_text)
    privacy_risks = sorted(_privacy_risk_flags(updated))
    redacted = bool(privacy_risks)

    privacy = dict(updated.get("privacy_posture", {}))
    privacy.setdefault("raw_query_allowed", bool(active_policy.get("privacy", {}).get("raw_query_allowed_for_synthetic_fixtures", True)))
    privacy["raw_query_retained"] = False
    privacy["raw_public_query_logging_enabled"] = False
    privacy["public_telemetry_enabled"] = False
    privacy["accounts_required"] = False
    privacy["private_data_allowed"] = False
    privacy["browser_state_collection_allowed"] = False
    privacy["account_identity_collected"] = False
    privacy["location_collected"] = False
    privacy["privacy_filtered"] = redacted
    privacy["privacy_risks"] = privacy_risks
    privacy["query_hash"] = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    privacy["redacted_query_text"] = "<redacted>" if redacted else normalized
    updated["privacy_posture"] = privacy

    if redacted and updated.get("observation_status") != "policy_blocked":
        updated["observation_status"] = "privacy_filtered"
        failure_modes = set(updated.get("failure_modes", []))
        failure_modes.add("privacy_filtered")
        updated["failure_modes"] = sorted(failure_modes)

    return updated


def detect_poisoning_risks(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_policy = policy or default_policy()
    text = _record_text(record)
    risk_flags: set[str] = set()
    for label, pattern in PRIVACY_PATTERNS + POISONING_PATTERNS:
        if pattern.search(text):
            risk_flags.add(label)
    if _has_repeated_spam_tokens(str(record.get("query_text", ""))):
        risk_flags.add("repeated_spam_query")
    if len(str(record.get("query_text", ""))) > int(active_policy.get("max_query_length", 160)):
        risk_flags.add("suspiciously_long_query")
    return {
        "poisoning_guarded": True,
        "risk_flags": sorted(risk_flags),
        "risk_count": len(risk_flags),
        "decision": "flag_for_review" if risk_flags else "no_risk_detected",
        "public_decision_made": False,
        "notes": [
            "Poisoning guard flags risks only; it does not make public ranking or truth decisions."
        ],
    }


def normalize_query(query_text: str) -> str:
    return " ".join(str(query_text).strip().casefold().split())


def format_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Query Observation Summary",
        "",
        f"- query_observation_id: {summary.get('query_observation_id')}",
        f"- observation_status: {summary.get('observation_status')}",
        f"- outcome_classification: {summary.get('outcome_classification')}",
        f"- result_count: {summary.get('result_count')}",
        f"- result_quality: {summary.get('result_quality')}",
        f"- review_required: {str(summary.get('review_required')).lower()}",
        "- public_truth: false",
        "- accepted_evidence: false",
        "- master_index_mutation: false",
    ]
    return "\n".join(lines) + "\n"


def _build_from_input_model(source: Mapping[str, Any]) -> dict[str, Any]:
    query_text = str(source.get("query_text", ""))
    normalized = normalize_query(query_text)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "query_observation_id": source.get("query_observation_id") or f"query_observation.{digest[:16]}.v0",
        "base_contract_ref": BASE_CONTRACT_REF,
        "observation_status": source.get("observation_status", "recorded_local"),
        "query_text": query_text,
        "query_id_optional": source.get("query_id_optional"),
        "query_source": source.get("query_source", "explicit_test_fixture"),
        "query_context": source.get("query_context", "local explicit input"),
        "submitted_via": source.get("submitted_via", "explicit_json_input"),
        "search_mode": source.get("search_mode", "local_only"),
        "local_index_mode": source.get("local_index_mode", "fixture_or_report_only"),
        "result_count": int(source.get("result_count", 0)),
        "top_result_refs": list(source.get("top_result_refs", [])),
        "result_quality": source.get("result_quality", "empty"),
        "first_useful_result_rank": source.get("first_useful_result_rank"),
        "failure_modes": list(source.get("failure_modes", [])),
        "limitations": list(source.get("limitations", [])),
        "privacy_posture": dict(source.get("privacy_posture", {})),
        "poisoning_guard_posture": dict(source.get("poisoning_guard_posture", {})),
        "notes": list(source.get("notes", [])),
    }


def _observation_id(record: Mapping[str, Any]) -> str:
    normalized = normalize_query(str(record.get("query_text", "")))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"query_observation.{digest[:16]}.v0"


def _default_review_gates() -> dict[str, bool]:
    return {field: True for field in REVIEW_TRUE_FIELDS}


def _default_truth_boundary() -> dict[str, bool]:
    boundary = {field: False for field in TRUTH_BOUNDARY_FALSE_FIELDS}
    boundary["human_review_required_for_downstream_use"] = True
    return boundary


def _default_product_boundary() -> dict[str, bool]:
    return {field: False for field in PRODUCT_BOUNDARY_FALSE_FIELDS}


def _default_output_candidates() -> list[dict[str, Any]]:
    return [
        {
            "output_type": "miss_ledger_seed_future",
            "output_status": "review_gated_future",
            "requires_review": True,
            "created": False,
        },
        {
            "output_type": "search_need_seed_future",
            "output_status": "review_gated_future",
            "requires_review": True,
            "created": False,
        },
    ]


def _privacy_risk_flags(record: Mapping[str, Any]) -> set[str]:
    text = _record_text({"query_text": record.get("query_text"), "notes": record.get("notes", [])})
    flags: set[str] = set()
    for label, pattern in PRIVACY_PATTERNS:
        if pattern.search(text):
            flags.add(label)
    return flags


def _record_text(value: Any) -> str:
    strings: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            strings.append(node)
        elif isinstance(node, Mapping):
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return "\n".join(strings)


def _has_repeated_spam_tokens(text: str) -> bool:
    tokens = TOKEN_RE.findall(text.casefold())
    if len(tokens) < 6:
        return False
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    return any(count >= 5 for count in counts.values())


def _check_false_map(value: Any, fields: set[str], label: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label} must be an object"]
    return [f"{label}.{field} must be false" for field in sorted(fields) if value.get(field) is not False]


def _check_true_map(value: Any, fields: set[str], label: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{label} must be an object"]
    return [f"{label}.{field} must be true" for field in sorted(fields) if value.get(field) is not True]


def _scan_for_forbidden_claims(record: Mapping[str, Any]) -> list[str]:
    text = _record_text(record).casefold()
    errors: list[str] = []
    for phrase in sorted(CLAIM_PHRASES):
        if phrase in text:
            errors.append(f"forbidden claim phrase: {phrase}")
    return errors
