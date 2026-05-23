"""Local-only candidate store helpers.

Candidate records are provisional review items, not accepted evidence, public
truth, or master-index records. This module is standard-library only and has no
file, network, provider, browser, telemetry, or runtime side effects.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "candidate_record.v0"
SNAPSHOT_SCHEMA_VERSION = "candidate_store_snapshot.v0"
REPORT_SCHEMA_VERSION = "candidate_store_runtime_report.v0"

ALLOWED_STATUSES = {
    "example_only",
    "proposed",
    "recorded_local",
    "normalized",
    "candidate",
    "needs_review",
    "evidence_needed",
    "duplicate_possible",
    "conflict_detected",
    "policy_blocked",
    "rights_blocked",
    "risk_blocked",
    "rejected",
    "deferred",
    "superseded",
    "accepted_public_future",
}

CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "proposed",
    "recorded_local",
    "candidate",
    "needs_review",
    "evidence_needed",
    "duplicate_possible",
    "conflict_detected",
    "policy_blocked",
    "rejected",
    "deferred",
}

ALLOWED_CANDIDATE_TYPES = {
    "object_candidate",
    "source_candidate",
    "evidence_candidate",
    "compatibility_candidate",
    "identity_candidate",
    "representation_candidate",
    "member_candidate",
    "version_or_state_candidate",
    "source_lead_candidate",
    "search_need_candidate",
    "workunit_seed_candidate",
    "pack_candidate_future",
    "extraction_candidate_future",
    "review_item_candidate_future",
    "policy_blocked_candidate",
    "not_evaluable_candidate",
}

ALLOWED_ORIGINS = {
    "search_need",
    "search_miss",
    "query_observation",
    "observation_candidate",
    "manual_observation_future",
    "agent_assisted_candidate",
    "local_eval",
    "static_demo",
    "source_lead",
    "workunit_result",
    "node_policy_evaluation",
    "source_cache_record_future",
    "evidence_ledger_record_future",
    "evidence_pack_future",
    "contribution_pack_future",
    "index_pack_future",
    "deep_extraction_future",
    "discussion_to_evidence_future",
    "ai_draft_future",
}

ALLOWED_OUTPUT_TYPES = {
    "candidate_record",
    "candidate_summary",
    "candidate_store_snapshot",
    "candidate_dedup_report",
    "review_item_future",
    "workunit_seed_future",
    "evidence_draft_future",
    "contribution_pack_draft_future",
}

FORBIDDEN_OUTPUT_TYPES = {
    "accepted_public_record",
    "accepted_evidence_truth",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
}

TRUTH_BOUNDARY_FALSE_FIELDS = {
    "candidate_store_is_master_index",
    "candidate_is_public_truth",
    "candidate_is_accepted_evidence",
    "candidate_can_mutate_master_index",
    "candidate_can_claim_rights_clearance",
    "candidate_can_claim_malware_safety",
    "candidate_can_claim_verified_installability",
    "candidate_can_claim_exhaustive_global_search",
    "candidate_can_claim_production_readiness",
}

TRUTH_BOUNDARY_TRUE_FIELDS = {"human_review_required_for_downstream_use"}

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

REVIEW_GATE_TRUE_FIELDS = {
    "human_review_required",
    "candidate_review_required",
    "evidence_review_required",
    "master_index_review_required",
    "rights_review_required",
    "risk_review_required",
    "privacy_review_required",
}

FORBIDDEN_CLAIM_PHRASES = {
    "accepted public truth",
    "accepted evidence truth",
    "accepted public record",
    "verified fact",
    "object is verified",
    "candidate is verified",
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
    "download enabled",
    "upload enabled",
    "account enabled",
    "master-index mutation allowed",
}


def default_policy() -> dict[str, Any]:
    return {
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "current_allowed_statuses": sorted(CURRENT_ALLOWED_STATUSES),
        "allowed_candidate_types": sorted(ALLOWED_CANDIDATE_TYPES),
        "allowed_origins": sorted(ALLOWED_ORIGINS),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "review_required_before_downstream_use": True,
        "merge_allowed": False,
        "automatic_merge_allowed": False,
        "conflict_preservation_required": True,
    }


def build_candidate_record(input_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build or normalize a provisional candidate record from explicit input."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(input_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        record = _normalize_candidate(source)
    else:
        record = _build_from_source(source)

    record["candidate_type"] = classify_candidate_type(record, active_policy)
    record["candidate_origin"] = classify_candidate_origin(record, active_policy)
    record["candidate_status"] = _normalized_status(str(record.get("candidate_status", "candidate")))
    if record["candidate_type"] == "policy_blocked_candidate":
        record["candidate_status"] = "policy_blocked"
    if record["candidate_type"] == "not_evaluable_candidate":
        record["candidate_status"] = "deferred"
    record["canonical_candidate_key"] = record.get("canonical_candidate_key") or _canonical_key(record)
    record["candidate_id"] = record.get("candidate_id") or f"candidate.{record['candidate_origin']}.{_digest(record)[:12]}.v0"
    record["truth_boundary"] = _truth_boundary(record.get("truth_boundary"))
    record["product_boundary"] = _product_boundary(record.get("product_boundary"))
    record["review_gates"] = _review_gates(record.get("review_gates"))
    record.setdefault("confidence_or_uncertainty", "low_confidence_review_required")
    record.setdefault("limitations", [])
    record.setdefault("notes", [])
    return record


def validate_candidate_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a candidate record."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required_fields = {
        "schema_version",
        "candidate_id",
        "candidate_status",
        "candidate_type",
        "candidate_origin",
        "candidate_label",
        "canonical_candidate_key",
        "review_gates",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required_fields):
        if field not in record:
            errors.append(f"missing required field: {field}")
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if record.get("candidate_status") not in active_policy.get("allowed_statuses", ALLOWED_STATUSES):
        errors.append(f"invalid candidate_status: {record.get('candidate_status')}")
    if record.get("candidate_status") == "accepted_public_future":
        errors.append("accepted_public_future is vocabulary-only and forbidden for current records")
    if record.get("candidate_type") not in active_policy.get("allowed_candidate_types", ALLOWED_CANDIDATE_TYPES):
        errors.append(f"invalid candidate_type: {record.get('candidate_type')}")
    if record.get("candidate_origin") not in active_policy.get("allowed_origins", ALLOWED_ORIGINS):
        errors.append(f"invalid candidate_origin: {record.get('candidate_origin')}")
    errors.extend(detect_candidate_truth_boundary_violations(record, active_policy))
    errors.extend(detect_candidate_product_boundary_violations(record, active_policy))
    errors.extend(_scan_forbidden_claims(record))
    return sorted(dict.fromkeys(errors))


def summarize_candidate_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": record.get("candidate_id"),
        "candidate_status": record.get("candidate_status"),
        "candidate_type": record.get("candidate_type"),
        "candidate_origin": record.get("candidate_origin"),
        "candidate_label": record.get("candidate_label"),
        "canonical_candidate_key": record.get("canonical_candidate_key"),
        "review_required": bool(record.get("truth_boundary", {}).get("human_review_required_for_downstream_use")),
        "candidate_is_public_truth": bool(record.get("truth_boundary", {}).get("candidate_is_public_truth")),
        "candidate_is_accepted_evidence": bool(record.get("truth_boundary", {}).get("candidate_is_accepted_evidence")),
        "candidate_can_mutate_master_index": bool(record.get("truth_boundary", {}).get("candidate_can_mutate_master_index")),
    }


def classify_candidate_type(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    del policy
    explicit = record.get("candidate_type")
    if explicit in ALLOWED_CANDIDATE_TYPES:
        return str(explicit)
    status = str(record.get("candidate_status", ""))
    origin = str(record.get("candidate_origin", ""))
    intent = str(record.get("desired_user_action") or record.get("need_intent") or "").lower()
    if status == "policy_blocked":
        return "policy_blocked_candidate"
    if status == "not_evaluable":
        return "not_evaluable_candidate"
    if origin == "source_lead":
        return "source_lead_candidate"
    if origin == "workunit_result":
        return "workunit_seed_candidate"
    if origin == "node_policy_evaluation":
        return "review_item_candidate_future"
    if origin == "search_need":
        if "driver" in intent or "compatibility" in intent:
            return "compatibility_candidate"
        if "version" in intent or record.get("version_or_state"):
            return "version_or_state_candidate"
        if "article" in intent or "member" in intent:
            return "member_candidate"
        return "search_need_candidate"
    return "object_candidate"


def classify_candidate_origin(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    del policy
    explicit = record.get("candidate_origin")
    if explicit in ALLOWED_ORIGINS:
        return str(explicit)
    return "static_demo"


def detect_candidate_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    del policy
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


def detect_candidate_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    del policy
    errors: list[str] = []
    product = record.get("product_boundary", {})
    if not isinstance(product, Mapping):
        return ["product_boundary must be an object"]
    for field in sorted(PRODUCT_BOUNDARY_FALSE_FIELDS):
        if product.get(field) is not False:
            errors.append(f"product_boundary.{field} must be false")
    return errors


def deduplicate_candidate_records(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Report duplicate candidate keys without merging or deleting records."""

    active_policy = policy or default_policy()
    normalized = [build_candidate_record(record, active_policy) for record in records]
    groups: dict[str, list[str]] = defaultdict(list)
    for record in normalized:
        groups[str(record["canonical_candidate_key"])].append(str(record["candidate_id"]))
    duplicate_groups = [
        {"canonical_candidate_key": key, "candidate_ids": ids, "duplicate_count": len(ids)}
        for key, ids in sorted(groups.items())
        if len(ids) > 1
    ]
    duplicate_ids = sorted({candidate_id for group in duplicate_groups for candidate_id in group["candidate_ids"]})
    return {
        "deduplication_mode": "exact_key_report_only",
        "candidate_count": len(normalized),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_possible_candidate_ids": duplicate_ids,
        "duplicate_groups": duplicate_groups,
        "merge_allowed": bool(active_policy.get("merge_allowed", False)),
        "automatic_merge_allowed": bool(active_policy.get("automatic_merge_allowed", False)),
        "merged_candidate_ids": [],
        "deleted_candidate_ids": [],
        "conflict_preservation_required": bool(active_policy.get("conflict_preservation_required", True)),
    }


def build_candidate_store_snapshot(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_policy = policy or default_policy()
    candidates = [build_candidate_record(record, active_policy) for record in records]
    status_counts = Counter(str(record["candidate_status"]) for record in candidates)
    type_counts = Counter(str(record["candidate_type"]) for record in candidates)
    origin_counts = Counter(str(record["candidate_origin"]) for record in candidates)
    dedup = deduplicate_candidate_records(candidates, active_policy)
    warnings = []
    if dedup["duplicate_group_count"]:
        warnings.append("duplicate_possible candidates were reported without merge or deletion")
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "candidate_store_snapshot_id": f"candidate_store_snapshot.{_digest({'ids': [c['candidate_id'] for c in candidates]})[:12]}.v0",
        "snapshot_status": "review_required",
        "generated_from": "explicit_input_only",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "status_counts": dict(sorted(status_counts.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "origin_counts": dict(sorted(origin_counts.items())),
        "deduplication_summary": dedup,
        "warnings": warnings,
        "review_required_count": sum(1 for record in candidates if record["review_gates"].get("human_review_required")),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Snapshot is local audit evidence, not a public index or master index.",
            "No candidate is accepted as truth or accepted evidence.",
        ],
    }


def summarize_candidate_store(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot = build_candidate_store_snapshot(records, policy)
    return {
        "candidate_count": snapshot["candidate_count"],
        "status_counts": snapshot["status_counts"],
        "type_counts": snapshot["type_counts"],
        "origin_counts": snapshot["origin_counts"],
        "duplicate_group_count": snapshot["deduplication_summary"]["duplicate_group_count"],
        "review_required_count": snapshot["review_required_count"],
        "candidate_store_is_master_index": snapshot["truth_boundary"]["candidate_store_is_master_index"],
    }


def format_candidate_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Candidate Store Summary",
        "",
        f"- Candidate count: {summary.get('candidate_count', 0)}",
        f"- Review required: {summary.get('review_required_count', 0)}",
        f"- Duplicate groups: {summary.get('duplicate_group_count', 0)}",
        f"- Master index: {str(summary.get('candidate_store_is_master_index', False)).lower()}",
        "",
        "## Status Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("status_counts", {})).items()))
    lines.extend(["", "## Type Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("type_counts", {})).items()))
    lines.extend(["", "## Origin Counts"])
    lines.extend(f"- {key}: {value}" for key, value in sorted(dict(summary.get("origin_counts", {})).items()))
    return "\n".join(lines) + "\n"


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _build_from_source(source: dict[str, Any]) -> dict[str, Any]:
    schema = str(source.get("schema_version", ""))
    if schema == "search_need_record.v0":
        return _candidate_from_search_need(source)
    if schema == "work_unit_result.v0":
        return _candidate_from_workunit_result(source)
    if schema == "node_policy_evaluation_result.v0":
        return _candidate_from_node_policy_evaluation(source)
    if schema in {"search_miss_ledger_record.v0", "search_miss_record.v0"}:
        return _base_candidate(source, "search_miss", "search_need_candidate", "Search miss candidate")
    if schema == "query_observation_runtime.v0":
        return _base_candidate(source, "query_observation", "search_need_candidate", "Query observation candidate")
    if schema == "observation_candidate.v0":
        return _base_candidate(source, "observation_candidate", "object_candidate", "Observation candidate")
    return _base_candidate(source, "static_demo", "object_candidate", str(source.get("candidate_label", "Minimal candidate")))


def _candidate_from_search_need(source: dict[str, Any]) -> dict[str, Any]:
    label = str(source.get("need_label") or source.get("search_need_id") or "SearchNeed candidate")
    status = "policy_blocked" if source.get("search_need_status") == "policy_blocked" else "candidate"
    if source.get("search_need_status") in {"evidence_needed", "source_gap", "capability_gap"}:
        status = "evidence_needed"
    record = _base_candidate(source, "search_need", "", label)
    record.update(
        {
            "candidate_status": status,
            "need_intent": source.get("need_intent"),
            "proposed_object_summary": {
                "object_family": source.get("object_family", ""),
                "product_or_topic": source.get("product_or_topic", ""),
                "version_or_state": source.get("version_or_state", ""),
                "platform_or_context": source.get("platform_or_context", ""),
                "artifact_type": source.get("artifact_type", ""),
                "desired_user_action": source.get("desired_user_action", source.get("need_intent", "")),
            },
            "related_search_need_refs": [str(source.get("search_need_id", ""))] if source.get("search_need_id") else [],
        }
    )
    return record


def _candidate_from_workunit_result(source: dict[str, Any]) -> dict[str, Any]:
    label = str(source.get("workunit_result_label") or source.get("workunit_result_id") or "WorkUnit result candidate")
    status = "policy_blocked" if source.get("workunit_result_status") == "policy_blocked" else "needs_review"
    record = _base_candidate(source, "workunit_result", "workunit_seed_candidate", label)
    record.update(
        {
            "candidate_status": status,
            "related_workunit_refs": [str(source.get("workunit_id", ""))] if source.get("workunit_id") else [],
            "related_workunit_result_refs": [str(source.get("workunit_result_id", ""))] if source.get("workunit_result_id") else [],
            "proposed_state_summary": str(source.get("workunit_result_status", "")),
        }
    )
    return record


def _candidate_from_node_policy_evaluation(source: dict[str, Any]) -> dict[str, Any]:
    label = f"Node policy evaluation {source.get('decision', 'candidate')}"
    status = "policy_blocked" if str(source.get("decision", "")).startswith("blocked") else "needs_review"
    record = _base_candidate(source, "node_policy_evaluation", "review_item_candidate_future", label)
    record.update(
        {
            "candidate_status": status,
            "related_node_policy_evaluation_refs": [str(source.get("evaluation_result_id", ""))] if source.get("evaluation_result_id") else [],
            "proposed_state_summary": str(source.get("decision", "")),
        }
    )
    return record


def _base_candidate(source: dict[str, Any], origin: str, candidate_type: str, label: str) -> dict[str, Any]:
    source_id = (
        source.get("search_need_id")
        or source.get("search_miss_id")
        or source.get("query_observation_id")
        or source.get("workunit_result_id")
        or source.get("evaluation_result_id")
        or source.get("candidate_id")
        or label
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_status": _normalized_status(str(source.get("candidate_status") or source.get("status") or "candidate")),
        "candidate_type": candidate_type,
        "candidate_origin": origin,
        "candidate_label": label,
        "canonical_candidate_key": str(source.get("canonical_candidate_key", "")),
        "proposed_object_summary": source.get("proposed_object_summary", {}),
        "proposed_source_summary": source.get("proposed_source_summary", {}),
        "proposed_evidence_summary": source.get("proposed_evidence_summary", {}),
        "proposed_representation_summary": source.get("proposed_representation_summary", {}),
        "proposed_compatibility_summary": source.get("proposed_compatibility_summary", {}),
        "proposed_state_summary": source.get("proposed_state_summary", ""),
        "related_query_observation_refs": _list_of_strings(source.get("related_query_observation_refs", [])),
        "related_search_miss_refs": _list_of_strings(source.get("related_search_miss_refs", [])),
        "related_search_need_refs": _list_of_strings(source.get("related_search_need_refs", [])),
        "related_workunit_refs": _list_of_strings(source.get("related_workunit_refs", [])),
        "related_workunit_result_refs": _list_of_strings(source.get("related_workunit_result_refs", [])),
        "related_node_policy_evaluation_refs": _list_of_strings(source.get("related_node_policy_evaluation_refs", [])),
        "related_observation_candidate_refs": _list_of_strings(source.get("related_observation_candidate_refs", [])),
        "source_lead_refs": _list_of_strings(source.get("source_lead_refs", [])),
        "evidence_refs_future": _list_of_strings(source.get("evidence_refs_future", [])),
        "pack_refs_future": _list_of_strings(source.get("pack_refs_future", [])),
        "review_refs_future": _list_of_strings(source.get("review_refs_future", [])),
        "confidence_or_uncertainty": source.get("confidence_or_uncertainty", "low_confidence_review_required"),
        "conflict_summary": source.get("conflict_summary", ""),
        "deduplication_summary": source.get("deduplication_summary", {"duplicate_possible": False, "automatic_merge_allowed": False}),
        "limitations": _list_of_strings(source.get("limitations", [])),
        "review_gates": _review_gates(source.get("review_gates")),
        "truth_boundary": _truth_boundary(source.get("truth_boundary")),
        "product_boundary": _product_boundary(source.get("product_boundary")),
        "notes": _list_of_strings(source.get("notes", [])),
        "_source_identity": str(source_id),
    }


def _normalize_candidate(source: dict[str, Any]) -> dict[str, Any]:
    record = _base_candidate(source, str(source.get("candidate_origin", "static_demo")), str(source.get("candidate_type", "")), str(source.get("candidate_label", "Candidate")))
    record.update(source)
    return record


def _normalized_status(status: str) -> str:
    if status in ALLOWED_STATUSES:
        return status
    if status in {"unresolved", "weakly_resolved", "partially_resolved"}:
        return "candidate"
    if status in {"pass", "warn", "allowed_for_dry_run", "gated"}:
        return "needs_review"
    if status in {"blocked", "policy_blocked"}:
        return "policy_blocked"
    if status in {"not_evaluable", "approval_gated", "deferred_future"}:
        return "deferred"
    return "candidate"


def _canonical_key(record: Mapping[str, Any]) -> str:
    basis = "|".join(
        str(record.get(key, "")).strip().lower()
        for key in ("candidate_origin", "candidate_type", "candidate_label", "_source_identity")
    )
    return "candidate:" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


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
            errors.extend(_scan_forbidden_claims(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_scan_forbidden_claims(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        for phrase in sorted(FORBIDDEN_CLAIM_PHRASES):
            if phrase in lowered:
                errors.append(f"{path}: forbidden claim phrase {phrase!r}")
    return errors

