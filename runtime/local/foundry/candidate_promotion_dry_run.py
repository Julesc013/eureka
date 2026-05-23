"""Candidate promotion dry-run helpers.

Promotion dry-runs are decision rehearsals for local review records. They never
accept candidates, accept evidence, create public records, mutate public indexes,
or mutate the master index. This module is standard-library only and has no file,
network, provider, browser, telemetry, or runtime side effects.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.local.foundry import candidate_store, evidence_ledger, review_queue


SCHEMA_VERSION = "candidate_promotion_dry_run.v0"
REPORT_SCHEMA_VERSION = "candidate_promotion_dry_run_report.v0"

ALLOWED_STATUSES = {
    "example_only",
    "evaluated_local",
    "ready_for_promotion_dry_run",
    "missing_evidence",
    "needs_review",
    "duplicate_possible",
    "conflict_detected",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "identity_uncertain",
    "source_uncertain",
    "representation_uncertain",
    "deferred",
    "not_evaluable",
    "rejected",
}

READINESS_VALUES = {
    "ready_for_future_reviewed_record_proposal",
    "not_ready_missing_evidence",
    "not_ready_missing_review",
    "not_ready_policy_blocked",
    "not_ready_rights_blocked",
    "not_ready_risk_blocked",
    "not_ready_conflict_unresolved",
    "not_ready_duplicate_uncertain",
    "not_ready_identity_uncertain",
    "not_ready_source_uncertain",
    "not_ready_representation_uncertain",
    "not_evaluable",
}

BLOCKER_CATEGORIES = {
    "missing_evidence",
    "missing_review",
    "missing_source_locator",
    "missing_provenance",
    "unresolved_conflict",
    "duplicate_uncertain",
    "identity_uncertain",
    "compatibility_uncertain",
    "representation_uncertain",
    "rights_block",
    "risk_block",
    "policy_block",
    "privacy_block",
    "source_policy_missing",
    "evidence_not_accepted",
    "candidate_not_reviewed",
    "review_decision_missing",
    "master_index_gate_missing",
    "not_evaluable",
}

REQUIREMENT_STATUSES = {
    "satisfied_for_dry_run",
    "missing",
    "partial",
    "conflict_detected",
    "duplicate_uncertain",
    "blocked",
    "deferred",
    "not_applicable",
    "not_evaluable",
}

ALLOWED_INPUT_TYPES = {
    "candidate_record",
    "candidate_promotion_dry_run",
    "committed_promotion_fixture",
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
    "promotion_dry_run_record",
    "promotion_dry_run_summary",
    "reviewed_public_record_proposal_future",
    "promotion_blocker_report",
    "review_item_future",
    "workunit_seed_future",
}

FORBIDDEN_OUTPUT_TYPES = {
    "accepted_candidate",
    "accepted_evidence_truth",
    "accepted_public_record",
    "public_index_mutation",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
}

TRUTH_BOUNDARY_FALSE_FIELDS = {
    "promotion_dry_run_is_public_truth",
    "promotion_dry_run_accepts_candidate",
    "promotion_dry_run_accepts_evidence",
    "promotion_dry_run_creates_public_record",
    "promotion_dry_run_mutates_public_index",
    "promotion_dry_run_mutates_master_index",
    "promotion_dry_run_can_claim_rights_clearance",
    "promotion_dry_run_can_claim_malware_safety",
    "promotion_dry_run_can_claim_verified_installability",
    "promotion_dry_run_can_claim_exhaustive_global_search",
    "promotion_dry_run_can_claim_production_readiness",
}

TRUTH_BOUNDARY_TRUE_FIELDS = {"human_review_required_for_actual_promotion"}

PRODUCT_BOUNDARY_FALSE_FIELDS = {
    "implemented_actual_promotion",
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
    "mutated_public_index",
    "mutated_master_index",
    "changed_public_search_behavior",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}

PRODUCT_BOUNDARY_TRUE_FIELDS = {"implemented_candidate_promotion_dry_run"}

FORBIDDEN_CLAIM_PHRASES = {
    "accepted public truth",
    "accepted evidence truth",
    "accepted public record",
    "candidate is accepted",
    "evidence is accepted",
    "promoted candidate",
    "actual promotion complete",
    "public index mutation allowed",
    "master-index mutation allowed",
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
        "allowed_readiness_values": sorted(READINESS_VALUES),
        "allowed_blocker_categories": sorted(BLOCKER_CATEGORIES),
        "allowed_requirement_statuses": sorted(REQUIREMENT_STATUSES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "required_review_inputs": ["approve_for_promotion_dry_run"],
        "required_evidence_inputs": ["evidence_candidate"],
        "promotion_dry_run_only": True,
        "automatic_candidate_acceptance_allowed": False,
        "automatic_evidence_acceptance_allowed": False,
        "automatic_public_record_creation_allowed": False,
        "automatic_public_index_mutation_allowed": False,
        "automatic_master_index_mutation_allowed": False,
    }


def build_candidate_promotion_dry_run(input_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build or normalize a promotion dry-run from explicit local inputs."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(input_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        record = _normalize_record(source)
    else:
        record = _build_from_inputs(source, active_policy)

    record["truth_boundary"] = _truth_boundary(record.get("truth_boundary"))
    record["product_boundary"] = _product_boundary(record.get("product_boundary"))
    record["promotion_readiness"] = classify_promotion_readiness(record, active_policy)
    record["promotion_dry_run_status"] = _status_for_readiness(record)
    record["promotion_dry_run_id"] = record.get("promotion_dry_run_id") or f"candidate_promotion_dry_run.{_digest(record)[:12]}.v0"
    record.setdefault("warnings", [])
    record.setdefault("limitations", [])
    record.setdefault("notes", [])
    record["allowed_next_actions"] = _allowed_next_actions(record)
    record["forbidden_next_actions"] = _forbidden_next_actions(record)
    return record


def validate_candidate_promotion_dry_run(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a promotion dry-run record."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required_fields = {
        "schema_version",
        "promotion_dry_run_id",
        "promotion_dry_run_status",
        "promotion_readiness",
        "candidate_ref",
        "candidate_summary",
        "evidence_refs",
        "review_entry_refs",
        "evidence_requirement_results",
        "review_requirement_results",
        "identity_requirement_results",
        "conflict_requirement_results",
        "duplicate_requirement_results",
        "rights_risk_requirement_results",
        "policy_requirement_results",
        "blockers",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required_fields):
        if field not in record:
            errors.append(f"missing required field: {field}")
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if record.get("promotion_dry_run_status") not in active_policy.get("allowed_statuses", ALLOWED_STATUSES):
        errors.append(f"promotion_dry_run_status is not allowed: {record.get('promotion_dry_run_status')}")
    if record.get("promotion_readiness") not in active_policy.get("allowed_readiness_values", READINESS_VALUES):
        errors.append(f"promotion_readiness is not allowed: {record.get('promotion_readiness')}")
    for blocker in record.get("blockers", []):
        if not isinstance(blocker, Mapping):
            errors.append("blockers must contain objects")
            continue
        if blocker.get("blocker_category") not in active_policy.get("allowed_blocker_categories", BLOCKER_CATEGORIES):
            errors.append(f"blocker category is not allowed: {blocker.get('blocker_category')}")
    for group_name in _requirement_group_names():
        for requirement in record.get(group_name, []):
            if not isinstance(requirement, Mapping):
                errors.append(f"{group_name} must contain objects")
                continue
            if requirement.get("requirement_status") not in REQUIREMENT_STATUSES:
                errors.append(f"{group_name}.{requirement.get('requirement_id')} has invalid requirement_status")
            if requirement.get("pass_fail_unknown") not in {"pass", "fail", "unknown"}:
                errors.append(f"{group_name}.{requirement.get('requirement_id')} has invalid pass_fail_unknown")
    if record.get("promotion_readiness") == "ready_for_future_reviewed_record_proposal" and record.get("blockers"):
        errors.append("ready dry-run records must not contain blockers")
    if record.get("promotion_dry_run_status") == "ready_for_promotion_dry_run" and record.get("promotion_readiness") != "ready_for_future_reviewed_record_proposal":
        errors.append("ready_for_promotion_dry_run status requires ready readiness")
    errors.extend(detect_promotion_truth_boundary_violations(record, active_policy))
    errors.extend(detect_promotion_product_boundary_violations(record, active_policy))
    errors.extend(_detect_blocker_boundary_violations(record))
    errors.extend(_scan_forbidden_claims(record))
    return sorted(dict.fromkeys(errors))


def summarize_candidate_promotion_dry_run(record: Mapping[str, Any]) -> dict[str, Any]:
    truth = record.get("truth_boundary", {})
    return {
        "promotion_dry_run_id": record.get("promotion_dry_run_id", ""),
        "promotion_dry_run_status": record.get("promotion_dry_run_status", ""),
        "promotion_readiness": record.get("promotion_readiness", ""),
        "candidate_ref": record.get("candidate_ref", ""),
        "evidence_ref_count": len(record.get("evidence_refs", [])),
        "review_entry_ref_count": len(record.get("review_entry_refs", [])),
        "blocker_count": len(record.get("blockers", [])),
        "blocker_categories": sorted({str(blocker.get("blocker_category")) for blocker in record.get("blockers", []) if isinstance(blocker, Mapping)}),
        "promotion_dry_run_accepts_candidate": bool(truth.get("promotion_dry_run_accepts_candidate", False)),
        "promotion_dry_run_accepts_evidence": bool(truth.get("promotion_dry_run_accepts_evidence", False)),
        "promotion_dry_run_mutates_public_index": bool(truth.get("promotion_dry_run_mutates_public_index", False)),
        "promotion_dry_run_mutates_master_index": bool(truth.get("promotion_dry_run_mutates_master_index", False)),
    }


def evaluate_candidate_evidence_requirements(
    candidate: Mapping[str, Any],
    evidence_records: Sequence[Mapping[str, Any]],
    review_entries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    evidence_refs = [_evidence_ref(record) for record in evidence_records]
    if not evidence_records:
        return [_requirement("evidence.present", "evidence", "missing", [], ["missing_evidence"], "fail", "No evidence candidate records were provided.")]
    validation_errors: list[str] = []
    for record in evidence_records:
        validation_errors.extend(evidence_ledger.validate_evidence_ledger_record(record))
    if validation_errors:
        return [_requirement("evidence.valid", "evidence", "blocked", evidence_refs, ["evidence_not_accepted"], "fail", "Evidence candidate validation errors were detected.")]
    return [_requirement("evidence.present", "evidence", "satisfied_for_dry_run", evidence_refs, [], "pass", "Evidence candidates are present for dry-run review only.")]


def evaluate_candidate_review_requirements(
    candidate: Mapping[str, Any],
    review_entries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    refs = [_review_ref(entry) for entry in review_entries]
    if not review_entries:
        return [_requirement("review.present", "review", "missing", [], ["missing_review", "review_decision_missing"], "fail", "No review queue entries were provided.")]
    ready_entries = [
        entry
        for entry in review_entries
        if entry.get("review_decision") == "approve_for_promotion_dry_run"
        and entry.get("review_entry_status") == "ready_for_promotion_dry_run"
    ]
    if ready_entries:
        return [_requirement("review.dry_run_approval", "review", "satisfied_for_dry_run", refs, [], "pass", "Local review includes promotion dry-run approval.")]
    return [_requirement("review.dry_run_approval", "review", "partial", refs, ["missing_review", "review_decision_missing"], "fail", "Review entries do not include promotion dry-run approval.")]


def evaluate_candidate_identity_requirements(candidate: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if candidate.get("canonical_candidate_key") and candidate.get("candidate_label"):
        return [_requirement("identity.candidate_key", "identity", "satisfied_for_dry_run", [str(candidate.get("candidate_id", ""))], [], "pass", "Candidate has a canonical key and label.")]
    return [_requirement("identity.candidate_key", "identity", "partial", [str(candidate.get("candidate_id", ""))], ["identity_uncertain"], "fail", "Candidate identity remains incomplete.")]


def evaluate_candidate_conflict_requirements(
    candidate: Mapping[str, Any],
    evidence_records: Sequence[Mapping[str, Any]],
    review_entries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    conflict_detected = candidate.get("candidate_status") == "conflict_detected"
    conflict_detected = conflict_detected or any(record.get("evidence_record_status") == "conflicting" for record in evidence_records)
    conflict_detected = conflict_detected or any(entry.get("review_entry_status") == "conflict_detected" for entry in review_entries)
    refs = [_review_ref(entry) for entry in review_entries if entry.get("review_entry_status") == "conflict_detected"]
    if conflict_detected:
        return [_requirement("conflict.none_unresolved", "conflict", "conflict_detected", refs, ["unresolved_conflict"], "fail", "Conflict marker blocks dry-run readiness.")]
    return [_requirement("conflict.none_unresolved", "conflict", "satisfied_for_dry_run", [], [], "pass", "No unresolved conflict marker was provided.")]


def evaluate_candidate_duplicate_requirements(
    candidate: Mapping[str, Any],
    review_entries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    dedup = candidate.get("deduplication_summary", {})
    duplicate = isinstance(dedup, Mapping) and dedup.get("duplicate_possible") is True
    duplicate = duplicate or candidate.get("candidate_status") == "duplicate_possible"
    duplicate = duplicate or any(entry.get("review_entry_status") == "duplicate_possible" for entry in review_entries)
    refs = [_review_ref(entry) for entry in review_entries if entry.get("review_entry_status") == "duplicate_possible"]
    if duplicate:
        return [_requirement("duplicate.none_uncertain", "duplicate", "duplicate_uncertain", refs, ["duplicate_uncertain"], "fail", "Duplicate uncertainty blocks dry-run readiness.")]
    return [_requirement("duplicate.none_uncertain", "duplicate", "satisfied_for_dry_run", [], [], "pass", "No duplicate uncertainty marker was provided.")]


def evaluate_candidate_rights_risk_requirements(
    candidate: Mapping[str, Any],
    review_entries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    refs = [_review_ref(entry) for entry in review_entries]
    if candidate.get("candidate_status") == "rights_blocked" or any(entry.get("review_decision") == "rights_block" or entry.get("review_entry_status") == "rights_blocked" for entry in review_entries):
        return [_requirement("rights.none_blocked", "rights_risk", "blocked", refs, ["rights_block"], "fail", "Rights block prevents dry-run readiness.")]
    if candidate.get("candidate_status") == "risk_blocked" or any(entry.get("review_decision") == "risk_block" or entry.get("review_entry_status") == "risk_blocked" for entry in review_entries):
        return [_requirement("risk.none_blocked", "rights_risk", "blocked", refs, ["risk_block"], "fail", "Risk block prevents dry-run readiness.")]
    return [_requirement("rights_risk.review_required", "rights_risk", "satisfied_for_dry_run", refs, [], "pass", "Rights and risk review gates remain required; no blocking claim was provided.")]


def classify_promotion_readiness(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    categories = [str(blocker.get("blocker_category")) for blocker in record.get("blockers", []) if isinstance(blocker, Mapping)]
    priority = [
        ("policy_block", "not_ready_policy_blocked"),
        ("rights_block", "not_ready_rights_blocked"),
        ("risk_block", "not_ready_risk_blocked"),
        ("unresolved_conflict", "not_ready_conflict_unresolved"),
        ("duplicate_uncertain", "not_ready_duplicate_uncertain"),
        ("missing_evidence", "not_ready_missing_evidence"),
        ("missing_review", "not_ready_missing_review"),
        ("review_decision_missing", "not_ready_missing_review"),
        ("identity_uncertain", "not_ready_identity_uncertain"),
        ("missing_source_locator", "not_ready_source_uncertain"),
        ("representation_uncertain", "not_ready_representation_uncertain"),
        ("not_evaluable", "not_evaluable"),
    ]
    for category, readiness in priority:
        if category in categories:
            return readiness
    existing = record.get("promotion_readiness")
    if existing in READINESS_VALUES and existing != "not_evaluable":
        return str(existing)
    return "ready_for_future_reviewed_record_proposal"


def detect_promotion_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    truth = record.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        return ["truth_boundary must be an object"]
    for field in sorted(TRUTH_BOUNDARY_FALSE_FIELDS):
        if truth.get(field) is not False:
            errors.append(f"truth_boundary.{field} must be false")
    for field in sorted(TRUTH_BOUNDARY_TRUE_FIELDS):
        if truth.get(field) is not True:
            errors.append(f"truth_boundary.{field} must be true")
    return errors


def detect_promotion_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    product = record.get("product_boundary", {})
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    for field in sorted(PRODUCT_BOUNDARY_TRUE_FIELDS):
        if product.get(field) is not True:
            errors.append(f"product_boundary.{field} must be true")
    return errors


def format_candidate_promotion_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Candidate Promotion Dry-Run Summary",
        "",
        f"- promotion_dry_run_id: {summary.get('promotion_dry_run_id', '')}",
        f"- promotion_dry_run_status: {summary.get('promotion_dry_run_status', '')}",
        f"- promotion_readiness: {summary.get('promotion_readiness', '')}",
        f"- candidate_ref: {summary.get('candidate_ref', '')}",
        f"- evidence_ref_count: {summary.get('evidence_ref_count', 0)}",
        f"- review_entry_ref_count: {summary.get('review_entry_ref_count', 0)}",
        f"- blocker_count: {summary.get('blocker_count', 0)}",
        f"- blocker_categories: {', '.join(summary.get('blocker_categories', []))}",
        f"- accepts_candidate: {str(summary.get('promotion_dry_run_accepts_candidate', False)).lower()}",
        f"- accepts_evidence: {str(summary.get('promotion_dry_run_accepts_evidence', False)).lower()}",
        f"- mutates_public_index: {str(summary.get('promotion_dry_run_mutates_public_index', False)).lower()}",
        f"- mutates_master_index: {str(summary.get('promotion_dry_run_mutates_master_index', False)).lower()}",
        "",
    ]
    return "\n".join(lines)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_from_inputs(source: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    candidate = candidate_store.build_candidate_record(source.get("candidate") or source)
    evidence_records = [evidence_ledger.build_evidence_ledger_record(record) for record in _as_list(source.get("evidence_records"))]
    review_entries = [review_queue.build_review_queue_entry(entry) for entry in _as_list(source.get("review_entries"))]
    source_cache_records = [deepcopy(dict(record)) for record in _as_list(source.get("source_cache_records"))]
    bridge_results = [deepcopy(dict(record)) for record in _as_list(source.get("bridge_results"))]

    evidence_results = evaluate_candidate_evidence_requirements(candidate, evidence_records, review_entries, policy)
    review_results = evaluate_candidate_review_requirements(candidate, review_entries, policy)
    identity_results = evaluate_candidate_identity_requirements(candidate, policy)
    conflict_results = evaluate_candidate_conflict_requirements(candidate, evidence_records, review_entries, policy)
    duplicate_results = evaluate_candidate_duplicate_requirements(candidate, review_entries, policy)
    rights_results = evaluate_candidate_rights_risk_requirements(candidate, review_entries, policy)
    policy_results = _evaluate_policy_requirements(candidate, review_entries)
    blockers = _blockers_from_requirements(
        evidence_results
        + review_results
        + identity_results
        + conflict_results
        + duplicate_results
        + rights_results
        + policy_results
    )
    record = {
        "schema_version": SCHEMA_VERSION,
        "input_id": source.get("input_id", candidate.get("candidate_id", "candidate_promotion_input")),
        "input_type": source.get("input_type", "candidate_record"),
        "promotion_dry_run_status": source.get("promotion_dry_run_status", "evaluated_local"),
        "promotion_readiness": source.get("promotion_readiness", "not_evaluable"),
        "candidate_ref": candidate.get("candidate_id", ""),
        "candidate_summary": source.get("candidate_summary") or candidate.get("candidate_label", ""),
        "evidence_refs": [_evidence_ref(record) for record in evidence_records],
        "review_entry_refs": [_review_ref(entry) for entry in review_entries],
        "source_cache_refs": [str(record.get("source_cache_record_id", record.get("source_id", ""))) for record in source_cache_records],
        "source_cache_bridge_refs": [str(record.get("bridge_result_id", "")) for record in bridge_results],
        "related_search_need_refs": candidate.get("related_search_need_refs", []),
        "related_workunit_refs": candidate.get("related_workunit_refs", []),
        "related_pack_refs_future": candidate.get("pack_refs_future", []),
        "evidence_requirement_results": evidence_results,
        "review_requirement_results": review_results,
        "identity_requirement_results": identity_results,
        "conflict_requirement_results": conflict_results,
        "duplicate_requirement_results": duplicate_results,
        "rights_risk_requirement_results": rights_results,
        "policy_requirement_results": policy_results,
        "blockers": blockers,
        "warnings": source.get("warnings", []),
        "proposed_reviewed_record_summary_future": source.get("proposed_reviewed_record_summary_future", _proposal_summary(candidate)),
        "allowed_next_actions": [],
        "forbidden_next_actions": [],
        "limitations": source.get("limitations", ["Dry-run conclusion is not promotion."]),
        "truth_boundary": source.get("truth_boundary"),
        "product_boundary": source.get("product_boundary"),
        "notes": source.get("notes", ["Promotion dry-run is local review evidence only."]),
    }
    return record


def _normalize_record(source: Mapping[str, Any]) -> dict[str, Any]:
    record = deepcopy(dict(source))
    record.setdefault("input_id", record.get("promotion_dry_run_id", "candidate_promotion_dry_run"))
    record.setdefault("input_type", "candidate_promotion_dry_run")
    record.setdefault("evidence_refs", [])
    record.setdefault("review_entry_refs", [])
    record.setdefault("source_cache_refs", [])
    record.setdefault("source_cache_bridge_refs", [])
    record.setdefault("related_search_need_refs", [])
    record.setdefault("related_workunit_refs", [])
    record.setdefault("related_pack_refs_future", [])
    for group_name in _requirement_group_names():
        record.setdefault(group_name, [])
    record.setdefault("blockers", [])
    record.setdefault("warnings", [])
    record.setdefault("proposed_reviewed_record_summary_future", "")
    record.setdefault("limitations", [])
    record.setdefault("notes", [])
    return record


def _evaluate_policy_requirements(candidate: Mapping[str, Any], review_entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    refs = [_review_ref(entry) for entry in review_entries]
    if candidate.get("candidate_status") == "policy_blocked" or candidate.get("candidate_type") == "policy_blocked_candidate":
        return [_requirement("policy.none_blocked", "policy", "blocked", [str(candidate.get("candidate_id", ""))], ["policy_block"], "fail", "Candidate policy block prevents dry-run readiness.")]
    if any(entry.get("review_decision") == "policy_block" or entry.get("review_entry_status") == "policy_blocked" for entry in review_entries):
        return [_requirement("policy.none_blocked", "policy", "blocked", refs, ["policy_block"], "fail", "Review policy block prevents dry-run readiness.")]
    return [_requirement("policy.none_blocked", "policy", "satisfied_for_dry_run", refs, [], "pass", "No policy block was provided.")]


def _blockers_from_requirements(requirements: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    blockers: dict[str, dict[str, Any]] = {}
    for requirement in requirements:
        for category in requirement.get("blocker_refs", []):
            if category not in BLOCKER_CATEGORIES:
                continue
            blockers.setdefault(
                category,
                {
                    "blocker_id": f"promotion_blocker.{category}.v0",
                    "blocker_category": category,
                    "blocker_summary": str(requirement.get("notes", "")),
                    "evidence_or_review_refs": sorted(set(requirement.get("evidence_or_review_refs", []))),
                    "automatic_resolution_allowed": False,
                    "automatic_merge_allowed": False,
                    "automatic_delete_allowed": False,
                },
            )
    return [blockers[key] for key in sorted(blockers)]


def _requirement(
    requirement_id: str,
    requirement_type: str,
    status: str,
    refs: Sequence[str],
    blockers: Sequence[str],
    pass_fail_unknown: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "requirement_type": requirement_type,
        "requirement_status": status,
        "evidence_or_review_refs": sorted({ref for ref in refs if ref}),
        "pass_fail_unknown": pass_fail_unknown,
        "blocker_refs": sorted(set(blockers)),
        "limitations": ["Satisfied for dry-run does not mean accepted truth."] if status == "satisfied_for_dry_run" else [],
        "notes": notes,
    }


def _status_for_readiness(record: Mapping[str, Any]) -> str:
    readiness = record.get("promotion_readiness")
    mapping = {
        "ready_for_future_reviewed_record_proposal": "ready_for_promotion_dry_run",
        "not_ready_missing_evidence": "missing_evidence",
        "not_ready_missing_review": "needs_review",
        "not_ready_policy_blocked": "policy_blocked",
        "not_ready_rights_blocked": "rights_blocked",
        "not_ready_risk_blocked": "risk_blocked",
        "not_ready_conflict_unresolved": "conflict_detected",
        "not_ready_duplicate_uncertain": "duplicate_possible",
        "not_ready_identity_uncertain": "identity_uncertain",
        "not_ready_source_uncertain": "source_uncertain",
        "not_ready_representation_uncertain": "representation_uncertain",
        "not_evaluable": "not_evaluable",
    }
    return mapping.get(str(readiness), str(record.get("promotion_dry_run_status", "evaluated_local")))


def _truth_boundary(existing: Any = None) -> dict[str, Any]:
    truth = {field: False for field in TRUTH_BOUNDARY_FALSE_FIELDS}
    truth.update({field: True for field in TRUTH_BOUNDARY_TRUE_FIELDS})
    if isinstance(existing, Mapping):
        for field in TRUTH_BOUNDARY_FALSE_FIELDS:
            if field in existing:
                truth[field] = existing[field]
        for field in TRUTH_BOUNDARY_TRUE_FIELDS:
            if field in existing:
                truth[field] = existing[field]
    return truth


def _product_boundary(existing: Any = None) -> dict[str, Any]:
    product = {field: False for field in PRODUCT_BOUNDARY_FALSE_FIELDS}
    product.update({field: True for field in PRODUCT_BOUNDARY_TRUE_FIELDS})
    if isinstance(existing, Mapping):
        for field in PRODUCT_BOUNDARY_FALSE_FIELDS | PRODUCT_BOUNDARY_TRUE_FIELDS:
            if field in existing:
                product[field] = existing[field]
    return product


def _allowed_next_actions(record: Mapping[str, Any]) -> list[str]:
    if record.get("promotion_readiness") == "ready_for_future_reviewed_record_proposal":
        return ["prepare_reviewed_public_record_proposal_future", "request_human_review"]
    return ["request_more_evidence", "request_review", "defer", "reject_local_dry_run"]


def _forbidden_next_actions(record: Mapping[str, Any]) -> list[str]:
    return [
        "accept_candidate",
        "accept_evidence_truth",
        "create_public_record",
        "mutate_public_index",
        "mutate_master_index",
        "automatic_merge",
        "automatic_delete",
        "claim_rights_clearance",
        "claim_malware_safety",
        "claim_verified_installability",
        "hosted_moderation",
    ]


def _proposal_summary(candidate: Mapping[str, Any]) -> str:
    return f"Future reviewed-public-record proposal could be drafted for {candidate.get('candidate_id', '')} after separate review."


def _requirement_group_names() -> tuple[str, ...]:
    return (
        "evidence_requirement_results",
        "review_requirement_results",
        "identity_requirement_results",
        "conflict_requirement_results",
        "duplicate_requirement_results",
        "rights_risk_requirement_results",
        "policy_requirement_results",
    )


def _detect_blocker_boundary_violations(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for blocker in record.get("blockers", []):
        if not isinstance(blocker, Mapping):
            continue
        for field in ("automatic_resolution_allowed", "automatic_merge_allowed", "automatic_delete_allowed"):
            if blocker.get(field) is not False:
                errors.append(f"blocker.{blocker.get('blocker_category')}.{field} must be false")
    return errors


def _scan_forbidden_claims(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_scan_forbidden_claims(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_scan_forbidden_claims(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in sorted(FORBIDDEN_CLAIM_PHRASES):
            if phrase in lowered:
                errors.append(f"forbidden claim phrase at {path}: {phrase}")
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"private path pattern at {path}")
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(value):
                errors.append(f"credential-like pattern at {path}")
    return errors


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _evidence_ref(record: Mapping[str, Any]) -> str:
    return str(record.get("evidence_record_id") or record.get("input_id") or "")


def _review_ref(entry: Mapping[str, Any]) -> str:
    return str(entry.get("review_entry_id") or entry.get("input_id") or "")


def _digest(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
