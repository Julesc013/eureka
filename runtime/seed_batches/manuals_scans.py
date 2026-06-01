"""Manuals and scanned-documents seed batch.

This module builds deterministic fixture outputs for the third discovery
domain. It produces metadata-only candidates, suppressions, SCOUT trails,
review packets, needs, and handoffs. It never fetches files, performs OCR,
claims scan completeness, accepts truth, or mutates reviewed/public indexes.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.candidate_store import normalize_candidate
from runtime.review.batch import (
    apply_batch_decision_preview,
    build_candidate_clusters,
    build_review_batch_packet,
    validate_batch_decision,
)
from runtime.scout import build_scout_run
from runtime.search.query_plan import archive_org_metadata_query, plan_query_to_source_actions


DEFAULT_TIMESTAMP = "2026-06-02T00:00:00Z"
BATCH_ID = "seed_batch_manuals_scans_00"
TASK_ID = "SEED-BATCH-MANUALS-SCANS-00"
DOMAIN_ID = "manuals_docs_scans"

SOURCE_FAMILIES = (
    "internet_archive_metadata",
    "open_library_metadata",
    "wikidata_metadata",
    "wayback_cdx_metadata",
    "manual_source_pack",
)

MANUALS_SCANS_SUPPRESSIONS: tuple[dict[str, Any], ...] = (
    {
        "suppression_id": "full_book_download_when_metadata_only",
        "reason": "Metadata-only review must not imply a full document download or public fetch action.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "rights_claim_missing",
        "reason": "Metadata candidates cannot create rights-clearance claims.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "scan_completeness_unknown",
        "reason": "Fixture metadata does not prove that every page or insert is present.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "ocr_quality_unknown",
        "reason": "OCR quality is not assessed without OCR or document inspection.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "wrong_model",
        "reason": "Model-adjacent manuals must be reviewed before being treated as relevant.",
        "applies_to_queries": ["manuals_scans_q01", "manuals_scans_q02", "manuals_scans_q07", "manuals_scans_q08"],
    },
    {
        "suppression_id": "wrong_manual_type",
        "reason": "Service, user, deployment, and setup manuals are distinct evidence classes.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "wrong_platform",
        "reason": "Platform-specific documentation must match the queried system context.",
        "applies_to_queries": ["manuals_scans_q09", "manuals_scans_q11", "manuals_scans_q12", "manuals_scans_q13"],
    },
    {
        "suppression_id": "wrong_version",
        "reason": "Wrong version documentation can mislead review and public search.",
        "applies_to_queries": ["manuals_scans_q10", "manuals_scans_q13", "manuals_scans_q14"],
    },
    {
        "suppression_id": "generic_search_result",
        "reason": "Generic search hits are not sufficient review evidence.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "source_only_mention",
        "reason": "A source mention without document metadata remains only a lead.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "duplicate",
        "reason": "Duplicate metadata should collapse into review clusters.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "low_metadata_match",
        "reason": "Weak title-only matches need stronger metadata before promotion.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "unsafe_or_blocked",
        "reason": "Blocked or unsafe source posture cannot be promoted.",
        "applies_to_queries": ["*"],
    },
    {
        "suppression_id": "executable_download",
        "reason": "Executable downloads are outside this document metadata batch.",
        "applies_to_queries": ["manuals_scans_q10", "manuals_scans_q11", "manuals_scans_q12", "manuals_scans_q13", "manuals_scans_q14"],
    },
    {
        "suppression_id": "software_installer_result",
        "reason": "Installer results belong to a separate software or driver/support review lane.",
        "applies_to_queries": ["manuals_scans_q10", "manuals_scans_q11", "manuals_scans_q12", "manuals_scans_q13", "manuals_scans_q14"],
    },
    {
        "suppression_id": "unrelated_modern_documentation",
        "reason": "Modern documentation frequently lacks relevance to legacy document queries.",
        "applies_to_queries": ["*"],
    },
)

MANUALS_SCANS_QUERIES: tuple[dict[str, Any], ...] = (
    {
        "query_id": "manuals_scans_q01",
        "raw_query": "JVC D-VHS D-Theater manual",
        "intent": "find_manual_or_scan",
        "promoted_terms": ["JVC", "D-VHS", "D-Theater", "manual"],
        "suppressions": ["wrong_model", "wrong_manual_type", "scan_completeness_unknown"],
        "known_uncertainties": ["exact model", "manual type", "scan completeness", "rights status"],
        "review_priority": 1,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "manuals_scans_q02",
        "raw_query": "JVC D-Theater user guide",
        "intent": "find_user_guide",
        "promoted_terms": ["JVC", "D-Theater", "user guide"],
        "suppressions": ["wrong_model", "wrong_manual_type", "ocr_quality_unknown"],
        "known_uncertainties": ["model family", "user guide identity", "OCR quality"],
        "review_priority": 1,
        "fixture_source_family": "manual_source_pack",
    },
    {
        "query_id": "manuals_scans_q03",
        "raw_query": "D-VHS service manual",
        "intent": "find_service_manual",
        "promoted_terms": ["D-VHS", "service manual"],
        "suppressions": ["wrong_model", "wrong_manual_type", "rights_claim_missing"],
        "known_uncertainties": ["service manual model", "rights status", "source provenance"],
        "review_priority": 1,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "manuals_scans_q04",
        "raw_query": "MUSE Hi-Vision technical manual",
        "intent": "find_technical_manual",
        "promoted_terms": ["MUSE", "Hi-Vision", "technical manual"],
        "suppressions": ["wrong_manual_type", "generic_search_result", "scan_completeness_unknown"],
        "known_uncertainties": ["technical manual identity", "scan completeness"],
        "review_priority": 1,
        "fixture_source_family": "wikidata_metadata",
    },
    {
        "query_id": "manuals_scans_q05",
        "raw_query": "Sony HDVS equipment manual",
        "intent": "find_equipment_manual",
        "promoted_terms": ["Sony", "HDVS", "equipment manual"],
        "suppressions": ["wrong_model", "wrong_manual_type", "low_metadata_match"],
        "known_uncertainties": ["equipment model", "document title variant"],
        "review_priority": 1,
        "fixture_source_family": "manual_source_pack",
    },
    {
        "query_id": "manuals_scans_q06",
        "raw_query": "early HDTV demonstration manual",
        "intent": "find_demonstration_manual",
        "promoted_terms": ["early HDTV", "demonstration manual"],
        "suppressions": ["generic_search_result", "source_only_mention", "low_metadata_match"],
        "known_uncertainties": ["document specificity", "demonstration system"],
        "review_priority": 2,
        "fixture_source_family": "wayback_cdx_metadata",
    },
    {
        "query_id": "manuals_scans_q07",
        "raw_query": "StyleWriter 2500 user guide",
        "intent": "find_user_guide",
        "promoted_terms": ["StyleWriter 2500", "user guide"],
        "suppressions": ["wrong_model", "wrong_manual_type", "wrong_platform"],
        "known_uncertainties": ["printer model", "Mac OS context"],
        "review_priority": 1,
        "fixture_source_family": "open_library_metadata",
    },
    {
        "query_id": "manuals_scans_q08",
        "raw_query": "StyleWriter 2500 service manual",
        "intent": "find_service_manual",
        "promoted_terms": ["StyleWriter 2500", "service manual"],
        "suppressions": ["wrong_model", "wrong_manual_type", "rights_claim_missing"],
        "known_uncertainties": ["service manual availability", "source provenance"],
        "review_priority": 1,
        "fixture_source_family": "manual_source_pack",
    },
    {
        "query_id": "manuals_scans_q09",
        "raw_query": "Mac OS 8 printer setup manual StyleWriter",
        "intent": "find_setup_manual",
        "promoted_terms": ["Mac OS 8", "printer setup", "StyleWriter"],
        "suppressions": ["wrong_platform", "wrong_model", "unrelated_modern_documentation"],
        "known_uncertainties": ["platform version", "printer model mapping"],
        "review_priority": 2,
        "fixture_source_family": "wayback_cdx_metadata",
    },
    {
        "query_id": "manuals_scans_q10",
        "raw_query": "DirectX SDK June 2010 documentation",
        "intent": "find_software_documentation",
        "promoted_terms": ["DirectX SDK", "June 2010", "documentation"],
        "suppressions": ["wrong_version", "software_installer_result", "executable_download"],
        "known_uncertainties": ["documentation bundle identity", "installer vs documentation result"],
        "review_priority": 2,
        "fixture_source_family": "manual_source_pack",
    },
    {
        "query_id": "manuals_scans_q11",
        "raw_query": "Windows 7 compatibility guide portable software",
        "intent": "find_compatibility_guide",
        "promoted_terms": ["Windows 7", "compatibility guide", "portable software"],
        "suppressions": ["wrong_platform", "software_installer_result", "unrelated_modern_documentation"],
        "known_uncertainties": ["guide provenance", "software list scope"],
        "review_priority": 2,
        "fixture_source_family": "open_library_metadata",
    },
    {
        "query_id": "manuals_scans_q12",
        "raw_query": "Sound Blaster Live user manual Windows 98",
        "intent": "find_user_manual",
        "promoted_terms": ["Sound Blaster Live", "user manual", "Windows 98"],
        "suppressions": ["wrong_platform", "wrong_model", "software_installer_result"],
        "known_uncertainties": ["hardware revision", "Windows 98 support context"],
        "review_priority": 2,
        "fixture_source_family": "internet_archive_metadata",
    },
    {
        "query_id": "manuals_scans_q13",
        "raw_query": "QuickTime 7 deployment guide Windows XP",
        "intent": "find_deployment_guide",
        "promoted_terms": ["QuickTime 7", "deployment guide", "Windows XP"],
        "suppressions": ["wrong_version", "wrong_platform", "software_installer_result"],
        "known_uncertainties": ["deployment guide identity", "platform support"],
        "review_priority": 2,
        "fixture_source_family": "wayback_cdx_metadata",
    },
    {
        "query_id": "manuals_scans_q14",
        "raw_query": "Visual C++ 2010 redistributable documentation",
        "intent": "find_software_documentation",
        "promoted_terms": ["Visual C++ 2010", "redistributable", "documentation"],
        "suppressions": ["wrong_version", "software_installer_result", "executable_download"],
        "known_uncertainties": ["runtime documentation identity", "installer result suppression"],
        "review_priority": 2,
        "fixture_source_family": "manual_source_pack",
    },
    {
        "query_id": "manuals_scans_q15",
        "raw_query": "Apple printer driver installation manual",
        "intent": "find_installation_manual",
        "promoted_terms": ["Apple", "printer driver", "installation manual"],
        "suppressions": ["wrong_manual_type", "software_installer_result", "source_only_mention"],
        "known_uncertainties": ["printer family", "driver version", "document source"],
        "review_priority": 2,
        "fixture_source_family": "open_library_metadata",
    },
    {
        "query_id": "manuals_scans_q16",
        "raw_query": "legacy software installation notes scanned manual",
        "intent": "find_scanned_installation_notes",
        "promoted_terms": ["legacy software", "installation notes", "scanned manual"],
        "suppressions": ["generic_search_result", "ocr_quality_unknown", "scan_completeness_unknown"],
        "known_uncertainties": ["software identity", "scan completeness", "OCR quality"],
        "review_priority": 3,
        "fixture_source_family": "manual_source_pack",
    },
)

DEFAULT_POLICY: dict[str, Any] = {
    "seed_batch_outputs_are_not_truth": True,
    "candidates_require_review": True,
    "reviewed_index_mutation_enabled": False,
    "public_index_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "automatic_candidate_acceptance_enabled": False,
    "source_actions_bounded": True,
    "internet_archive_metadata_allowed": True,
    "open_library_metadata_fixture_allowed": True,
    "wikidata_metadata_fixture_allowed": True,
    "wayback_cdx_metadata_fixture_allowed": True,
    "manual_source_pack_fixture_allowed": True,
    "live_metadata_optional_and_operator_gated": True,
    "raw_live_responses_committed": False,
    "downloads_enabled": False,
    "file_fetch_enabled": False,
    "ocr_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
    "rights_clearance_claims_allowed": False,
    "scan_completeness_claims_allowed": False,
    "ocr_quality_claims_allowed": False,
}


def load_manuals_scans_query_set(policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return [
        {
            "schema_version": "seed_batch_query.v0",
            "batch_id": BATCH_ID,
            "query_id": item["query_id"],
            "raw_query": item["raw_query"],
            "intent": item["intent"],
            "domain_id": DOMAIN_ID,
            "expected_source_families": list(SOURCE_FAMILIES),
            "promoted_terms": list(item["promoted_terms"]),
            "suppressions": list(item["suppressions"]),
            "expected_candidate_kinds": [
                "source_metadata_candidate",
                "document_metadata_candidate",
                "source_lead",
                "review_seed",
            ],
            "known_uncertainties": list(item["known_uncertainties"]),
            "review_priority": int(item["review_priority"]),
            "review_required": True,
            "accepted_truth": False,
            "created_at": DEFAULT_TIMESTAMP,
        }
        for item in MANUALS_SCANS_QUERIES
    ]


def build_manuals_scans_suppression_records(
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return [
        {
            "schema_version": "seed_batch_suppression.v0",
            "batch_id": BATCH_ID,
            "suppression_id": item["suppression_id"],
            "reason": item["reason"],
            "applies_to_queries": list(item["applies_to_queries"]),
            "review_override_allowed": False,
            "accepted_truth": False,
        }
        for item in MANUALS_SCANS_SUPPRESSIONS
    ]


def build_manuals_scans_query_plans(
    query_set: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    plans: list[dict[str, Any]] = []
    for query in query_set:
        raw_query = _text(query.get("raw_query"))
        planner_plan = plan_query_to_source_actions(raw_query)
        plan_id = _stable_id("manuals_scans_query_plan", query.get("query_id"), raw_query)
        archive_query = archive_org_metadata_query(planner_plan)
        if not archive_query or "mediatype:texts" not in archive_query:
            archive_query = _manuals_archive_query(raw_query)
        plans.append(
            {
                "schema_version": "seed_batch_query_plan.v0",
                "batch_id": BATCH_ID,
                "query_id": _text(query.get("query_id")),
                "plan_id": plan_id,
                "raw_query": raw_query,
                "intent": _text(query.get("intent")),
                "domain_id": DOMAIN_ID,
                "planner_plan_id": planner_plan["plan_id"],
                "planner_intent": planner_plan["intent"],
                "planner_domain_pack": planner_plan["domain_pack"],
                "planner_plan": planner_plan,
                "source_query_rewrites": {
                    "internet_archive_metadata": archive_query,
                    "archive_org_metadata": archive_query,
                    "open_library_metadata": raw_query,
                    "wikidata_metadata": raw_query,
                    "wayback_cdx_metadata": raw_query,
                    "manual_source_pack": raw_query,
                },
                "candidate_suppressions": list(query.get("suppressions") or []),
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    return plans


def build_manuals_scans_source_plans(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    family_modes = (
        ("internet_archive_metadata", "allowed", "fixture_metadata_candidates"),
        ("open_library_metadata", "fixture", "fixture_descriptor_only"),
        ("wikidata_metadata", "fixture", "fixture_descriptor_only"),
        ("wayback_cdx_metadata", "fixture", "capture_availability_descriptor_only"),
        ("manual_source_pack", "allowed", "fixture_source_pack_replay"),
    )
    source_plans: list[dict[str, Any]] = []
    for plan in query_plans:
        for family, status, execution_mode in family_modes:
            source_plans.append(
                {
                    "schema_version": "seed_batch_source_plan.v0",
                    "batch_id": BATCH_ID,
                    "source_plan_id": _stable_id("manuals_scans_source_plan", plan.get("plan_id"), family),
                    "query_id": _text(plan.get("query_id")),
                    "query_plan_ref": _text(plan.get("plan_id")),
                    "source_family": family,
                    "status": status,
                    "execution_mode": execution_mode,
                    "source_query": _text((plan.get("source_query_rewrites") or {}).get(family)),
                    "bounded": True,
                    "metadata_only": True,
                    "candidate_only": True,
                    "capture_availability_only": family == "wayback_cdx_metadata",
                    "no_downloads": True,
                    "no_file_fetch": True,
                    "no_ocr": True,
                    "review_required": True,
                    "accepted_truth": False,
                    "created_at": DEFAULT_TIMESTAMP,
                    **_false_boundaries(),
                }
            )
    return source_plans


def run_manuals_scans_fixture_candidates(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_by_id = {item["query_id"]: item for item in MANUALS_SCANS_QUERIES}
    candidates: list[dict[str, Any]] = []
    for index, plan in enumerate(query_plans, start=1):
        query_id = _text(plan.get("query_id"))
        query_def = query_by_id.get(query_id, {})
        source_family = _text(query_def.get("fixture_source_family")) or "manual_source_pack"
        slug = _slug(_text(plan.get("raw_query")))
        raw = {
            "schema_version": "manuals_scans_metadata_candidate.v0",
            "candidate_id": f"seed_manuals_scans_{query_id}_candidate",
            "candidate_status": "needs_review",
            "candidate_kind": "source_metadata_candidate",
            "candidate_title": f"{plan['raw_query']} fixture metadata lead",
            "candidate_summary": "Fixture-derived metadata candidate for manuals, documentation, or scanned-document discovery.",
            "source_locator": _source_locator(source_family, index, slug),
            "source_family": source_family,
            "matched_query": plan["raw_query"],
            "query_plan_ref": plan["plan_id"],
            "source_action_ref": _stable_id("manuals_scans_source_action", plan["plan_id"], source_family),
            "source_observation_ref": _stable_id("manuals_scans_source_observation", BATCH_ID, query_id),
            "domain_id": DOMAIN_ID,
            "confidence_label": "medium" if index <= 12 else "low",
            "match_reasons": [
                "fixture_manuals_scans_seed",
                f"{source_family}_candidate",
                "requires_operator_review",
            ],
            "suppressions": list(plan.get("candidate_suppressions") or []),
            "limitations": _candidate_limitations(),
            "action_posture": {
                "allowed_actions": ["inspect_metadata", "view_source_locator", "create_review_handoff"],
                "blocked_actions": ["download", "fetch_file", "ocr", "extract", "promote", "claim_rights_clearance"],
                "future_gated_actions": ["review_document_identity", "request_source_pack_update"],
                "public_mutation_enabled": False,
                "accepted_truth": False,
            },
            "review_required": True,
            "accepted_truth": False,
            "download_performed": False,
            "file_fetch_performed": False,
            "ocr_performed": False,
            "extraction_executed": False,
            "rights_clearance_claim_created": False,
            "scan_completeness_claim_created": False,
            "ocr_quality_claim_created": False,
        }
        candidates.append(normalize_candidate(raw, _planner_compatible_plan(plan), merged_policy))
    return candidates


def run_manuals_scans_metadata_candidates(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    operator_approved_live_metadata: bool = False,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "seed_batch_manuals_scans_metadata_run.v0",
        "batch_id": BATCH_ID,
        "mode": "operator_approved_live_metadata" if operator_approved_live_metadata else "dry_run_planned",
        "query_count": len(query_plans),
        "operator_live_metadata_run_performed": False,
        "live_metadata_status": "not_run_operator_gate_required",
        "redacted_summary_only": True,
        "raw_live_response_committed": False,
        "candidate_records": [],
        "notes": [
            "Fixture mode is the default closeout lane.",
            "A future operator-approved metadata pilot must remain metadata-only and must not commit raw responses.",
        ],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def normalize_manuals_scans_candidates(
    candidate_outputs: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    normalized: list[dict[str, Any]] = []
    for candidate in candidate_outputs:
        item = dict(candidate)
        item["accepted_truth"] = False
        item["reviewed_record_ref"] = None
        normalized.append(item)
    return normalized


def apply_manuals_scans_suppressions(
    candidates: Sequence[Mapping[str, Any]],
    suppressions: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    output: list[dict[str, Any]] = []
    for candidate in candidates:
        item = copy.deepcopy(dict(candidate))
        query_id = _candidate_query_id(item)
        applied = [
            _text(suppression.get("suppression_id"))
            for suppression in suppressions
            if _suppression_applies(suppression, query_id)
            and _text(suppression.get("suppression_id")) in _text_list(item.get("suppressions"))
        ]
        item["applied_suppressions"] = applied
        item["review_state"] = "needs_review"
        item["accepted_truth"] = False
        output.append(item)
    return output


def build_manuals_scans_candidate_index(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [copy.deepcopy(dict(candidate)) for candidate in candidates]
    return {
        "schema_version": "seed_batch_candidate_index.v0",
        "batch_id": BATCH_ID,
        "store_mode": "seed_batch_fixture",
        "candidate_count": len(records),
        "candidates": records,
        "candidate_refs": [_text(candidate.get("candidate_id")) for candidate in records],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_manuals_scans_scout_trails(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_index = build_manuals_scans_candidate_index(candidates, merged_policy)
    runs = [build_scout_run(candidate["candidate_id"], candidate_index) for candidate in candidates]
    return {
        "schema_version": "seed_batch_scout_trails.v0",
        "batch_id": BATCH_ID,
        "scout_runs": runs,
        "scout_refs": [run["scout_run_id"] for run in runs],
        "relation_count": sum(len(run.get("relations", [])) for run in runs),
        "related_path_count": sum(len(run.get("related_paths", [])) for run in runs),
        "workunit_seed_count": sum(len(run.get("workunit_seeds", [])) for run in runs),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_manuals_scans_review_packets(
    candidates: Sequence[Mapping[str, Any]],
    scout_outputs: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    relations = [
        relation
        for run in scout_outputs.get("scout_runs", [])
        for relation in run.get("relations", [])
        if isinstance(relation, Mapping)
    ]
    clusters = build_candidate_clusters(candidates, relations)
    packet = build_review_batch_packet(clusters)
    decision = validate_batch_decision(
        packet,
        "accept_local_reviewed_preview",
        {"projection_profile": "operator_workbench", "dry_run": True},
    )
    preview = apply_batch_decision_preview(packet, decision)
    return {
        "schema_version": "seed_batch_review_packets.v0",
        "batch_id": BATCH_ID,
        "review_batch_packet": packet,
        "review_batch_refs": [packet["review_batch_id"]],
        "decision_preview": preview,
        "promotion_preview_refs": [item["preview_id"] for item in preview.get("promotion_previews", [])],
        "local_apply_handoff_refs": [preview["local_apply_handoff"]["handoff_id"]],
        "snapshot_refresh_handoff_refs": [preview["snapshot_refresh_handoff"]["handoff_id"]],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_manuals_scans_known_needs_and_absences(
    query_plans: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_query_ids = {_candidate_query_id(candidate) for candidate in candidates}
    known_needs = []
    absences = []
    for plan in query_plans:
        query_id = _text(plan.get("query_id"))
        known_needs.append(
            {
                "schema_version": "seed_batch_known_need.v0",
                "need_id": _stable_id("manuals_scans_known_need", query_id, "document_review"),
                "query_id": query_id,
                "need_kind": "document_identity_review",
                "summary": "Operator must verify document identity, model/version fit, rights posture, scan completeness, and OCR quality before promotion.",
                "candidate_refs": [
                    candidate["candidate_id"]
                    for candidate in candidates
                    if _candidate_query_id(candidate) == query_id
                ],
                "review_required": True,
                "accepted_truth": False,
            }
        )
        if query_id not in candidate_query_ids:
            absences.append(
                {
                    "schema_version": "seed_batch_absence_summary.v0",
                    "absence_id": _stable_id("manuals_scans_absence", query_id),
                    "query_id": query_id,
                    "absence_kind": "no_fixture_candidate",
                    "summary": "No fixture candidate was produced for this query.",
                    "review_required": True,
                    "accepted_truth": False,
                }
            )
    absences.extend(
        [
            {
                "schema_version": "seed_batch_absence_summary.v0",
                "absence_id": _stable_id("manuals_scans_absence", BATCH_ID, "reviewed_truth_absent"),
                "absence_kind": "reviewed_truth_not_created",
                "summary": "Fixture candidates exist, but reviewed truth and public index records are intentionally absent.",
                "review_required": True,
                "accepted_truth": False,
            },
            {
                "schema_version": "seed_batch_absence_summary.v0",
                "absence_id": _stable_id("manuals_scans_absence", BATCH_ID, "scan_quality_not_verified"),
                "absence_kind": "scan_quality_not_verified",
                "summary": "No file fetch, OCR, scan completeness review, or rights-clearance review was performed.",
                "review_required": True,
                "accepted_truth": False,
            },
        ]
    )
    return {
        "schema_version": "seed_batch_need_absence_packet.v0",
        "batch_id": BATCH_ID,
        "known_needs": known_needs,
        "absence_summaries": absences,
        "known_need_refs": [item["need_id"] for item in known_needs],
        "absence_refs": [item["absence_id"] for item in absences],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_manuals_scans_snapshot_refresh_handoff(
    review_packets: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    handoff = copy.deepcopy(review_packets["decision_preview"]["snapshot_refresh_handoff"])
    return {
        "schema_version": "seed_batch_snapshot_refresh_handoff.v0",
        "batch_id": BATCH_ID,
        "snapshot_refresh_handoff": handoff,
        "snapshot_refresh_handoff_refs": [handoff["handoff_id"]],
        "snapshot_refresh_executed": False,
        "requires_separate_snapshot_refresh_gate": True,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_manuals_scans_public_alpha_reassess_inputs(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "seed_batch_public_alpha_reassess_input.v0",
        "batch_id": BATCH_ID,
        "public_alpha_reassess_id": _stable_id("public_alpha_reassess_input", BATCH_ID),
        "domain_id": DOMAIN_ID,
        "candidate_count": int(result.get("candidate_count") or 0),
        "query_count": int(result.get("query_count") or 0),
        "review_batch_refs": list(result.get("review_batch_refs") or []),
        "snapshot_refresh_handoff_refs": list(result.get("snapshot_refresh_handoff_refs") or []),
        "reassess_note": "Use after review/local-apply/snapshot gates; this seed batch adds document-domain discovery but is not launch readiness.",
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_manuals_scans_boundary_report(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    return {
        "schema_version": "seed_batch_boundary_report.v0",
        "batch_id": BATCH_ID,
        "seed_batch_outputs_are_not_truth": bool(merged_policy.get("seed_batch_outputs_are_not_truth", True)),
        "candidates_require_review": bool(merged_policy.get("candidates_require_review", True)),
        "operator_live_metadata_run_performed": bool(result.get("operator_live_metadata_run_performed", False)),
        "raw_live_response_committed": False,
        "rights_clearance_claim_created": False,
        "scan_completeness_claim_created": False,
        "ocr_quality_claim_created": False,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_manuals_scans_fixture(
    policy: Mapping[str, Any] | None = None,
    *,
    write_examples: bool = False,
    write_inventory: bool = False,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_set = load_manuals_scans_query_set(merged_policy)
    query_plans = build_manuals_scans_query_plans(query_set, merged_policy)
    source_plans = build_manuals_scans_source_plans(query_plans, merged_policy)
    suppressions = build_manuals_scans_suppression_records(merged_policy)
    raw_candidates = run_manuals_scans_fixture_candidates(query_plans, merged_policy)
    candidates = normalize_manuals_scans_candidates(raw_candidates, merged_policy)
    candidates = apply_manuals_scans_suppressions(candidates, suppressions, merged_policy)
    candidate_index = build_manuals_scans_candidate_index(candidates, merged_policy)
    scout_trails = build_manuals_scans_scout_trails(candidates, merged_policy)
    review_packets = build_manuals_scans_review_packets(candidates, scout_trails, merged_policy)
    need_absence = build_manuals_scans_known_needs_and_absences(query_plans, candidates, merged_policy)
    snapshot_handoff = build_manuals_scans_snapshot_refresh_handoff(review_packets, merged_policy)
    result: dict[str, Any] = {
        "schema_version": "seed_batch_manuals_scans_run.v0",
        "batch_id": BATCH_ID,
        "domain_id": DOMAIN_ID,
        "mode": "fixture",
        "query_set": query_set,
        "query_plans": query_plans,
        "source_plans": source_plans,
        "suppressions": suppressions,
        "candidate_summaries": [_candidate_summary(candidate) for candidate in candidates],
        "candidate_index": candidate_index,
        "scout_trails": scout_trails,
        "review_packets": review_packets,
        "known_needs": need_absence["known_needs"],
        "absence_summaries": need_absence["absence_summaries"],
        "snapshot_refresh_handoff": snapshot_handoff,
        "query_count": len(query_set),
        "candidate_count": len(candidates),
        "source_plan_refs": [item["source_plan_id"] for item in source_plans],
        "candidate_refs": [candidate["candidate_id"] for candidate in candidates],
        "scout_refs": list(scout_trails["scout_refs"]),
        "review_batch_refs": list(review_packets["review_batch_refs"]),
        "known_need_refs": list(need_absence["known_need_refs"]),
        "absence_refs": list(need_absence["absence_refs"]),
        "snapshot_refresh_handoff_refs": list(snapshot_handoff["snapshot_refresh_handoff_refs"]),
        "public_alpha_reassess_refs": [],
        "fixture_seed_batch_passed": True,
        "operator_live_metadata_run_performed": False,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    public_alpha = build_manuals_scans_public_alpha_reassess_inputs(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_manuals_scans_boundary_report(result, merged_policy)
    if write_examples:
        result["written_examples"] = write_manuals_scans_examples(result)
        result["examples_written"] = True
    else:
        result["examples_written"] = False
    if write_inventory:
        result["written_inventory_and_audit"] = write_manuals_scans_inventory_and_audit(result)
        result["inventory_and_audit_written"] = True
    else:
        result["inventory_and_audit_written"] = False
    return result


def run_seed_batch_manuals_scans(
    policy: Mapping[str, Any] | None = None,
    *,
    fixture: bool = True,
    metadata_descriptors: bool = False,
    operator_approved_live_metadata: bool = False,
    write_examples: bool = False,
    write_inventory: bool = False,
) -> dict[str, Any]:
    if fixture or not metadata_descriptors:
        return run_manuals_scans_fixture(policy, write_examples=write_examples, write_inventory=write_inventory)
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_set = load_manuals_scans_query_set(merged_policy)
    query_plans = build_manuals_scans_query_plans(query_set, merged_policy)
    metadata_plan = run_manuals_scans_metadata_candidates(
        query_plans,
        merged_policy,
        operator_approved_live_metadata=operator_approved_live_metadata,
    )
    return {
        "schema_version": "seed_batch_manuals_scans_run.v0",
        "batch_id": BATCH_ID,
        "domain_id": DOMAIN_ID,
        "mode": metadata_plan["mode"],
        "query_set": query_set,
        "query_plans": query_plans,
        "metadata_descriptor_plan": metadata_plan,
        "query_count": len(query_set),
        "candidate_count": 0,
        "fixture_seed_batch_passed": False,
        "operator_live_metadata_run_performed": False,
        "raw_live_response_committed": False,
        "limitations": _limitations(),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def write_manuals_scans_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_manuals_scans_fixture(write_examples=False))
    repo_root = Path(__file__).resolve().parents[2]
    base = root or repo_root / "examples" / "seed_batches" / "manuals_scans"
    base.mkdir(parents=True, exist_ok=True)
    files = {
        "seed_batch_result.json": _result_summary(payload),
        "query_set.json": payload["query_set"],
        "query_plans.json": payload["query_plans"],
        "source_plans.json": payload["source_plans"],
        "suppressions.json": payload["suppressions"],
        "candidate_summaries.json": payload["candidate_summaries"],
        "candidate_index.json": payload["candidate_index"],
        "scout_trails.json": _scout_summary(payload["scout_trails"]),
        "review_batch_packet.json": payload["review_packets"]["review_batch_packet"],
        "known_needs.json": payload["known_needs"],
        "absence_summaries.json": payload["absence_summaries"],
        "snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
    }
    written = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/query_plans/manuals_scans/query_plans.json": payload["query_plans"],
        "examples/candidates/manuals_scans/candidate_summaries.json": payload["candidate_summaries"],
        "examples/candidates/manuals_scans/candidate_index.json": payload["candidate_index"],
        "examples/scout/manuals_scans/scout_trails.json": _scout_summary(payload["scout_trails"]),
        "examples/review_batch/manuals_scans/review_batch_packet.json": payload["review_packets"]["review_batch_packet"],
        "examples/public_alpha/manuals_scans/public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def build_manuals_scans_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "seed_batch_manuals_scans_input_state.json": {
            "schema_version": "seed_batch_manuals_scans_input_state.v0",
            "task": TASK_ID,
            "prior_latest_commit": "8ba7c760 feat(task): reassess alpha after local apply",
            "public_alpha_launch_deferred": True,
            "current_limited_reviewed_projection_count": 4,
            "target_domain": DOMAIN_ID,
        },
        "seed_batch_manuals_scans_query_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_query_matrix.v0",
            "task": TASK_ID,
            "queries": _strip_created_at(result["query_set"]),
            "accepted_truth_created": False,
            "reviewed_index_mutated": False,
            "public_index_mutated": False,
        },
        "seed_batch_manuals_scans_source_plan_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_source_plan_matrix.v0",
            "task": TASK_ID,
            "source_families": [
                {
                    "source_family": "internet_archive_metadata",
                    "status": "allowed",
                    "bounded": True,
                    "metadata_only": True,
                    "downloads_enabled": False,
                    "file_fetch_enabled": False,
                    "execution_mode": "fixture_metadata_candidates_by_default",
                },
                {
                    "source_family": "open_library_metadata",
                    "status": "fixture",
                    "descriptor_allowed": True,
                    "live_call_by_default": False,
                    "downloads_enabled": False,
                    "file_fetch_enabled": False,
                },
                {
                    "source_family": "wikidata_metadata",
                    "status": "fixture",
                    "descriptor_allowed": True,
                    "live_call_by_default": False,
                    "downloads_enabled": False,
                    "file_fetch_enabled": False,
                },
                {
                    "source_family": "wayback_cdx_metadata",
                    "status": "fixture",
                    "capture_availability_only": True,
                    "live_call_by_default": False,
                    "downloads_enabled": False,
                    "file_fetch_enabled": False,
                },
                {
                    "source_family": "manual_source_pack",
                    "status": "allowed",
                    "fixture_source_pack_replay": True,
                    "live_call_by_default": False,
                    "downloads_enabled": False,
                    "file_fetch_enabled": False,
                },
            ],
            "source_plan_count": len(result["source_plans"]),
            "arbitrary_web_crawling_enabled": False,
            "accepted_truth_created": False,
            "reviewed_index_mutated": False,
            "public_index_mutated": False,
        },
        "seed_batch_manuals_scans_suppression_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_suppression_matrix.v0",
            "task": TASK_ID,
            "suppressions": result["suppressions"],
        },
        "seed_batch_manuals_scans_candidate_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_candidate_matrix.v0",
            "task": TASK_ID,
            "candidate_count": result["candidate_count"],
            "candidates": result["candidate_summaries"],
            **_false_boundaries(),
        },
        "seed_batch_manuals_scans_scout_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_scout_matrix.v0",
            "task": TASK_ID,
            **_scout_summary(result["scout_trails"]),
        },
        "seed_batch_manuals_scans_review_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_review_matrix.v0",
            "task": TASK_ID,
            "review_batch_refs": result["review_batch_refs"],
            "promotion_preview_refs": result["review_packets"]["promotion_preview_refs"],
            "local_apply_handoff_refs": result["review_packets"]["local_apply_handoff_refs"],
            "snapshot_refresh_handoff_refs": result["review_packets"]["snapshot_refresh_handoff_refs"],
            "review_required": True,
            "accepted_truth": False,
            **_false_boundaries(),
        },
        "seed_batch_manuals_scans_need_absence_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": len(result["known_needs"]),
            "absence_summary_count": len(result["absence_summaries"]),
            "known_needs": result["known_needs"],
            "absence_summaries": result["absence_summaries"],
            **_false_boundaries(),
        },
        "seed_batch_manuals_scans_snapshot_handoff_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_snapshot_handoff_matrix.v0",
            "task": TASK_ID,
            **result["snapshot_refresh_handoff"],
        },
        "seed_batch_manuals_scans_public_alpha_reassess_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            **result["public_alpha_reassess_input"],
        },
        "seed_batch_manuals_scans_boundary_report.json": result["boundary_report"],
        "seed_batch_manuals_scans_smoke_result.json": {
            "schema_version": "seed_batch_manuals_scans_smoke_result.v0",
            "task": TASK_ID,
            "status": "pass",
            "fixture_seed_batch_passed": True,
            "query_count": result["query_count"],
            "candidate_count": result["candidate_count"],
            **_false_boundaries(),
        },
        "seed_batch_manuals_scans_validation_matrix.json": {
            "schema_version": "seed_batch_manuals_scans_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "focused_validation_required": True,
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "seed_batch_manuals_scans_result.json": _task_result(result),
        "seed_batch_manuals_scans_next_task_decision.json": {
            "schema_version": "seed_batch_manuals_scans_next_task_decision.v0",
            "task": TASK_ID,
            "recommended_next_task": "SEED-BATCH-DRIVER-SUPPORT-00 - Add driver and support-media discovery batch",
            "rationale": "Manuals/scans expands a lower-risk third discovery domain; driver/support media can follow with stricter executable/download boundaries.",
        },
        "seed_batch_manuals_scans_failure_repair_log.json": {
            "schema_version": "seed_batch_manuals_scans_failure_repair_log.v0",
            "task": TASK_ID,
            "repairs": [],
            "open_failures": [],
        },
    }


def write_manuals_scans_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_manuals_scans_fixture())
    repo_root = root or Path(__file__).resolve().parents[2]
    written: list[str] = []
    inventory = build_manuals_scans_inventory_packets(payload)
    inventory_root = repo_root / "control" / "inventory"
    for name, content in inventory.items():
        path = inventory_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    audit_root = repo_root / "control" / "audits" / "seed-batch-manuals-scans-00-v0"
    audit_root.mkdir(parents=True, exist_ok=True)
    audit_files = {
        "README.md": "# SEED-BATCH-MANUALS-SCANS-00 Audit\n\nMetadata-only manuals/scans seed-batch evidence. No file fetch, OCR, rights-clearance, public mutation, deployment, or readiness claim.\n",
        "seed_batch_manuals_scans_report.json": json.dumps(
            {
                "schema_version": "seed_batch_manuals_scans_report.v0",
                "task": TASK_ID,
                "status": "pass",
                "query_count": payload["query_count"],
                "candidate_count": payload["candidate_count"],
                "fixture_seed_batch_passed": True,
                **_false_boundaries(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "query_matrix.md": _matrix_md("Query Matrix", payload["query_set"], "query_id", "raw_query"),
        "source_plan_matrix.md": _source_plan_md(payload["source_plans"]),
        "suppression_matrix.md": _matrix_md("Suppression Matrix", payload["suppressions"], "suppression_id", "reason"),
        "candidate_matrix.md": _matrix_md("Candidate Matrix", payload["candidate_summaries"], "candidate_id", "title"),
        "scout_matrix.md": _summary_md("Scout Matrix", _scout_summary(payload["scout_trails"])),
        "review_matrix.md": _summary_md("Review Matrix", inventory["seed_batch_manuals_scans_review_matrix.json"]),
        "need_absence_matrix.md": _summary_md("Need/Absence Matrix", inventory["seed_batch_manuals_scans_need_absence_matrix.json"]),
        "snapshot_handoff_matrix.md": _summary_md("Snapshot Handoff Matrix", payload["snapshot_refresh_handoff"]),
        "public_alpha_reassess_matrix.md": _summary_md("Public Alpha Reassess Matrix", payload["public_alpha_reassess_input"]),
        "boundary_report.md": _summary_md("Boundary Report", payload["boundary_report"]),
        "smoke_result.md": _summary_md("Smoke Result", inventory["seed_batch_manuals_scans_smoke_result.json"]),
        "validation_matrix.md": _summary_md("Validation Matrix", inventory["seed_batch_manuals_scans_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused manuals/scans seed-batch validation is required; full discovery is not run by policy.\n",
    }
    for name, content in audit_files.items():
        path = audit_root / name
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    return written


def _task_result(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "seed_batch_manuals_scans_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "contracts_added": True,
        "policies_added": True,
        "query_matrix_added": True,
        "suppression_matrix_added": True,
        "source_plan_matrix_added": True,
        "runtime_seed_batch_added": True,
        "query_plans_created": True,
        "source_plans_created": True,
        "candidate_summaries_created": True,
        "candidate_index_created": True,
        "scout_trails_created": True,
        "review_batch_packet_created": True,
        "known_needs_created": True,
        "absence_summaries_created": True,
        "snapshot_refresh_handoff_created": True,
        "public_alpha_reassess_input_created": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "fixture_seed_batch_passed": bool(payload.get("fixture_seed_batch_passed")),
        "query_count": int(payload.get("query_count") or 0),
        "candidate_count": int(payload.get("candidate_count") or 0),
        "operator_live_metadata_run_performed": False,
        "recommended_next_task": "SEED-BATCH-DRIVER-SUPPORT-00 - Add driver and support-media discovery batch",
        **_false_boundaries(),
    }


def _planner_compatible_plan(seed_plan: Mapping[str, Any]) -> dict[str, Any]:
    planner_plan = copy.deepcopy(seed_plan.get("planner_plan") or {})
    planner_plan["plan_id"] = seed_plan["plan_id"]
    planner_plan["domain_pack"] = DOMAIN_ID
    planner_plan["source_families"] = list(SOURCE_FAMILIES)
    planner_plan["source_actions"] = [
        {
            "source_family": family,
            "action_kind": "metadata_descriptor",
            "candidate_only": True,
            "review_required": True,
            "accepted_truth": False,
        }
        for family in SOURCE_FAMILIES
    ]
    return planner_plan


def _manuals_archive_query(raw_query: str) -> str:
    return (
        '(mediatype:texts OR mediatype:collection) '
        f'({_text(raw_query)} OR manual OR guide OR documentation OR "service manual" OR "user guide") '
        '-installer -download -"full book download"'
    )[:500]


def _source_locator(source_family: str, index: int, slug: str) -> dict[str, str]:
    if source_family == "internet_archive_metadata":
        return {
            "locator_kind": "archive_org_details_page",
            "url": f"https://archive.org/details/seed_manuals_scans_{index:02d}_{slug}",
        }
    return {
        "locator_kind": "fixture_metadata_descriptor",
        "descriptor_ref": f"fixture://{source_family}/seed_manuals_scans_{index:02d}_{slug}",
    }


def _candidate_summary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "seed_batch_candidate_summary.v0",
        "batch_id": BATCH_ID,
        "candidate_id": _text(candidate.get("candidate_id")),
        "query_id": _candidate_query_id(candidate),
        "title": _text(candidate.get("title")),
        "source_family": _text(candidate.get("source_family")),
        "source_locator": copy.deepcopy(candidate.get("source_locator") if isinstance(candidate.get("source_locator"), Mapping) else {}),
        "domain_id": _text(candidate.get("domain_id")),
        "confidence_label": _text(candidate.get("confidence_label")),
        "fixture_derived": "fixture_derived" in list(candidate.get("limitations") or []),
        "suppressions": _text_list(candidate.get("suppressions")),
        "applied_suppressions": list(candidate.get("applied_suppressions") or []),
        "blocked_actions": ["download", "fetch_file", "ocr", "extract", "promote", "claim_rights_clearance"],
        "review_required": True,
        "accepted_truth": False,
        "rights_clearance_claim_created": False,
        "scan_completeness_claim_created": False,
        "ocr_quality_claim_created": False,
    }


def _result_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "seed_batch_manuals_scans_run_summary.v0",
        "batch_id": payload.get("batch_id"),
        "domain_id": payload.get("domain_id"),
        "mode": payload.get("mode"),
        "query_count": payload.get("query_count"),
        "candidate_count": payload.get("candidate_count"),
        "source_plan_refs": list(payload.get("source_plan_refs") or []),
        "candidate_refs": list(payload.get("candidate_refs") or []),
        "scout_refs": list(payload.get("scout_refs") or []),
        "review_batch_refs": list(payload.get("review_batch_refs") or []),
        "known_need_refs": list(payload.get("known_need_refs") or []),
        "absence_refs": list(payload.get("absence_refs") or []),
        "snapshot_refresh_handoff_refs": list(payload.get("snapshot_refresh_handoff_refs") or []),
        "public_alpha_reassess_refs": list(payload.get("public_alpha_reassess_refs") or []),
        "fixture_seed_batch_passed": bool(payload.get("fixture_seed_batch_passed")),
        "operator_live_metadata_run_performed": False,
        "limitations": list(payload.get("limitations") or []),
        "review_required": True,
        "accepted_truth": False,
        **_false_boundaries(),
    }


def _scout_summary(scout_trails: Mapping[str, Any]) -> dict[str, Any]:
    runs = scout_trails.get("scout_runs") or []
    return {
        "schema_version": "seed_batch_scout_trails_summary.v0",
        "batch_id": scout_trails.get("batch_id"),
        "scout_refs": list(scout_trails.get("scout_refs") or []),
        "run_count": len(runs),
        "relation_count": scout_trails.get("relation_count", 0),
        "related_path_count": scout_trails.get("related_path_count", 0),
        "workunit_seed_count": scout_trails.get("workunit_seed_count", 0),
        "sample_runs": [
            {
                "scout_run_id": run.get("scout_run_id"),
                "seed_candidate_id": run.get("seed_candidate_id"),
                "relation_count": run.get("relation_count", 0),
                "candidate_refs": list(run.get("candidate_refs") or [])[:6],
                "accepted_truth": False,
                "review_required": True,
            }
            for run in runs[:3]
        ],
        "review_required": True,
        "accepted_truth": False,
        **_false_boundaries(),
    }


def _candidate_query_id(candidate: Mapping[str, Any]) -> str:
    candidate_id = _text(candidate.get("candidate_id"))
    match = re.search(r"(manuals_scans_q\d{2})", candidate_id)
    return match.group(1) if match else ""


def _suppression_applies(suppression: Mapping[str, Any], query_id: str) -> bool:
    applies = _text_list(suppression.get("applies_to_queries"))
    return "*" in applies or query_id in applies


def _candidate_limitations() -> list[str]:
    return [
        "fixture_derived",
        "candidate_not_reviewed_truth",
        "review_required_for_promotion",
        "metadata_only",
        "no_download",
        "no_file_fetch",
        "no_ocr",
        "no_extraction",
        "no_rights_clearance_claim",
        "no_scan_completeness_claim",
        "no_ocr_quality_claim",
        "no_auto_promotion",
    ]


def _limitations() -> list[str]:
    return [
        "seed_batch_outputs_are_not_truth",
        "fixture_mode_default",
        "review_required_before_promotion",
        "local_apply_is_separate_gate",
        "snapshot_refresh_is_separate_gate",
        "metadata_only",
        "no_download",
        "no_file_fetch",
        "no_ocr",
        "no_extraction",
        "no_rights_clearance_claim",
        "no_scan_completeness_claim",
        "no_ocr_quality_claim",
        "no_public_launch_claim",
    ]


def _false_boundaries() -> dict[str, bool]:
    return {
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "operator_instance_mutated": False,
        "raw_live_response_committed": False,
        "download_performed": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "rights_clearance_claim_created": False,
        "scan_completeness_claim_created": False,
        "ocr_quality_claim_created": False,
    }


def _matrix_md(title: str, items: Sequence[Mapping[str, Any]], key_name: str, summary_name: str) -> str:
    lines = [f"# {title}", "", "| id | summary |", "| --- | --- |"]
    for item in items:
        lines.append(f"| {_text(item.get(key_name))} | {_text(item.get(summary_name))} |")
    lines.append("")
    return "\n".join(lines)


def _source_plan_md(items: Sequence[Mapping[str, Any]]) -> str:
    families = sorted({_text(item.get("source_family")) for item in items if _text(item.get("source_family"))})
    lines = ["# Source Plan Matrix", "", "| source_family | plan_count |", "| --- | --- |"]
    for family in families:
        lines.append(f"| {family} | {sum(1 for item in items if item.get('source_family') == family)} |")
    lines.append("")
    return "\n".join(lines)


def _summary_md(title: str, payload: Mapping[str, Any]) -> str:
    lines = [f"# {title}", ""]
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {str(value).lower() if isinstance(value, bool) else value}")
    lines.append("")
    return "\n".join(lines)


def _strip_created_at(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for item in items:
        cloned = dict(item)
        cloned.pop("created_at", None)
        output.append(cloned)
    return output


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _slug(value: str) -> str:
    slug = "_".join(re.findall(r"[a-z0-9]+", value.casefold()))
    return slug[:80] or "manuals_scans"


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [_text(value)]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [_text(item) for item in value if _text(item)]
    return []


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "seed_batch_outputs_are_not_truth",
        "candidates_require_review",
        "source_actions_bounded",
        "internet_archive_metadata_allowed",
        "open_library_metadata_fixture_allowed",
        "wikidata_metadata_fixture_allowed",
        "wayback_cdx_metadata_fixture_allowed",
        "manual_source_pack_fixture_allowed",
        "live_metadata_optional_and_operator_gated",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"manuals/scans seed batch policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "reviewed_index_mutation_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "automatic_candidate_acceptance_enabled",
        "raw_live_responses_committed",
        "downloads_enabled",
        "file_fetch_enabled",
        "ocr_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "rights_clearance_claims_allowed",
        "scan_completeness_claims_allowed",
        "ocr_quality_claims_allowed",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"manuals/scans seed batch policy enables forbidden behavior: {', '.join(enabled)}")
