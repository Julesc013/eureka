"""Local review queue helpers.

Review queue entries are governance records for candidates, source cache
records, evidence candidates, bridge results, and WorkUnit outputs. They are
not promotion, evidence acceptance, public truth, hosted moderation, or
master-index mutation.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "local_review_queue_entry.v0"
SNAPSHOT_SCHEMA_VERSION = "local_review_queue_snapshot.v0"
REPORT_SCHEMA_VERSION = "local_review_queue_runtime_report.v0"

ALLOWED_STATUSES = {
    "example_only",
    "queued",
    "needs_review",
    "under_review_future",
    "request_more_evidence",
    "duplicate_possible",
    "conflict_detected",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "rejected",
    "deferred",
    "superseded",
    "ready_for_promotion_dry_run",
    "accepted_public_future",
    "withdrawn_future",
    "takedown_pending_future",
}

CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "queued",
    "needs_review",
    "request_more_evidence",
    "duplicate_possible",
    "conflict_detected",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "rejected",
    "deferred",
    "ready_for_promotion_dry_run",
}

ALLOWED_SUBJECT_TYPES = {
    "candidate_record",
    "evidence_candidate",
    "source_cache_record",
    "source_cache_to_evidence_bridge_result",
    "search_need",
    "search_miss",
    "query_observation",
    "observation_candidate",
    "source_lead_candidate",
    "workunit",
    "workunit_result",
    "node_policy_evaluation",
    "pack_draft_future",
    "source_policy_decision_future",
    "connector_approval_future",
    "promotion_dry_run_future",
    "policy_blocked_subject",
    "not_evaluable_subject",
}

ALLOWED_DECISIONS = {
    "no_decision_yet",
    "approve_for_promotion_dry_run",
    "approve_as_source_lead",
    "approve_as_workunit_seed",
    "approve_as_search_need_seed",
    "approve_for_manual_observation",
    "request_more_evidence",
    "mark_duplicate_possible",
    "preserve_conflict",
    "reject",
    "defer",
    "policy_block",
    "rights_block",
    "risk_block",
    "not_evaluable",
    "accept_public_future",
    "withdraw_future",
    "supersede_future",
}

CURRENT_ALLOWED_DECISIONS = {
    "no_decision_yet",
    "approve_for_promotion_dry_run",
    "approve_as_source_lead",
    "approve_as_workunit_seed",
    "approve_as_search_need_seed",
    "approve_for_manual_observation",
    "request_more_evidence",
    "mark_duplicate_possible",
    "preserve_conflict",
    "reject",
    "defer",
    "policy_block",
    "rights_block",
    "risk_block",
    "not_evaluable",
}

ALLOWED_INPUT_TYPES = {
    "candidate_record",
    "evidence_candidate",
    "source_cache_record",
    "source_cache_to_evidence_bridge_result",
    "workunit_result",
    "node_policy_evaluation",
    "search_need",
    "search_miss",
    "query_observation",
    "observation_candidate",
    "review_queue_entry",
    "committed_review_fixture",
    "committed_public_data_summary",
}

FORBIDDEN_INPUT_TYPES = {
    "unapproved_live_source_result",
    "scraped_search_result",
    "scraped_forum_thread",
    "bulk_reddit_content",
    "private_user_file",
    "secret_or_credential",
    "executable_download",
    "installer_payload",
    "raw_browser_profile",
    "account_session_data",
    "telemetry_stream",
    "unreviewed_external_api_payload",
    "hosted_moderation_payload",
}

ALLOWED_OUTPUT_TYPES = {
    "review_queue_entry",
    "review_queue_summary",
    "review_queue_snapshot",
    "promotion_dry_run_allowance",
    "missing_evidence_report",
    "duplicate_review_report",
    "conflict_review_report",
    "review_item_future",
}

FORBIDDEN_OUTPUT_TYPES = {
    "accepted_public_record",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "master_index_mutation",
    "public_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
    "hosted_moderation_state",
}

TRUTH_BOUNDARY_FALSE_FIELDS = {
    "review_queue_snapshot_is_master_index",
    "review_entry_is_public_truth",
    "review_entry_accepts_evidence",
    "review_entry_accepts_candidate",
    "review_entry_mutates_master_index",
    "review_entry_allows_public_index_mutation",
    "review_entry_can_claim_rights_clearance",
    "review_entry_can_claim_malware_safety",
    "review_entry_can_claim_verified_installability",
    "review_entry_can_claim_exhaustive_global_search",
    "review_entry_can_claim_production_readiness",
}

TRUTH_BOUNDARY_TRUE_FIELDS = {"human_review_required_for_downstream_use"}

PRODUCT_BOUNDARY_FALSE_FIELDS = {
    "implemented_hosted_review_runtime",
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
    "enabled_model_provider_calls",
    "mutated_master_index",
    "changed_public_search_behavior",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
    "implemented_candidate_promotion",
    "implemented_evidence_acceptance",
    "implemented_public_truth_acceptance",
}

REVIEW_GATE_TRUE_FIELDS = {
    "human_review_required",
    "downstream_review_required",
    "promotion_dry_run_review_required",
    "candidate_review_required",
    "evidence_review_required",
    "source_cache_review_required",
    "public_index_review_required",
    "master_index_review_required",
    "rights_review_required",
    "malware_safety_review_required",
    "installability_review_required",
    "privacy_review_required",
    "conflict_review_required",
}

FORBIDDEN_CLAIM_PHRASES = {
    "accepted public truth",
    "accepted evidence truth",
    "accepted public record",
    "candidate is accepted",
    "evidence is accepted",
    "verified fact",
    "source is canonical",
    "rights clearance confirmed",
    "rights are cleared",
    "malware safe",
    "malware safety established",
    "installability is verified",
    "verified installability",
    "whole web was searched",
    "exhaustive global search",
    "production readiness",
    "telemetry enabled",
    "hosted moderation active",
    "hosted backend enabled",
    "source sync enabled",
    "live probe enabled",
    "download enabled",
    "upload enabled",
    "account enabled",
    "master-index mutation allowed",
    "automatic merge allowed",
}

PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"/home/[^/\s]+", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+", re.IGNORECASE),
    re.compile(r"\.aide\.local/", re.IGNORECASE),
    re.compile(r"\.local/eureka/", re.IGNORECASE),
    re.compile(r"\.cache/eureka/", re.IGNORECASE),
)

CREDENTIAL_PATTERNS = (
    re.compile(r"\b(api[_-]?key|secret|token|password|cookie|session)\b\s*[:=]", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9]{12,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{12,}\b"),
)


def default_policy() -> dict[str, Any]:
    return {
        "allowed_input_types": sorted(ALLOWED_INPUT_TYPES),
        "forbidden_input_types": sorted(FORBIDDEN_INPUT_TYPES),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "current_allowed_statuses": sorted(CURRENT_ALLOWED_STATUSES),
        "allowed_subject_types": sorted(ALLOWED_SUBJECT_TYPES),
        "allowed_decisions": sorted(ALLOWED_DECISIONS),
        "current_allowed_decisions": sorted(CURRENT_ALLOWED_DECISIONS),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "review_required_before_downstream_use": True,
        "public_review_disabled_current": True,
        "hosted_moderation_disabled_current": True,
        "evidence_acceptance_disabled_current": True,
        "candidate_acceptance_disabled_current": True,
        "public_index_use_disabled_current": True,
        "master_index_mutation_disabled_current": True,
    }


def build_review_queue_entry(input_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build or normalize a local review queue entry from explicit input."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(input_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        entry = _normalize_entry(source)
    else:
        entry = _build_from_source(source)

    entry["review_subject_type"] = classify_review_subject(entry, active_policy)
    entry["review_decision"] = classify_review_decision(entry, active_policy)
    entry["review_entry_status"] = classify_review_status(entry, active_policy)
    entry["review_entry_id"] = entry.get("review_entry_id") or f"review_queue.{entry['review_subject_type']}.{_digest(entry)[:12]}.v0"
    entry["truth_boundary"] = _truth_boundary(entry.get("truth_boundary"))
    entry["product_boundary"] = _product_boundary(entry.get("product_boundary"))
    entry["review_gates"] = _review_gates(entry.get("review_gates"))
    entry["promotion_readiness"] = _promotion_readiness(entry)
    entry["allowed_next_actions"] = _allowed_next_actions(entry)
    entry["forbidden_next_actions"] = _forbidden_next_actions(entry)
    entry.setdefault("required_evidence", [])
    entry.setdefault("missing_evidence", [])
    entry.setdefault("limitations", [])
    entry.setdefault("notes", [])
    return entry


def validate_review_queue_entry(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a review queue entry."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required_fields = {
        "schema_version",
        "review_entry_id",
        "review_entry_status",
        "review_subject_type",
        "review_subject_ref",
        "review_subject_summary",
        "review_decision",
        "decision_scope",
        "decision_rationale",
        "required_evidence",
        "missing_evidence",
        "promotion_readiness",
        "allowed_next_actions",
        "forbidden_next_actions",
        "review_gates",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required_fields):
        if field not in entry:
            errors.append(f"missing required field: {field}")
    if entry.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if entry.get("review_entry_status") not in active_policy.get("allowed_statuses", ALLOWED_STATUSES):
        errors.append(f"review_entry_status is not allowed: {entry.get('review_entry_status')}")
    if entry.get("review_entry_status") not in active_policy.get("current_allowed_statuses", CURRENT_ALLOWED_STATUSES):
        errors.append(f"review_entry_status is not allowed in current runtime: {entry.get('review_entry_status')}")
    if entry.get("review_subject_type") not in active_policy.get("allowed_subject_types", ALLOWED_SUBJECT_TYPES):
        errors.append(f"review_subject_type is not allowed: {entry.get('review_subject_type')}")
    if entry.get("review_decision") not in active_policy.get("allowed_decisions", ALLOWED_DECISIONS):
        errors.append(f"review_decision is not allowed: {entry.get('review_decision')}")
    if entry.get("review_decision") not in active_policy.get("current_allowed_decisions", CURRENT_ALLOWED_DECISIONS):
        errors.append(f"review_decision is not allowed in current runtime: {entry.get('review_decision')}")
    input_type = str(entry.get("input_type", "review_queue_entry"))
    if input_type in active_policy.get("forbidden_input_types", FORBIDDEN_INPUT_TYPES):
        errors.append(f"input_type is forbidden: {input_type}")
    if input_type not in active_policy.get("allowed_input_types", ALLOWED_INPUT_TYPES):
        errors.append(f"input_type is not allowed: {input_type}")
    errors.extend(detect_review_truth_boundary_violations(entry, active_policy))
    errors.extend(detect_review_product_boundary_violations(entry, active_policy))
    errors.extend(detect_review_missing_evidence_requirements(entry, active_policy))
    errors.extend(detect_review_promotion_blockers(entry, active_policy))
    errors.extend(_detect_review_gate_violations(entry))
    errors.extend(_scan_forbidden_claims(entry))
    return sorted(dict.fromkeys(errors))


def summarize_review_queue_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    truth = entry.get("truth_boundary", {})
    readiness = entry.get("promotion_readiness", {})
    return {
        "review_entry_id": entry.get("review_entry_id", ""),
        "review_entry_status": entry.get("review_entry_status", ""),
        "review_subject_type": entry.get("review_subject_type", ""),
        "review_subject_ref": entry.get("review_subject_ref", ""),
        "review_decision": entry.get("review_decision", ""),
        "promotion_dry_run_ready": bool(readiness.get("ready_for_promotion_dry_run", False)),
        "review_entry_is_public_truth": bool(truth.get("review_entry_is_public_truth", False)),
        "review_entry_accepts_evidence": bool(truth.get("review_entry_accepts_evidence", False)),
        "review_entry_accepts_candidate": bool(truth.get("review_entry_accepts_candidate", False)),
        "review_entry_mutates_master_index": bool(truth.get("review_entry_mutates_master_index", False)),
    }


def classify_review_subject(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    explicit = str(entry.get("review_subject_type", "")).strip()
    allowed = set((policy or default_policy()).get("allowed_subject_types", ALLOWED_SUBJECT_TYPES))
    if explicit in allowed:
        return explicit
    schema = str(entry.get("schema_version", ""))
    mapping = {
        "candidate_record.v0": "candidate_record",
        "local_evidence_ledger_record.v0": "evidence_candidate",
        "local_source_cache_record.v0": "source_cache_record",
        "source_cache_to_evidence_bridge_result.v0": "source_cache_to_evidence_bridge_result",
        "work_unit_result.v0": "workunit_result",
        "node_policy_evaluation_result.v0": "node_policy_evaluation",
        "search_need_record.v0": "search_need",
        "observation_candidate.v0": "observation_candidate",
    }
    return mapping.get(schema, "not_evaluable_subject")


def classify_review_status(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    explicit = str(entry.get("review_entry_status", "")).strip()
    allowed = set((policy or default_policy()).get("allowed_statuses", ALLOWED_STATUSES))
    if explicit in allowed:
        return explicit
    decision = str(entry.get("review_decision", ""))
    if decision == "approve_for_promotion_dry_run":
        return "ready_for_promotion_dry_run"
    if decision == "request_more_evidence":
        return "request_more_evidence"
    if decision == "mark_duplicate_possible":
        return "duplicate_possible"
    if decision == "preserve_conflict":
        return "conflict_detected"
    if decision == "reject":
        return "rejected"
    if decision == "defer" or decision == "not_evaluable":
        return "deferred"
    if decision == "policy_block":
        return "policy_blocked"
    if decision == "rights_block":
        return "rights_blocked"
    if decision == "risk_block":
        return "risk_blocked"
    text = " ".join(str(entry.get(key, "")) for key in ("review_subject_summary", "policy_summary", "decision_rationale")).lower()
    if "policy_blocked" in text or "policy blocked" in text:
        return "policy_blocked"
    return "needs_review"


def classify_review_decision(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    explicit = str(entry.get("review_decision", "")).strip()
    allowed = set((policy or default_policy()).get("allowed_decisions", ALLOWED_DECISIONS))
    if explicit in allowed:
        return explicit
    status = str(entry.get("review_entry_status", ""))
    mapping = {
        "request_more_evidence": "request_more_evidence",
        "duplicate_possible": "mark_duplicate_possible",
        "conflict_detected": "preserve_conflict",
        "policy_blocked": "policy_block",
        "rights_blocked": "rights_block",
        "risk_blocked": "risk_block",
        "rejected": "reject",
        "deferred": "defer",
        "ready_for_promotion_dry_run": "approve_for_promotion_dry_run",
    }
    return mapping.get(status, "no_decision_yet")


def detect_review_truth_boundary_violations(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    truth = entry.get("truth_boundary", {})
    errors: list[str] = []
    if not isinstance(truth, Mapping):
        return ["truth_boundary must be an object"]
    for field in sorted(TRUTH_BOUNDARY_FALSE_FIELDS):
        if truth.get(field) is not False:
            errors.append(f"truth_boundary.{field} must be false")
    for field in sorted(TRUTH_BOUNDARY_TRUE_FIELDS):
        if truth.get(field) is not True:
            errors.append(f"truth_boundary.{field} must be true")
    return errors


def detect_review_product_boundary_violations(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    product = entry.get("product_boundary", {})
    errors: list[str] = []
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    return errors


def detect_review_missing_evidence_requirements(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if entry.get("review_entry_status") == "request_more_evidence" or entry.get("review_decision") == "request_more_evidence":
        if not _list_of_strings(entry.get("missing_evidence", [])):
            errors.append("request_more_evidence entries require missing_evidence")
    return errors


def detect_review_promotion_blockers(entry: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    readiness = entry.get("promotion_readiness", {})
    if not isinstance(readiness, Mapping):
        return ["promotion_readiness must be an object"]
    if readiness.get("ready_for_promotion_dry_run") is True:
        if entry.get("review_decision") != "approve_for_promotion_dry_run":
            errors.append("promotion dry-run readiness requires approve_for_promotion_dry_run decision")
        if readiness.get("promotion_is_public_acceptance") is not False:
            errors.append("promotion_readiness.promotion_is_public_acceptance must be false")
        if readiness.get("master_index_mutation_allowed") is not False:
            errors.append("promotion_readiness.master_index_mutation_allowed must be false")
    duplicate = entry.get("duplicate_summary", {})
    if isinstance(duplicate, Mapping):
        for field in ("automatic_merge_allowed", "automatic_delete_allowed"):
            if duplicate.get(field) is not False:
                errors.append(f"duplicate_summary.{field} must be false")
    conflict = entry.get("conflict_summary", {})
    if isinstance(conflict, Mapping):
        for field in ("automatic_conflict_resolution_allowed", "automatic_merge_allowed"):
            if conflict.get(field) is not False:
                errors.append(f"conflict_summary.{field} must be false")
    rights = entry.get("rights_risk_summary", {})
    if isinstance(rights, Mapping):
        for field in (
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "verified_installability_claimed",
        ):
            if rights.get(field) is not False:
                errors.append(f"rights_risk_summary.{field} must be false")
    return errors


def build_review_queue_snapshot(entries: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_policy = policy or default_policy()
    normalized = [build_review_queue_entry(entry, active_policy) for entry in entries]
    status_counts = Counter(str(entry["review_entry_status"]) for entry in normalized)
    subject_counts = Counter(str(entry["review_subject_type"]) for entry in normalized)
    decision_counts = Counter(str(entry["review_decision"]) for entry in normalized)
    warnings: list[str] = []
    for entry in normalized:
        validation_errors = validate_review_queue_entry(entry, active_policy)
        warnings.extend(f"{entry['review_entry_id']}: {error}" for error in validation_errors)
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "review_queue_snapshot_id": f"review_queue_snapshot.{_digest({'ids': [entry['review_entry_id'] for entry in normalized]})[:12]}.v0",
        "snapshot_status": "review_required",
        "generated_from": "explicit_input_only",
        "review_entry_count": len(normalized),
        "entries": normalized,
        "status_counts": dict(sorted(status_counts.items())),
        "subject_type_counts": dict(sorted(subject_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "promotion_dry_run_ready_count": sum(1 for entry in normalized if entry["promotion_readiness"].get("ready_for_promotion_dry_run")),
        "request_more_evidence_count": sum(1 for entry in normalized if entry["review_entry_status"] == "request_more_evidence"),
        "blocked_count": sum(1 for entry in normalized if entry["review_entry_status"] in {"policy_blocked", "rights_blocked", "risk_blocked"}),
        "rejected_count": sum(1 for entry in normalized if entry["review_entry_status"] == "rejected"),
        "warnings": sorted(dict.fromkeys(warnings)),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Review queue snapshot is local governance evidence only.",
            "It is not hosted moderation, evidence acceptance, public truth, or a master index.",
        ],
    }


def summarize_review_queue(entries: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot = build_review_queue_snapshot(entries, policy)
    return {
        "review_entry_count": snapshot["review_entry_count"],
        "status_counts": snapshot["status_counts"],
        "subject_type_counts": snapshot["subject_type_counts"],
        "decision_counts": snapshot["decision_counts"],
        "promotion_dry_run_ready_count": snapshot["promotion_dry_run_ready_count"],
        "request_more_evidence_count": snapshot["request_more_evidence_count"],
        "blocked_count": snapshot["blocked_count"],
        "rejected_count": snapshot["rejected_count"],
        "review_queue_snapshot_is_master_index": snapshot["truth_boundary"]["review_queue_snapshot_is_master_index"],
        "warning_count": len(snapshot["warnings"]),
    }


def format_review_queue_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Review Queue Summary",
        "",
        f"- Review entries: {summary.get('review_entry_count', 0)}",
        f"- Promotion dry-run ready: {summary.get('promotion_dry_run_ready_count', 0)}",
        f"- Request more evidence: {summary.get('request_more_evidence_count', 0)}",
        f"- Blocked: {summary.get('blocked_count', 0)}",
        f"- Rejected: {summary.get('rejected_count', 0)}",
        f"- Warning count: {summary.get('warning_count', 0)}",
        f"- Master index: {str(summary.get('review_queue_snapshot_is_master_index', False)).lower()}",
        "",
        "## Status Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("status_counts", {})).items()))
    lines.extend(["", "## Subject Type Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("subject_type_counts", {})).items()))
    lines.extend(["", "## Decision Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("decision_counts", {})).items()))
    return "\n".join(lines) + "\n"


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _build_from_source(source: dict[str, Any]) -> dict[str, Any]:
    schema = str(source.get("schema_version", ""))
    if schema == "candidate_record.v0":
        return _entry_from_candidate(source)
    if schema == "local_evidence_ledger_record.v0":
        return _entry_from_evidence(source)
    if schema == "local_source_cache_record.v0":
        return _entry_from_source_cache(source)
    if schema == "source_cache_to_evidence_bridge_result.v0":
        return _entry_from_bridge(source)
    if schema == "work_unit_result.v0":
        return _entry_from_workunit_result(source)
    if schema == "node_policy_evaluation_result.v0":
        return _entry_from_node_policy_evaluation(source)
    if schema == "search_need_record.v0":
        return _base_entry(source, "search_need", "search_need", str(source.get("search_need_id", "search_need")), str(source.get("need_label", "SearchNeed review")))
    if schema == "observation_candidate.v0":
        return _base_entry(source, "observation_candidate", "observation_candidate", str(source.get("candidate_id", "observation_candidate")), str(source.get("candidate_label", "Observation candidate review")))
    return _base_entry(source, str(source.get("input_type", "committed_review_fixture")), str(source.get("review_subject_type", "not_evaluable_subject")), str(source.get("review_subject_ref", source.get("input_id", "review_subject"))), str(source.get("review_subject_summary", "Review queue fixture")))


def _entry_from_candidate(source: dict[str, Any]) -> dict[str, Any]:
    ref = str(source.get("candidate_id", "candidate"))
    entry = _base_entry(source, "candidate_record", "candidate_record", ref, str(source.get("candidate_label", ref)))
    entry["related_candidate_refs"] = [ref]
    if source.get("candidate_status") == "policy_blocked":
        entry["review_entry_status"] = "policy_blocked"
        entry["review_decision"] = "policy_block"
    return entry


def _entry_from_evidence(source: dict[str, Any]) -> dict[str, Any]:
    ref = str(source.get("evidence_record_id", "evidence_candidate"))
    entry = _base_entry(source, "evidence_candidate", "evidence_candidate", ref, str(source.get("evidence_label", ref)))
    entry["related_evidence_refs"] = [ref]
    if source.get("evidence_record_status") == "policy_blocked":
        entry["review_entry_status"] = "policy_blocked"
        entry["review_decision"] = "policy_block"
    return entry


def _entry_from_source_cache(source: dict[str, Any]) -> dict[str, Any]:
    ref = str(source.get("source_cache_record_id", "source_cache_record"))
    entry = _base_entry(source, "source_cache_record", "source_cache_record", ref, str(source.get("source_label", ref)))
    entry["related_source_cache_refs"] = [ref]
    if source.get("source_cache_record_status") == "policy_blocked":
        entry["review_entry_status"] = "policy_blocked"
        entry["review_decision"] = "policy_block"
    return entry


def _entry_from_bridge(source: dict[str, Any]) -> dict[str, Any]:
    ref = str(source.get("bridge_result_id", "bridge_result"))
    entry = _base_entry(source, "source_cache_to_evidence_bridge_result", "source_cache_to_evidence_bridge_result", ref, ref)
    entry["related_bridge_refs"] = [ref]
    evidence_refs = []
    for candidate in source.get("generated_evidence_candidates", []):
        if isinstance(candidate, Mapping) and candidate.get("evidence_record_id"):
            evidence_refs.append(str(candidate["evidence_record_id"]))
    entry["related_evidence_refs"] = evidence_refs
    if source.get("bridge_status") == "policy_blocked":
        entry["review_entry_status"] = "policy_blocked"
        entry["review_decision"] = "policy_block"
    return entry


def _entry_from_workunit_result(source: dict[str, Any]) -> dict[str, Any]:
    ref = str(source.get("workunit_result_id", "workunit_result"))
    entry = _base_entry(source, "workunit_result", "workunit_result", ref, str(source.get("workunit_result_label", ref)))
    entry["related_workunit_refs"] = [str(source.get("workunit_id", ref))]
    if source.get("workunit_result_status") == "policy_blocked":
        entry["review_entry_status"] = "policy_blocked"
        entry["review_decision"] = "policy_block"
    return entry


def _entry_from_node_policy_evaluation(source: dict[str, Any]) -> dict[str, Any]:
    ref = str(source.get("evaluation_result_id", "node_policy_evaluation"))
    entry = _base_entry(source, "node_policy_evaluation", "node_policy_evaluation", ref, str(source.get("decision", ref)))
    if str(source.get("decision", "")).startswith("blocked"):
        entry["review_entry_status"] = "policy_blocked"
        entry["review_decision"] = "policy_block"
    return entry


def _base_entry(source: dict[str, Any], input_type: str, subject_type: str, subject_ref: str, summary: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "input_id": str(source.get("input_id") or source.get("review_entry_id") or subject_ref),
        "input_type": input_type,
        "input_ref": str(source.get("input_ref", "")),
        "input_public_safe": bool(source.get("input_public_safe", True)),
        "review_entry_status": str(source.get("review_entry_status", "needs_review")),
        "review_subject_type": subject_type,
        "review_subject_ref": subject_ref,
        "review_subject_summary": summary,
        "review_decision": str(source.get("review_decision", "no_decision_yet")),
        "decision_scope": str(source.get("decision_scope", "local_review_only")),
        "decision_rationale": str(source.get("decision_rationale", "Review required before downstream use.")),
        "reviewer_posture": str(source.get("reviewer_posture", "not_reviewed")),
        "reviewed_at_note": str(source.get("reviewed_at_note", "No reviewed timestamp; fixture only.")),
        "required_evidence": _list_of_strings(source.get("required_evidence", ["source_or_candidate_context"])),
        "missing_evidence": _list_of_strings(source.get("missing_evidence", [])),
        "conflict_summary": source.get("conflict_summary", {"conflict_detected": False, "automatic_conflict_resolution_allowed": False, "automatic_merge_allowed": False}),
        "duplicate_summary": source.get("duplicate_summary", {"duplicate_possible": False, "automatic_merge_allowed": False, "automatic_delete_allowed": False}),
        "rights_risk_summary": source.get("rights_risk_summary", {"rights_review_required": True, "rights_clearance_claimed": False, "malware_safety_claimed": False, "verified_installability_claimed": False}),
        "policy_summary": str(source.get("policy_summary", "Local review policy applies.")),
        "promotion_readiness": source.get("promotion_readiness", {}),
        "allowed_next_actions": _list_of_strings(source.get("allowed_next_actions", [])),
        "forbidden_next_actions": _list_of_strings(source.get("forbidden_next_actions", [])),
        "related_candidate_refs": _list_of_strings(source.get("related_candidate_refs", [])),
        "related_evidence_refs": _list_of_strings(source.get("related_evidence_refs", [])),
        "related_source_cache_refs": _list_of_strings(source.get("related_source_cache_refs", [])),
        "related_bridge_refs": _list_of_strings(source.get("related_bridge_refs", [])),
        "related_workunit_refs": _list_of_strings(source.get("related_workunit_refs", [])),
        "related_pack_refs_future": _list_of_strings(source.get("related_pack_refs_future", [])),
        "review_gates": _review_gates(source.get("review_gates")),
        "limitations": _list_of_strings(source.get("limitations", [])),
        "truth_boundary": _truth_boundary(source.get("truth_boundary")),
        "product_boundary": _product_boundary(source.get("product_boundary")),
        "notes": _list_of_strings(source.get("notes", [])),
    }


def _normalize_entry(source: dict[str, Any]) -> dict[str, Any]:
    entry = _base_entry(
        source,
        str(source.get("input_type", "review_queue_entry")),
        str(source.get("review_subject_type", "")),
        str(source.get("review_subject_ref", "")),
        str(source.get("review_subject_summary", "Review queue entry")),
    )
    entry.update(source)
    return entry


def _promotion_readiness(entry: Mapping[str, Any]) -> dict[str, bool]:
    existing = entry.get("promotion_readiness", {})
    readiness = {
        "ready_for_promotion_dry_run": entry.get("review_decision") == "approve_for_promotion_dry_run",
        "promotion_is_public_acceptance": False,
        "evidence_acceptance_allowed": False,
        "candidate_acceptance_allowed": False,
        "public_index_mutation_allowed": False,
        "master_index_mutation_allowed": False,
    }
    if isinstance(existing, Mapping):
        for key in readiness:
            if key in existing:
                readiness[key] = bool(existing[key])
    return readiness


def _allowed_next_actions(entry: Mapping[str, Any]) -> list[str]:
    explicit = _list_of_strings(entry.get("allowed_next_actions", []))
    if explicit:
        return explicit
    decision = entry.get("review_decision")
    if decision == "approve_for_promotion_dry_run":
        return ["prepare_promotion_dry_run_future"]
    if decision == "request_more_evidence":
        return ["request_more_evidence"]
    if decision == "mark_duplicate_possible":
        return ["preserve_duplicate_marker"]
    if decision == "preserve_conflict":
        return ["preserve_conflict_marker"]
    if decision in {"reject", "policy_block", "rights_block", "risk_block", "defer", "not_evaluable"}:
        return ["preserve_review_record"]
    return ["review_locally", "request_more_evidence", "defer", "reject"]


def _forbidden_next_actions(entry: Mapping[str, Any]) -> list[str]:
    explicit = _list_of_strings(entry.get("forbidden_next_actions", []))
    base = [
        "accept_public_truth",
        "accept_evidence_truth",
        "accept_candidate_truth",
        "mutate_master_index",
        "mutate_public_index",
        "automatic_merge",
        "automatic_delete",
        "hosted_moderation",
        "claim_rights_clearance",
        "claim_malware_safety",
        "claim_verified_installability",
    ]
    return sorted(dict.fromkeys(explicit + base))


def _truth_boundary(existing: Any = None) -> dict[str, bool]:
    truth = {field: False for field in TRUTH_BOUNDARY_FALSE_FIELDS}
    truth.update({field: True for field in TRUTH_BOUNDARY_TRUE_FIELDS})
    if isinstance(existing, Mapping):
        for key in truth:
            if key in existing:
                truth[key] = bool(existing[key])
    return truth


def _product_boundary(existing: Any = None) -> dict[str, bool]:
    product = {field: False for field in PRODUCT_BOUNDARY_FALSE_FIELDS}
    if isinstance(existing, Mapping):
        for key in product:
            if key in existing:
                product[key] = bool(existing[key])
    return product


def _review_gates(existing: Any = None) -> dict[str, bool]:
    gates = {field: True for field in REVIEW_GATE_TRUE_FIELDS}
    if isinstance(existing, Mapping):
        for key, value in existing.items():
            if key.endswith("_required"):
                gates[str(key)] = bool(value)
    return gates


def _detect_review_gate_violations(entry: Mapping[str, Any]) -> list[str]:
    gates = entry.get("review_gates", {})
    errors: list[str] = []
    if not isinstance(gates, Mapping):
        return ["review_gates must be an object"]
    for field in sorted(REVIEW_GATE_TRUE_FIELDS):
        if gates.get(field) is not True:
            errors.append(f"review_gates.{field} must be true")
    return errors


def _list_of_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [str(value)]


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _scan_forbidden_claims(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in {"api_key", "secret", "credential", "password", "cookie", "session_token", "token"}:
                errors.append(f"{path}.{key}: credential-like field is forbidden")
            errors.extend(_scan_forbidden_claims(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_scan_forbidden_claims(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in sorted(FORBIDDEN_CLAIM_PHRASES):
            if phrase in lowered:
                errors.append(f"{path}: forbidden claim phrase: {phrase}")
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path}: private local path is forbidden")
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path}: credential-like text is forbidden")
    return errors
