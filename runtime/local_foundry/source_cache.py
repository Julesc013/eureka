"""Fixture-only local source cache helpers.

Source cache records are repo-local observations, not evidence truth, public
truth, source-sync output, or master-index records. This module is
standard-library only and has no file, network, provider, browser, telemetry,
or runtime side effects.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "local_source_cache_record.v0"
SNAPSHOT_SCHEMA_VERSION = "local_source_cache_snapshot.v0"
REPORT_SCHEMA_VERSION = "local_source_cache_runtime_report.v0"

ALLOWED_STATUSES = {
    "example_only",
    "fixture_only",
    "recorded_local",
    "normalized",
    "source_observation",
    "candidate_source_record",
    "needs_review",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "stale",
    "superseded",
    "deferred",
    "future_live_probe_result",
    "accepted_public_future",
    "rejected_future",
}

CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "fixture_only",
    "recorded_local",
    "normalized",
    "source_observation",
    "candidate_source_record",
    "needs_review",
    "policy_blocked",
    "deferred",
}

ALLOWED_RECORD_TYPES = {
    "source_metadata",
    "source_locator",
    "source_policy_record",
    "source_health_record",
    "source_coverage_record",
    "source_lead_record",
    "connector_fixture_record",
    "source_identity_record",
    "source_limitations_record",
    "source_access_posture_record",
    "approved_metadata_probe_result_future",
    "approved_api_result_future",
    "static_dump_record_future",
}

CURRENT_ALLOWED_RECORD_TYPES = {
    "source_metadata",
    "source_locator",
    "source_policy_record",
    "source_health_record",
    "source_coverage_record",
    "source_lead_record",
    "connector_fixture_record",
    "source_identity_record",
    "source_limitations_record",
    "source_access_posture_record",
}

ALLOWED_INPUT_TYPES = {
    "committed_source_fixture",
    "committed_pack_example",
    "committed_static_artifact",
    "committed_audit_report",
    "committed_public_data_summary",
    "source_lead_candidate",
    "candidate_record",
    "search_need_record",
    "workunit_result",
    "node_policy_evaluation",
    "manual_observation_record_future",
    "approved_metadata_probe_result_future",
    "approved_api_result_future",
    "source_cache_record",
}

CURRENT_ALLOWED_INPUT_TYPES = {
    "committed_source_fixture",
    "committed_pack_example",
    "committed_static_artifact",
    "committed_audit_report",
    "committed_public_data_summary",
    "source_lead_candidate",
    "candidate_record",
    "search_need_record",
    "workunit_result",
    "node_policy_evaluation",
    "source_cache_record",
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
}

ALLOWED_SOURCE_ACCESS_MODES = {
    "committed_fixture_only",
    "repo_local_only",
    "manual_human_only",
    "no_autonomous_access",
}

FORBIDDEN_SOURCE_ACCESS_MODES = {
    "approved_metadata_probe_future",
    "approved_api_future",
    "approved_static_dump_future",
    "approved_common_crawl_or_archive_future",
    "live_probe",
    "source_sync",
    "arbitrary_url_fetch",
    "scraping",
    "crawling",
    "download",
    "api_call",
    "credentialed_access",
}

ALLOWED_OUTPUT_TYPES = {
    "source_cache_record",
    "source_cache_summary",
    "source_cache_snapshot",
    "review_item_future",
    "evidence_candidate_future",
    "candidate_store_use_request_future",
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
    "source_cache_snapshot_is_master_index",
    "source_cache_record_is_public_truth",
    "source_cache_record_is_accepted_evidence",
    "source_cache_record_can_mutate_master_index",
    "source_cache_record_can_claim_rights_clearance",
    "source_cache_record_can_claim_malware_safety",
    "source_cache_record_can_claim_verified_installability",
    "source_cache_record_can_claim_exhaustive_global_search",
    "source_cache_record_can_claim_production_readiness",
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
    "implemented_source_cache_to_evidence_bridge",
}

REVIEW_GATE_TRUE_FIELDS = {
    "human_review_required",
    "source_cache_review_required",
    "evidence_ledger_bridge_review_required",
    "candidate_store_review_required",
    "public_index_review_required",
    "pack_export_review_required",
    "rights_review_required",
    "risk_review_required",
    "privacy_review_required",
}

FORBIDDEN_CLAIM_PHRASES = {
    "accepted public truth",
    "accepted evidence truth",
    "accepted public record",
    "accepted evidence",
    "verified fact",
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
    "hosted query capture enabled",
    "public search behavior changed",
    "source sync enabled",
    "live probe enabled",
    "connector runtime enabled",
    "download enabled",
    "upload enabled",
    "account enabled",
    "master-index mutation allowed",
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
        "allowed_source_access_modes": sorted(ALLOWED_SOURCE_ACCESS_MODES),
        "forbidden_source_access_modes": sorted(FORBIDDEN_SOURCE_ACCESS_MODES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "review_required_before_downstream_use": True,
        "source_access_disabled_current": True,
        "source_sync_disabled_current": True,
        "live_probe_disabled_current": True,
    }


def build_source_cache_record(input_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build or normalize a fixture-only source cache record from explicit input."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(input_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        record = _normalize_record(source)
    else:
        record = _build_from_source(source)

    record["source_cache_record_type"] = classify_source_cache_record_type(record, active_policy)
    record["source_cache_record_status"] = classify_source_cache_record_status(record, active_policy)
    if record["source_access_mode"] in FORBIDDEN_SOURCE_ACCESS_MODES:
        record["source_cache_record_status"] = "policy_blocked"
    if record["source_cache_record_type"] == "source_access_posture_record" and record["source_policy_status"] == "policy_blocked":
        record["source_cache_record_status"] = "policy_blocked"
    record["source_id"] = record.get("source_id") or _source_id(record)
    record["source_cache_record_id"] = record.get("source_cache_record_id") or f"source_cache.{record['source_cache_record_type']}.{_digest(record)[:12]}.v0"
    record["truth_boundary"] = _truth_boundary(record.get("truth_boundary"))
    record["product_boundary"] = _product_boundary(record.get("product_boundary"))
    record["review_gates"] = _review_gates(record.get("review_gates"))
    record["privacy_posture"] = _privacy_posture(record.get("privacy_posture"))
    record["rights_risk_posture"] = _rights_risk_posture(record.get("rights_risk_posture"))
    record.setdefault("source_limitations", [])
    record.setdefault("notes", [])
    return record


def validate_source_cache_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a source cache record."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required_fields = {
        "schema_version",
        "source_cache_record_id",
        "source_cache_record_status",
        "source_cache_record_type",
        "source_id",
        "source_label",
        "source_family",
        "source_kind",
        "source_locator",
        "source_access_mode",
        "source_policy_status",
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
    if record.get("source_cache_record_status") not in active_policy.get("allowed_statuses", ALLOWED_STATUSES):
        errors.append(f"source_cache_record_status is not allowed: {record.get('source_cache_record_status')}")
    if record.get("source_cache_record_status") not in active_policy.get("current_allowed_statuses", CURRENT_ALLOWED_STATUSES):
        errors.append(f"source_cache_record_status is not allowed in current runtime: {record.get('source_cache_record_status')}")
    if record.get("source_cache_record_type") not in active_policy.get("allowed_record_types", ALLOWED_RECORD_TYPES):
        errors.append(f"source_cache_record_type is not allowed: {record.get('source_cache_record_type')}")
    if record.get("source_cache_record_type") not in active_policy.get("current_allowed_record_types", CURRENT_ALLOWED_RECORD_TYPES):
        errors.append(f"source_cache_record_type is not allowed in current runtime: {record.get('source_cache_record_type')}")
    errors.extend(detect_source_access_violations(record, active_policy))
    errors.extend(detect_truth_boundary_violations(record, active_policy))
    errors.extend(detect_product_boundary_violations(record, active_policy))
    errors.extend(_detect_posture_violations(record))
    errors.extend(_scan_forbidden_claims(record))
    return sorted(dict.fromkeys(errors))


def summarize_source_cache_record(record: Mapping[str, Any]) -> dict[str, Any]:
    truth = record.get("truth_boundary", {})
    product = record.get("product_boundary", {})
    review = record.get("review_gates", {})
    return {
        "source_cache_record_id": record.get("source_cache_record_id", ""),
        "source_cache_record_status": record.get("source_cache_record_status", ""),
        "source_cache_record_type": record.get("source_cache_record_type", ""),
        "source_id": record.get("source_id", ""),
        "source_label": record.get("source_label", ""),
        "source_family": record.get("source_family", ""),
        "source_access_mode": record.get("source_access_mode", ""),
        "review_required": bool(review.get("human_review_required", True)),
        "source_cache_record_is_public_truth": bool(truth.get("source_cache_record_is_public_truth", False)),
        "source_cache_record_is_accepted_evidence": bool(truth.get("source_cache_record_is_accepted_evidence", False)),
        "source_cache_record_can_mutate_master_index": bool(truth.get("source_cache_record_can_mutate_master_index", False)),
        "enabled_network_access": bool(product.get("enabled_network_access", False)),
    }


def classify_source_cache_record_type(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    explicit = str(record.get("source_cache_record_type", "")).strip()
    allowed = set((policy or default_policy()).get("allowed_record_types", ALLOWED_RECORD_TYPES))
    if explicit in allowed:
        return explicit
    text = " ".join(
        str(record.get(key, ""))
        for key in ("source_label", "source_family", "source_kind", "source_metadata_summary", "source_coverage_summary", "source_policy_status")
    ).lower()
    if "connector" in text:
        return "connector_fixture_record"
    if "coverage" in text:
        return "source_coverage_record"
    if "policy" in text or "blocked" in text:
        return "source_policy_record"
    if "locator" in text:
        return "source_locator"
    if "lead" in text:
        return "source_lead_record"
    return "source_metadata"


def classify_source_cache_record_status(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    explicit = str(record.get("source_cache_record_status", "")).strip()
    allowed = set((policy or default_policy()).get("allowed_statuses", ALLOWED_STATUSES))
    if explicit in allowed:
        return explicit
    source_status = str(record.get("source_policy_status", "")).strip()
    if source_status == "policy_blocked":
        return "policy_blocked"
    if record.get("source_cache_record_type") == "connector_fixture_record":
        return "fixture_only"
    if record.get("source_cache_record_type") == "source_lead_record":
        return "candidate_source_record"
    return "recorded_local"


def detect_source_access_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    active_policy = policy or default_policy()
    errors: list[str] = []
    mode = str(record.get("source_access_mode", ""))
    if mode not in active_policy.get("allowed_source_access_modes", ALLOWED_SOURCE_ACCESS_MODES):
        errors.append(f"source_access_mode is not allowed in current runtime: {mode}")
    if mode in active_policy.get("forbidden_source_access_modes", FORBIDDEN_SOURCE_ACCESS_MODES):
        errors.append(f"source_access_mode is forbidden in current runtime: {mode}")
    if _contains_url_like_locator(record.get("source_locator")):
        errors.append("source_locator must be a repo-local fixture locator, not a live URL")
    input_type = str(record.get("input_type", "source_cache_record"))
    if input_type in FORBIDDEN_INPUT_TYPES:
        errors.append(f"input_type is forbidden: {input_type}")
    if input_type not in active_policy.get("current_allowed_input_types", CURRENT_ALLOWED_INPUT_TYPES):
        errors.append(f"input_type is not allowed in current runtime: {input_type}")
    return errors


def detect_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
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


def detect_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    product = record.get("product_boundary", {})
    errors: list[str] = []
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    return errors


def build_source_cache_snapshot(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_policy = policy or default_policy()
    normalized = [build_source_cache_record(record, active_policy) for record in records]
    status_counts = Counter(str(record["source_cache_record_status"]) for record in normalized)
    type_counts = Counter(str(record["source_cache_record_type"]) for record in normalized)
    family_counts = Counter(str(record.get("source_family", "")) for record in normalized)
    access_counts = Counter(str(record.get("source_access_mode", "")) for record in normalized)
    warnings: list[str] = []
    for record in normalized:
        warnings.extend(f"{record['source_cache_record_id']}: {error}" for error in validate_source_cache_record(record, active_policy))
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "source_cache_snapshot_id": f"source_cache_snapshot.{_digest({'ids': [r['source_cache_record_id'] for r in normalized]})[:12]}.v0",
        "snapshot_status": "review_required",
        "generated_from": "explicit_input_only",
        "source_cache_record_count": len(normalized),
        "records": normalized,
        "status_counts": dict(sorted(status_counts.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "source_family_counts": dict(sorted(family_counts.items())),
        "source_access_mode_counts": dict(sorted(access_counts.items())),
        "warnings": sorted(dict.fromkeys(warnings)),
        "review_required_count": sum(1 for record in normalized if record["review_gates"].get("human_review_required")),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Snapshot is explicit local audit evidence, not a master index, evidence ledger, or public index.",
            "Source cache records are observations and require review before downstream use.",
        ],
    }


def summarize_source_cache(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot = build_source_cache_snapshot(records, policy)
    return {
        "source_cache_record_count": snapshot["source_cache_record_count"],
        "status_counts": snapshot["status_counts"],
        "type_counts": snapshot["type_counts"],
        "source_family_counts": snapshot["source_family_counts"],
        "source_access_mode_counts": snapshot["source_access_mode_counts"],
        "review_required_count": snapshot["review_required_count"],
        "source_cache_snapshot_is_master_index": snapshot["truth_boundary"]["source_cache_snapshot_is_master_index"],
        "warning_count": len(snapshot["warnings"]),
    }


def format_source_cache_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Source Cache Summary",
        "",
        f"- Source cache records: {summary.get('source_cache_record_count', 0)}",
        f"- Review required: {summary.get('review_required_count', 0)}",
        f"- Warning count: {summary.get('warning_count', 0)}",
        f"- Master index: {str(summary.get('source_cache_snapshot_is_master_index', False)).lower()}",
        "",
        "## Status Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("status_counts", {})).items()))
    lines.extend(["", "## Type Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("type_counts", {})).items()))
    lines.extend(["", "## Source Family Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("source_family_counts", {})).items()))
    lines.extend(["", "## Source Access Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("source_access_mode_counts", {})).items()))
    return "\n".join(lines) + "\n"


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _build_from_source(source: dict[str, Any]) -> dict[str, Any]:
    schema = str(source.get("schema_version", ""))
    if schema == "candidate_record.v0":
        return _record_from_candidate(source)
    if schema == "search_need_record.v0":
        return _record_from_search_need(source)
    if schema == "work_unit_result.v0":
        return _record_from_workunit_result(source)
    if schema == "node_policy_evaluation_result.v0":
        return _record_from_node_policy_evaluation(source)
    return _base_record(source, str(source.get("input_type", "committed_source_fixture")), str(source.get("source_cache_record_type", "")), str(source.get("source_label_optional") or source.get("source_label") or "Source cache fixture"))


def _record_from_candidate(source: dict[str, Any]) -> dict[str, Any]:
    candidate_type = str(source.get("candidate_type", ""))
    record_type = "source_lead_record" if candidate_type == "source_lead_candidate" else "source_metadata"
    label = str(source.get("candidate_label") or source.get("candidate_id") or "Candidate source cache record")
    record = _base_record(source, "candidate_record", record_type, label)
    record.update(
        {
            "source_cache_record_status": "candidate_source_record" if record_type == "source_lead_record" else "needs_review",
            "related_candidate_refs": [str(source.get("candidate_id", ""))] if source.get("candidate_id") else [],
            "source_observation_summary": str(source.get("proposed_source_summary") or source.get("proposed_object_summary") or label),
        }
    )
    return record


def _record_from_search_need(source: dict[str, Any]) -> dict[str, Any]:
    label = str(source.get("need_label") or source.get("search_need_id") or "SearchNeed source cache record")
    record = _base_record(source, "search_need_record", "source_lead_record", label)
    record.update(
        {
            "source_cache_record_status": "candidate_source_record",
            "related_search_need_refs": [str(source.get("search_need_id", ""))] if source.get("search_need_id") else [],
            "source_observation_summary": str(source.get("source_gap_summary") or source.get("candidate_summary") or label),
        }
    )
    return record


def _record_from_workunit_result(source: dict[str, Any]) -> dict[str, Any]:
    label = str(source.get("workunit_result_label") or source.get("workunit_result_id") or "WorkUnit result source cache record")
    status = "policy_blocked" if source.get("workunit_result_status") == "policy_blocked" else "needs_review"
    record = _base_record(source, "workunit_result", "source_metadata", label)
    record.update(
        {
            "source_cache_record_status": status,
            "related_workunit_refs": [str(source.get("workunit_id", ""))] if source.get("workunit_id") else [],
            "source_observation_summary": str(source.get("workunit_result_status", "")),
        }
    )
    return record


def _record_from_node_policy_evaluation(source: dict[str, Any]) -> dict[str, Any]:
    decision = str(source.get("decision", ""))
    label = f"Node policy evaluation source posture {decision or 'record'}"
    record = _base_record(source, "node_policy_evaluation", "source_policy_record", label)
    record.update(
        {
            "source_cache_record_status": "policy_blocked" if decision.startswith("blocked") else "needs_review",
            "related_workunit_refs": [str(source.get("evaluated_workunit_ref", ""))] if source.get("evaluated_workunit_ref") else [],
            "source_policy_status": "policy_blocked" if decision.startswith("blocked") else "review_required",
            "source_observation_summary": decision,
        }
    )
    return record


def _base_record(source: dict[str, Any], input_type: str, record_type: str, label: str) -> dict[str, Any]:
    source_identity = (
        source.get("source_id")
        or source.get("source_id_optional")
        or source.get("candidate_id")
        or source.get("search_need_id")
        or source.get("workunit_result_id")
        or source.get("evaluation_result_id")
        or label
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "input_id": str(source.get("input_id") or source_identity),
        "input_type": input_type,
        "input_ref": str(source.get("input_ref", "")),
        "input_status": str(source.get("input_status", source.get("candidate_status", source.get("search_need_status", "fixture_only")))),
        "input_public_safe": bool(source.get("input_public_safe", True)),
        "input_summary": str(source.get("input_summary", source.get("candidate_label", source.get("need_label", label)))),
        "source_cache_record_status": str(source.get("source_cache_record_status", source.get("input_status", "recorded_local"))),
        "source_cache_record_type": record_type,
        "source_id": str(source.get("source_id") or source.get("source_id_optional") or ""),
        "source_label": label,
        "source_family": str(source.get("source_family", "synthetic_fixture")),
        "source_kind": str(source.get("source_kind", "committed_fixture")),
        "source_locator": str(source.get("source_locator") or source.get("source_url_or_locator_optional") or "fixture:source-cache:local"),
        "source_access_mode": str(source.get("source_access_mode", "committed_fixture_only")),
        "source_policy_status": str(source.get("source_policy_status", "fixture_only")),
        "source_authority_posture": str(source.get("source_authority_posture", "not_authoritative")),
        "source_coverage_summary": source.get("source_coverage_summary", ""),
        "source_metadata_summary": source.get("source_metadata_summary", source.get("input_summary", "")),
        "source_health_summary": source.get("source_health_summary", ""),
        "source_limitations": _list_of_strings(source.get("source_limitations", source.get("limitations", []))),
        "source_observation_summary": str(source.get("source_observation_summary", source.get("notes", ""))),
        "normalized_fields": source.get("normalized_fields", {}),
        "related_candidate_refs": _list_of_strings(source.get("related_candidate_refs", [])),
        "related_search_need_refs": _list_of_strings(source.get("related_search_need_refs", [])),
        "related_workunit_refs": _list_of_strings(source.get("related_workunit_refs", [])),
        "related_source_lead_refs": _list_of_strings(source.get("related_source_lead_refs", source.get("source_lead_refs", []))),
        "related_pack_refs_future": _list_of_strings(source.get("related_pack_refs_future", [])),
        "related_evidence_refs_future": _list_of_strings(source.get("related_evidence_refs_future", [])),
        "review_gates": _review_gates(source.get("review_gates")),
        "privacy_posture": _privacy_posture(source.get("privacy_posture")),
        "rights_risk_posture": _rights_risk_posture(source.get("rights_risk_posture")),
        "truth_boundary": _truth_boundary(source.get("truth_boundary")),
        "product_boundary": _product_boundary(source.get("product_boundary")),
        "notes": _list_of_strings(source.get("notes", [])),
        "_source_identity": str(source_identity),
    }


def _normalize_record(source: dict[str, Any]) -> dict[str, Any]:
    record = _base_record(
        source,
        str(source.get("input_type", "source_cache_record")),
        str(source.get("source_cache_record_type", "")),
        str(source.get("source_label", "Source cache record")),
    )
    record.update(source)
    return record


def _source_id(record: Mapping[str, Any]) -> str:
    basis = "|".join(
        str(record.get(key, "")).strip().lower()
        for key in ("source_family", "source_kind", "source_label", "source_locator", "_source_identity")
    )
    return "source:" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


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


def _list_of_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [str(value)]


def _contains_url_like_locator(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return lowered.startswith(("http://", "https://", "ftp://")) or "://live" in lowered
    return False


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
        for field in (
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "verified_installability_claimed",
            "executable_payload_present",
            "download_or_installer_present",
        ):
            if rights.get(field) is not False:
                errors.append(f"rights_risk_posture.{field} must be false")
        if rights.get("review_required") is not True:
            errors.append("rights_risk_posture.review_required must be true")
    return errors
