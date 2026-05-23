"""Local-only SearchNeed runtime helpers.

This module is intentionally standard-library only and side-effect free. It
does not call networks, read browser state, write files, mutate public search,
execute WorkUnits, or mutate index state.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from typing import Any, Mapping

from runtime.local.foundry import query_observation, search_miss_ledger


SCHEMA_VERSION = "search_need_record.v0"
REPORT_SCHEMA_VERSION = "search_need_runtime_report.v0"

ALLOWED_STATUSES = {
    "example_only",
    "recorded_local",
    "privacy_filtered",
    "poisoning_guarded",
    "unresolved",
    "weakly_resolved",
    "partially_resolved",
    "candidate_available",
    "evidence_needed",
    "source_gap",
    "capability_gap",
    "policy_blocked",
    "needs_review",
    "approved_for_workunit_seed_future",
    "approved_for_source_lead_future",
    "approved_for_candidate_review_future",
    "rejected",
    "duplicate",
    "deferred",
    "not_evaluable",
}
CURRENT_ALLOWED_STATUSES = {
    "example_only",
    "recorded_local",
    "privacy_filtered",
    "poisoning_guarded",
    "unresolved",
    "weakly_resolved",
    "source_gap",
    "capability_gap",
    "policy_blocked",
    "needs_review",
    "not_evaluable",
}
ALLOWED_NEED_INTENTS = {
    "find_software",
    "find_exact_version",
    "find_compatible_version",
    "find_driver",
    "find_file_inside_container",
    "find_article_inside_scan",
    "find_manual_or_documentation",
    "find_source_release",
    "find_package_metadata",
    "compare_sources",
    "verify_identity",
    "verify_compatibility",
    "explain_absence",
    "source_gap_research",
    "policy_review",
    "not_evaluable",
}
ALLOWED_INPUT_TYPES = {
    "search_miss_record",
    "query_observation_record",
    "manual_observation_record",
    "observation_candidate",
    "local_eval_failure",
    "static_demo_fixture",
    "agent_assisted_candidate",
    "explicit_test_fixture",
}
ALLOWED_OUTPUT_TYPES = {
    "search_need_record",
    "search_need_summary",
    "workunit_seed_future",
    "source_lead_candidate_future",
    "candidate_review_seed_future",
    "observation_candidate_future",
    "review_item_future",
}
FORBIDDEN_OUTPUT_TYPES = {
    "global_absence_proof",
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
    "search_need_is_public_truth",
    "search_need_is_accepted_evidence",
    "search_need_can_mutate_master_index",
    "search_need_is_exhaustive_global_absence",
    "search_need_claims_source_universe_exhausted",
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
PRIVACY_FALSE_FIELDS = query_observation.PRIVACY_FALSE_FIELDS
REVIEW_TRUE_FIELDS = {
    "human_review_required_for_downstream_use",
    "workunit_review_required",
    "source_lead_review_required",
    "candidate_review_required",
    "master_index_review_required",
}
OVERCLAIM_PHRASES = {
    "whole web was searched",
    "archive universe was searched",
    "source universe is exhausted",
    "source universe exhausted",
    "requested object does not exist globally",
    "object does not exist",
    "does not exist anywhere",
    "globally absent",
    "global absence proof",
    "exhaustive global absence",
    "exhaustive global search proof",
}
FORBIDDEN_CLAIM_PHRASES = OVERCLAIM_PHRASES | {
    "accepted public truth",
    "accepted evidence truth",
    "canonical source observation",
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
    "production readiness",
}


def default_policy() -> dict[str, Any]:
    return {
        "allowed_input_types": sorted(ALLOWED_INPUT_TYPES),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "current_allowed_statuses": sorted(CURRENT_ALLOWED_STATUSES),
        "allowed_need_intents": sorted(ALLOWED_NEED_INTENTS),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "review_required_before_downstream_use": True,
    }


def build_search_need_from_search_miss(
    search_miss_record: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build or normalize a SearchNeed record from explicit local input."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(search_miss_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        record = _normalize_search_need(source)
    else:
        miss = search_miss_ledger.build_search_miss_from_query_observation(source)
        record = _build_from_search_miss(miss)

    record["need_intent"] = classify_need_intent(record)
    record["privacy_posture"] = preserve_privacy_posture(record, active_policy)
    record["poisoning_guard_posture"] = detect_poisoning_risks(record, active_policy)
    if record.get("search_need_status") in {"policy_blocked", "not_evaluable"}:
        pass
    elif record["privacy_posture"].get("privacy_filtered"):
        record["search_need_status"] = "privacy_filtered"
    record["exhaustive_absence_claimed"] = bool(record.get("exhaustive_absence_claimed", False))
    record["canonical_need_key"] = record.get("canonical_need_key") or _canonical_need_key(record)
    record["search_need_id"] = record.get("search_need_id") or f"search_need.{record['need_intent']}.{_stable_digest(record)[:12]}.v0"
    record["downstream_seed_candidates"] = _default_downstream_seed_candidates(record)
    return record


def build_search_need_from_query_observation(
    query_observation_record: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    miss = search_miss_ledger.build_search_miss_from_query_observation(query_observation_record)
    return build_search_need_from_search_miss(miss, policy)


def validate_search_need(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a SearchNeed record."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required = {
        "schema_version",
        "search_need_id",
        "search_need_status",
        "need_intent",
        "need_label",
        "canonical_need_key",
        "query_summary",
        "interpreted_intent",
        "object_family",
        "product_or_topic",
        "version_or_state",
        "platform_or_context",
        "artifact_type",
        "desired_user_action",
        "aliases",
        "demand_summary",
        "source_gap_summary",
        "capability_gap_summary",
        "extraction_gap_summary",
        "compatibility_gap_summary",
        "representation_gap_summary",
        "identity_gap_summary",
        "temporal_version_gap_summary",
        "ranking_gap_summary",
        "policy_block_summary",
        "absence_scope",
        "exhaustive_absence_claimed",
        "near_match_summary",
        "candidate_summary",
        "downstream_seed_candidates",
        "review_gates",
        "privacy_posture",
        "poisoning_guard_posture",
        "limitations",
        "truth_boundary",
        "product_boundary",
        "notes",
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if record.get("search_need_status") not in ALLOWED_STATUSES:
        errors.append("search_need_status is not allowed")
    if record.get("search_need_status") not in CURRENT_ALLOWED_STATUSES:
        errors.append("current search_need_status is not allowed")
    if record.get("need_intent") not in ALLOWED_NEED_INTENTS:
        errors.append("need_intent is not allowed")

    query_summary = record.get("query_summary", {})
    if not isinstance(query_summary, Mapping):
        errors.append("query_summary must be an object")
    else:
        input_type = query_summary.get("input_type")
        if input_type not in ALLOWED_INPUT_TYPES:
            errors.append("query_summary.input_type is not allowed")

    demand = record.get("demand_summary", {})
    if not isinstance(demand, Mapping):
        errors.append("demand_summary must be an object")
    else:
        if demand.get("aggregate_only") is not True:
            errors.append("demand_summary.aggregate_only must be true")
        if demand.get("raw_query_retention") != "synthetic_or_reviewed_input_only":
            errors.append("demand_summary.raw_query_retention must be synthetic_or_reviewed_input_only")
        if demand.get("public_telemetry_enabled") is not False:
            errors.append("demand_summary.public_telemetry_enabled must be false")
        if demand.get("account_level_tracking") is not False:
            errors.append("demand_summary.account_level_tracking must be false")
        if demand.get("production_analytics") is not False:
            errors.append("demand_summary.production_analytics must be false")

    for output in record.get("downstream_seed_candidates", []):
        output_type = output.get("output_type") if isinstance(output, Mapping) else None
        if output_type in FORBIDDEN_OUTPUT_TYPES:
            errors.append(f"forbidden downstream output: {output_type}")
        if output_type not in ALLOWED_OUTPUT_TYPES:
            errors.append(f"unknown downstream output: {output_type}")
        if isinstance(output, Mapping) and output.get("requires_review") is not True:
            errors.append(f"downstream output {output_type} must require review")
        if isinstance(output, Mapping) and output.get("created") is not False:
            errors.append(f"downstream output {output_type} must not be created by this milestone")

    privacy = record.get("privacy_posture", {})
    if not isinstance(privacy, Mapping):
        errors.append("privacy_posture must be an object")
    else:
        for key in sorted(PRIVACY_FALSE_FIELDS):
            if privacy.get(key) is not False:
                errors.append(f"privacy_posture.{key} must be false")

    poisoning = record.get("poisoning_guard_posture", {})
    if not isinstance(poisoning, Mapping):
        errors.append("poisoning_guard_posture must be an object")
    elif poisoning.get("poisoning_guarded") is not True:
        errors.append("poisoning_guard_posture.poisoning_guarded must be true")

    if record.get("exhaustive_absence_claimed") is not False:
        errors.append("exhaustive_absence_claimed must be false")
    if detect_exhaustive_absence_overclaim(record):
        errors.append("record contains exhaustive absence overclaim")

    errors.extend(_check_true_map(record.get("review_gates", {}), REVIEW_TRUE_FIELDS, "review_gates"))
    errors.extend(_check_false_map(record.get("truth_boundary", {}), TRUTH_BOUNDARY_FALSE_FIELDS, "truth_boundary"))
    if isinstance(record.get("truth_boundary"), Mapping):
        if record["truth_boundary"].get("human_review_required_for_downstream_use") is not True:
            errors.append("truth_boundary.human_review_required_for_downstream_use must be true")
    errors.extend(_check_false_map(record.get("product_boundary", {}), PRODUCT_BOUNDARY_FALSE_FIELDS, "product_boundary"))
    errors.extend(_scan_for_forbidden_claims(record))

    return sorted(errors)


def summarize_search_need(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "search_need_id": record.get("search_need_id"),
        "search_need_status": record.get("search_need_status"),
        "need_intent": record.get("need_intent"),
        "need_label": record.get("need_label"),
        "canonical_need_key": record.get("canonical_need_key"),
        "query_text": record.get("query_summary", {}).get("query_text"),
        "demand_source_count": record.get("demand_summary", {}).get("demand_source_count"),
        "review_required": record.get("truth_boundary", {}).get("human_review_required_for_downstream_use") is True,
        "exhaustive_absence_claimed": record.get("exhaustive_absence_claimed") is True,
        "truth_boundary": {
            "search_need_is_public_truth": False,
            "search_need_is_accepted_evidence": False,
            "search_need_can_mutate_master_index": False,
        },
    }


def classify_need_intent(record: Mapping[str, Any]) -> str:
    declared = record.get("need_intent")
    if declared in ALLOWED_NEED_INTENTS:
        return str(declared)
    status = record.get("search_need_status")
    if status == "policy_blocked" or record.get("policy_block_summary"):
        return "policy_review"
    if status == "not_evaluable":
        return "not_evaluable"

    text = _record_text(
        {
            "query": record.get("query_summary", {}),
            "label": record.get("need_label", ""),
            "object_family": record.get("object_family", ""),
            "artifact_type": record.get("artifact_type", ""),
            "notes": record.get("notes", []),
        }
    ).casefold()
    if "driver" in text:
        return "find_driver"
    if "article" in text or "scan" in text or "magazine" in text:
        return "find_article_inside_scan"
    if "exact version" in text or "version" in text or any(token in text for token in ("v1.", "v2.", "v3.")):
        return "find_exact_version"
    if "compatible" in text or "compatibility" in text:
        return "find_compatible_version"
    if "manual" in text or "documentation" in text:
        return "find_manual_or_documentation"
    if "source release" in text:
        return "find_source_release"
    if "package metadata" in text:
        return "find_package_metadata"
    if record.get("source_gap_summary"):
        return "source_gap_research"
    return "find_software"


def derive_workunit_seed_candidate(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "output_type": "workunit_seed_future",
        "output_status": "review_gated_future",
        "requires_review": True,
        "created": False,
        "source_search_need_id": record.get("search_need_id"),
        "seed_summary": "Future WorkUnit seed may inspect this review-gated SearchNeed.",
    }


def derive_source_lead_candidate(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "output_type": "source_lead_candidate_future",
        "output_status": "review_gated_future",
        "requires_review": True,
        "created": False,
        "source_search_need_id": record.get("search_need_id"),
        "seed_summary": "Future source lead may be prepared after SearchNeed review.",
    }


def detect_exhaustive_absence_overclaim(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> bool:
    if record.get("exhaustive_absence_claimed") is True:
        return True
    text = _record_text(record).casefold()
    return any(phrase in text for phrase in OVERCLAIM_PHRASES)


def preserve_privacy_posture(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(record.get("privacy_posture", {}))
    query_text = str(record.get("query_summary", {}).get("query_text", ""))
    if not query_text:
        query_text = str(record.get("query_text", ""))
    privacy_source = query_observation.redact_or_hash_query_if_required(
        {
            "query_text": query_text,
            "privacy_posture": source,
            "notes": record.get("notes", []),
        }
    )
    privacy = dict(privacy_source["privacy_posture"])
    privacy["raw_query_retained"] = False
    privacy["public_telemetry_enabled"] = False
    privacy["accounts_required"] = False
    privacy["raw_public_query_logging_enabled"] = False
    privacy["private_data_allowed"] = False
    privacy["browser_state_collection_allowed"] = False
    privacy["account_identity_collected"] = False
    privacy["location_collected"] = False
    return privacy


def detect_poisoning_risks(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return query_observation.detect_poisoning_risks(
        {
            "query_text": record.get("query_summary", {}).get("query_text", record.get("query_text", "")),
            "notes": record.get("notes", []),
            "aliases": record.get("aliases", []),
            "near_match_summary": record.get("near_match_summary", {}),
            "candidate_summary": record.get("candidate_summary", {}),
        }
    )


def format_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# SearchNeed Summary",
        "",
        f"- search_need_id: {summary.get('search_need_id')}",
        f"- search_need_status: {summary.get('search_need_status')}",
        f"- need_intent: {summary.get('need_intent')}",
        f"- need_label: {summary.get('need_label')}",
        f"- review_required: {str(summary.get('review_required')).lower()}",
        "- public_truth: false",
        "- accepted_evidence: false",
        "- master_index_mutation: false",
        "- exhaustive_absence: false",
    ]
    return "\n".join(lines) + "\n"


def _normalize_search_need(source: Mapping[str, Any]) -> dict[str, Any]:
    record = deepcopy(dict(source))
    record.setdefault("search_need_status", "unresolved")
    record.setdefault("need_intent", "find_software")
    record.setdefault("need_label", "Unresolved local search need")
    record.setdefault("canonical_need_key", "")
    record.setdefault("query_summary", {})
    record.setdefault("interpreted_intent", {})
    record.setdefault("object_family", "")
    record.setdefault("product_or_topic", "")
    record.setdefault("version_or_state", "")
    record.setdefault("platform_or_context", "")
    record.setdefault("artifact_type", "")
    record.setdefault("desired_user_action", "")
    record.setdefault("aliases", [])
    record.setdefault("demand_summary", _default_demand_summary(record))
    record.setdefault("source_gap_summary", "")
    record.setdefault("capability_gap_summary", "")
    record.setdefault("extraction_gap_summary", "")
    record.setdefault("compatibility_gap_summary", "")
    record.setdefault("representation_gap_summary", "")
    record.setdefault("identity_gap_summary", "")
    record.setdefault("temporal_version_gap_summary", "")
    record.setdefault("ranking_gap_summary", "")
    record.setdefault("policy_block_summary", "")
    record.setdefault("absence_scope", "local_explicit_input_only")
    record.setdefault("exhaustive_absence_claimed", False)
    record.setdefault("near_match_summary", {})
    record.setdefault("candidate_summary", {})
    record.setdefault("downstream_seed_candidates", [])
    record.setdefault("review_gates", _default_review_gates())
    record.setdefault("privacy_posture", {})
    record.setdefault("poisoning_guard_posture", {})
    record.setdefault("limitations", [])
    record.setdefault("truth_boundary", _default_truth_boundary())
    record.setdefault("product_boundary", _default_product_boundary())
    record.setdefault("notes", [])
    record.setdefault("schema_version", SCHEMA_VERSION)
    return record


def _build_from_search_miss(miss: Mapping[str, Any]) -> dict[str, Any]:
    status = _status_from_miss(miss)
    query_text = miss.get("query_summary", {}).get("query_text", "")
    record = {
        "schema_version": SCHEMA_VERSION,
        "search_need_id": "",
        "search_need_status": status,
        "need_intent": "",
        "need_label": _need_label_from_miss(miss),
        "canonical_need_key": "",
        "query_summary": {
            "source_record_ref": miss.get("search_miss_id"),
            "input_type": "search_miss_record",
            "query_text": query_text,
            "query_id_optional": miss.get("query_summary", {}).get("query_id_optional"),
            "related_query_observation_ref": miss.get("related_query_observation_ref"),
            "related_search_miss_ref": miss.get("search_miss_id"),
            "source_mode": "local_only",
            "search_mode": miss.get("query_summary", {}).get("search_mode", "local_only"),
            "observed_result_summary": deepcopy(miss.get("observed_result_summary", {})),
            "miss_reason_summary": miss.get("miss_reason_summary"),
            "failure_modes": list(miss.get("failure_modes", [])),
            "sources_checked": [],
            "sources_not_checked": ["live_web", "external_archives", "hosted_user_traffic"],
        },
        "interpreted_intent": {
            "source": "deterministic_keyword_classification",
            "confidence": "low",
            "limitations": ["Intent is a local planning hint, not object identity truth."],
        },
        "object_family": _object_family_from_text(query_text),
        "product_or_topic": query_text,
        "version_or_state": "",
        "platform_or_context": "",
        "artifact_type": "",
        "desired_user_action": "find_reviewable_source_or_candidate",
        "aliases": [],
        "demand_summary": _default_demand_summary(miss),
        "source_gap_summary": miss.get("source_gap_summary", ""),
        "capability_gap_summary": miss.get("capability_gap_summary", ""),
        "extraction_gap_summary": miss.get("extraction_gap_summary", ""),
        "compatibility_gap_summary": miss.get("compatibility_gap_summary", ""),
        "representation_gap_summary": miss.get("representation_gap_summary", ""),
        "identity_gap_summary": miss.get("identity_gap_summary", ""),
        "temporal_version_gap_summary": miss.get("temporal_version_gap_summary", ""),
        "ranking_gap_summary": miss.get("ranking_gap_summary", ""),
        "policy_block_summary": miss.get("policy_block_summary", ""),
        "absence_scope": "local_explicit_input_only",
        "exhaustive_absence_claimed": False,
        "near_match_summary": {"near_matches": deepcopy(miss.get("near_matches", []))},
        "candidate_summary": {"candidate_available": False, "accepted_public_status": False},
        "downstream_seed_candidates": [],
        "review_gates": _default_review_gates(),
        "privacy_posture": deepcopy(miss.get("privacy_posture", {})),
        "poisoning_guard_posture": deepcopy(miss.get("poisoning_guard_posture", {})),
        "limitations": list(miss.get("limitations", [])) + [
            "SearchNeed is derived from explicit local input only.",
            "No WorkUnit, live source, model, or public traffic action was executed.",
        ],
        "truth_boundary": _default_truth_boundary(),
        "product_boundary": _default_product_boundary(),
        "notes": sorted(set(list(miss.get("notes", [])) + ["SearchNeed is a review-gated unresolved-search object only."])),
    }
    return record


def _status_from_miss(miss: Mapping[str, Any]) -> str:
    if miss.get("search_miss_status") == "policy_blocked" or miss.get("search_miss_kind") == "policy_blocked":
        return "policy_blocked"
    if miss.get("search_miss_status") == "not_evaluable" or miss.get("search_miss_kind") == "not_evaluable":
        return "not_evaluable"
    if miss.get("source_gap_summary"):
        return "source_gap"
    if miss.get("capability_gap_summary"):
        return "capability_gap"
    if miss.get("search_miss_kind") in {"weak_result", "near_match_only", "noisy_result_list", "ranking_gap"}:
        return "weakly_resolved"
    return "unresolved"


def _need_label_from_miss(miss: Mapping[str, Any]) -> str:
    query = str(miss.get("query_summary", {}).get("query_text", "local search need")).strip()
    return f"Resolve local search need for {query}" if query else "Resolve local search need"


def _object_family_from_text(text: str) -> str:
    lowered = text.casefold()
    if "driver" in lowered:
        return "driver"
    if "article" in lowered or "scan" in lowered or "magazine" in lowered:
        return "article_or_scan_member"
    if "manual" in lowered or "documentation" in lowered:
        return "documentation"
    if "package" in lowered or "software" in lowered or "app" in lowered:
        return "software"
    return "unresolved_object"


def _default_downstream_seed_candidates(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        derive_workunit_seed_candidate(record),
        derive_source_lead_candidate(record),
        {
            "output_type": "candidate_review_seed_future",
            "output_status": "review_gated_future",
            "requires_review": True,
            "created": False,
            "source_search_need_id": record.get("search_need_id"),
            "seed_summary": "Future candidate review seed may be prepared after SearchNeed review.",
        },
    ]


def _default_demand_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "demand_source_count": 1,
        "demand_signal_sources": [str(source.get("search_miss_id") or source.get("search_need_id") or "explicit_local_input")],
        "aggregate_only": True,
        "raw_query_retention": "synthetic_or_reviewed_input_only",
        "privacy_filtered": False,
        "poisoning_guarded": True,
        "demand_score_available": False,
        "demand_score": None,
        "demand_score_limitations": "No production analytics or public telemetry are used.",
        "first_seen_or_recorded_when_available": "not_recorded",
        "last_seen_or_recorded_when_available": "not_recorded",
        "public_telemetry_enabled": False,
        "account_level_tracking": False,
        "production_analytics": False,
        "notes": ["Demand summary is a local aggregate planning hint only."],
    }


def _default_review_gates() -> dict[str, bool]:
    return {field: True for field in REVIEW_TRUE_FIELDS}


def _default_truth_boundary() -> dict[str, bool]:
    boundary = {field: False for field in TRUTH_BOUNDARY_FALSE_FIELDS}
    boundary["human_review_required_for_downstream_use"] = True
    return boundary


def _default_product_boundary() -> dict[str, bool]:
    return {field: False for field in PRODUCT_BOUNDARY_FALSE_FIELDS}


def _canonical_need_key(record: Mapping[str, Any]) -> str:
    pieces = [
        str(record.get("need_intent", "")),
        str(record.get("object_family", "")),
        str(record.get("product_or_topic", "")),
        str(record.get("version_or_state", "")),
        str(record.get("platform_or_context", "")),
        str(record.get("artifact_type", "")),
    ]
    normalized = query_observation.normalize_query(" ".join(piece for piece in pieces if piece))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"search_need_key.{digest[:16]}.v0"


def _stable_digest(record: Mapping[str, Any]) -> str:
    text = "|".join(
        [
            str(record.get("need_intent", "")),
            str(record.get("query_summary", {}).get("query_text", "")),
            str(record.get("product_or_topic", "")),
            str(record.get("version_or_state", "")),
        ]
    )
    return hashlib.sha256(query_observation.normalize_query(text).encode("utf-8")).hexdigest()


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
    for phrase in sorted(FORBIDDEN_CLAIM_PHRASES):
        if phrase in text:
            errors.append(f"forbidden claim phrase: {phrase}")
    return errors
