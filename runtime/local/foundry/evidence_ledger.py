"""Fixture-only local evidence ledger helpers.

Evidence ledger records are evidence candidates and provenance events, not
accepted evidence, public truth, source-cache bridge output, or master-index
records. This module is standard-library only and has no file, network,
provider, browser, telemetry, or runtime side effects.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "local_evidence_ledger_record.v0"
SNAPSHOT_SCHEMA_VERSION = "local_evidence_ledger_snapshot.v0"
REPORT_SCHEMA_VERSION = "local_evidence_ledger_runtime_report.v0"

ALLOWED_STATUSES = {
    "example_only",
    "fixture_only",
    "recorded_local",
    "normalized",
    "evidence_candidate",
    "metadata_claim_candidate",
    "identity_claim_candidate",
    "compatibility_claim_candidate",
    "checksum_claim_candidate",
    "filename_or_member_claim_candidate",
    "source_observation_candidate",
    "source_locator_candidate",
    "pack_claim_candidate",
    "contribution_claim_candidate",
    "conflicting",
    "needs_review",
    "evidence_needed",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "stale",
    "superseded",
    "deferred",
    "accepted_public_future",
    "rejected_future",
}

CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "fixture_only",
    "recorded_local",
    "normalized",
    "evidence_candidate",
    "metadata_claim_candidate",
    "identity_claim_candidate",
    "compatibility_claim_candidate",
    "checksum_claim_candidate",
    "filename_or_member_claim_candidate",
    "source_observation_candidate",
    "source_locator_candidate",
    "pack_claim_candidate",
    "conflicting",
    "needs_review",
    "evidence_needed",
    "policy_blocked",
    "deferred",
}

ALLOWED_RECORD_TYPES = {
    "source_observation",
    "metadata_claim",
    "identity_claim",
    "compatibility_claim",
    "checksum_claim",
    "filename_or_member_claim",
    "source_locator",
    "manual_observation_claim",
    "pack_claim",
    "contribution_claim",
    "conflict_record",
    "review_status_record",
    "provenance_link",
    "source_cache_derived_claim_future",
    "ai_draft_future",
    "discussion_derived_future",
}

CURRENT_ALLOWED_RECORD_TYPES = {
    "source_observation",
    "metadata_claim",
    "identity_claim",
    "compatibility_claim",
    "checksum_claim",
    "filename_or_member_claim",
    "source_locator",
    "manual_observation_claim",
    "pack_claim",
    "contribution_claim",
    "conflict_record",
    "review_status_record",
    "provenance_link",
}

ALLOWED_CLAIM_TYPES = {
    "source_observation",
    "metadata",
    "identity",
    "compatibility",
    "checksum",
    "filename_or_member",
    "source_locator",
    "manual_observation",
    "pack_claim",
    "contribution_claim",
    "conflict",
    "review_status",
    "provenance",
    "not_evaluable",
}

ALLOWED_INPUT_TYPES = {
    "committed_evidence_fixture",
    "committed_pack_example",
    "committed_candidate_example",
    "committed_source_cache_example",
    "committed_audit_report",
    "committed_public_data_summary",
    "candidate_record",
    "source_cache_record",
    "search_need_record",
    "workunit_result",
    "node_policy_evaluation",
    "evidence_pack_example",
    "manual_observation_record_future",
    "source_cache_bridge_result_future",
    "contribution_pack_future",
    "evidence_ledger_record",
}

CURRENT_ALLOWED_INPUT_TYPES = {
    "committed_evidence_fixture",
    "committed_pack_example",
    "committed_candidate_example",
    "committed_source_cache_example",
    "committed_audit_report",
    "committed_public_data_summary",
    "candidate_record",
    "source_cache_record",
    "search_need_record",
    "workunit_result",
    "node_policy_evaluation",
    "evidence_pack_example",
    "evidence_ledger_record",
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
    "AI_output_claiming_truth",
}

ALLOWED_OUTPUT_TYPES = {
    "evidence_ledger_record",
    "evidence_ledger_summary",
    "evidence_ledger_snapshot",
    "provenance_report",
    "conflict_report",
    "review_item_future",
    "candidate_store_use_request_future",
    "evidence_pack_draft_future",
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

TRUTH_BOUNDARY_FALSE_FIELDS = {
    "evidence_ledger_snapshot_is_master_index",
    "evidence_record_is_public_truth",
    "evidence_record_is_accepted_evidence",
    "evidence_record_can_mutate_master_index",
    "evidence_record_can_claim_rights_clearance",
    "evidence_record_can_claim_malware_safety",
    "evidence_record_can_claim_verified_installability",
    "evidence_record_can_claim_exhaustive_global_search",
    "evidence_record_can_claim_production_readiness",
}

TRUTH_BOUNDARY_TRUE_FIELDS = {"human_review_required_for_downstream_use"}

PRODUCT_BOUNDARY_FALSE_FIELDS = {
    "implemented_source_cache_bridge",
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
    "conflict_review_required",
}

FORBIDDEN_CLAIM_PHRASES = {
    "accepted public truth",
    "accepted evidence truth",
    "accepted evidence",
    "accepted public record",
    "verified fact",
    "object is verified",
    "source is canonical truth",
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
        "allowed_input_types": sorted(ALLOWED_INPUT_TYPES),
        "current_allowed_input_types": sorted(CURRENT_ALLOWED_INPUT_TYPES),
        "forbidden_input_types": sorted(FORBIDDEN_INPUT_TYPES),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "current_allowed_statuses": sorted(CURRENT_ALLOWED_STATUSES),
        "allowed_record_types": sorted(ALLOWED_RECORD_TYPES),
        "current_allowed_record_types": sorted(CURRENT_ALLOWED_RECORD_TYPES),
        "allowed_claim_types": sorted(ALLOWED_CLAIM_TYPES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "review_required_before_downstream_use": True,
        "source_cache_bridge_disabled_current": True,
        "evidence_acceptance_disabled_current": True,
        "public_index_use_disabled_current": True,
        "master_index_mutation_disabled_current": True,
    }


def build_evidence_ledger_record(input_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build or normalize a fixture-only evidence ledger record from explicit input."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(input_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        record = _normalize_record(source)
    else:
        record = _build_from_source(source)

    record["evidence_record_type"] = classify_evidence_record_type(record, active_policy)
    record["evidence_record_status"] = classify_evidence_record_status(record, active_policy)
    if record.get("input_type") in FORBIDDEN_INPUT_TYPES:
        record["evidence_record_status"] = "policy_blocked"
    record["claim_type"] = _normalize_claim_type(record.get("claim_type"), record["evidence_record_type"])
    record["evidence_record_id"] = record.get("evidence_record_id") or f"evidence.{record['evidence_record_type']}.{_digest(record)[:12]}.v0"
    record["truth_boundary"] = _truth_boundary(record.get("truth_boundary"))
    record["product_boundary"] = _product_boundary(record.get("product_boundary"))
    record["review_gates"] = _review_gates(record.get("review_gates"))
    record["privacy_posture"] = _privacy_posture(record.get("privacy_posture"))
    record["rights_risk_posture"] = _rights_risk_posture(record.get("rights_risk_posture"))
    record.setdefault("limitations", [])
    record.setdefault("notes", [])
    return record


def validate_evidence_ledger_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for an evidence ledger record."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required_fields = {
        "schema_version",
        "evidence_record_id",
        "evidence_record_status",
        "evidence_record_type",
        "evidence_label",
        "source_id",
        "source_label",
        "source_locator",
        "claim_type",
        "claim_summary",
        "claim_subject",
        "observation_summary",
        "provenance_summary",
        "review_gates",
        "privacy_posture",
        "rights_risk_posture",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required_fields):
        if field not in record:
            errors.append(f"missing required field: {field}")
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if record.get("evidence_record_status") not in active_policy.get("allowed_statuses", ALLOWED_STATUSES):
        errors.append(f"evidence_record_status is not allowed: {record.get('evidence_record_status')}")
    if record.get("evidence_record_status") not in active_policy.get("current_allowed_statuses", CURRENT_ALLOWED_STATUSES):
        errors.append(f"evidence_record_status is not allowed in current runtime: {record.get('evidence_record_status')}")
    if record.get("evidence_record_type") not in active_policy.get("allowed_record_types", ALLOWED_RECORD_TYPES):
        errors.append(f"evidence_record_type is not allowed: {record.get('evidence_record_type')}")
    if record.get("evidence_record_type") not in active_policy.get("current_allowed_record_types", CURRENT_ALLOWED_RECORD_TYPES):
        errors.append(f"evidence_record_type is not allowed in current runtime: {record.get('evidence_record_type')}")
    if record.get("claim_type") not in active_policy.get("allowed_claim_types", ALLOWED_CLAIM_TYPES):
        errors.append(f"claim_type is not allowed: {record.get('claim_type')}")
    input_type = str(record.get("input_type", "evidence_ledger_record"))
    if input_type in FORBIDDEN_INPUT_TYPES:
        errors.append(f"input_type is forbidden: {input_type}")
    if input_type not in active_policy.get("current_allowed_input_types", CURRENT_ALLOWED_INPUT_TYPES):
        errors.append(f"input_type is not allowed in current runtime: {input_type}")
    errors.extend(detect_evidence_truth_boundary_violations(record, active_policy))
    errors.extend(detect_evidence_product_boundary_violations(record, active_policy))
    errors.extend(detect_provenance_gaps(record, active_policy))
    errors.extend(detect_conflict_requirements(record, active_policy))
    errors.extend(_detect_posture_violations(record))
    errors.extend(_scan_forbidden_claims(record))
    return sorted(dict.fromkeys(errors))


def summarize_evidence_ledger_record(record: Mapping[str, Any]) -> dict[str, Any]:
    truth = record.get("truth_boundary", {})
    product = record.get("product_boundary", {})
    review = record.get("review_gates", {})
    return {
        "evidence_record_id": record.get("evidence_record_id", ""),
        "evidence_record_status": record.get("evidence_record_status", ""),
        "evidence_record_type": record.get("evidence_record_type", ""),
        "evidence_label": record.get("evidence_label", ""),
        "claim_type": record.get("claim_type", ""),
        "claim_subject": record.get("claim_subject", ""),
        "source_id": record.get("source_id", ""),
        "review_required": bool(review.get("human_review_required", True)),
        "evidence_record_is_public_truth": bool(truth.get("evidence_record_is_public_truth", False)),
        "evidence_record_is_accepted_evidence": bool(truth.get("evidence_record_is_accepted_evidence", False)),
        "evidence_record_can_mutate_master_index": bool(truth.get("evidence_record_can_mutate_master_index", False)),
        "implemented_source_cache_bridge": bool(product.get("implemented_source_cache_bridge", False)),
    }


def classify_evidence_record_type(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    explicit = str(record.get("evidence_record_type", "")).strip()
    allowed = set((policy or default_policy()).get("allowed_record_types", ALLOWED_RECORD_TYPES))
    if explicit in allowed:
        return explicit
    claim_type = str(record.get("claim_type", "")).strip()
    mapping = {
        "metadata": "metadata_claim",
        "identity": "identity_claim",
        "compatibility": "compatibility_claim",
        "checksum": "checksum_claim",
        "filename_or_member": "filename_or_member_claim",
        "source_locator": "source_locator",
        "pack_claim": "pack_claim",
        "conflict": "conflict_record",
        "provenance": "provenance_link",
    }
    return mapping.get(claim_type, "metadata_claim")


def classify_evidence_record_status(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    explicit = str(record.get("evidence_record_status", "")).strip()
    allowed = set((policy or default_policy()).get("allowed_statuses", ALLOWED_STATUSES))
    if explicit in allowed:
        return explicit
    record_type = str(record.get("evidence_record_type", ""))
    status_by_type = {
        "metadata_claim": "metadata_claim_candidate",
        "identity_claim": "identity_claim_candidate",
        "compatibility_claim": "compatibility_claim_candidate",
        "checksum_claim": "checksum_claim_candidate",
        "filename_or_member_claim": "filename_or_member_claim_candidate",
        "source_locator": "source_locator_candidate",
        "pack_claim": "pack_claim_candidate",
        "conflict_record": "conflicting",
    }
    return status_by_type.get(record_type, "evidence_candidate")


def detect_evidence_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    truth = record.get("truth_boundary", {})
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


def detect_evidence_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    product = record.get("product_boundary", {})
    errors: list[str] = []
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    return errors


def detect_provenance_gaps(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if not str(record.get("claim_subject", "")).strip():
        errors.append("claim_subject is required")
    if not str(record.get("provenance_summary", "")).strip() and not record.get("lineage_refs"):
        limitations = " ".join(_list_of_strings(record.get("limitations", []))).lower()
        if "missing provenance" not in limitations:
            errors.append("missing provenance requires limitation")
    if _contains_url_like_locator(record.get("source_locator")):
        errors.append("source_locator must be a repo-local fixture locator, not a live URL")
    return errors


def detect_conflict_requirements(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    is_conflict = record.get("evidence_record_status") == "conflicting" or record.get("evidence_record_type") == "conflict_record"
    conflict = record.get("conflict_summary", "")
    if is_conflict and not conflict:
        errors.append("conflicting evidence records require conflict_summary")
    if isinstance(conflict, Mapping):
        for field in ("automatic_conflict_resolution_allowed", "automatic_merge_allowed"):
            if conflict.get(field) is not False:
                errors.append(f"conflict_summary.{field} must be false")
        if conflict.get("conflict_preservation_required") is not True:
            errors.append("conflict_summary.conflict_preservation_required must be true")
    return errors


def build_evidence_ledger_snapshot(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_policy = policy or default_policy()
    normalized = [build_evidence_ledger_record(record, active_policy) for record in records]
    status_counts = Counter(str(record["evidence_record_status"]) for record in normalized)
    type_counts = Counter(str(record["evidence_record_type"]) for record in normalized)
    claim_counts = Counter(str(record.get("claim_type", "")) for record in normalized)
    source_counts = Counter(str(record.get("source_id", "")) for record in normalized)
    warnings: list[str] = []
    for record in normalized:
        warnings.extend(f"{record['evidence_record_id']}: {error}" for error in validate_evidence_ledger_record(record, active_policy))
    conflicting_ids = [record["evidence_record_id"] for record in normalized if record["evidence_record_status"] == "conflicting" or record["evidence_record_type"] == "conflict_record"]
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "evidence_ledger_snapshot_id": f"evidence_ledger_snapshot.{_digest({'ids': [r['evidence_record_id'] for r in normalized]})[:12]}.v0",
        "snapshot_status": "review_required",
        "generated_from": "explicit_input_only",
        "evidence_record_count": len(normalized),
        "records": normalized,
        "status_counts": dict(sorted(status_counts.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "claim_type_counts": dict(sorted(claim_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "conflict_summary": {
            "conflict_preservation_required": True,
            "automatic_conflict_resolution_allowed": False,
            "automatic_merge_allowed": False,
            "conflicting_record_count": len(conflicting_ids),
            "conflicting_record_ids": sorted(conflicting_ids),
        },
        "warnings": sorted(dict.fromkeys(warnings)),
        "review_required_count": sum(1 for record in normalized if record["review_gates"].get("human_review_required")),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Snapshot is explicit local audit evidence, not accepted evidence, a public evidence database, or a master index.",
            "Append intent is represented in shape only; no persistent append runtime is implemented.",
        ],
    }


def summarize_evidence_ledger(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot = build_evidence_ledger_snapshot(records, policy)
    return {
        "evidence_record_count": snapshot["evidence_record_count"],
        "status_counts": snapshot["status_counts"],
        "type_counts": snapshot["type_counts"],
        "claim_type_counts": snapshot["claim_type_counts"],
        "source_counts": snapshot["source_counts"],
        "conflicting_record_count": snapshot["conflict_summary"]["conflicting_record_count"],
        "review_required_count": snapshot["review_required_count"],
        "evidence_ledger_snapshot_is_master_index": snapshot["truth_boundary"]["evidence_ledger_snapshot_is_master_index"],
        "warning_count": len(snapshot["warnings"]),
    }


def format_evidence_ledger_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Evidence Ledger Summary",
        "",
        f"- Evidence records: {summary.get('evidence_record_count', 0)}",
        f"- Review required: {summary.get('review_required_count', 0)}",
        f"- Conflicting records: {summary.get('conflicting_record_count', 0)}",
        f"- Warning count: {summary.get('warning_count', 0)}",
        f"- Master index: {str(summary.get('evidence_ledger_snapshot_is_master_index', False)).lower()}",
        "",
        "## Status Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("status_counts", {})).items()))
    lines.extend(["", "## Type Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("type_counts", {})).items()))
    lines.extend(["", "## Claim Type Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("claim_type_counts", {})).items()))
    lines.extend(["", "## Source Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("source_counts", {})).items()))
    return "\n".join(lines) + "\n"


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _build_from_source(source: dict[str, Any]) -> dict[str, Any]:
    schema = str(source.get("schema_version", ""))
    if schema == "local_source_cache_record.v0":
        return _record_from_source_cache(source)
    if schema == "candidate_record.v0":
        return _record_from_candidate(source)
    if schema == "search_need_record.v0":
        return _base_record(source, "search_need_record", "metadata_claim", "metadata", str(source.get("need_label", "SearchNeed evidence candidate")))
    if schema == "work_unit_result.v0":
        return _base_record(source, "workunit_result", "review_status_record", "review_status", str(source.get("workunit_result_id", "WorkUnit result evidence candidate")))
    if schema == "node_policy_evaluation_result.v0":
        return _base_record(source, "node_policy_evaluation", "review_status_record", "review_status", str(source.get("evaluation_result_id", "Node policy evaluation evidence candidate")))
    return _base_record(source, str(source.get("input_type", "committed_evidence_fixture")), str(source.get("evidence_record_type", "")), str(source.get("claim_type", "")), str(source.get("evidence_label", "Evidence fixture")))


def _record_from_source_cache(source: dict[str, Any]) -> dict[str, Any]:
    label = str(source.get("source_label") or source.get("source_cache_record_id") or "Source cache observation candidate")
    record = _base_record(source, "source_cache_record", "source_observation", "source_observation", label)
    record.update(
        {
            "evidence_record_status": "source_observation_candidate",
            "source_id": str(source.get("source_id", "")),
            "source_label": label,
            "source_locator": str(source.get("source_locator", "")),
            "related_source_cache_refs_future": [str(source.get("source_cache_record_id", ""))] if source.get("source_cache_record_id") else [],
            "provenance_summary": "Derived from explicit source cache record input; source-cache bridge runtime remains disabled.",
            "lineage_refs": [str(source.get("source_cache_record_id", ""))] if source.get("source_cache_record_id") else [],
        }
    )
    return record


def _record_from_candidate(source: dict[str, Any]) -> dict[str, Any]:
    label = str(source.get("candidate_label") or source.get("candidate_id") or "Candidate evidence record")
    record = _base_record(source, "candidate_record", "metadata_claim", "metadata", label)
    record.update(
        {
            "evidence_record_status": "evidence_candidate",
            "related_candidate_refs": [str(source.get("candidate_id", ""))] if source.get("candidate_id") else [],
            "provenance_summary": "Derived from explicit candidate example input.",
        }
    )
    return record


def _base_record(source: dict[str, Any], input_type: str, record_type: str, claim_type: str, label: str) -> dict[str, Any]:
    source_id = str(source.get("source_id") or source.get("source_id_optional") or "source:fixture:evidence")
    source_locator = str(source.get("source_locator") or source.get("source_locator_optional") or "fixture:evidence-ledger:local")
    claim_subject = str(source.get("claim_subject") or source.get("candidate_id_optional") or source.get("pack_id_optional") or label)
    return {
        "schema_version": SCHEMA_VERSION,
        "input_id": str(source.get("input_id") or source.get("evidence_record_id") or source.get("candidate_id") or source.get("source_cache_record_id") or label),
        "input_type": input_type,
        "input_ref": str(source.get("input_ref", "")),
        "input_status": str(source.get("input_status", source.get("evidence_status", "fixture_only"))),
        "input_public_safe": bool(source.get("input_public_safe", True)),
        "input_summary": str(source.get("input_summary", source.get("claim_text_or_summary", label))),
        "evidence_record_status": str(source.get("evidence_record_status", source.get("evidence_status", ""))),
        "evidence_record_type": record_type,
        "evidence_label": label,
        "source_id": source_id,
        "source_label": str(source.get("source_label", source_id)),
        "source_locator": source_locator,
        "claim_type": claim_type,
        "claim_summary": str(source.get("claim_summary") or source.get("claim_text_or_summary") or source.get("input_summary") or label),
        "claim_value_optional": source.get("claim_value_optional", source.get("claim_value", "")),
        "claim_subject": claim_subject,
        "observation_summary": str(source.get("observation_summary", source.get("input_summary", label))),
        "provenance_summary": str(source.get("provenance_summary", "Committed fixture input only.")),
        "lineage_refs": _list_of_strings(source.get("lineage_refs", [])),
        "related_candidate_refs": _list_of_strings(source.get("related_candidate_refs", [])),
        "related_source_cache_refs_future": _list_of_strings(source.get("related_source_cache_refs_future", [])),
        "related_search_need_refs": _list_of_strings(source.get("related_search_need_refs", [])),
        "related_workunit_refs": _list_of_strings(source.get("related_workunit_refs", [])),
        "related_pack_refs": _list_of_strings(source.get("related_pack_refs", [])),
        "related_review_refs_future": _list_of_strings(source.get("related_review_refs_future", [])),
        "confidence_or_uncertainty": str(source.get("confidence_or_uncertainty", "low_confidence_review_required")),
        "conflict_summary": source.get("conflict_summary", ""),
        "review_gates": _review_gates(source.get("review_gates")),
        "privacy_posture": _privacy_posture(source.get("privacy_posture")),
        "rights_risk_posture": _rights_risk_posture(source.get("rights_risk_posture")),
        "limitations": _list_of_strings(source.get("limitations", [])),
        "truth_boundary": _truth_boundary(source.get("truth_boundary")),
        "product_boundary": _product_boundary(source.get("product_boundary")),
        "notes": _list_of_strings(source.get("notes", [])),
    }


def _normalize_record(source: dict[str, Any]) -> dict[str, Any]:
    record = _base_record(
        source,
        str(source.get("input_type", "evidence_ledger_record")),
        str(source.get("evidence_record_type", "")),
        str(source.get("claim_type", "")),
        str(source.get("evidence_label", "Evidence ledger record")),
    )
    record.update(source)
    return record


def _normalize_claim_type(claim_type: Any, record_type: str) -> str:
    explicit = str(claim_type or "").strip()
    if explicit in ALLOWED_CLAIM_TYPES:
        return explicit
    mapping = {
        "metadata_claim": "metadata",
        "identity_claim": "identity",
        "compatibility_claim": "compatibility",
        "checksum_claim": "checksum",
        "filename_or_member_claim": "filename_or_member",
        "source_locator": "source_locator",
        "pack_claim": "pack_claim",
        "conflict_record": "conflict",
        "review_status_record": "review_status",
        "provenance_link": "provenance",
        "source_observation": "source_observation",
    }
    return mapping.get(record_type, "metadata")


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


def _privacy_posture(existing: Any = None) -> dict[str, bool]:
    posture = {
        "public_safe_fixture_only": True,
        "raw_user_history_retained": False,
        "private_user_data_retained": False,
        "credentials_retained": False,
        "account_session_retained": False,
        "telemetry_retained": False,
    }
    if isinstance(existing, Mapping):
        for key in posture:
            if key in existing:
                posture[key] = bool(existing[key])
    return posture


def _rights_risk_posture(existing: Any = None) -> dict[str, bool]:
    posture = {
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "executable_payload_present": False,
        "download_or_installer_present": False,
        "review_required": True,
    }
    if isinstance(existing, Mapping):
        for key in posture:
            if key in existing:
                posture[key] = bool(existing[key])
    return posture


def _detect_posture_violations(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    privacy = record.get("privacy_posture", {})
    if not isinstance(privacy, Mapping):
        errors.append("privacy_posture must be an object")
    else:
        if privacy.get("public_safe_fixture_only") is not True:
            errors.append("privacy_posture.public_safe_fixture_only must be true")
        for field in ("raw_user_history_retained", "private_user_data_retained", "credentials_retained", "account_session_retained", "telemetry_retained"):
            if privacy.get(field) is not False:
                errors.append(f"privacy_posture.{field} must be false")
    if record.get("input_public_safe") is not True:
        errors.append("input_public_safe must be true")
    rights = record.get("rights_risk_posture", {})
    if not isinstance(rights, Mapping):
        errors.append("rights_risk_posture must be an object")
    else:
        for field in ("rights_clearance_claimed", "malware_safety_claimed", "verified_installability_claimed", "executable_payload_present", "download_or_installer_present"):
            if rights.get(field) is not False:
                errors.append(f"rights_risk_posture.{field} must be false")
        if rights.get("review_required") is not True:
            errors.append("rights_risk_posture.review_required must be true")
    return errors


def _contains_url_like_locator(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return lowered.startswith(("http://", "https://", "ftp://")) or "://live" in lowered
    return False


def _list_of_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [str(value)]


def _scan_forbidden_claims(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in {"api_key", "secret", "credential", "password", "cookie", "session_token", "token"}:
                errors.append(f"{path}.{key}: forbidden credential-like field")
            errors.extend(_scan_forbidden_claims(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_scan_forbidden_claims(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in sorted(FORBIDDEN_CLAIM_PHRASES):
            if phrase in lowered:
                errors.append(f"{path}: forbidden claim phrase {phrase!r}")
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path}: private path-like text is forbidden")
        for pattern in CREDENTIAL_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path}: credential-like text is forbidden")
    return errors
