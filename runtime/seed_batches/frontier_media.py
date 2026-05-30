"""Frontier-resolution media seed batch.

This module builds deterministic fixture outputs for the first curated media
discovery batch. It produces candidates, trails, review packets, needs, and
handoffs, but never accepted truth or index mutation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.candidate_store import archive_org_candidate_to_record
from runtime.review.batch import (
    apply_batch_decision_preview,
    build_candidate_clusters,
    build_review_batch_packet,
    validate_batch_decision,
)
from runtime.scout import build_scout_run
from runtime.search.query_plan import archive_org_metadata_query, plan_query_to_source_actions


DEFAULT_TIMESTAMP = "2026-05-31T00:00:00Z"
BATCH_ID = "seed_batch_frontier_media_00"
DOMAIN_ID = "frontier_resolution_media"

FRONTIER_MEDIA_QUERIES: tuple[dict[str, Any], ...] = (
    {
        "query_id": "frontier_media_q01",
        "raw_query": "New York 1993 D-Theater HD demo tape original source",
        "promoted_terms": ["New York", "1993", "D-Theater", "HD demo", "demo tape", "original source"],
        "suppressions": ["suppress_generic_city_or_tourism_media"],
        "known_uncertainties": ["exact source tape identity", "rights status", "metadata provenance"],
        "review_priority": 1,
    },
    {
        "query_id": "frontier_media_q02",
        "raw_query": "New York 1993 D-VHS HDTV demo tape",
        "promoted_terms": ["New York", "1993", "D-VHS", "HDTV", "demo tape"],
        "suppressions": ["suppress_generic_city_or_tourism_media"],
        "known_uncertainties": ["format naming may vary between D-VHS and D-Theater"],
        "review_priority": 1,
    },
    {
        "query_id": "frontier_media_q03",
        "raw_query": "JVC D-Theater New York HD demo",
        "promoted_terms": ["JVC", "D-Theater", "New York", "HD demo"],
        "suppressions": ["suppress_generic_city_or_tourism_media"],
        "known_uncertainties": ["JVC may describe demo media under collection or device metadata"],
        "review_priority": 2,
    },
    {
        "query_id": "frontier_media_q04",
        "raw_query": "D-Theater D-VHS city footage 1993",
        "promoted_terms": ["D-Theater", "D-VHS", "city footage", "1993"],
        "suppressions": ["suppress_generic_city_or_tourism_media", "suppress_stock_footage"],
        "known_uncertainties": ["city footage may be generic unless technical format evidence appears"],
        "review_priority": 2,
    },
    {
        "query_id": "frontier_media_q05",
        "raw_query": "Hi-Vision MUSE New York 1993 HDTV demo",
        "promoted_terms": ["Hi-Vision", "MUSE", "New York", "1993", "HDTV demo"],
        "suppressions": ["suppress_generic_city_or_tourism_media"],
        "known_uncertainties": ["MUSE/Hi-Vision media may be cataloged as broadcast or LaserDisc"],
        "review_priority": 1,
    },
    {
        "query_id": "frontier_media_q06",
        "raw_query": "early HDTV New York 1993 demo footage",
        "promoted_terms": ["early HDTV", "New York", "1993", "demo footage"],
        "suppressions": ["suppress_generic_city_or_tourism_media", "suppress_modern_hd_stock"],
        "known_uncertainties": ["query is broad and needs technical-format confirmation"],
        "review_priority": 3,
    },
    {
        "query_id": "frontier_media_q07",
        "raw_query": "D-Theater demo tape JVC city",
        "promoted_terms": ["D-Theater", "demo tape", "JVC", "city"],
        "suppressions": ["suppress_generic_city_or_tourism_media"],
        "known_uncertainties": ["city location may be absent from metadata"],
        "review_priority": 2,
    },
    {
        "query_id": "frontier_media_q08",
        "raw_query": "HDVS Hi-Vision demo New York footage",
        "promoted_terms": ["HDVS", "Hi-Vision", "demo", "New York", "footage"],
        "suppressions": ["suppress_generic_city_or_tourism_media"],
        "known_uncertainties": ["HDVS equipment references may not imply source media"],
        "review_priority": 2,
    },
    {
        "query_id": "frontier_media_q09",
        "raw_query": "Japanese HDTV demonstration tape New York",
        "promoted_terms": ["Japanese HDTV", "demonstration tape", "New York"],
        "suppressions": ["suppress_generic_city_or_tourism_media", "suppress_tourism_media"],
        "known_uncertainties": ["Japanese-language metadata may use alternate romanization"],
        "review_priority": 3,
    },
    {
        "query_id": "frontier_media_q10",
        "raw_query": "MUSE LaserDisc New York HD demo",
        "promoted_terms": ["MUSE", "LaserDisc", "New York", "HD demo"],
        "suppressions": ["suppress_generic_city_or_tourism_media"],
        "known_uncertainties": ["LaserDisc metadata may lack capture/provenance details"],
        "review_priority": 2,
    },
    {
        "query_id": "frontier_media_q11",
        "raw_query": "D-VHS demo tape urban footage",
        "promoted_terms": ["D-VHS", "demo tape", "urban footage"],
        "suppressions": ["suppress_generic_city_or_tourism_media", "suppress_stock_footage"],
        "known_uncertainties": ["urban footage is broad without date/location markers"],
        "review_priority": 3,
    },
    {
        "query_id": "frontier_media_q12",
        "raw_query": "early high definition city footage archival source",
        "promoted_terms": ["early high definition", "city footage", "archival source"],
        "suppressions": ["suppress_generic_city_or_tourism_media", "suppress_modern_hd_stock"],
        "known_uncertainties": ["broad query should produce needs and absences if metadata is weak"],
        "review_priority": 4,
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
    "archive_org_metadata_candidates_allowed": True,
    "live_metadata_optional_and_operator_gated": True,
    "raw_live_responses_committed": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
}


def load_frontier_media_query_set(policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    queries: list[dict[str, Any]] = []
    for item in FRONTIER_MEDIA_QUERIES:
        queries.append(
            {
                "schema_version": "seed_batch_query.v0",
                "batch_id": BATCH_ID,
                "query_id": item["query_id"],
                "raw_query": item["raw_query"],
                "intent": "find_frontier_resolution_media",
                "domain_id": DOMAIN_ID,
                "expected_source_families": [
                    "internet_archive_metadata",
                    "wayback_cdx_metadata",
                    "wikidata_metadata",
                    "manual_source_pack",
                ],
                "promoted_terms": list(item["promoted_terms"]),
                "suppressions": list(item["suppressions"]),
                "expected_candidate_kinds": [
                    "source_metadata_candidate",
                    "provenance_lead",
                    "review_seed",
                ],
                "known_uncertainties": list(item["known_uncertainties"]),
                "review_priority": int(item["review_priority"]),
                "review_required": True,
                "accepted_truth": False,
                "created_at": DEFAULT_TIMESTAMP,
            }
        )
    return queries


def build_seed_batch_query_plans(
    query_set: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    plans: list[dict[str, Any]] = []
    for query in query_set:
        raw_query = _text(query.get("raw_query"))
        planner_plan = plan_query_to_source_actions(raw_query)
        plan_id = _stable_id("seed_query_plan", query.get("query_id"), raw_query)
        archive_query = archive_org_metadata_query(planner_plan)
        if "D-Theater" not in archive_query and "D-VHS" not in archive_query:
            archive_query = _frontier_archive_query(raw_query)
        plans.append(
            {
                "schema_version": "seed_batch_query_plan.v0",
                "batch_id": BATCH_ID,
                "query_id": _text(query.get("query_id")),
                "plan_id": plan_id,
                "raw_query": raw_query,
                "intent": "find_frontier_resolution_media",
                "domain_id": DOMAIN_ID,
                "planner_plan_id": planner_plan["plan_id"],
                "planner_intent": planner_plan["intent"],
                "planner_domain_pack": planner_plan["domain_pack"],
                "planner_plan": planner_plan,
                "source_query_rewrites": {
                    "internet_archive_metadata": archive_query,
                    "archive_org_metadata": archive_query,
                    "wayback_cdx_metadata": raw_query,
                    "wikidata_metadata": raw_query,
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


def build_seed_batch_source_plans(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    source_plans: list[dict[str, Any]] = []
    for plan in query_plans:
        for family, status, execution_mode in (
            ("internet_archive_metadata", "allowed", "fixture_metadata_candidates"),
            ("wayback_cdx_metadata", "planned", "descriptor_only"),
            ("wikidata_metadata", "planned", "descriptor_only"),
            ("manual_source_pack", "allowed", "fixture_source_pack_replay"),
        ):
            source_plans.append(
                {
                    "schema_version": "seed_batch_source_plan.v0",
                    "batch_id": BATCH_ID,
                    "source_plan_id": _stable_id("seed_source_plan", plan.get("plan_id"), family),
                    "query_id": _text(plan.get("query_id")),
                    "query_plan_ref": _text(plan.get("plan_id")),
                    "source_family": family,
                    "status": status,
                    "execution_mode": execution_mode,
                    "source_query": _text((plan.get("source_query_rewrites") or {}).get(family)),
                    "bounded": True,
                    "metadata_only": True,
                    "candidate_only": True,
                    "no_downloads": True,
                    "review_required": True,
                    "accepted_truth": False,
                    "created_at": DEFAULT_TIMESTAMP,
                    **_false_boundaries(),
                }
            )
    return source_plans


def run_seed_batch_fixture_candidates(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidates: list[dict[str, Any]] = []
    for index, plan in enumerate(query_plans, start=1):
        query_id = _text(plan.get("query_id"))
        slug = _slug(_text(plan.get("raw_query")))
        raw = {
            "schema_version": "archive_org_metadata_candidate.v0",
            "candidate_id": f"seed_frontier_media_{query_id}_candidate",
            "candidate_status": "needs_review",
            "candidate_type": "archive_org_item_metadata_candidate",
            "candidate_title": f"{plan['raw_query']} fixture metadata lead",
            "candidate_summary": "Fixture-derived Archive.org metadata candidate for frontier-resolution media discovery.",
            "identifier": f"seed_frontier_media_{index:02d}_{slug}",
            "source_locator": {
                "locator_kind": "archive_org_details_page",
                "url": f"https://archive.org/details/seed_frontier_media_{index:02d}_{slug}",
            },
            "source_family": "internet_archive_metadata",
            "matched_query": plan["raw_query"],
            "query_plan_ref": plan["plan_id"],
            "source_action_ref": _stable_id("seed_source_action", plan["plan_id"], "internet_archive_metadata"),
            "source_observation_ref": _stable_id("seed_source_observation", BATCH_ID, query_id),
            "domain_id": DOMAIN_ID,
            "confidence_label": "medium" if index <= 5 else "low",
            "match_reasons": [
                "fixture_frontier_media_seed",
                "archive_org_metadata_candidate",
                "requires_operator_review",
            ],
            "suppressions": list(plan.get("candidate_suppressions") or []),
            "limitations": [
                "fixture_derived",
                "candidate_not_reviewed_truth",
                "review_required_for_promotion",
                "no_download",
                "no_extraction",
                "no_auto_promotion",
            ],
            "accepted_truth": False,
            "review_required": True,
            "download_performed": False,
            "extraction_executed": False,
        }
        candidates.append(archive_org_candidate_to_record(raw, _planner_compatible_plan(plan), merged_policy))
    return candidates


def run_seed_batch_archive_org_metadata_candidates(
    query_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    operator_approved_live_metadata: bool = False,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "seed_batch_archive_org_metadata_run.v0",
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
            "A future operator-approved live metadata pilot must remain metadata-only and must not commit raw responses.",
        ],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def normalize_seed_batch_candidates(
    candidate_outputs: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    normalized = []
    for candidate in candidate_outputs:
        item = dict(candidate)
        item["accepted_truth"] = False
        item["reviewed_record_ref"] = None
        normalized.append(item)
    return normalized


def build_seed_batch_candidate_index(
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


def build_seed_batch_scout_trails(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_index = build_seed_batch_candidate_index(candidates, merged_policy)
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


def build_seed_batch_review_packets(
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


def build_seed_batch_known_needs_and_absences(
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
                "need_id": _stable_id("seed_known_need", query_id, "provenance_review"),
                "query_id": query_id,
                "need_kind": "provenance_review",
                "summary": "Operator must verify source identity, format, rights, and provenance before promotion.",
                "candidate_refs": [candidate["candidate_id"] for candidate in candidates if _candidate_query_id(candidate) == query_id],
                "review_required": True,
                "accepted_truth": False,
            }
        )
        if query_id not in candidate_query_ids:
            absences.append(
                {
                    "schema_version": "seed_batch_absence_summary.v0",
                    "absence_id": _stable_id("seed_absence", query_id),
                    "query_id": query_id,
                    "absence_kind": "no_fixture_candidate",
                    "summary": "No fixture candidate was produced for this query.",
                    "review_required": True,
                    "accepted_truth": False,
                }
            )
    if not absences:
        absences.append(
            {
                "schema_version": "seed_batch_absence_summary.v0",
                "absence_id": _stable_id("seed_absence", BATCH_ID, "reviewed_truth_absent"),
                "absence_kind": "reviewed_truth_not_created",
                "summary": "Fixture candidates exist, but reviewed truth and public index records are intentionally absent.",
                "review_required": True,
                "accepted_truth": False,
            }
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


def build_seed_batch_snapshot_refresh_handoff(
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


def build_seed_batch_public_alpha_reassess_inputs(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "seed_batch_public_alpha_reassess_input.v0",
        "batch_id": BATCH_ID,
        "public_alpha_reassess_id": _stable_id("public_alpha_reassess_input", BATCH_ID),
        "candidate_count": int(result.get("candidate_count") or 0),
        "query_count": int(result.get("query_count") or 0),
        "review_batch_refs": list(result.get("review_batch_refs") or []),
        "snapshot_refresh_handoff_refs": list(result.get("snapshot_refresh_handoff_refs") or []),
        "reassess_note": "Use after review/local-apply/snapshot gates; this seed batch itself is not public launch readiness.",
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_seed_batch_boundary_report(
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
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_seed_batch_fixture(
    policy: Mapping[str, Any] | None = None,
    *,
    write_examples: bool = False,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_set = load_frontier_media_query_set(merged_policy)
    query_plans = build_seed_batch_query_plans(query_set, merged_policy)
    source_plans = build_seed_batch_source_plans(query_plans, merged_policy)
    candidates = normalize_seed_batch_candidates(run_seed_batch_fixture_candidates(query_plans, merged_policy), merged_policy)
    candidate_index = build_seed_batch_candidate_index(candidates, merged_policy)
    scout_trails = build_seed_batch_scout_trails(candidates, merged_policy)
    review_packets = build_seed_batch_review_packets(candidates, scout_trails, merged_policy)
    need_absence = build_seed_batch_known_needs_and_absences(query_plans, candidates, merged_policy)
    snapshot_handoff = build_seed_batch_snapshot_refresh_handoff(review_packets, merged_policy)
    result: dict[str, Any] = {
        "schema_version": "seed_batch_frontier_media_run.v0",
        "batch_id": BATCH_ID,
        "domain_id": DOMAIN_ID,
        "mode": "fixture",
        "query_set": query_set,
        "query_plans": query_plans,
        "source_plans": source_plans,
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
    public_alpha = build_seed_batch_public_alpha_reassess_inputs(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_seed_batch_boundary_report(result, merged_policy)
    if write_examples:
        write_frontier_media_examples(result)
        result["examples_written"] = True
    else:
        result["examples_written"] = False
    return result


def run_seed_batch_frontier_media(
    policy: Mapping[str, Any] | None = None,
    *,
    fixture: bool = True,
    archive_org_metadata: bool = False,
    operator_approved_live_metadata: bool = False,
    write_examples: bool = False,
) -> dict[str, Any]:
    """Run the frontier media seed batch in a governed mode.

    Fixture mode is the only execution path that produces candidates in this
    task. The Archive.org metadata mode records a dry-run descriptor unless a
    future operator gate authorizes a bounded live metadata pilot.
    """

    if fixture or not archive_org_metadata:
        return run_seed_batch_fixture(policy, write_examples=write_examples)
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    query_set = load_frontier_media_query_set(merged_policy)
    query_plans = build_seed_batch_query_plans(query_set, merged_policy)
    metadata_plan = run_seed_batch_archive_org_metadata_candidates(
        query_plans,
        merged_policy,
        operator_approved_live_metadata=operator_approved_live_metadata,
    )
    return {
        "schema_version": "seed_batch_frontier_media_run.v0",
        "batch_id": BATCH_ID,
        "domain_id": DOMAIN_ID,
        "mode": metadata_plan["mode"],
        "query_set": query_set,
        "query_plans": query_plans,
        "archive_org_metadata_plan": metadata_plan,
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


def write_frontier_media_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_seed_batch_fixture(write_examples=False))
    base = root or Path(__file__).resolve().parents[2] / "examples" / "seed_batches" / "frontier_media"
    base.mkdir(parents=True, exist_ok=True)
    files = {
        "seed_batch_result.json": _result_summary(payload),
        "query_set.json": payload["query_set"],
        "query_plans.json": payload["query_plans"],
        "source_plans.json": payload["source_plans"],
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
        path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(str(path.relative_to(Path(__file__).resolve().parents[2])))
    mirrors = {
        "examples/query_plans/frontier_media/query_plans.json": payload["query_plans"],
        "examples/candidates/frontier_media/candidate_summaries.json": payload["candidate_summaries"],
        "examples/candidates/frontier_media/candidate_index.json": payload["candidate_index"],
        "examples/scout/frontier_media/scout_trails.json": _scout_summary(payload["scout_trails"]),
        "examples/review_batch/frontier_media/review_batch_packet.json": payload["review_packets"]["review_batch_packet"],
        "examples/public_alpha/frontier_media/public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
    }
    for rel_path, content in mirrors.items():
        path = Path(__file__).resolve().parents[2] / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(rel_path)
    return written


def _result_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "seed_batch_frontier_media_run_summary.v0",
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


def _planner_compatible_plan(seed_plan: Mapping[str, Any]) -> dict[str, Any]:
    planner_plan = copy.deepcopy(seed_plan.get("planner_plan") or {})
    planner_plan["plan_id"] = seed_plan["plan_id"]
    planner_plan["domain_pack"] = DOMAIN_ID
    planner_plan["source_families"] = ["internet_archive_metadata", "wayback_cdx_metadata", "wikidata_metadata", "manual_source_pack"]
    planner_plan["source_actions"] = [
        {
            "source_family": "internet_archive_metadata",
            "action_kind": "metadata_search",
            "candidate_only": True,
            "review_required": True,
            "accepted_truth": False,
        }
    ]
    return planner_plan


def _frontier_archive_query(raw_query: str) -> str:
    return (
        '(mediatype:movies OR mediatype:texts OR mediatype:collection) '
        f'({_text(raw_query)} OR "D-Theater" OR "D-VHS" OR JVC OR "Hi-Vision" OR MUSE OR "HD demo" OR "demo tape") '
        '-tourism -"stock footage"'
    )[:500]


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
        "review_required": True,
        "accepted_truth": False,
    }


def _candidate_query_id(candidate: Mapping[str, Any]) -> str:
    candidate_id = _text(candidate.get("candidate_id"))
    match = re.search(r"(frontier_media_q\d{2})", candidate_id)
    return match.group(1) if match else ""


def _limitations() -> list[str]:
    return [
        "seed_batch_outputs_are_not_truth",
        "fixture_mode_default",
        "review_required_before_promotion",
        "local_apply_is_separate_gate",
        "snapshot_refresh_is_separate_gate",
        "no_download",
        "no_extraction",
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
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _slug(value: str) -> str:
    slug = "_".join(re.findall(r"[a-z0-9]+", value.casefold()))
    return slug[:80] or "frontier_media"


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


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
        "archive_org_metadata_candidates_allowed",
        "live_metadata_optional_and_operator_gated",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"seed batch policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "reviewed_index_mutation_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "automatic_candidate_acceptance_enabled",
        "raw_live_responses_committed",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"seed batch policy enables forbidden behavior: {', '.join(enabled)}")
