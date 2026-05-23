"""Local-only Search Miss Ledger runtime helpers.

This module is intentionally standard-library only and side-effect free. It
does not call networks, read browser state, write files, mutate public search,
or mutate index state.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from typing import Any, Mapping

from runtime.local.foundry import query_observation


SCHEMA_VERSION = "search_miss_ledger_record.v0"
REPORT_SCHEMA_VERSION = "search_miss_ledger_runtime_report.v0"
QUERY_OBSERVATION_CONTRACT_REF = "contracts/query/query_observation.v0.json"

ALLOWED_STATUSES = {
    "example_only",
    "recorded_local",
    "privacy_filtered",
    "poisoning_guarded",
    "needs_review",
    "approved_for_search_need_seed_future",
    "approved_for_workunit_seed_future",
    "approved_for_source_lead_future",
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
ALLOWED_MISS_KINDS = {
    "empty_result",
    "weak_result",
    "near_match_only",
    "noisy_result_list",
    "policy_blocked",
    "capability_gap",
    "source_gap",
    "extraction_gap",
    "compatibility_gap",
    "representation_gap",
    "identity_gap",
    "temporal_version_gap",
    "ranking_gap",
    "query_interpretation_gap",
    "dead_link_or_unavailable",
    "external_baseline_unavailable",
    "not_evaluable",
}
ALLOWED_INPUT_SOURCES = {
    "query_observation_record",
    "explicit_test_fixture",
    "local_eval",
    "manual_observation_candidate",
    "public_search_rehearsal_fixture",
    "static_demo_fixture",
    "agent_assisted_candidate",
    "future_public_search_with_privacy_filter",
    "future_node_workunit",
}
CURRENT_ALLOWED_INPUT_SOURCES = {
    "query_observation_record",
    "explicit_test_fixture",
    "local_eval",
    "manual_observation_candidate",
    "public_search_rehearsal_fixture",
    "static_demo_fixture",
    "agent_assisted_candidate",
}
ALLOWED_FAILURE_MODES = ALLOWED_MISS_KINDS | {
    "none",
    "privacy_filtered",
    "poisoning_risk",
}
ALLOWED_OUTPUT_TYPES = {
    "search_miss_record",
    "search_miss_summary",
    "search_need_seed_future",
    "workunit_seed_future",
    "source_lead_candidate_future",
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
    "search_miss_is_public_truth",
    "search_miss_is_accepted_evidence",
    "search_miss_can_mutate_master_index",
    "search_miss_is_exhaustive_global_absence",
    "search_miss_claims_source_universe_exhausted",
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
    "search_need_review_required",
    "workunit_review_required",
    "source_lead_review_required",
    "master_index_review_required",
}
OVERCLAIM_PHRASES = {
    "whole web was searched",
    "source universe is exhausted",
    "source universe exhausted",
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
        "allowed_input_sources": sorted(ALLOWED_INPUT_SOURCES),
        "current_allowed_input_sources": sorted(CURRENT_ALLOWED_INPUT_SOURCES),
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "current_allowed_statuses": sorted(CURRENT_ALLOWED_STATUSES),
        "allowed_miss_kinds": sorted(ALLOWED_MISS_KINDS),
        "allowed_failure_modes": sorted(ALLOWED_FAILURE_MODES),
        "allowed_output_types": sorted(ALLOWED_OUTPUT_TYPES),
        "forbidden_output_types": sorted(FORBIDDEN_OUTPUT_TYPES),
        "review_required_before_downstream_use": True,
    }


def build_search_miss_from_query_observation(
    query_observation_record: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build or normalize a search miss from explicit local input."""

    active_policy = policy or default_policy()
    source = deepcopy(dict(query_observation_record))
    if source.get("schema_version") == SCHEMA_VERSION:
        record = _normalize_search_miss(source)
    else:
        observation = query_observation.build_query_observation(source)
        record = _build_from_query_observation(observation)

    record["privacy_posture"] = preserve_privacy_posture(record, active_policy)
    record["poisoning_guard_posture"] = detect_poisoning_risks(record, active_policy)
    record["failure_modes"] = classify_miss_failure_modes(record)
    if record.get("search_miss_kind") in {"policy_blocked", "not_evaluable"}:
        record["search_miss_status"] = record["search_miss_kind"]
    elif record["privacy_posture"].get("privacy_filtered"):
        record["search_miss_status"] = "privacy_filtered"
    record["downstream_seed_candidates"] = _default_downstream_seed_candidates(record)
    record["exhaustive_absence_claimed"] = bool(record.get("exhaustive_absence_claimed", False))
    return record


def validate_search_miss(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return deterministic validation errors for a search miss record."""

    active_policy = policy or default_policy()
    errors: list[str] = []
    required = {
        "schema_version",
        "search_miss_id",
        "search_miss_status",
        "search_miss_kind",
        "related_query_observation_ref",
        "query_summary",
        "observed_result_summary",
        "miss_reason_summary",
        "failure_modes",
        "near_matches",
        "rejected_matches",
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
    if record.get("search_miss_status") not in ALLOWED_STATUSES:
        errors.append("search_miss_status is not allowed")
    if record.get("search_miss_status") not in CURRENT_ALLOWED_STATUSES:
        errors.append("current search_miss_status is not allowed")
    if record.get("search_miss_kind") not in ALLOWED_MISS_KINDS:
        errors.append("search_miss_kind is not allowed")

    query_summary = record.get("query_summary", {})
    if not isinstance(query_summary, Mapping):
        errors.append("query_summary must be an object")
    else:
        source = query_summary.get("query_source")
        if source not in ALLOWED_INPUT_SOURCES:
            errors.append("query_summary.query_source is not allowed")
        if source not in CURRENT_ALLOWED_INPUT_SOURCES:
            errors.append("current runtime cannot accept future query source")

    failure_modes = record.get("failure_modes", [])
    if not isinstance(failure_modes, list):
        errors.append("failure_modes must be a list")
    else:
        unknown = sorted(str(mode) for mode in failure_modes if mode not in ALLOWED_FAILURE_MODES)
        if unknown:
            errors.append(f"failure_modes contains unknown values: {', '.join(unknown)}")

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


def summarize_search_miss(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "search_miss_id": record.get("search_miss_id"),
        "search_miss_status": record.get("search_miss_status"),
        "search_miss_kind": record.get("search_miss_kind"),
        "related_query_observation_ref": record.get("related_query_observation_ref"),
        "failure_modes": list(record.get("failure_modes", [])),
        "result_count": record.get("observed_result_summary", {}).get("result_count"),
        "result_quality": record.get("observed_result_summary", {}).get("result_quality"),
        "near_match_count": len(record.get("near_matches", [])),
        "review_required": record.get("truth_boundary", {}).get("human_review_required_for_downstream_use") is True,
        "exhaustive_absence_claimed": record.get("exhaustive_absence_claimed") is True,
        "truth_boundary": {
            "search_miss_is_public_truth": False,
            "search_miss_is_accepted_evidence": False,
            "search_miss_can_mutate_master_index": False,
        },
    }


def classify_miss_failure_modes(record: Mapping[str, Any]) -> list[str]:
    modes = set(record.get("failure_modes", []))
    kind = str(record.get("search_miss_kind", ""))
    if kind in ALLOWED_MISS_KINDS:
        modes.add(kind)

    observed = record.get("observed_result_summary", {})
    quality = observed.get("result_quality")
    result_count = observed.get("result_count")
    first_useful = observed.get("first_useful_result_rank")
    if record.get("search_miss_status") == "policy_blocked" or quality == "blocked":
        modes.add("policy_blocked")
    elif record.get("search_miss_status") == "not_evaluable" or quality == "not_evaluable":
        modes.add("not_evaluable")
    elif result_count == 0 or quality == "empty":
        modes.add("empty_result")
    elif record.get("near_matches") and first_useful is None:
        modes.add("near_match_only")
    elif quality == "noisy":
        modes.add("noisy_result_list")
    elif quality in {"weak", "mixed"} or first_useful is None:
        modes.add("weak_result")
    return sorted(mode for mode in modes if mode in ALLOWED_FAILURE_MODES)


def derive_search_need_seed_candidate(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "output_type": "search_need_seed_future",
        "output_status": "review_gated_future",
        "requires_review": True,
        "created": False,
        "source_search_miss_id": record.get("search_miss_id"),
        "seed_summary": record.get("miss_reason_summary"),
    }


def derive_workunit_seed_candidate(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "output_type": "workunit_seed_future",
        "output_status": "review_gated_future",
        "requires_review": True,
        "created": False,
        "source_search_miss_id": record.get("search_miss_id"),
        "seed_summary": "Future WorkUnit seed may inspect this review-gated search miss.",
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
    query_text = str(record.get("query_summary", {}).get("query_text", ""))
    if not query_text:
        query_text = str(record.get("query_text", ""))
    return query_observation.detect_poisoning_risks(
        {
            "query_text": query_text,
            "notes": record.get("notes", []),
            "near_matches": record.get("near_matches", []),
            "rejected_matches": record.get("rejected_matches", []),
        }
    )


def format_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Search Miss Summary",
        "",
        f"- search_miss_id: {summary.get('search_miss_id')}",
        f"- search_miss_status: {summary.get('search_miss_status')}",
        f"- search_miss_kind: {summary.get('search_miss_kind')}",
        f"- result_count: {summary.get('result_count')}",
        f"- result_quality: {summary.get('result_quality')}",
        f"- review_required: {str(summary.get('review_required')).lower()}",
        "- public_truth: false",
        "- accepted_evidence: false",
        "- master_index_mutation: false",
        "- exhaustive_absence: false",
    ]
    return "\n".join(lines) + "\n"


def _normalize_search_miss(source: Mapping[str, Any]) -> dict[str, Any]:
    record = deepcopy(dict(source))
    record.setdefault("search_miss_status", "recorded_local")
    record.setdefault("search_miss_kind", "weak_result")
    record.setdefault("related_query_observation_ref", None)
    record.setdefault("query_summary", {})
    record.setdefault("interpreted_intent_optional", None)
    record.setdefault("observed_result_summary", {})
    record.setdefault("miss_reason_summary", "Local explicit input suggests a review-gated search gap.")
    record.setdefault("failure_modes", [])
    record.setdefault("near_matches", [])
    record.setdefault("rejected_matches", [])
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
    record.setdefault("downstream_seed_candidates", [])
    record.setdefault("review_gates", _default_review_gates())
    record.setdefault("privacy_posture", {})
    record.setdefault("poisoning_guard_posture", {})
    record.setdefault("limitations", [])
    record.setdefault("truth_boundary", _default_truth_boundary())
    record.setdefault("product_boundary", _default_product_boundary())
    record.setdefault("notes", [])
    record.setdefault("schema_version", SCHEMA_VERSION)
    record.setdefault("search_miss_id", _search_miss_id(record))
    return record


def _build_from_query_observation(observation: Mapping[str, Any]) -> dict[str, Any]:
    outcome = query_observation.classify_query_outcome(observation)
    miss_kind = _miss_kind_from_outcome(outcome, observation)
    record = {
        "schema_version": SCHEMA_VERSION,
        "search_miss_id": f"search_miss.{miss_kind}.{_stable_digest(observation)[:12]}.v0",
        "search_miss_status": _status_from_kind(miss_kind),
        "search_miss_kind": miss_kind,
        "related_query_observation_ref": observation.get("query_observation_id"),
        "query_summary": {
            "query_text": observation.get("query_text"),
            "query_id_optional": observation.get("query_id_optional"),
            "query_source": "query_observation_record",
            "source_query_observation_query_source": observation.get("query_source"),
            "search_mode": observation.get("search_mode"),
            "local_index_mode": observation.get("local_index_mode"),
            "query_hash": observation.get("privacy_posture", {}).get("query_hash"),
            "redacted_query_text": observation.get("privacy_posture", {}).get("redacted_query_text"),
        },
        "interpreted_intent_optional": None,
        "observed_result_summary": {
            "result_count": observation.get("result_count"),
            "result_quality": observation.get("result_quality"),
            "top_result_refs": list(observation.get("top_result_refs", [])),
            "first_useful_result_rank": observation.get("first_useful_result_rank"),
        },
        "miss_reason_summary": _miss_reason_summary(miss_kind),
        "failure_modes": list(observation.get("failure_modes", [])),
        "near_matches": [],
        "rejected_matches": [],
        "source_gap_summary": "Local explicit input did not identify a useful source." if miss_kind in {"empty_result", "source_gap"} else "",
        "capability_gap_summary": "",
        "extraction_gap_summary": "",
        "compatibility_gap_summary": "",
        "representation_gap_summary": "",
        "identity_gap_summary": "",
        "temporal_version_gap_summary": "",
        "ranking_gap_summary": "Useful result was not available in the local explicit result set." if miss_kind in {"weak_result", "noisy_result_list"} else "",
        "policy_block_summary": "Requested action remains blocked by source/runtime policy." if miss_kind == "policy_blocked" else "",
        "absence_scope": "local_explicit_input_only",
        "exhaustive_absence_claimed": False,
        "downstream_seed_candidates": [],
        "review_gates": _default_review_gates(),
        "privacy_posture": deepcopy(observation.get("privacy_posture", {})),
        "poisoning_guard_posture": deepcopy(observation.get("poisoning_guard_posture", {})),
        "limitations": [
            "Search miss is derived from explicit local input only.",
            "No live source, web, archive, or public traffic search was performed.",
        ],
        "truth_boundary": _default_truth_boundary(),
        "product_boundary": _default_product_boundary(),
        "notes": sorted(set(list(observation.get("notes", [])) + ["Search miss is a review-gated gap signal only."])),
    }
    return record


def _miss_kind_from_outcome(outcome: str, observation: Mapping[str, Any]) -> str:
    if outcome == "policy_blocked":
        return "policy_blocked"
    if outcome == "not_evaluable":
        return "not_evaluable"
    if outcome == "empty_result":
        return "empty_result"
    if "ranking_gap" in observation.get("failure_modes", []):
        return "ranking_gap"
    return "weak_result"


def _status_from_kind(kind: str) -> str:
    if kind in {"policy_blocked", "not_evaluable"}:
        return kind
    return "recorded_local"


def _miss_reason_summary(kind: str) -> str:
    summaries = {
        "empty_result": "Local explicit input produced no result to review.",
        "weak_result": "Local explicit input produced weak or non-useful results.",
        "near_match_only": "Local explicit input produced near matches but no useful result.",
        "noisy_result_list": "Local explicit input produced noisy results that need review.",
        "policy_blocked": "Policy blocks the requested source or runtime action.",
        "not_evaluable": "Local explicit input was not evaluable.",
    }
    return summaries.get(kind, "Local explicit input suggests a review-gated search gap.")


def _default_downstream_seed_candidates(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        derive_search_need_seed_candidate(record),
        derive_workunit_seed_candidate(record),
        {
            "output_type": "source_lead_candidate_future",
            "output_status": "review_gated_future",
            "requires_review": True,
            "created": False,
            "source_search_miss_id": record.get("search_miss_id"),
            "seed_summary": "Future source lead may be prepared after review.",
        },
    ]


def _default_review_gates() -> dict[str, bool]:
    return {field: True for field in REVIEW_TRUE_FIELDS}


def _default_truth_boundary() -> dict[str, bool]:
    boundary = {field: False for field in TRUTH_BOUNDARY_FALSE_FIELDS}
    boundary["human_review_required_for_downstream_use"] = True
    return boundary


def _default_product_boundary() -> dict[str, bool]:
    return {field: False for field in PRODUCT_BOUNDARY_FALSE_FIELDS}


def _search_miss_id(record: Mapping[str, Any]) -> str:
    return f"search_miss.{record.get('search_miss_kind', 'unknown')}.{_stable_digest(record)[:12]}.v0"


def _stable_digest(record: Mapping[str, Any]) -> str:
    text = "|".join(
        [
            str(record.get("query_text", "")),
            str(record.get("query_summary", {}).get("query_text", "")),
            str(record.get("related_query_observation_ref", "")),
            str(record.get("search_miss_kind", "")),
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
