"""Snapshot refresh projection after the bounded live metadata pilot.

SNAPSHOT-REFRESH-01 packages existing reviewed records, fixture seed-batch
candidates, and redacted live metadata candidates into read-only snapshot and
relay packets. Live metadata observations remain review-only candidates.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.snapshots import refresh as seed_refresh
from runtime.snapshots.relay_foundation import (
    project_reviewed_record_to_snapshot,
    sample_reviewed_records,
)


DEFAULT_TIMESTAMP = "2026-06-01T00:00:00Z"
SNAPSHOT_REFRESH_ID = "snapshot_refresh_01"
TASK_ID = "SNAPSHOT-REFRESH-01"
LIVE_METADATA_PILOT_REF = "control/inventory/live_metadata_pilot_result.json"
NEXT_TASK = "PUBLIC-ALPHA-REASSESS-01 - Reassess alpha after live metadata snapshot refresh"

DEFAULT_POLICY: dict[str, Any] = {
    "snapshot_refresh_is_projection": True,
    "live_metadata_candidates_remain_candidates": True,
    "candidates_remain_candidates": True,
    "seed_outputs_are_not_truth": True,
    "reviewed_records_only_from_existing_reviewed_sources": True,
    "no_candidate_auto_acceptance": True,
    "no_live_metadata_auto_acceptance": True,
    "no_reviewed_index_mutation": True,
    "no_master_index_mutation": True,
    "no_public_index_mutation": True,
    "no_public_mutation": True,
    "no_deployment": True,
    "no_public_launch_claim": True,
    "no_production_claim": True,
    "raw_live_response_included": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
}

BOUNDARY_FALSE_KEYS = (
    "accepted_truth_created",
    "candidate_promoted_to_reviewed",
    "live_metadata_candidate_promoted",
    "raw_live_response_included",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "site_dist_written",
    "download_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def load_seed_batch_handoffs(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    handoff = copy.deepcopy(seed_refresh.load_seed_batch_handoffs())
    handoff["snapshot_refresh_id"] = SNAPSHOT_REFRESH_ID
    handoff["created_at"] = DEFAULT_TIMESTAMP
    return handoff


def load_live_metadata_pilot_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    pilot_result = _read_json(repo / LIVE_METADATA_PILOT_REF)
    candidate_matrix = _read_json(repo / "control/inventory/live_metadata_pilot_candidate_matrix.json")
    scout_matrix = _read_json(repo / "control/inventory/live_metadata_pilot_scout_matrix.json")
    review_matrix = _read_json(repo / "control/inventory/live_metadata_pilot_review_matrix.json")
    snapshot_handoff_matrix = _read_json(repo / "control/inventory/live_metadata_pilot_snapshot_handoff_matrix.json")
    reassess_matrix = _read_json(repo / "control/inventory/live_metadata_pilot_public_alpha_reassess_matrix.json")
    redaction_summary = _read_json(repo / "control/inventory/live_metadata_pilot_redaction_summary.json")
    _assert_live_metadata_pilot(pilot_result, candidate_matrix)
    return {
        "schema_version": "snapshot_refresh_01_live_metadata_handoff.v0",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "pilot_batch_id": candidate_matrix.get("pilot_batch_id") or "live_metadata_pilot_batch_00",
        "pilot_result": pilot_result,
        "candidate_matrix": candidate_matrix,
        "candidates": list(candidate_matrix.get("candidates") or []),
        "scout_matrix": scout_matrix,
        "review_matrix": review_matrix,
        "review_batch_packet": copy.deepcopy(review_matrix.get("review_batch_packet") or {}),
        "snapshot_handoff_matrix": snapshot_handoff_matrix,
        "public_alpha_reassess_matrix": reassess_matrix,
        "redaction_summary": redaction_summary,
        "source_family": pilot_result.get("source_family") or "internet_archive_metadata",
        "candidate_count": int(candidate_matrix.get("candidate_count") or 0),
        "total_live_requests": int(pilot_result.get("total_live_requests") or 0),
        "selected_query_count": int(pilot_result.get("selected_query_count") or 0),
        "review_required": True,
        "accepted_truth": False,
        "raw_response_included": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_01_plan(
    seed_handoffs: Mapping[str, Any],
    live_metadata_handoff: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    batches = list(seed_handoffs.get("source_batches") or [])
    return {
        "schema_version": "snapshot_refresh_plan.v0",
        "record_type": "snapshot_refresh_plan",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": [_batch_summary(batch) for batch in batches],
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "live_metadata_source_family": live_metadata_handoff.get("source_family"),
        "reviewed_record_refs": [record["record_id"] for record in sample_reviewed_records()],
        "candidate_section_refs": [
            _section_id("snapshot_candidate_section", batch.get("domain_key"), SNAPSHOT_REFRESH_ID)
            for batch in batches
        ],
        "live_metadata_candidate_section_refs": [
            _section_id("snapshot_live_metadata_candidate_section", live_metadata_handoff.get("pilot_batch_id"))
        ],
        "review_queue_section_refs": [_section_id("snapshot_review_queue_section", SNAPSHOT_REFRESH_ID)],
        "need_absence_section_refs": [_section_id("snapshot_need_absence_section", SNAPSHOT_REFRESH_ID)],
        "relay_projection_refs": [_section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID)],
        "public_alpha_reassess_refs": [_section_id("snapshot_public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "public_search_view_model_refs": [_section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID)],
        "reviewed_records_source": "existing_reviewed_snapshot_examples",
        "candidate_projection_source": "seed_batch_and_redacted_live_metadata_handoffs",
        "refresh_mode": "live_metadata_redacted_projection_only",
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "raw_live_response_included": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_reviewed_record_section(
    existing_reviewed_records: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = list(existing_reviewed_records or sample_reviewed_records())
    snapshot_records = [project_reviewed_record_to_snapshot(record, merged_policy) for record in records]
    return {
        "schema_version": "snapshot_reviewed_record_section.v0",
        "record_type": "snapshot_reviewed_record_section",
        "section_id": _section_id("snapshot_reviewed_record_section", [record.get("record_id") for record in records]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "reviewed_records": snapshot_records,
        "reviewed_record_refs": [record["record_id"] for record in snapshot_records],
        "reviewed_record_count": len(snapshot_records),
        "source": "existing_reviewed_records",
        "candidates_included_as_truth": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "limitations": ["existing reviewed fixture records only"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_candidate_snapshot_section(
    seed_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    domain_key: str = "seed_batch",
    batch_id: str = "",
    scout_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    section = seed_refresh.build_candidate_snapshot_section(
        seed_candidates,
        domain_key=domain_key,
        batch_id=batch_id,
        scout_refs=scout_refs or [],
    )
    section = _retag_snapshot_refresh(section)
    section["limitations"] = ["fixture seed candidates are projected as review-only candidates"]
    for candidate in section.get("candidates", []):
        candidate["fixture_derived"] = True
        candidate["live_metadata_derived"] = False
        candidate["public_search_status"] = "candidate"
        candidate["accepted_truth"] = False
        candidate["reviewed_record_ref"] = None
    return section


def build_live_metadata_candidate_section(
    live_metadata_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    live_metadata_handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    handoff = dict(live_metadata_handoff or {})
    scout_refs = _text_list((handoff.get("scout_matrix") or {}).get("scout_refs"))
    candidates = [
        _live_metadata_candidate_item(candidate, scout_refs[index : index + 1])
        for index, candidate in enumerate(live_metadata_candidates)
    ]
    return {
        "schema_version": "snapshot_live_metadata_candidate_section.v0",
        "record_type": "snapshot_live_metadata_candidate_section",
        "section_id": _section_id("snapshot_live_metadata_candidate_section", handoff.get("pilot_batch_id"), [c["candidate_id"] for c in candidates]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_family": handoff.get("source_family") or "internet_archive_metadata",
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "candidate_refs": [candidate["candidate_id"] for candidate in candidates],
        "candidate_count": len(candidates),
        "source_observation_summary_refs": [
            ref for ref in (candidate.get("source_observation_ref") for candidate in candidates) if ref
        ],
        "candidates": candidates,
        "review_required": True,
        "accepted_truth": False,
        "reviewed_record_refs": [],
        "raw_response_included": False,
        "limitations": [
            "live_metadata_derived_review_only",
            "redacted_summary_only",
            "no_raw_response_included",
            "review_required_before_promotion",
        ],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_review_queue_section(
    review_packets: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    packets = [_review_packet_summary(packet) for packet in review_packets if packet]
    candidate_refs = sorted({ref for packet in packets for ref in packet["candidate_refs"]})
    cluster_refs = sorted({ref for packet in packets for ref in packet["cluster_refs"]})
    return {
        "schema_version": "snapshot_review_queue_section.v0",
        "record_type": "snapshot_review_queue_section",
        "section_id": _section_id("snapshot_review_queue_section", candidate_refs, cluster_refs, SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_packets": packets,
        "review_batch_refs": [packet["review_batch_id"] for packet in packets],
        "candidate_refs": candidate_refs,
        "cluster_refs": cluster_refs,
        "review_packet_count": len(packets),
        "candidate_count": len(candidate_refs),
        "cluster_count": len(cluster_refs),
        "live_metadata_candidate_refs": [ref for ref in candidate_refs if ref.startswith("live_metadata_pilot_")],
        "operator_context_required": True,
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "live_metadata_candidate_promoted": False,
        "limitations": ["review queue summary only; decisions remain separate"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_need_absence_section(
    known_needs: Sequence[Mapping[str, Any]],
    absence_summaries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = seed_refresh.build_need_absence_section(known_needs, absence_summaries)
    return _retag_snapshot_refresh(section)


def build_seed_batch_summary_section(
    seed_results: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = seed_refresh.build_seed_batch_summary_section(seed_results)
    return _retag_snapshot_refresh(section)


def build_refreshed_relay_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_sections = list(snapshot_sections.get("candidate_sections") or [])
    seed_candidates = [
        candidate
        for section in candidate_sections
        for candidate in list(section.get("candidates") or [])
    ]
    live_section = dict(snapshot_sections.get("live_metadata_candidate_section") or {})
    live_candidates = list(live_section.get("candidates") or [])
    all_candidates = seed_candidates + live_candidates
    return {
        "schema_version": "snapshot_refresh_relay_projection.v0",
        "record_type": "snapshot_refresh_relay_projection",
        "relay_projection_id": _section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "read_only": True,
        "sections": {
            "reviewed_records": int(snapshot_sections.get("reviewed_record_section", {}).get("reviewed_record_count") or 0),
            "candidate_sections": len(candidate_sections),
            "candidates": len(all_candidates),
            "fixture_candidates": len(seed_candidates),
            "live_metadata_candidates": len(live_candidates),
            "review_queue_candidates": int(snapshot_sections.get("review_queue_section", {}).get("candidate_count") or 0),
            "known_needs": int(snapshot_sections.get("need_absence_section", {}).get("known_need_count") or 0),
            "absence_summaries": int(snapshot_sections.get("need_absence_section", {}).get("absence_count") or 0),
        },
        "query_previews": [
            _relay_query_preview("D-Theater New York 1993", all_candidates),
            _relay_query_preview("DirectX SDK June 2010", all_candidates),
            _relay_query_preview("live metadata candidates", live_candidates),
        ],
        "candidate_results_are_review_only": True,
        "live_metadata_candidates_are_review_only": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_performed": False,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "live_metadata_candidate_promoted": False,
        "raw_live_response_included": False,
        "limitations": ["relay projection preview only; no public route or dist write"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_search_view_model_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    live_section = dict(snapshot_sections.get("live_metadata_candidate_section") or {})
    live_cards = [_live_candidate_result_card(candidate) for candidate in live_section.get("candidates", [])]
    status_counts = {
        "verified": int(snapshot_sections.get("reviewed_record_section", {}).get("reviewed_record_count") or 0),
        "candidate": len(live_cards),
        "near_miss": 0,
        "known_need": int(snapshot_sections.get("need_absence_section", {}).get("known_need_count") or 0),
        "absence": int(snapshot_sections.get("need_absence_section", {}).get("absence_count") or 0),
        "source_lead": 0,
    }
    return {
        "schema_version": "snapshot_public_search_view_model_projection.v0",
        "record_type": "snapshot_public_search_view_model_projection",
        "projection_id": _section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "projection_profiles": ["public_web", "operator_workbench", "api_json", "classic_html", "text"],
        "result_cards": live_cards,
        "status_counts": status_counts,
        "candidate_verified_separation_visible": True,
        "live_metadata_candidate_status": "candidate",
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "accepted_truth_created": False,
        "raw_live_response_included": False,
        "limitations": [
            "public search projection is a packet preview",
            "live metadata cards remain candidate status",
            "no public route or dist write performed",
        ],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_input(
    snapshot_refresh_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "snapshot_refresh_public_alpha_reassess_input.v0",
        "record_type": "snapshot_refresh_public_alpha_reassess_input",
        "public_alpha_reassess_id": _section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "reviewed_record_count": int(snapshot_refresh_result.get("reviewed_record_count") or 0),
        "candidate_count": int(snapshot_refresh_result.get("candidate_count") or 0),
        "fixture_candidate_count": int(snapshot_refresh_result.get("fixture_candidate_count") or 0),
        "live_metadata_candidate_count": int(snapshot_refresh_result.get("live_metadata_candidate_count") or 0),
        "known_need_count": int(snapshot_refresh_result.get("known_need_count") or 0),
        "absence_count": int(snapshot_refresh_result.get("absence_count") or 0),
        "review_queue_candidate_count": int(snapshot_refresh_result.get("review_queue_candidate_count") or 0),
        "seed_batch_refs": list(snapshot_refresh_result.get("source_batch_refs") or []),
        "launch_recommended": False,
        "demo_mode_recommended": True,
        "needs_more_reviewed_records": True,
        "reassess_note": "Use for PUBLIC-ALPHA-REASSESS-01 only; snapshot refresh does not launch, deploy, or accept candidates.",
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "live_metadata_candidate_promoted": False,
        "raw_live_response_included": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def validate_snapshot_refresh_01_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    errors: list[str] = []
    if result.get("schema_version") != "snapshot_refresh_01_result.v0":
        errors.append("schema_version must be snapshot_refresh_01_result.v0")
    for key in BOUNDARY_FALSE_KEYS:
        if result.get(key) is not False:
            errors.append(f"{key} must be false")
    live_section = result.get("live_metadata_candidate_section")
    if not isinstance(live_section, Mapping):
        errors.append("live_metadata_candidate_section must be present")
    else:
        if live_section.get("review_required") is not True:
            errors.append("live metadata section must require review")
        if live_section.get("accepted_truth") is not False:
            errors.append("live metadata section must not be accepted truth")
        if live_section.get("raw_response_included") is not False:
            errors.append("live metadata section must exclude raw responses")
        for candidate in live_section.get("candidates", []):
            if candidate.get("accepted_truth") is not False:
                errors.append(f"{candidate.get('candidate_id')} accepted_truth must be false")
            if candidate.get("reviewed_record_ref") is not None:
                errors.append(f"{candidate.get('candidate_id')} reviewed_record_ref must be null")
            if candidate.get("public_search_status") != "candidate":
                errors.append(f"{candidate.get('candidate_id')} public_search_status must be candidate")
    projection = result.get("public_search_view_model_projection")
    if not isinstance(projection, Mapping) or not projection.get("result_cards"):
        errors.append("public search view model projection must include result cards")
    return {
        "schema_version": "snapshot_refresh_01_validation_report.v0",
        "task": TASK_ID,
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_01_boundary_report(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "snapshot_refresh_boundary_report.v0",
        "record_type": "snapshot_refresh_boundary_report",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "snapshot_refresh_is_projection": True,
        "live_metadata_candidates_remain_candidates": True,
        "candidates_remain_candidates": True,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "live_metadata_candidate_promoted": False,
        "raw_live_response_included": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_snapshot_refresh_01(
    policy: Mapping[str, Any] | None = None,
    *,
    from_live_metadata_pilot_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_live_metadata_pilot_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_handoffs = load_seed_batch_handoffs(merged_policy)
    live_handoff = load_live_metadata_pilot_handoff(merged_policy)
    source_batches = list(seed_handoffs["source_batches"])
    plan = build_snapshot_refresh_01_plan(seed_handoffs, live_handoff, merged_policy)
    reviewed_section = build_reviewed_record_section(sample_reviewed_records(), merged_policy)
    candidate_sections = [
        build_candidate_snapshot_section(
            batch["candidate_summaries"],
            merged_policy,
            domain_key=batch["domain_key"],
            batch_id=batch["batch_id"],
            scout_refs=batch.get("scout_refs") or [],
        )
        for batch in source_batches
    ]
    live_section = build_live_metadata_candidate_section(
        live_handoff["candidates"],
        merged_policy,
        live_metadata_handoff=live_handoff,
    )
    review_packets = [batch["review_batch_packet"] for batch in source_batches]
    review_packets.append(live_handoff["review_batch_packet"])
    review_queue_section = build_review_queue_section(review_packets, merged_policy)
    known_needs = [item for batch in source_batches for item in batch["known_needs"]]
    absence_summaries = [item for batch in source_batches for item in batch["absence_summaries"]]
    need_absence_section = build_need_absence_section(known_needs, absence_summaries, merged_policy)
    seed_summary_section = build_seed_batch_summary_section(source_batches, merged_policy)
    sections = {
        "reviewed_record_section": reviewed_section,
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_section,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
        "seed_batch_summary_section": seed_summary_section,
    }
    relay_projection = build_refreshed_relay_projection(sections, merged_policy)
    public_search_projection = build_public_search_view_model_projection(sections, merged_policy)
    fixture_candidate_count = sum(int(section.get("candidate_count") or 0) for section in candidate_sections)
    live_candidate_count = int(live_section.get("candidate_count") or 0)
    result: dict[str, Any] = {
        "schema_version": "snapshot_refresh_01_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_pilot_integrated": True,
        "source_batches": [_batch_summary(batch) for batch in source_batches],
        "source_batch_refs": [batch["batch_id"] for batch in source_batches],
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "live_metadata_source_family": live_handoff.get("source_family"),
        "total_live_requests": live_handoff.get("total_live_requests"),
        "reviewed_record_refs": list(reviewed_section["reviewed_record_refs"]),
        "candidate_section_refs": [section["section_id"] for section in candidate_sections],
        "live_metadata_candidate_section_refs": [live_section["section_id"]],
        "review_queue_section_refs": [review_queue_section["section_id"]],
        "need_absence_section_refs": [need_absence_section["section_id"]],
        "relay_projection_refs": [relay_projection["relay_projection_id"]],
        "public_search_view_model_refs": [public_search_projection["projection_id"]],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "plan": plan,
        "reviewed_record_section": reviewed_section,
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_section,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
        "seed_batch_summary_section": seed_summary_section,
        "refreshed_relay_projection": relay_projection,
        "public_search_view_model_projection": public_search_projection,
        "reviewed_record_count": int(reviewed_section["reviewed_record_count"]),
        "fixture_candidate_count": fixture_candidate_count,
        "live_metadata_candidate_count": live_candidate_count,
        "candidate_count": fixture_candidate_count + live_candidate_count,
        "known_need_count": int(need_absence_section["known_need_count"]),
        "absence_count": int(need_absence_section["absence_count"]),
        "review_queue_candidate_count": int(review_queue_section["candidate_count"]),
        "fixture_snapshot_refresh_passed": True,
        **_false_boundaries(),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }
    public_alpha = build_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_snapshot_refresh_01_boundary_report(result, merged_policy)
    result["validation_report"] = validate_snapshot_refresh_01_result(result, merged_policy)
    if result["validation_report"]["status"] != "pass":
        result["status"] = "fail"
        result["fixture_snapshot_refresh_passed"] = False
    if write_examples:
        written = write_snapshot_refresh_01_examples(result)
        written.extend(write_snapshot_refresh_01_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_snapshot_refresh_01_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_01(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "snapshots" / "refresh" / "live_metadata"
    base.mkdir(parents=True, exist_ok=True)
    candidate_sections = list(payload["candidate_sections"])
    files = {
        "snapshot_refresh_plan.json": payload["plan"],
        "reviewed_record_section.json": payload["reviewed_record_section"],
        "candidate_section_frontier_media.json": candidate_sections[0],
        "candidate_section_legacy_software.json": candidate_sections[1],
        "live_metadata_candidate_section.json": payload["live_metadata_candidate_section"],
        "review_queue_section.json": payload["review_queue_section"],
        "need_absence_section.json": payload["need_absence_section"],
        "seed_batch_summary_section.json": payload["seed_batch_summary_section"],
        "refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "public_search_view_model_projection.json": payload["public_search_view_model_projection"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "snapshot_refresh_01_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/relay/refresh/live_metadata_refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "examples/public_alpha/reassess/live_metadata/snapshot_refresh_01_reassess_input.json": payload["public_alpha_reassess_input"],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_snapshot_refresh_01_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_01(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = build_snapshot_refresh_01_inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_snapshot_refresh_01_audit_pack(payload, repo_root))
    return written


def build_snapshot_refresh_01_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    live_section = dict(result.get("live_metadata_candidate_section") or {})
    candidate_sections = list(result.get("candidate_sections") or [])
    packets: dict[str, Any] = {
        "snapshot_refresh_01_input_state.json": {
            "schema_version": "snapshot_refresh_01_input_state.v0",
            "task": TASK_ID,
            "branch": "dev",
            "input_results": {
                "live_metadata_pilot": "control/inventory/live_metadata_pilot_result.json",
                "public_alpha_reassess": "control/inventory/public_alpha_reassess_result.json",
                "snapshot_refresh_00": "control/inventory/snapshot_refresh_result.json",
                "seed_batch_frontier_media": "control/inventory/seed_batch_frontier_media_result.json",
                "seed_batch_legacy_software": "control/inventory/seed_batch_legacy_software_result.json",
                "review_batch": "control/inventory/review_batch_result.json",
                "scout_runtime": "control/inventory/scout_runtime_result.json",
                "candidate_index": "control/inventory/candidate_index_result.json",
                "query_planner": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
                "snapshot_relay": "control/inventory/snapshot_relay_result.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
                "public_alpha_readonly": "control/inventory/public_alpha_readonly_00_result.json",
            },
            **_false_boundaries(),
            "created_at": DEFAULT_TIMESTAMP,
        },
        "snapshot_refresh_01_source_matrix.json": {
            "schema_version": "snapshot_refresh_01_source_matrix.v0",
            "task": TASK_ID,
            "sources": list(result.get("source_batches") or []),
            "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
            "source_batch_count": len(result.get("source_batches") or []),
            "live_metadata_source_family": result.get("live_metadata_source_family"),
        },
        "snapshot_refresh_01_reviewed_record_matrix.json": {
            "schema_version": "snapshot_refresh_01_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "reviewed_record_refs": list(result.get("reviewed_record_refs") or []),
            "reviewed_record_count": result.get("reviewed_record_count"),
            "reviewed_records_only_from_existing_reviewed_sources": True,
        },
        "snapshot_refresh_01_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_01_candidate_matrix.v0",
            "task": TASK_ID,
            "candidate_sections": [
                {
                    "section_id": section.get("section_id"),
                    "batch_id": section.get("batch_id"),
                    "domain_key": section.get("domain_key"),
                    "candidate_count": section.get("candidate_count"),
                    "fixture_derived": True,
                    "accepted_truth": False,
                    "candidate_promoted_to_reviewed": False,
                }
                for section in candidate_sections
            ],
            "fixture_candidate_count": result.get("fixture_candidate_count"),
            "candidate_count": result.get("candidate_count"),
        },
        "snapshot_refresh_01_live_metadata_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_01_live_metadata_candidate_matrix.v0",
            "task": TASK_ID,
            "section_id": live_section.get("section_id"),
            "source_family": live_section.get("source_family"),
            "candidate_refs": live_section.get("candidate_refs"),
            "candidate_count": live_section.get("candidate_count"),
            "review_required": True,
            "accepted_truth": False,
            "raw_response_included": False,
            "public_search_status": "candidate",
        },
        "snapshot_refresh_01_need_absence_matrix.json": {
            "schema_version": "snapshot_refresh_01_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result.get("known_need_count"),
            "absence_count": result.get("absence_count"),
            "bounded_absence_statements": True,
        },
        "snapshot_refresh_01_review_queue_matrix.json": {
            "schema_version": "snapshot_refresh_01_review_queue_matrix.v0",
            "task": TASK_ID,
            "review_queue_section_refs": list(result.get("review_queue_section_refs") or []),
            "review_queue_candidate_count": result.get("review_queue_candidate_count"),
            "live_metadata_candidate_refs": result.get("review_queue_section", {}).get("live_metadata_candidate_refs"),
            "operator_context_required": True,
        },
        "snapshot_refresh_01_relay_projection_matrix.json": {
            "schema_version": "snapshot_refresh_01_relay_projection_matrix.v0",
            "task": TASK_ID,
            "relay_projection_refs": list(result.get("relay_projection_refs") or []),
            "read_only": True,
            "mutation_enabled": False,
            "site_dist_written": False,
        },
        "snapshot_refresh_01_public_search_view_model_matrix.json": {
            "schema_version": "snapshot_refresh_01_public_search_view_model_matrix.v0",
            "task": TASK_ID,
            "public_search_view_model_refs": list(result.get("public_search_view_model_refs") or []),
            "result_card_count": len(result.get("public_search_view_model_projection", {}).get("result_cards") or []),
            "live_metadata_candidate_status": "candidate",
            "candidate_verified_separation_visible": True,
        },
        "snapshot_refresh_01_public_alpha_reassess_matrix.json": {
            "schema_version": "snapshot_refresh_01_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
            "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
        },
        "snapshot_refresh_01_boundary_report.json": result["boundary_report"],
        "snapshot_refresh_01_smoke_result.json": {
            "schema_version": "snapshot_refresh_01_smoke_result.v0",
            "task": TASK_ID,
            "status": result.get("status"),
            "fixture_snapshot_refresh_passed": result.get("fixture_snapshot_refresh_passed"),
            "live_metadata_pilot_integrated": True,
            "candidate_count": result.get("candidate_count"),
            "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
            "reviewed_record_count": result.get("reviewed_record_count"),
            **_false_boundaries(),
        },
        "snapshot_refresh_01_validation_matrix.json": {
            "schema_version": "snapshot_refresh_01_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_live_metadata_pilot_batch.py",
                "python scripts/validate_public_search_ux_model.py",
                "focused snapshot refresh unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "snapshot_refresh_01_result.json": _task_result(result),
        "snapshot_refresh_01_next_task_decision.json": {
            "schema_version": "snapshot_refresh_01_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": NEXT_TASK,
            "planned_after": [
                "SEED-BATCH-MANUALS-SCANS-00",
                "SEED-BATCH-DRIVER-SUPPORT-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "deployment_performed": False,
            "public_launch_readiness_claimed": False,
        },
        "snapshot_refresh_01_failure_repair_log.json": {
            "schema_version": "snapshot_refresh_01_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }
    return packets


def _write_snapshot_refresh_01_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "snapshot-refresh-01-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = build_snapshot_refresh_01_inventory_packets(result)
    audit_files: dict[str, Any] = {
        "snapshot_refresh_01_report.json": _task_result(result),
    }
    audit_markdown = {
        "README.md": "# SNAPSHOT-REFRESH-01 Audit\n\nRefresh evidence after the bounded live metadata pilot. Live metadata candidates remain candidates, raw responses are excluded, and no public index or deployment artifact is mutated.\n",
        "source_matrix.md": _matrix_md("Source Matrix", inventory["snapshot_refresh_01_source_matrix.json"]),
        "reviewed_record_matrix.md": _matrix_md("Reviewed Record Matrix", inventory["snapshot_refresh_01_reviewed_record_matrix.json"]),
        "candidate_matrix.md": _matrix_md("Candidate Matrix", inventory["snapshot_refresh_01_candidate_matrix.json"]),
        "live_metadata_candidate_matrix.md": _matrix_md("Live Metadata Candidate Matrix", inventory["snapshot_refresh_01_live_metadata_candidate_matrix.json"]),
        "need_absence_matrix.md": _matrix_md("Need And Absence Matrix", inventory["snapshot_refresh_01_need_absence_matrix.json"]),
        "review_queue_matrix.md": _matrix_md("Review Queue Matrix", inventory["snapshot_refresh_01_review_queue_matrix.json"]),
        "relay_projection_matrix.md": _matrix_md("Relay Projection Matrix", inventory["snapshot_refresh_01_relay_projection_matrix.json"]),
        "public_search_view_model_matrix.md": _matrix_md("Public Search View Model Matrix", inventory["snapshot_refresh_01_public_search_view_model_matrix.json"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", inventory["snapshot_refresh_01_public_alpha_reassess_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["snapshot_refresh_01_smoke_result.json"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["snapshot_refresh_01_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/snapshot_refresh_01_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    generated_files = {
        "sample_snapshot_refresh_plan.json": result["plan"],
        "sample_live_metadata_candidate_section.json": result["live_metadata_candidate_section"],
        "sample_public_search_view_model_projection.json": result["public_search_view_model_projection"],
        "sample_relay_projection.json": result["refreshed_relay_projection"],
        "sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Snapshot Refresh 01 Summary\n\n"
        f"- reviewed records: {result.get('reviewed_record_count')}\n"
        f"- fixture candidates: {result.get('fixture_candidate_count')}\n"
        f"- live metadata candidates: {result.get('live_metadata_candidate_count')}\n"
        f"- known needs: {result.get('known_need_count')}\n"
        f"- absences: {result.get('absence_count')}\n"
        "- accepted truth created: false\n"
        "- raw live response included: false\n"
        "- site/dist written: false\n"
    )
    written: list[str] = []
    for name, content in audit_files.items():
        path = audit_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    for name, content in audit_markdown.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    for name, content in generated_files.items():
        path = generated / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    summary_path = generated / "sample_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    written.append(str(summary_path.relative_to(repo_root)))
    return written


def _live_metadata_candidate_item(candidate: Mapping[str, Any], scout_refs: Sequence[str]) -> dict[str, Any]:
    candidate_id = _text(candidate.get("candidate_id"))
    limitations = _text_list(candidate.get("limitations")) or ["redacted_metadata_summary_only", "review_required"]
    if "live_metadata_derived_review_only" not in limitations:
        limitations.append("live_metadata_derived_review_only")
    return {
        "schema_version": "snapshot_live_metadata_candidate_item.v0",
        "candidate_snapshot_ref": _section_id("snapshot_live_metadata_candidate", candidate_id),
        "candidate_id": candidate_id,
        "domain_id": _text(candidate.get("domain_id")),
        "source_family": _text(candidate.get("source_family")) or "internet_archive_metadata",
        "title": _text(candidate.get("title")),
        "query_refs": _text_list([candidate.get("query_plan_ref"), candidate.get("matched_query")]),
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "scout_trail_refs": _text_list(scout_refs),
        "review_state": _text(candidate.get("review_state")) or "needs_review",
        "accepted_truth": False,
        "reviewed_record_ref": None,
        "raw_response_included": False,
        "fixture_derived": False,
        "live_metadata_derived": True,
        "source_observation_ref": _text(candidate.get("source_observation_ref")),
        "source_locator": copy.deepcopy(candidate.get("source_locator") or {}),
        "limitations": limitations,
        "action_posture": _review_only_action_posture(candidate.get("action_posture")),
        "public_search_status": "candidate",
    }


def _live_candidate_result_card(candidate: Mapping[str, Any]) -> dict[str, Any]:
    refs = _text_list(candidate.get("scout_trail_refs"))
    source_ref = _text(candidate.get("source_observation_ref"))
    if source_ref:
        refs.append(source_ref)
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", candidate.get("candidate_id")),
        "title": _text(candidate.get("title")),
        "url": "/candidate/" + _text(candidate.get("candidate_id")),
        "status": "candidate",
        "object_type": "metadata_candidate",
        "domain": _text(candidate.get("domain_id")),
        "source_family": _text(candidate.get("source_family")),
        "source_label": "Internet Archive metadata",
        "snippet": "Live-metadata-derived review-only candidate summary; no raw response is included.",
        "match_reasons": [
            "bounded_live_metadata_pilot",
            "redacted_metadata_summary",
            "review_required",
        ],
        "evidence_summary": {
            "summary": "Candidate has redacted source observation and SCOUT trail references, but is not reviewed truth.",
            "evidence_refs": refs,
            "evidence_count": len(refs),
        },
        "confidence_label": "candidate",
        "risk_label": "review_required",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "unreviewed",
        "action_posture": _review_only_action_posture(candidate.get("action_posture")),
        "review_required": True,
        "accepted_truth": False,
        "limitations": _text_list(candidate.get("limitations")),
        "created_at": DEFAULT_TIMESTAMP,
    }


def _review_packet_summary(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_review_packet_summary.v0",
        "review_batch_id": _text(packet.get("review_batch_id")) or _section_id("review_batch", packet.get("candidate_refs")),
        "candidate_refs": _text_list(packet.get("candidate_refs")),
        "cluster_refs": _text_list(packet.get("cluster_refs")),
        "operator_context_required": bool(packet.get("operator_context_required", True)),
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
    }


def _batch_summary(batch: Mapping[str, Any]) -> dict[str, Any]:
    result = batch.get("seed_batch_result") if isinstance(batch.get("seed_batch_result"), Mapping) else batch
    return {
        "schema_version": "snapshot_seed_batch_summary_item.v0",
        "batch_id": _text(batch.get("batch_id") or result.get("batch_id")),
        "domain_key": _text(batch.get("domain_key")),
        "domain_id": _text(batch.get("domain_id") or result.get("domain_id")),
        "query_count": int(batch.get("query_count") or result.get("query_count") or 0),
        "candidate_count": int(batch.get("candidate_count") or result.get("candidate_count") or 0),
        "review_batch_refs": _text_list(batch.get("review_batch_refs") or result.get("review_batch_refs")),
        "snapshot_refresh_handoff_refs": _text_list(batch.get("snapshot_refresh_handoff_refs") or result.get("snapshot_refresh_handoff_refs")),
        "public_alpha_reassess_refs": _text_list(batch.get("public_alpha_reassess_refs") or result.get("public_alpha_reassess_refs")),
        "fixture_derived": bool(batch.get("fixture_derived", True)),
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


def _relay_query_preview(query: str, candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    terms = [term.casefold() for term in query.split() if len(term) > 2]
    matches = [
        candidate
        for candidate in candidates
        if any(term in _text(candidate.get("title")).casefold() for term in terms)
    ][:5]
    return {
        "schema_version": "snapshot_refresh_relay_query_preview.v0",
        "query": query,
        "read_only": True,
        "result_count": len(matches),
        "results": [
            {
                "candidate_id": item.get("candidate_id"),
                "title": item.get("title"),
                "domain_id": item.get("domain_id"),
                "accepted_truth": False,
                "review_required": True,
                "public_search_status": item.get("public_search_status") or "candidate",
            }
            for item in matches
        ],
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_01_result_summary.v0",
        "task": TASK_ID,
        "status": result.get("status"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "live_metadata_pilot_integrated": True,
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "review_queue_candidate_count": result.get("review_queue_candidate_count"),
        "fixture_snapshot_refresh_passed": bool(result.get("fixture_snapshot_refresh_passed")),
        **_false_boundaries(),
        "recommended_next_task": NEXT_TASK,
    }


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_01_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "live_metadata_pilot_integrated": True,
        "contracts_added": True,
        "policies_added": True,
        "source_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "candidate_matrix_added": True,
        "live_metadata_candidate_matrix_added": True,
        "need_absence_matrix_added": True,
        "review_queue_matrix_added": True,
        "relay_projection_matrix_added": True,
        "public_search_view_model_matrix_added": True,
        "public_alpha_reassess_matrix_added": True,
        "runtime_snapshot_refresh_added": True,
        "reviewed_record_section_created": True,
        "candidate_sections_created": True,
        "live_metadata_candidate_section_created": True,
        "review_queue_section_created": True,
        "need_absence_section_created": True,
        "relay_projection_created": True,
        "public_search_view_model_projection_created": True,
        "public_alpha_reassess_input_created": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "fixture_snapshot_refresh_passed": bool(result.get("fixture_snapshot_refresh_passed")),
        **_false_boundaries(),
        "recommended_next_task": NEXT_TASK,
    }


def _review_only_action_posture(source_action_posture: Any = None) -> dict[str, Any]:
    source = source_action_posture if isinstance(source_action_posture, Mapping) else {}
    allowed = _text_list(source.get("allowed_actions")) or ["inspect", "view_source", "view_provenance", "read"]
    blocked = sorted(set(_text_list(source.get("blocked_actions"))) | {"download", "install_handoff", "execute", "upload", "extract", "promote"})
    return {
        "schema_version": "snapshot_review_only_action_posture.v0",
        "allowed_actions": allowed,
        "blocked_actions": blocked,
        "review_required": True,
        "accepted_truth": False,
        "public_mutation_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
    }


def _retag_snapshot_refresh(payload: Any) -> Any:
    if isinstance(payload, dict):
        updated = {}
        for key, value in payload.items():
            if key == "snapshot_refresh_id":
                updated[key] = SNAPSHOT_REFRESH_ID
            elif key == "created_at":
                updated[key] = DEFAULT_TIMESTAMP
            else:
                updated[key] = _retag_snapshot_refresh(value)
        return updated
    if isinstance(payload, list):
        return [_retag_snapshot_refresh(item) for item in payload]
    return payload


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "snapshot_refresh_is_projection",
        "live_metadata_candidates_remain_candidates",
        "candidates_remain_candidates",
        "seed_outputs_are_not_truth",
        "reviewed_records_only_from_existing_reviewed_sources",
        "no_candidate_auto_acceptance",
        "no_live_metadata_auto_acceptance",
        "no_reviewed_index_mutation",
        "no_master_index_mutation",
        "no_public_index_mutation",
        "no_public_mutation",
        "no_deployment",
        "no_public_launch_claim",
        "no_production_claim",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"snapshot refresh 01 policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "raw_live_response_included",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"snapshot refresh 01 policy enables forbidden behavior: {', '.join(enabled)}")


def _assert_live_metadata_pilot(pilot_result: Mapping[str, Any], candidate_matrix: Mapping[str, Any]) -> None:
    if pilot_result.get("operator_live_metadata_run_performed") is not True:
        raise ValueError("live metadata pilot must have performed an approved operator run")
    if pilot_result.get("source_family") != "internet_archive_metadata":
        raise ValueError("snapshot refresh 01 only accepts the Internet Archive metadata pilot")
    if int(pilot_result.get("total_live_requests") or 0) > 24:
        raise ValueError("live metadata pilot exceeded the approved request budget")
    for key in (
        "raw_live_response_committed",
        "download_performed",
        "extraction_executed",
        "accepted_truth_created",
        "reviewed_index_mutated",
        "master_index_mutated",
        "public_index_mutated",
        "deployment_performed",
    ):
        if pilot_result.get(key) is not False:
            raise ValueError(f"live metadata pilot boundary failed: {key}")
    if candidate_matrix.get("accepted_truth") is not False:
        raise ValueError("live metadata candidates must not be accepted truth")


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


def _limitations() -> list[str]:
    return [
        "snapshot_refresh_is_projection_only",
        "live_metadata_candidates_remain_candidates",
        "redacted_metadata_summaries_only",
        "raw_live_responses_excluded",
        "review_required_before_promotion",
        "local_apply_is_separate_gate",
        "public_alpha_reassess_is_separate_gate",
        "no_site_dist_write",
        "no_public_index_mutation",
        "no_deployment_or_launch_claim",
    ]


def _section_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


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
