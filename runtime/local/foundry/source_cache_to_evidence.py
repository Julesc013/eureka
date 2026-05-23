"""Fixture-only source-cache to evidence-ledger bridge helpers.

The bridge maps explicit repo-local source cache records into reviewable
evidence ledger candidate records. It does not fetch sources, accept claims,
write persistent ledger state, or mutate public indexes.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.local.foundry import evidence_ledger, source_cache


SCHEMA_VERSION = "source_cache_to_evidence_bridge_result.v0"
REPORT_SCHEMA_VERSION = "source_cache_to_evidence_bridge_report.v0"

ALLOWED_BRIDGE_STATUSES = {
    "example_only",
    "mapped_local",
    "fixture_only",
    "needs_review",
    "evidence_candidate_created",
    "provenance_incomplete",
    "source_locator_missing",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "conflict_detected",
    "deferred",
    "not_evaluable",
    "rejected_future",
}

CURRENT_ALLOWED_BRIDGE_STATUSES = {
    "example_only",
    "mapped_local",
    "fixture_only",
    "needs_review",
    "evidence_candidate_created",
    "provenance_incomplete",
    "policy_blocked",
    "deferred",
    "not_evaluable",
}

ALLOWED_MAPPING_STATUSES = {
    "mapped_local",
    "evidence_candidate_created",
    "needs_review",
    "provenance_incomplete",
    "source_locator_missing",
    "policy_blocked",
    "deferred",
    "not_evaluable",
}

ALLOWED_OUTPUT_TYPES = {
    "bridge_result",
    "bridge_summary",
    "evidence_candidate_record",
    "provenance_gap_report",
    "conflict_report",
    "review_item_future",
}

FORBIDDEN_OUTPUT_TYPES = {
    "accepted_evidence_truth",
    "accepted_public_record",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
}

MAPPING_RULES = {
    "source_metadata": {"evidence_record_type": "metadata_claim", "claim_type": "metadata"},
    "source_locator": {"evidence_record_type": "source_observation", "claim_type": "source_observation"},
    "source_policy_record": {"evidence_record_type": "source_observation", "claim_type": "source_observation"},
    "source_health_record": {"evidence_record_type": "metadata_claim", "claim_type": "metadata"},
    "source_coverage_record": {"evidence_record_type": "metadata_claim", "claim_type": "metadata"},
    "source_lead_record": {"evidence_record_type": "source_observation", "claim_type": "source_observation"},
    "connector_fixture_record": {"evidence_record_type": "source_observation", "claim_type": "source_observation"},
    "source_identity_record": {"evidence_record_type": "identity_claim", "claim_type": "identity"},
    "source_limitations_record": {"evidence_record_type": "metadata_claim", "claim_type": "metadata"},
    "source_access_posture_record": {"evidence_record_type": "source_observation", "claim_type": "source_observation"},
}

FORBIDDEN_CONVERSIONS = {
    "source_cache_record_to_accepted_evidence_truth",
    "source_cache_record_to_accepted_public_record",
    "source_cache_record_to_master_index_record",
    "source_observation_to_accepted_truth",
    "metadata_claim_to_rights_clearance",
    "checksum_claim_to_authenticity_proof_without_review",
    "compatibility_claim_to_verified_compatibility_without_review",
    "AI_draft_to_evidence_truth",
    "contribution_claim_to_accepted_public_record",
}

TRUTH_BOUNDARY_FALSE_FIELDS = {
    "source_cache_record_is_public_truth",
    "bridge_output_is_accepted_evidence",
    "bridge_output_is_accepted_public_truth",
    "bridge_output_can_mutate_master_index",
    "bridge_output_can_claim_rights_clearance",
    "bridge_output_can_claim_malware_safety",
    "bridge_output_can_claim_verified_installability",
    "bridge_output_can_claim_exhaustive_global_search",
    "bridge_output_can_claim_production_readiness",
}

TRUTH_BOUNDARY_TRUE_FIELDS = {"human_review_required_for_downstream_use"}

PRODUCT_BOUNDARY_FALSE_FIELDS = {
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
    "changed_public_search_behavior",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}

REVIEW_GATE_TRUE_FIELDS = {
    "human_review_required",
    "candidate_store_review_required",
    "public_index_review_required",
    "pack_export_review_required",
    "master_index_review_required",
    "rights_review_required",
    "malware_safety_review_required",
    "installability_review_required",
    "privacy_review_required",
    "provenance_review_required",
}

FORBIDDEN_CLAIM_PHRASES = {
    "accepted public truth",
    "accepted evidence truth",
    "accepted public record",
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
    "hosted backend enabled",
    "source sync enabled",
    "live probe enabled",
    "download enabled",
    "upload enabled",
    "account enabled",
    "master-index mutation allowed",
    "ai draft evidence truth",
    "discussion derived truth",
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
        "allowed_source_cache_record_statuses": sorted(source_cache.ALLOWED_STATUSES),
        "current_allowed_source_cache_record_statuses": sorted(source_cache.CURRENT_ALLOWED_STATUSES),
        "allowed_source_cache_record_types": sorted(source_cache.ALLOWED_RECORD_TYPES),
        "current_allowed_source_cache_record_types": sorted(source_cache.CURRENT_ALLOWED_RECORD_TYPES),
        "allowed_output_evidence_types": sorted(evidence_ledger.CURRENT_ALLOWED_RECORD_TYPES),
        "allowed_bridge_statuses": sorted(ALLOWED_BRIDGE_STATUSES),
        "current_allowed_bridge_statuses": sorted(CURRENT_ALLOWED_BRIDGE_STATUSES),
        "allowed_mapping_statuses": sorted(ALLOWED_MAPPING_STATUSES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "forbidden_conversions": sorted(FORBIDDEN_CONVERSIONS),
        "mapping_rules": deepcopy(MAPPING_RULES),
        "review_required_before_downstream_use": True,
        "bridge_runtime_scope": "fixture_only",
        "live_source_access_enabled": False,
        "source_sync_enabled": False,
        "evidence_acceptance_enabled": False,
        "public_index_use_enabled": False,
        "master_index_mutation_enabled": False,
    }


def load_source_cache_record(path: str | Path) -> dict[str, Any]:
    """Load and normalize one explicit source cache record JSON file."""

    payload = source_cache.load_json(path)
    record = source_cache.build_source_cache_record(payload)
    errors = source_cache.validate_source_cache_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


def map_source_cache_record_to_evidence_candidates(
    record: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Map a source cache observation into reviewable evidence candidates."""

    active_policy = policy or default_policy()
    source_record = source_cache.build_source_cache_record(record)
    rule = dict(active_policy.get("mapping_rules", MAPPING_RULES)).get(source_record["source_cache_record_type"])
    if source_record["source_cache_record_status"] == "policy_blocked":
        candidate = _build_policy_blocked_candidate(source_record)
    elif not rule:
        candidate = _build_not_evaluable_candidate(source_record)
    else:
        candidate = _build_evidence_candidate(source_record, rule)

    normalized = evidence_ledger.build_evidence_ledger_record(candidate)
    return [normalized]


def build_bridge_result(
    source_cache_record: Mapping[str, Any],
    evidence_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic bridge result envelope without accepting claims."""

    active_policy = policy or default_policy()
    source_record = source_cache.build_source_cache_record(source_cache_record)
    normalized_candidates = [evidence_ledger.build_evidence_ledger_record(candidate) for candidate in evidence_candidates]
    mapping_results = [
        _mapping_result(source_record, candidate, index)
        for index, candidate in enumerate(normalized_candidates, start=1)
    ]
    status = _bridge_status(source_record, normalized_candidates, mapping_results)
    return {
        "schema_version": SCHEMA_VERSION,
        "bridge_result_id": f"source_cache_bridge.{source_record['source_cache_record_id']}.{_digest({'candidates': [c['evidence_record_id'] for c in normalized_candidates]})[:12]}.v0",
        "bridge_status": status,
        "source_cache_record_ref": source_record["source_cache_record_id"],
        "source_cache_record_type": source_record["source_cache_record_type"],
        "source_cache_record_status": source_record["source_cache_record_status"],
        "generated_evidence_candidates": normalized_candidates,
        "mapping_results": mapping_results,
        "provenance_summary": _provenance_summary(source_record),
        "source_locator_summary": source_record.get("source_locator", ""),
        "limitations": sorted(dict.fromkeys(_list_of_strings(source_record.get("source_limitations", [])) + _bridge_limitations(source_record))),
        "warnings": _bridge_warnings(source_record, normalized_candidates, active_policy),
        "review_gates": _review_gates(),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Bridge output is a review candidate only.",
            "No live source access, evidence acceptance, or master-index mutation is performed.",
        ],
    }


def validate_bridge_result(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a bridge result."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required_fields = {
        "schema_version",
        "bridge_result_id",
        "bridge_status",
        "source_cache_record_ref",
        "source_cache_record_type",
        "source_cache_record_status",
        "generated_evidence_candidates",
        "mapping_results",
        "review_gates",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required_fields):
        if field not in result:
            errors.append(f"missing required field: {field}")
    if result.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if result.get("bridge_status") not in active_policy.get("allowed_bridge_statuses", ALLOWED_BRIDGE_STATUSES):
        errors.append(f"bridge_status is not allowed: {result.get('bridge_status')}")
    if result.get("bridge_status") not in active_policy.get("current_allowed_bridge_statuses", CURRENT_ALLOWED_BRIDGE_STATUSES):
        errors.append(f"bridge_status is not allowed in current runtime: {result.get('bridge_status')}")
    if result.get("source_cache_record_type") not in active_policy.get("allowed_source_cache_record_types", source_cache.ALLOWED_RECORD_TYPES):
        errors.append(f"source_cache_record_type is not allowed: {result.get('source_cache_record_type')}")
    if result.get("source_cache_record_status") not in active_policy.get("allowed_source_cache_record_statuses", source_cache.ALLOWED_STATUSES):
        errors.append(f"source_cache_record_status is not allowed: {result.get('source_cache_record_status')}")

    candidates = result.get("generated_evidence_candidates", [])
    if not isinstance(candidates, list):
        errors.append("generated_evidence_candidates must be a list")
        candidates = []
    for index, candidate in enumerate(candidates, start=1):
        errors.extend(f"generated_evidence_candidates[{index}]: {error}" for error in validate_bridge_evidence_candidate(candidate, active_policy))

    mapping_results = result.get("mapping_results", [])
    if not isinstance(mapping_results, list):
        errors.append("mapping_results must be a list")
        mapping_results = []
    for index, mapping in enumerate(mapping_results, start=1):
        errors.extend(f"mapping_results[{index}]: {error}" for error in _validate_mapping_result(mapping, active_policy))

    errors.extend(detect_bridge_truth_boundary_violations(result, active_policy))
    errors.extend(detect_bridge_product_boundary_violations(result, active_policy))
    errors.extend(_detect_posture_violations(result))
    errors.extend(_scan_forbidden_claims(result))
    return sorted(dict.fromkeys(errors))


def validate_bridge_evidence_candidate(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors = evidence_ledger.validate_evidence_ledger_record(record)
    truth = record.get("truth_boundary", {})
    if isinstance(truth, Mapping):
        if truth.get("evidence_record_is_public_truth") is not False:
            errors.append("evidence candidate cannot be public truth")
        if truth.get("evidence_record_is_accepted_evidence") is not False:
            errors.append("evidence candidate cannot be accepted")
        if truth.get("evidence_record_can_mutate_master_index") is not False:
            errors.append("evidence candidate cannot mutate master index")
    else:
        errors.append("evidence candidate truth_boundary must be an object")
    return sorted(dict.fromkeys(errors))


def summarize_bridge_result(result: Mapping[str, Any]) -> dict[str, Any]:
    truth = result.get("truth_boundary", {})
    review = result.get("review_gates", {})
    candidates = result.get("generated_evidence_candidates", [])
    return {
        "bridge_result_id": result.get("bridge_result_id", ""),
        "bridge_status": result.get("bridge_status", ""),
        "source_cache_record_ref": result.get("source_cache_record_ref", ""),
        "source_cache_record_type": result.get("source_cache_record_type", ""),
        "source_cache_record_status": result.get("source_cache_record_status", ""),
        "generated_evidence_candidate_count": len(candidates) if isinstance(candidates, list) else 0,
        "generated_evidence_candidate_ids": [str(candidate.get("evidence_record_id", "")) for candidate in candidates if isinstance(candidate, Mapping)],
        "review_required": bool(review.get("human_review_required", True)),
        "bridge_output_is_accepted_evidence": bool(truth.get("bridge_output_is_accepted_evidence", False)),
        "bridge_output_is_accepted_public_truth": bool(truth.get("bridge_output_is_accepted_public_truth", False)),
        "bridge_output_can_mutate_master_index": bool(truth.get("bridge_output_can_mutate_master_index", False)),
        "warning_count": len(result.get("warnings", [])) if isinstance(result.get("warnings", []), list) else 0,
    }


def detect_bridge_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    truth = result.get("truth_boundary", {})
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


def detect_bridge_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    product = result.get("product_boundary", {})
    errors: list[str] = []
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    return errors


def detect_forbidden_source_cache_conversion(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    source_record = source_cache.build_source_cache_record(record)
    errors: list[str] = []
    errors.extend(source_cache.detect_truth_boundary_violations(source_record))
    errors.extend(source_cache.detect_product_boundary_violations(source_record))
    errors.extend(_scan_forbidden_claims(source_record))
    if source_record.get("source_cache_record_status") in {"rights_blocked", "risk_blocked"}:
        errors.append(f"source_cache_record_status cannot be bridged: {source_record.get('source_cache_record_status')}")
    return sorted(dict.fromkeys(errors))


def detect_missing_source_locator_or_provenance(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    source_record = source_cache.build_source_cache_record(record)
    errors: list[str] = []
    if not str(source_record.get("source_locator", "")).strip():
        errors.append("source_locator is required when available")
    if not str(source_record.get("source_cache_record_id", "")).strip():
        errors.append("source_cache_record_id is required for provenance")
    if not str(source_record.get("input_ref", "")).strip() and not source_record.get("related_candidate_refs"):
        errors.append("input_ref or related candidate refs should be present for provenance")
    return errors


def format_bridge_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Source Cache To Evidence Bridge Summary",
        "",
        f"- Bridge result: {summary.get('bridge_result_id', '')}",
        f"- Status: {summary.get('bridge_status', '')}",
        f"- Source cache record: {summary.get('source_cache_record_ref', '')}",
        f"- Source cache type: {summary.get('source_cache_record_type', '')}",
        f"- Evidence candidates: {summary.get('generated_evidence_candidate_count', 0)}",
        f"- Review required: {str(summary.get('review_required', True)).lower()}",
        f"- Accepted as evidence: {str(summary.get('bridge_output_is_accepted_evidence', False)).lower()}",
        f"- Public truth: {str(summary.get('bridge_output_is_accepted_public_truth', False)).lower()}",
        f"- Master-index mutation: {str(summary.get('bridge_output_can_mutate_master_index', False)).lower()}",
        "",
        "## Evidence Candidate IDs",
    ]
    ids = summary.get("generated_evidence_candidate_ids", [])
    if isinstance(ids, list) and ids:
        lines.extend(f"- {item}" for item in ids)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _build_evidence_candidate(source_record: Mapping[str, Any], rule: Mapping[str, str]) -> dict[str, Any]:
    record_type = str(rule.get("evidence_record_type", "metadata_claim"))
    claim_type = str(rule.get("claim_type", "metadata"))
    return {
        "schema_version": evidence_ledger.SCHEMA_VERSION,
        "input_id": source_record["source_cache_record_id"],
        "input_type": "source_cache_record",
        "input_ref": str(source_record.get("input_ref", "")),
        "input_status": source_record["source_cache_record_status"],
        "input_public_safe": True,
        "input_summary": str(source_record.get("input_summary", source_record.get("source_observation_summary", ""))),
        "evidence_record_status": _evidence_status_for_type(record_type),
        "evidence_record_type": record_type,
        "evidence_label": f"Evidence candidate from {source_record.get('source_label', source_record['source_cache_record_id'])}",
        "source_id": str(source_record.get("source_id", "")),
        "source_label": str(source_record.get("source_label", "")),
        "source_locator": str(source_record.get("source_locator", "")),
        "claim_type": claim_type,
        "claim_summary": _claim_summary_for(source_record, record_type, claim_type),
        "claim_value": _claim_value_for(source_record, claim_type),
        "claim_subject": str(source_record.get("source_id") or source_record.get("source_label") or source_record["source_cache_record_id"]),
        "observation_summary": str(source_record.get("source_observation_summary") or source_record.get("source_metadata_summary") or source_record.get("source_coverage_summary") or source_record.get("source_policy_status", "")),
        "provenance_summary": f"Mapped from explicit source cache record {source_record['source_cache_record_id']}.",
        "lineage_refs": [source_record["source_cache_record_id"]],
        "related_candidate_refs": _list_of_strings(source_record.get("related_candidate_refs", [])),
        "related_source_cache_refs_future": [source_record["source_cache_record_id"]],
        "related_search_need_refs": _list_of_strings(source_record.get("related_search_need_refs", [])),
        "related_workunit_refs": _list_of_strings(source_record.get("related_workunit_refs", [])),
        "related_pack_refs": _list_of_strings(source_record.get("related_pack_refs_future", [])),
        "confidence_or_uncertainty": "low_confidence_review_required",
        "conflict_summary": "",
        "limitations": sorted(dict.fromkeys(_list_of_strings(source_record.get("source_limitations", [])) + ["Bridge output requires human review before downstream use."])),
        "notes": [
            "Generated by the fixture-only source-cache bridge.",
            "No source fetch, source sync, or public index mutation occurred.",
        ],
    }


def _build_policy_blocked_candidate(source_record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": evidence_ledger.SCHEMA_VERSION,
        "input_id": source_record["source_cache_record_id"],
        "input_type": "source_cache_record",
        "input_ref": str(source_record.get("input_ref", "")),
        "input_status": "policy_blocked",
        "input_public_safe": True,
        "input_summary": str(source_record.get("input_summary", "Policy-blocked source cache record.")),
        "evidence_record_status": "policy_blocked",
        "evidence_record_type": "review_status_record",
        "evidence_label": f"Policy blocked bridge candidate from {source_record.get('source_label', source_record['source_cache_record_id'])}",
        "source_id": str(source_record.get("source_id", "")),
        "source_label": str(source_record.get("source_label", "")),
        "source_locator": str(source_record.get("source_locator", "fixture:source-cache:policy-blocked")),
        "claim_type": "review_status",
        "claim_summary": "Source cache record is policy-blocked and requires review before any evidence use.",
        "claim_subject": source_record["source_cache_record_id"],
        "observation_summary": str(source_record.get("source_observation_summary", "Policy-blocked source cache observation.")),
        "provenance_summary": f"Policy-blocked source cache record {source_record['source_cache_record_id']} was inspected locally.",
        "lineage_refs": [source_record["source_cache_record_id"]],
        "related_source_cache_refs_future": [source_record["source_cache_record_id"]],
        "limitations": sorted(dict.fromkeys(_list_of_strings(source_record.get("source_limitations", [])) + ["Policy block is preserved."])),
        "notes": ["No bridge promotion occurred."],
    }


def _build_not_evaluable_candidate(source_record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": evidence_ledger.SCHEMA_VERSION,
        "input_id": source_record["source_cache_record_id"],
        "input_type": "source_cache_record",
        "input_ref": str(source_record.get("input_ref", "")),
        "input_status": "needs_review",
        "input_public_safe": True,
        "input_summary": str(source_record.get("input_summary", "Source cache record has no bridge mapping.")),
        "evidence_record_status": "evidence_needed",
        "evidence_record_type": "review_status_record",
        "evidence_label": f"Not evaluable bridge candidate from {source_record.get('source_label', source_record['source_cache_record_id'])}",
        "source_id": str(source_record.get("source_id", "")),
        "source_label": str(source_record.get("source_label", "")),
        "source_locator": str(source_record.get("source_locator", "fixture:source-cache:not-evaluable")),
        "claim_type": "not_evaluable",
        "claim_summary": "No current bridge mapping exists for this source cache record type.",
        "claim_subject": source_record["source_cache_record_id"],
        "observation_summary": str(source_record.get("source_observation_summary", "")),
        "provenance_summary": f"Source cache record {source_record['source_cache_record_id']} was inspected locally.",
        "lineage_refs": [source_record["source_cache_record_id"]],
        "related_source_cache_refs_future": [source_record["source_cache_record_id"]],
        "limitations": ["No current mapping rule exists."],
        "notes": ["Record remains review-only."],
    }


def _mapping_result(source_record: Mapping[str, Any], candidate: Mapping[str, Any], index: int) -> dict[str, Any]:
    status = "policy_blocked" if candidate.get("evidence_record_status") == "policy_blocked" else "evidence_candidate_created"
    if candidate.get("claim_type") == "not_evaluable":
        status = "not_evaluable"
    provenance_status = "complete" if candidate.get("lineage_refs") and candidate.get("provenance_summary") else "provenance_incomplete"
    if not str(source_record.get("source_locator", "")).strip():
        provenance_status = "source_locator_missing"
    return {
        "mapping_id": f"mapping.{source_record['source_cache_record_id']}.{index}",
        "input_field": "source_cache_record",
        "input_value_summary": str(source_record.get("source_observation_summary") or source_record.get("source_metadata_summary") or source_record.get("source_coverage_summary") or source_record["source_cache_record_id"]),
        "output_evidence_type": str(candidate.get("evidence_record_type", "")),
        "output_claim_type": str(candidate.get("claim_type", "")),
        "output_status": status,
        "provenance_status": provenance_status,
        "review_required": True,
        "accepted_as_evidence": False,
        "accepted_as_public_truth": False,
        "master_index_mutation_allowed": False,
        "limitations": _list_of_strings(candidate.get("limitations", [])),
        "notes": ["Mapping is deterministic and fixture-only."],
    }


def _validate_mapping_result(mapping: Any, policy: Mapping[str, Any]) -> list[str]:
    if not isinstance(mapping, Mapping):
        return ["mapping result must be an object"]
    errors: list[str] = []
    required = {
        "mapping_id",
        "input_field",
        "output_evidence_type",
        "output_claim_type",
        "output_status",
        "provenance_status",
        "review_required",
        "accepted_as_evidence",
        "accepted_as_public_truth",
        "master_index_mutation_allowed",
    }
    for field in sorted(required):
        if field not in mapping:
            errors.append(f"missing required field: {field}")
    if mapping.get("output_status") not in policy.get("allowed_mapping_statuses", ALLOWED_MAPPING_STATUSES):
        errors.append(f"output_status is not allowed: {mapping.get('output_status')}")
    for field in ("accepted_as_evidence", "accepted_as_public_truth", "master_index_mutation_allowed"):
        if mapping.get(field) is not False:
            errors.append(f"{field} must be false")
    if mapping.get("review_required") is not True:
        errors.append("review_required must be true")
    return errors


def _bridge_status(source_record: Mapping[str, Any], candidates: Sequence[Mapping[str, Any]], mapping_results: Sequence[Mapping[str, Any]]) -> str:
    if source_record.get("source_cache_record_status") == "policy_blocked":
        return "policy_blocked"
    if not candidates:
        return "not_evaluable"
    if any(mapping.get("provenance_status") == "provenance_incomplete" for mapping in mapping_results):
        return "provenance_incomplete"
    if any(candidate.get("claim_type") == "not_evaluable" for candidate in candidates):
        return "not_evaluable"
    return "evidence_candidate_created"


def _bridge_warnings(source_record: Mapping[str, Any], candidates: Sequence[Mapping[str, Any]], policy: Mapping[str, Any]) -> list[str]:
    warnings: list[str] = []
    warnings.extend(detect_missing_source_locator_or_provenance(source_record, policy))
    warnings.extend(detect_forbidden_source_cache_conversion(source_record, policy))
    for candidate in candidates:
        warnings.extend(f"{candidate.get('evidence_record_id', 'candidate')}: {error}" for error in validate_bridge_evidence_candidate(candidate, policy))
    return sorted(dict.fromkeys(warnings))


def _bridge_limitations(source_record: Mapping[str, Any]) -> list[str]:
    limitations = [
        "Bridge output is not evidence acceptance.",
        "Bridge output cannot mutate a public index.",
    ]
    if source_record.get("source_cache_record_status") == "policy_blocked":
        limitations.append("Policy block is preserved in the bridge result.")
    return limitations


def _provenance_summary(source_record: Mapping[str, Any]) -> str:
    return f"Mapped from explicit source cache record {source_record['source_cache_record_id']} with locator {source_record.get('source_locator', '')}."


def _evidence_status_for_type(record_type: str) -> str:
    return {
        "metadata_claim": "metadata_claim_candidate",
        "identity_claim": "identity_claim_candidate",
        "compatibility_claim": "compatibility_claim_candidate",
        "checksum_claim": "checksum_claim_candidate",
        "filename_or_member_claim": "filename_or_member_claim_candidate",
        "source_locator": "source_locator_candidate",
        "source_observation": "source_observation_candidate",
        "pack_claim": "pack_claim_candidate",
        "conflict_record": "conflicting",
        "review_status_record": "needs_review",
    }.get(record_type, "evidence_candidate")


def _claim_summary_for(source_record: Mapping[str, Any], record_type: str, claim_type: str) -> str:
    if record_type == "source_observation":
        return f"Source observation candidate for {source_record.get('source_label', source_record['source_cache_record_id'])}."
    if source_record.get("source_cache_record_type") == "source_coverage_record":
        return f"Source coverage candidate: {source_record.get('source_coverage_summary', '')}"
    if source_record.get("source_cache_record_type") == "source_health_record":
        return f"Source health metadata candidate: {source_record.get('source_health_summary', '')}"
    if claim_type == "identity":
        return f"Source identity candidate for {source_record.get('source_label', '')}."
    return f"Metadata claim candidate from {source_record.get('source_label', source_record['source_cache_record_id'])}."


def _claim_value_for(source_record: Mapping[str, Any], claim_type: str) -> Any:
    if claim_type == "source_observation":
        return {
            "source_policy_status": source_record.get("source_policy_status", ""),
            "source_access_mode": source_record.get("source_access_mode", ""),
            "source_observation_summary": source_record.get("source_observation_summary", ""),
        }
    if claim_type == "identity":
        return {
            "source_id": source_record.get("source_id", ""),
            "source_label": source_record.get("source_label", ""),
            "source_family": source_record.get("source_family", ""),
        }
    return {
        "source_family": source_record.get("source_family", ""),
        "source_kind": source_record.get("source_kind", ""),
        "source_metadata_summary": source_record.get("source_metadata_summary", ""),
        "source_coverage_summary": source_record.get("source_coverage_summary", ""),
        "normalized_fields": source_record.get("normalized_fields", {}),
    }


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


def _detect_posture_violations(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    review = result.get("review_gates", {})
    if not isinstance(review, Mapping):
        errors.append("review_gates must be an object")
    else:
        for field in sorted(REVIEW_GATE_TRUE_FIELDS):
            if review.get(field) is not True:
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
