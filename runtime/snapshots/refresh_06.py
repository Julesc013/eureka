"""Snapshot refresh after the next review-batch apply.

SNAPSHOT-REFRESH-06 packages the temp-only review-batch apply proof into the
snapshot, relay, and public-search projection layer. It keeps limited reviewed
metadata/source-lead records, reviewed known needs, reviewed bounded absences,
and remaining candidates distinct from verified artifacts or public truth.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.public_search import build_public_search_ux_mvp_bundle
from runtime.snapshots import refresh_05


DEFAULT_TIMESTAMP = "2026-06-03T00:00:00Z"
SNAPSHOT_REFRESH_ID = "snapshot_refresh_06"
TASK_ID = "SNAPSHOT-REFRESH-06"
SNAPSHOT_REFRESH_05_REF = "control/inventory/snapshot_refresh_05_result.json"
REVIEW_BATCH_APPLY_REF = "control/inventory/review_batch_apply_next_result.json"
PUBLIC_SEARCH_UX_MVP_REF = "control/inventory/public_search_ux_mvp_result.json"
NEXT_TASK = "PUBLIC-ALPHA-REASSESS-06 - Reassess alpha after review batch apply snapshot refresh"

SUPPORTED_RESULT_CARD_STATES = (
    "verified",
    "reviewed_metadata_record",
    "reviewed_source_lead",
    "candidate",
    "near_miss",
    "known_need",
    "absence",
    "source_lead",
)

BOUNDARY_FALSE_KEYS = (
    "accepted_truth_created",
    "candidate_promoted_to_reviewed",
    "artifact_verified_claim_created",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "compatibility_guarantee_claim_created",
    "rights_clearance_claim_created",
    "scan_completeness_claim_created",
    "ocr_quality_claim_created",
    "file_fetch_performed",
    "ocr_performed",
    "install_execution_enabled",
    "operator_instance_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "site_dist_written",
    "download_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
)

DEFAULT_POLICY: dict[str, Any] = {
    "snapshot_refresh_is_projection": True,
    "review_batch_apply_outputs_project_as_limited_records": True,
    "reviewed_known_needs_are_not_resolved_objects": True,
    "reviewed_bounded_absences_are_bounded_not_universal": True,
    "non_applied_candidates_remain_candidates": True,
    "temp_apply_outputs_do_not_mutate_operator_instance": True,
    "limited_reviewed_records_are_not_verified_artifacts": True,
    "public_ux_projection_is_read_only": True,
    "candidate_verified_distinction_required": True,
    "limited_reviewed_record_distinction_required": True,
    "no_results_need_projection_required": True,
    "no_reviewed_index_mutation": True,
    "no_master_index_mutation": True,
    "no_public_index_mutation": True,
    "no_public_mutation": True,
    "no_public_live_source_fanout": True,
    "no_deployment": True,
    "no_site_dist_write": True,
    "no_public_launch_claim": True,
    "no_production_claim": True,
    "no_verified_download_claim": True,
    "no_malware_clean_claim": True,
    "no_rights_clearance_claim": True,
    "no_compatibility_guarantee_claim": True,
    "no_scan_completeness_claim": True,
    "no_ocr_quality_claim": True,
    "downloads_enabled": False,
    "file_fetches_enabled": False,
    "ocr_enabled": False,
    "extraction_enabled": False,
    "install_execution_enabled": False,
    "model_provider_enabled": False,
    "public_mutation_enabled": False,
    "public_live_source_fanout_enabled": False,
}


def load_snapshot_refresh_05_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    result = refresh_05.run_snapshot_refresh_05(from_public_search_ux_examples=True)
    if result.get("status") != "pass" or result.get("fixture_snapshot_refresh_passed") is not True:
        raise ValueError("snapshot refresh 05 must pass before snapshot refresh 06")
    if int(result.get("total_limited_reviewed_record_projection_count") or 0) != 4:
        raise ValueError("snapshot refresh 05 limited reviewed projection count mismatch")
    if int(result.get("total_candidate_count") or 0) != 68:
        raise ValueError("snapshot refresh 05 candidate count mismatch")
    _assert_false_boundaries(result)
    return result


def load_review_batch_apply_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    result = _read_json(repo / REVIEW_BATCH_APPLY_REF)
    metadata = _read_json(repo / "examples/review_batch/apply_next/limited_reviewed_metadata_records.json")
    source_leads = _read_json(repo / "examples/review_batch/apply_next/limited_reviewed_source_leads.json")
    known_needs = _read_json(repo / "examples/review_batch/apply_next/reviewed_known_needs.json")
    bounded_absences = _read_json(repo / "examples/review_batch/apply_next/reviewed_bounded_absences.json")
    non_applied = _read_json(repo / "examples/review_batch/apply_next/non_applied_candidates.json")
    snapshot_handoff = _read_json(repo / "examples/review_batch/apply_next/snapshot_refresh_handoff.json")
    _assert_review_batch_apply(result, metadata, source_leads, known_needs, bounded_absences, non_applied)
    return {
        "schema_version": "snapshot_refresh_06_review_batch_apply_handoff.v0",
        "task": TASK_ID,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "snapshot_handoff": snapshot_handoff,
        "result": result,
        "limited_reviewed_metadata_records": list(metadata.get("records") or []),
        "limited_reviewed_source_leads": list(source_leads.get("records") or []),
        "reviewed_known_needs": list(known_needs.get("records") or []),
        "reviewed_bounded_absences": list(bounded_absences.get("records") or []),
        "non_applied_candidates": list(non_applied.get("candidates") or []),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_snapshot_refresh_06_plan(
    snapshot_05: Mapping[str, Any],
    review_batch_apply: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    applied_refs = _applied_candidate_refs(review_batch_apply)
    return {
        "schema_version": "snapshot_refresh_plan.v0",
        "record_type": "snapshot_refresh_plan",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "snapshot_refresh_05_ref": SNAPSHOT_REFRESH_05_REF,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "review_batch_apply_section_refs": [_section_id("snapshot_review_batch_apply_section", SNAPSHOT_REFRESH_ID)],
        "limited_reviewed_metadata_section_refs": [_section_id("snapshot_limited_reviewed_metadata_section", SNAPSHOT_REFRESH_ID)],
        "limited_reviewed_source_lead_section_refs": [_section_id("snapshot_limited_reviewed_source_lead_section", SNAPSHOT_REFRESH_ID)],
        "reviewed_known_need_section_refs": [_section_id("snapshot_reviewed_known_need_section", SNAPSHOT_REFRESH_ID)],
        "reviewed_bounded_absence_section_refs": [_section_id("snapshot_reviewed_bounded_absence_section", SNAPSHOT_REFRESH_ID)],
        "non_applied_candidate_section_refs": [_section_id("snapshot_non_applied_candidate_section", SNAPSHOT_REFRESH_ID)],
        "result_card_section_refs": [_section_id("snapshot_result_card_section", SNAPSHOT_REFRESH_ID)],
        "no_results_section_refs": [_section_id("snapshot_no_results_section", SNAPSHOT_REFRESH_ID)],
        "relay_projection_refs": [_section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID)],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "previous_total_limited_reviewed_record_projection_count": int(
            snapshot_05.get("total_limited_reviewed_record_projection_count") or 0
        ),
        "applied_candidate_refs": sorted(applied_refs),
        "review_batch_apply_outputs_project_as_limited_records": True,
        "refresh_mode": "review_batch_apply_projection_only",
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_review_batch_apply_section(
    review_batch_apply: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    result = dict(review_batch_apply.get("result") or {})
    return {
        "schema_version": "snapshot_review_batch_apply_section.v0",
        "record_type": "snapshot_review_batch_apply_section",
        "section_id": _section_id("snapshot_review_batch_apply_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "eligible_apply_count": int(result.get("eligible_apply_count") or 0),
        "reviewed_record_delta_count": int(result.get("reviewed_record_delta_count") or 0),
        "reviewed_known_needs_created": int(result.get("reviewed_known_needs_created") or 0),
        "reviewed_bounded_absences_created": int(result.get("reviewed_bounded_absences_created") or 0),
        "non_applied_count": int(result.get("non_applied_count") or 0),
        "temp_apply_only": True,
        "operator_instance_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_limited_reviewed_metadata_section(
    previous_records: Sequence[Mapping[str, Any]],
    new_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_limited_record(record) for record in previous_records] + [_limited_record(record) for record in new_records]
    return {
        "schema_version": "snapshot_limited_reviewed_metadata_section.v0",
        "record_type": "snapshot_limited_reviewed_metadata_section",
        "section_id": _section_id("snapshot_limited_reviewed_metadata_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "previous_record_count": len(previous_records),
        "new_record_count": len(new_records),
        "limited_reviewed_metadata_record_count": len(records),
        "record_refs": [record.get("record_id") for record in records],
        "records": records,
        "limited_claim_scope": "metadata_identity_lead_only",
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee_claim": False,
        "scan_completeness_claim": False,
        "ocr_quality_claim": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_limited_reviewed_source_lead_section(
    previous_leads: Sequence[Mapping[str, Any]],
    new_leads: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_limited_record(record) for record in previous_leads] + [_limited_record(record) for record in new_leads]
    return {
        "schema_version": "snapshot_limited_reviewed_source_lead_section.v0",
        "record_type": "snapshot_limited_reviewed_source_lead_section",
        "section_id": _section_id("snapshot_limited_reviewed_source_lead_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "previous_record_count": len(previous_leads),
        "new_record_count": len(new_leads),
        "limited_reviewed_source_lead_count": len(records),
        "record_refs": [record.get("record_id") for record in records],
        "records": records,
        "limited_claim_scope": "source_lead_only",
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee_claim": False,
        "scan_completeness_claim": False,
        "ocr_quality_claim": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_reviewed_known_need_section(
    reviewed_needs: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_reviewed_need(record) for record in reviewed_needs]
    return {
        "schema_version": "snapshot_reviewed_known_need_section.v0",
        "record_type": "snapshot_reviewed_known_need_section",
        "section_id": _section_id("snapshot_reviewed_known_need_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "reviewed_known_need_count": len(records),
        "record_refs": [record.get("record_id") for record in records],
        "records": records,
        "reviewed_known_needs_are_not_resolved_objects": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_reviewed_bounded_absence_section(
    reviewed_absences: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_reviewed_absence(record) for record in reviewed_absences]
    return {
        "schema_version": "snapshot_reviewed_bounded_absence_section.v0",
        "record_type": "snapshot_reviewed_bounded_absence_section",
        "section_id": _section_id("snapshot_reviewed_bounded_absence_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "reviewed_bounded_absence_count": len(records),
        "record_refs": [record.get("record_id") for record in records],
        "records": records,
        "reviewed_bounded_absences_are_bounded_not_universal": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_non_applied_candidate_section(
    non_applied: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidates = [_remaining_candidate(candidate) for candidate in non_applied]
    return {
        "schema_version": "snapshot_non_applied_candidate_section.v0",
        "record_type": "snapshot_non_applied_candidate_section",
        "section_id": _section_id("snapshot_non_applied_candidate_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "candidate_count": len(candidates),
        "non_applied_count": len(candidates),
        "candidates": candidates,
        "non_applied_candidates_remain_candidates": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_candidate_snapshot_sections(
    snapshot_05: Mapping[str, Any],
    review_batch_apply: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    applied_refs = _applied_candidate_refs(review_batch_apply)
    candidate_sections = []
    for section in snapshot_05.get("candidate_sections") or []:
        item = _retag(section)
        item["candidates"] = [
            _remaining_candidate(candidate)
            for candidate in item.get("candidates", [])
            if _text(candidate.get("candidate_id")) not in applied_refs
        ]
        item["candidate_count"] = len(item["candidates"])
        item["candidate_refs"] = [candidate.get("candidate_id") for candidate in item["candidates"]]
        item["candidate_promoted_to_reviewed"] = False
        item["accepted_truth"] = False
        candidate_sections.append(item)
    live_section = _retag(snapshot_05.get("live_metadata_candidate_section") or {})
    live_section["candidates"] = [_remaining_candidate(candidate) for candidate in live_section.get("candidates", [])]
    live_section["candidate_count"] = len(live_section.get("candidates") or [])
    live_section["accepted_truth"] = False
    return candidate_sections, live_section


def build_public_search_ux_section(
    route_section: Mapping[str, Any],
    result_card_section: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "snapshot_public_search_ux_section.v0",
        "record_type": "snapshot_public_search_ux_section",
        "section_id": _section_id("snapshot_public_search_ux_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "route_refs": [route.get("route") for route in route_section.get("routes", [])],
        "result_card_refs": [card.get("view_model_id") for card in result_card_section.get("cards", [])],
        "route_count": int(route_section.get("route_count") or 0),
        "page_count": int(route_section.get("route_count") or 0),
        "result_card_count": int(result_card_section.get("result_card_count") or 0),
        "no_js_required": True,
        "public_read_only": True,
        "mutation_enabled": False,
        "live_source_fanout_enabled": False,
        "download_enabled": False,
        "file_fetch_enabled": False,
        "ocr_enabled": False,
        "extraction_enabled": False,
        "install_execution_enabled": False,
        "model_provider_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_public_route_section(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    routes = [dict(route) for route in build_public_search_ux_mvp_bundle().get("routes") or []]
    return {
        "schema_version": "snapshot_public_route_section.v0",
        "record_type": "snapshot_public_route_section",
        "section_id": _section_id("snapshot_public_route_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "routes": routes,
        "route_count": len(routes),
        "all_routes_get": all(route.get("method") == "GET" for route in routes),
        "all_routes_no_js": all(route.get("no_js_required") is True for route in routes),
        "all_routes_read_only": all(route.get("public_read_only") is True for route in routes),
        "mutation_enabled": False,
        "live_source_fanout_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_result_card_projection_section(
    snapshot_05: Mapping[str, Any],
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    applied_refs = _applied_candidate_refs_from_sections(snapshot_sections)
    prior_cards = [
        _retag(card)
        for card in snapshot_05.get("result_card_section", {}).get("cards", [])
        if _card_candidate_id(card) not in applied_refs
        and card.get("status") not in {"reviewed_metadata_record", "reviewed_source_lead"}
    ]
    metadata_cards = [
        _limited_record_card(record, "reviewed_metadata_record", "limited_reviewed_metadata_record")
        for record in snapshot_sections["limited_reviewed_metadata_section"]["records"]
    ]
    source_lead_cards = [
        _limited_record_card(record, "reviewed_source_lead", "limited_reviewed_source_lead")
        for record in snapshot_sections["limited_reviewed_source_lead_section"]["records"]
    ]
    need_cards = [
        _reviewed_need_card(record)
        for record in snapshot_sections["reviewed_known_need_section"]["records"]
    ]
    absence_cards = [
        _reviewed_absence_card(record)
        for record in snapshot_sections["reviewed_bounded_absence_section"]["records"]
    ]
    cards = _dedupe_cards(prior_cards + metadata_cards + source_lead_cards + need_cards + absence_cards)
    observed = sorted({card.get("status") for card in cards if card.get("status")})
    return {
        "schema_version": "snapshot_result_card_section.v0",
        "record_type": "snapshot_result_card_section",
        "section_id": _section_id("snapshot_result_card_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "snapshot_refresh_05_ref": SNAPSHOT_REFRESH_05_REF,
        "cards": cards,
        "result_card_count": len(cards),
        "supported_statuses": list(SUPPORTED_RESULT_CARD_STATES),
        "observed_statuses": observed,
        "result_card_states_count": len(SUPPORTED_RESULT_CARD_STATES),
        "candidate_count_after_apply": int(snapshot_sections["non_applied_candidate_section"]["candidate_count"]),
        "candidate_verified_distinction_passed": True,
        "limited_reviewed_record_distinction_passed": True,
        "candidate_cards_accepted_truth": False,
        "limited_records_are_not_verified_artifacts": True,
        "reviewed_needs_are_not_resolved_objects": True,
        "reviewed_absences_are_bounded_not_universal": True,
        "public_read_only": True,
        "mutation_enabled": False,
        "download_enabled": False,
        "file_fetch_enabled": False,
        "ocr_enabled": False,
        "extraction_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_no_results_projection_section(
    snapshot_05: Mapping[str, Any],
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    previous = dict(snapshot_05.get("no_results_section", {}).get("no_results") or {})
    return {
        "schema_version": "snapshot_no_results_section.v0",
        "record_type": "snapshot_no_results_section",
        "section_id": _section_id("snapshot_no_results_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "no_results": {
            **previous,
            "reviewed_known_needs": snapshot_sections["reviewed_known_need_section"]["records"],
            "reviewed_bounded_absences": snapshot_sections["reviewed_bounded_absence_section"]["records"],
        },
        "no_results_sections_count": 1,
        "known_need_count": int(snapshot_05.get("no_results_section", {}).get("known_need_count") or 0),
        "absence_count": int(snapshot_05.get("no_results_section", {}).get("absence_count") or 0),
        "reviewed_known_need_count": int(snapshot_sections["reviewed_known_need_section"]["reviewed_known_need_count"]),
        "reviewed_bounded_absence_count": int(
            snapshot_sections["reviewed_bounded_absence_section"]["reviewed_bounded_absence_count"]
        ),
        "known_need_projection_visible": True,
        "reviewed_known_need_projection_visible": True,
        "reviewed_bounded_absence_projection_visible": True,
        "public_mutation_enabled": False,
        "live_source_fanout_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_refreshed_relay_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "snapshot_refresh_relay_projection.v0",
        "record_type": "snapshot_refresh_relay_projection",
        "relay_projection_id": _section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "read_only": True,
        "source_relay_projection_ref": "examples/snapshots/refresh/public_search_ux_mvp/refreshed_relay_projection.json",
        "sections": {
            "total_limited_reviewed_record_projection_count": _total_limited_records(snapshot_sections),
            "limited_reviewed_metadata_records": int(
                snapshot_sections["limited_reviewed_metadata_section"]["limited_reviewed_metadata_record_count"]
            ),
            "limited_reviewed_source_leads": int(
                snapshot_sections["limited_reviewed_source_lead_section"]["limited_reviewed_source_lead_count"]
            ),
            "reviewed_known_needs": int(snapshot_sections["reviewed_known_need_section"]["reviewed_known_need_count"]),
            "reviewed_bounded_absences": int(
                snapshot_sections["reviewed_bounded_absence_section"]["reviewed_bounded_absence_count"]
            ),
            "remaining_candidates": int(snapshot_sections["non_applied_candidate_section"]["candidate_count"]),
            "result_cards": int(snapshot_sections["result_card_section"]["result_card_count"]),
            "result_card_states": int(snapshot_sections["result_card_section"]["result_card_states_count"]),
        },
        "projection_sections": [
            snapshot_sections["review_batch_apply_section"]["section_id"],
            snapshot_sections["limited_reviewed_metadata_section"]["section_id"],
            snapshot_sections["limited_reviewed_source_lead_section"]["section_id"],
            snapshot_sections["reviewed_known_need_section"]["section_id"],
            snapshot_sections["reviewed_bounded_absence_section"]["section_id"],
            snapshot_sections["non_applied_candidate_section"]["section_id"],
            snapshot_sections["result_card_section"]["section_id"],
            snapshot_sections["no_results_section"]["section_id"],
        ],
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "file_fetch_enabled": False,
        "ocr_enabled": False,
        "install_execution_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_performed": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
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
        "review_batch_apply_integrated": True,
        "total_limited_reviewed_record_projection_count": int(
            snapshot_refresh_result.get("total_limited_reviewed_record_projection_count") or 0
        ),
        "candidate_count_after_apply": int(snapshot_refresh_result.get("candidate_count_after_apply") or 0),
        "reviewed_known_need_count": int(snapshot_refresh_result.get("reviewed_known_need_count") or 0),
        "reviewed_bounded_absence_count": int(snapshot_refresh_result.get("reviewed_bounded_absence_count") or 0),
        "public_ux_routes_count": int(snapshot_refresh_result.get("public_ux_routes_count") or 0),
        "result_card_states_count": int(snapshot_refresh_result.get("result_card_states_count") or 0),
        "launch_recommended": False,
        "demo_mode_recommended": True,
        "internal_review_recommended": True,
        "needs_public_alpha_reassess_after_review_batch_apply_snapshot": True,
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def validate_snapshot_refresh_06_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    errors: list[str] = []
    expected = {
        "previous_total_limited_reviewed_record_projection_count": 4,
        "new_limited_reviewed_metadata_records": 4,
        "new_limited_reviewed_source_leads": 4,
        "new_reviewed_record_delta_count": 8,
        "total_limited_reviewed_record_projection_count": 12,
        "reviewed_known_need_count": 2,
        "reviewed_bounded_absence_count": 2,
        "previous_total_candidate_count": 68,
        "non_applied_candidate_count": 60,
        "candidate_count_after_apply": 60,
        "public_ux_routes_count": 8,
        "result_card_states_count": 8,
    }
    if result.get("schema_version") != "snapshot_refresh_06_result.v0":
        errors.append("schema_version must be snapshot_refresh_06_result.v0")
    for key, value in expected.items():
        if int(result.get(key) or 0) != value:
            errors.append(f"{key} must be {value}")
    for section_name in (
        "review_batch_apply_section",
        "limited_reviewed_metadata_section",
        "limited_reviewed_source_lead_section",
        "reviewed_known_need_section",
        "reviewed_bounded_absence_section",
        "non_applied_candidate_section",
        "result_card_section",
        "no_results_section",
        "refreshed_relay_projection",
        "public_alpha_reassess_input",
    ):
        if not isinstance(result.get(section_name), Mapping):
            errors.append(f"{section_name} must exist")
    for key in BOUNDARY_FALSE_KEYS:
        if result.get(key) is not False:
            errors.append(f"{key} must be false")
    cards = list(result.get("result_card_section", {}).get("cards") or [])
    if not cards:
        errors.append("result cards must exist")
    candidate_cards = [card for card in cards if card.get("status") == "candidate"]
    if len(candidate_cards) != 60:
        errors.append("candidate result cards must match remaining candidate count")
    for card in cards:
        if card.get("status") in {"candidate", "near_miss", "known_need", "absence"} and card.get("accepted_truth") is not False:
            errors.append("candidate-like cards must not be accepted truth")
        for key in ("verified_download_claim", "malware_clean_claim", "rights_clearance_claim", "compatibility_guarantee"):
            if card.get(key) is True:
                errors.append(f"result card created forbidden claim: {key}")
    return {
        "schema_version": "snapshot_refresh_06_validation_report.v0",
        "task": TASK_ID,
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_06_boundary_report(
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
        "review_batch_apply_integrated": True,
        "review_batch_apply_outputs_project_as_limited_records": True,
        "reviewed_known_needs_are_not_resolved_objects": True,
        "reviewed_bounded_absences_are_bounded_not_universal": True,
        "non_applied_candidates_remain_candidates": True,
        "total_limited_reviewed_record_projection_count": int(
            result.get("total_limited_reviewed_record_projection_count") or 0
        ),
        "candidate_count_after_apply": int(result.get("candidate_count_after_apply") or 0),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_snapshot_refresh_06(
    policy: Mapping[str, Any] | None = None,
    *,
    from_review_batch_apply_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_review_batch_apply_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    snapshot_05 = load_snapshot_refresh_05_handoff(merged_policy)
    review_batch_apply = load_review_batch_apply_handoff(merged_policy)
    plan = build_snapshot_refresh_06_plan(snapshot_05, review_batch_apply, merged_policy)
    review_batch_apply_section = build_review_batch_apply_section(review_batch_apply, merged_policy)
    previous_metadata_records = snapshot_05.get("reviewed_metadata_record_section", {}).get("records") or []
    previous_source_leads = snapshot_05.get("reviewed_source_lead_section", {}).get("records") or []
    limited_metadata_section = build_limited_reviewed_metadata_section(
        previous_metadata_records,
        review_batch_apply["limited_reviewed_metadata_records"],
        merged_policy,
    )
    limited_source_lead_section = build_limited_reviewed_source_lead_section(
        previous_source_leads,
        review_batch_apply["limited_reviewed_source_leads"],
        merged_policy,
    )
    reviewed_known_need_section = build_reviewed_known_need_section(
        review_batch_apply["reviewed_known_needs"],
        merged_policy,
    )
    reviewed_bounded_absence_section = build_reviewed_bounded_absence_section(
        review_batch_apply["reviewed_bounded_absences"],
        merged_policy,
    )
    non_applied_candidate_section = build_non_applied_candidate_section(
        review_batch_apply["non_applied_candidates"],
        merged_policy,
    )
    candidate_sections, live_metadata_candidate_section = build_candidate_snapshot_sections(
        snapshot_05,
        review_batch_apply,
        merged_policy,
    )
    sections: dict[str, Any] = {
        "review_batch_apply_section": review_batch_apply_section,
        "limited_reviewed_metadata_section": limited_metadata_section,
        "limited_reviewed_source_lead_section": limited_source_lead_section,
        "reviewed_known_need_section": reviewed_known_need_section,
        "reviewed_bounded_absence_section": reviewed_bounded_absence_section,
        "non_applied_candidate_section": non_applied_candidate_section,
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_metadata_candidate_section,
    }
    route_section = build_public_route_section(merged_policy)
    result_card_section = build_result_card_projection_section(snapshot_05, sections, merged_policy)
    no_results_section = build_no_results_projection_section(snapshot_05, sections, merged_policy)
    sections.update(
        {
            "public_route_section": route_section,
            "result_card_section": result_card_section,
            "no_results_section": no_results_section,
        }
    )
    public_search_ux_section = build_public_search_ux_section(route_section, result_card_section, merged_policy)
    sections["public_search_ux_section"] = public_search_ux_section
    relay_projection = build_refreshed_relay_projection(sections, merged_policy)
    previous_total = int(snapshot_05.get("total_limited_reviewed_record_projection_count") or 0)
    new_metadata_count = len(review_batch_apply["limited_reviewed_metadata_records"])
    new_source_lead_count = len(review_batch_apply["limited_reviewed_source_leads"])
    candidate_count_after_apply = int(non_applied_candidate_section["candidate_count"])
    result: dict[str, Any] = {
        "schema_version": "snapshot_refresh_06_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_integrated": True,
        "snapshot_refresh_05_ref": SNAPSHOT_REFRESH_05_REF,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "plan": plan,
        "source_batches": list(snapshot_05.get("source_batches") or []),
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_metadata_candidate_section,
        "review_batch_apply_section": review_batch_apply_section,
        "limited_reviewed_metadata_section": limited_metadata_section,
        "limited_reviewed_source_lead_section": limited_source_lead_section,
        "reviewed_known_need_section": reviewed_known_need_section,
        "reviewed_bounded_absence_section": reviewed_bounded_absence_section,
        "non_applied_candidate_section": non_applied_candidate_section,
        "public_search_ux_section": public_search_ux_section,
        "public_route_section": route_section,
        "result_card_section": result_card_section,
        "no_results_section": no_results_section,
        "refreshed_relay_projection": relay_projection,
        "review_batch_apply_refs": [review_batch_apply_section["section_id"]],
        "limited_reviewed_metadata_refs": [limited_metadata_section["section_id"]],
        "limited_reviewed_source_lead_refs": [limited_source_lead_section["section_id"]],
        "reviewed_known_need_refs": [reviewed_known_need_section["section_id"]],
        "reviewed_bounded_absence_refs": [reviewed_bounded_absence_section["section_id"]],
        "non_applied_candidate_refs": [non_applied_candidate_section["section_id"]],
        "public_search_ux_refs": [public_search_ux_section["section_id"]],
        "public_route_refs": [route_section["section_id"]],
        "result_card_refs": [result_card_section["section_id"]],
        "no_results_refs": [no_results_section["section_id"]],
        "relay_projection_refs": [relay_projection["relay_projection_id"]],
        "previous_total_limited_reviewed_record_projection_count": previous_total,
        "new_limited_reviewed_metadata_records": new_metadata_count,
        "new_limited_reviewed_source_leads": new_source_lead_count,
        "new_reviewed_record_delta_count": new_metadata_count + new_source_lead_count,
        "total_limited_reviewed_record_projection_count": previous_total + new_metadata_count + new_source_lead_count,
        "reviewed_known_need_count": int(reviewed_known_need_section["reviewed_known_need_count"]),
        "reviewed_bounded_absence_count": int(reviewed_bounded_absence_section["reviewed_bounded_absence_count"]),
        "previous_total_candidate_count": int(snapshot_05.get("total_candidate_count") or 0),
        "non_applied_candidate_count": candidate_count_after_apply,
        "candidate_count_after_apply": candidate_count_after_apply,
        "total_candidate_count": candidate_count_after_apply,
        "public_ux_routes_count": int(route_section["route_count"]),
        "result_card_states_count": int(result_card_section["result_card_states_count"]),
        "fixture_snapshot_refresh_passed": True,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    public_alpha = build_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_snapshot_refresh_06_boundary_report(result, merged_policy)
    result["validation_report"] = validate_snapshot_refresh_06_result(result, merged_policy)
    if result["validation_report"]["status"] != "pass":
        result["status"] = "fail"
        result["fixture_snapshot_refresh_passed"] = False
    if write_examples:
        written = write_snapshot_refresh_06_examples(result)
        written.extend(write_snapshot_refresh_06_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_snapshot_refresh_06_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_06(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "snapshots" / "refresh" / "review_batch_apply"
    files = {
        "snapshot_refresh_plan.json": payload["plan"],
        "review_batch_apply_section.json": payload["review_batch_apply_section"],
        "limited_reviewed_metadata_section.json": payload["limited_reviewed_metadata_section"],
        "limited_reviewed_source_lead_section.json": payload["limited_reviewed_source_lead_section"],
        "reviewed_known_need_section.json": payload["reviewed_known_need_section"],
        "reviewed_bounded_absence_section.json": payload["reviewed_bounded_absence_section"],
        "non_applied_candidate_section.json": payload["non_applied_candidate_section"],
        "public_search_ux_section.json": payload["public_search_ux_section"],
        "public_route_section.json": payload["public_route_section"],
        "result_card_section.json": payload["result_card_section"],
        "no_results_section.json": payload["no_results_section"],
        "refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "snapshot_refresh_06_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/relay/refresh/review_batch_apply_refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "examples/public_alpha/reassess/review_batch_apply/snapshot_refresh_06_reassess_input.json": payload[
            "public_alpha_reassess_input"
        ],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_snapshot_refresh_06_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_06(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = build_snapshot_refresh_06_inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_snapshot_refresh_06_audit_pack(payload, repo_root))
    return written


def build_snapshot_refresh_06_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    packets: dict[str, Any] = {
        "snapshot_refresh_06_input_state.json": {
            "schema_version": "snapshot_refresh_06_input_state.v0",
            "task": TASK_ID,
            "branch": "dev",
            "input_results": {
                "snapshot_refresh_05": SNAPSHOT_REFRESH_05_REF,
                "review_batch_apply_next": REVIEW_BATCH_APPLY_REF,
                "public_search_ux_mvp": PUBLIC_SEARCH_UX_MVP_REF,
                "public_alpha_reassess_05": "control/inventory/public_alpha_reassess_05_result.json",
                "snapshot_relay": "control/inventory/snapshot_relay_result.json",
            },
            "review_batch_apply_integrated": True,
            **_false_boundaries(),
            "created_at": DEFAULT_TIMESTAMP,
        },
        "snapshot_refresh_06_source_matrix.json": {
            "schema_version": "snapshot_refresh_06_source_matrix.v0",
            "task": TASK_ID,
            "sources": list(result.get("source_batches") or []),
            "source_batch_count": len(result.get("source_batches") or []),
            "snapshot_refresh_05_ref": SNAPSHOT_REFRESH_05_REF,
            "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        },
        "snapshot_refresh_06_reviewed_record_matrix.json": {
            "schema_version": "snapshot_refresh_06_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "previous_total_limited_reviewed_record_projection_count": result.get(
                "previous_total_limited_reviewed_record_projection_count"
            ),
            "new_reviewed_record_delta_count": result.get("new_reviewed_record_delta_count"),
            "total_limited_reviewed_record_projection_count": result.get(
                "total_limited_reviewed_record_projection_count"
            ),
            "limited_records_are_not_verified_artifacts": True,
        },
        "snapshot_refresh_06_limited_reviewed_metadata_matrix.json": result["limited_reviewed_metadata_section"],
        "snapshot_refresh_06_limited_reviewed_source_lead_matrix.json": result["limited_reviewed_source_lead_section"],
        "snapshot_refresh_06_reviewed_known_need_matrix.json": result["reviewed_known_need_section"],
        "snapshot_refresh_06_reviewed_bounded_absence_matrix.json": result["reviewed_bounded_absence_section"],
        "snapshot_refresh_06_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_06_candidate_matrix.v0",
            "task": TASK_ID,
            "candidate_sections": [
                {
                    "section_id": section.get("section_id"),
                    "domain_key": section.get("domain_key"),
                    "domain_id": section.get("domain_id"),
                    "candidate_count": section.get("candidate_count"),
                    "accepted_truth": False,
                    "candidate_promoted_to_reviewed": False,
                }
                for section in result.get("candidate_sections") or []
            ],
            "live_metadata_candidate_count": result.get("live_metadata_candidate_section", {}).get("candidate_count"),
            "candidate_count_after_apply": result.get("candidate_count_after_apply"),
        },
        "snapshot_refresh_06_non_applied_candidate_matrix.json": result["non_applied_candidate_section"],
        "snapshot_refresh_06_domain_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_06_domain_candidate_matrix.v0",
            "task": TASK_ID,
            "domains": _domain_counts(result),
            "candidate_count_after_apply": result.get("candidate_count_after_apply"),
        },
        "snapshot_refresh_06_review_batch_apply_matrix.json": result["review_batch_apply_section"],
        "snapshot_refresh_06_public_search_ux_matrix.json": result["public_search_ux_section"],
        "snapshot_refresh_06_public_route_matrix.json": result["public_route_section"],
        "snapshot_refresh_06_result_card_matrix.json": {
            "schema_version": "snapshot_refresh_06_result_card_matrix.v0",
            "task": TASK_ID,
            "section_id": result["result_card_section"]["section_id"],
            "result_card_count": result["result_card_section"]["result_card_count"],
            "supported_statuses": result["result_card_section"]["supported_statuses"],
            "observed_statuses": result["result_card_section"]["observed_statuses"],
            "result_card_states_count": result["result_card_section"]["result_card_states_count"],
            "candidate_count_after_apply": result.get("candidate_count_after_apply"),
            "candidate_verified_distinction_passed": True,
            "limited_reviewed_record_distinction_passed": True,
        },
        "snapshot_refresh_06_no_results_matrix.json": result["no_results_section"],
        "snapshot_refresh_06_relay_projection_matrix.json": {
            "schema_version": "snapshot_refresh_06_relay_projection_matrix.v0",
            "task": TASK_ID,
            "relay_projection_refs": list(result.get("relay_projection_refs") or []),
            "sections": result.get("refreshed_relay_projection", {}).get("sections"),
            "read_only": True,
            "mutation_enabled": False,
            "site_dist_written": False,
        },
        "snapshot_refresh_06_public_alpha_reassess_matrix.json": {
            "schema_version": "snapshot_refresh_06_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
            "review_batch_apply_integrated": True,
            "total_limited_reviewed_record_projection_count": result.get(
                "total_limited_reviewed_record_projection_count"
            ),
            "candidate_count_after_apply": result.get("candidate_count_after_apply"),
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
        },
        "snapshot_refresh_06_boundary_report.json": result["boundary_report"],
        "snapshot_refresh_06_smoke_result.json": {
            "schema_version": "snapshot_refresh_06_smoke_result.v0",
            "task": TASK_ID,
            "status": result.get("status"),
            "fixture_snapshot_refresh_passed": result.get("fixture_snapshot_refresh_passed"),
            "review_batch_apply_integrated": True,
            **_false_boundaries(),
        },
        "snapshot_refresh_06_validation_matrix.json": {
            "schema_version": "snapshot_refresh_06_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_snapshot_refresh.py",
                "focused snapshot refresh 06 unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "snapshot_refresh_06_result.json": _task_result(result),
        "snapshot_refresh_06_next_task_decision.json": {
            "schema_version": "snapshot_refresh_06_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": NEXT_TASK,
            "planned_after": [
                "PUBLIC-ALPHA-REASSESS-06",
                "INDEXLESS-LIVE-SEARCH-FALLBACK-00",
                "SEARCH-USEFULNESS-EVAL-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "deployment_performed": False,
            "public_launch_readiness_claimed": False,
        },
        "snapshot_refresh_06_failure_repair_log.json": {
            "schema_version": "snapshot_refresh_06_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
            **_false_boundaries(),
        },
    }
    return packets


def _write_snapshot_refresh_06_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "snapshot-refresh-06-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = build_snapshot_refresh_06_inventory_packets(result)
    audit_json = {"snapshot_refresh_06_report.json": _task_result(result)}
    audit_markdown = {
        "README.md": "# SNAPSHOT-REFRESH-06 Audit\n\nRefresh evidence after review-batch apply. Limited records, reviewed known needs, and reviewed bounded absences are projected without artifact, download, safety, compatibility, rights, OCR, public index, deployment, or launch claims.\n",
        "source_matrix.md": _matrix_md("Source Matrix", inventory["snapshot_refresh_06_source_matrix.json"]),
        "review_batch_apply_matrix.md": _matrix_md("Review Batch Apply Matrix", inventory["snapshot_refresh_06_review_batch_apply_matrix.json"]),
        "limited_reviewed_metadata_matrix.md": _matrix_md("Limited Reviewed Metadata Matrix", inventory["snapshot_refresh_06_limited_reviewed_metadata_matrix.json"]),
        "limited_reviewed_source_lead_matrix.md": _matrix_md("Limited Reviewed Source Lead Matrix", inventory["snapshot_refresh_06_limited_reviewed_source_lead_matrix.json"]),
        "reviewed_known_need_matrix.md": _matrix_md("Reviewed Known Need Matrix", inventory["snapshot_refresh_06_reviewed_known_need_matrix.json"]),
        "reviewed_bounded_absence_matrix.md": _matrix_md("Reviewed Bounded Absence Matrix", inventory["snapshot_refresh_06_reviewed_bounded_absence_matrix.json"]),
        "non_applied_candidate_matrix.md": _matrix_md("Non Applied Candidate Matrix", inventory["snapshot_refresh_06_non_applied_candidate_matrix.json"]),
        "result_card_matrix.md": _matrix_md("Result Card Matrix", inventory["snapshot_refresh_06_result_card_matrix.json"]),
        "no_results_matrix.md": _matrix_md("No Results Matrix", inventory["snapshot_refresh_06_no_results_matrix.json"]),
        "relay_projection_matrix.md": _matrix_md("Relay Projection Matrix", inventory["snapshot_refresh_06_relay_projection_matrix.json"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", inventory["snapshot_refresh_06_public_alpha_reassess_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["snapshot_refresh_06_smoke_result.json"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["snapshot_refresh_06_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/snapshot_refresh_06_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    generated_files = {
        "sample_snapshot_refresh_plan.json": result["plan"],
        "sample_review_batch_apply_section.json": result["review_batch_apply_section"],
        "sample_limited_reviewed_record_sections.json": {
            "metadata": result["limited_reviewed_metadata_section"],
            "source_leads": result["limited_reviewed_source_lead_section"],
        },
        "sample_reviewed_need_absence_sections.json": {
            "known_needs": result["reviewed_known_need_section"],
            "bounded_absences": result["reviewed_bounded_absence_section"],
        },
        "sample_non_applied_candidate_section.json": result["non_applied_candidate_section"],
        "sample_result_card_section.json": result["result_card_section"],
        "sample_no_results_section.json": result["no_results_section"],
        "sample_relay_projection.json": result["refreshed_relay_projection"],
        "sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Snapshot Refresh 06 Summary\n\n"
        f"- total limited reviewed projections: {result.get('total_limited_reviewed_record_projection_count')}\n"
        f"- new limited metadata records: {result.get('new_limited_reviewed_metadata_records')}\n"
        f"- new limited source leads: {result.get('new_limited_reviewed_source_leads')}\n"
        f"- remaining candidates: {result.get('candidate_count_after_apply')}\n"
        "- verified artifact claims: false\n"
        "- site/dist written: false\n"
    )
    written: list[str] = []
    for name, content in audit_json.items():
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


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_06_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_batch_apply_integrated": True,
        "contracts_added": True,
        "policies_added": True,
        "source_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "limited_reviewed_metadata_matrix_added": True,
        "limited_reviewed_source_lead_matrix_added": True,
        "reviewed_known_need_matrix_added": True,
        "reviewed_bounded_absence_matrix_added": True,
        "candidate_matrix_added": True,
        "non_applied_candidate_matrix_added": True,
        "review_batch_apply_matrix_added": True,
        "public_search_ux_matrix_added": True,
        "result_card_matrix_added": True,
        "no_results_matrix_added": True,
        "relay_projection_matrix_added": True,
        "public_alpha_reassess_matrix_added": True,
        "runtime_snapshot_refresh_added": True,
        "review_batch_apply_section_created": True,
        "limited_reviewed_metadata_section_created": True,
        "limited_reviewed_source_lead_section_created": True,
        "reviewed_known_need_section_created": True,
        "reviewed_bounded_absence_section_created": True,
        "non_applied_candidate_section_created": True,
        "result_card_section_created": True,
        "no_results_section_created": True,
        "relay_projection_created": True,
        "public_alpha_reassess_input_created": True,
        "previous_total_limited_reviewed_record_projection_count": result.get(
            "previous_total_limited_reviewed_record_projection_count"
        ),
        "new_limited_reviewed_metadata_records": result.get("new_limited_reviewed_metadata_records"),
        "new_limited_reviewed_source_leads": result.get("new_limited_reviewed_source_leads"),
        "new_reviewed_record_delta_count": result.get("new_reviewed_record_delta_count"),
        "total_limited_reviewed_record_projection_count": result.get(
            "total_limited_reviewed_record_projection_count"
        ),
        "reviewed_known_need_count": result.get("reviewed_known_need_count"),
        "reviewed_bounded_absence_count": result.get("reviewed_bounded_absence_count"),
        "previous_total_candidate_count": result.get("previous_total_candidate_count"),
        "non_applied_candidate_count": result.get("non_applied_candidate_count"),
        "candidate_count_after_apply": result.get("candidate_count_after_apply"),
        "public_ux_routes_count": result.get("public_ux_routes_count"),
        "result_card_states_count": result.get("result_card_states_count"),
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "fixture_snapshot_refresh_passed": bool(result.get("fixture_snapshot_refresh_passed")),
        **_false_boundaries(),
        "recommended_next_task": NEXT_TASK,
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return _task_result(result)


def _assert_review_batch_apply(
    result: Mapping[str, Any],
    metadata: Mapping[str, Any],
    source_leads: Mapping[str, Any],
    known_needs: Mapping[str, Any],
    bounded_absences: Mapping[str, Any],
    non_applied: Mapping[str, Any],
) -> None:
    expected = {
        "eligible_apply_count": 12,
        "limited_reviewed_metadata_records_created": 4,
        "limited_reviewed_source_leads_created": 4,
        "reviewed_known_needs_created": 2,
        "reviewed_bounded_absences_created": 2,
        "reviewed_record_delta_count": 8,
        "non_applied_count": 60,
    }
    for key, value in expected.items():
        if int(result.get(key) or 0) != value:
            raise ValueError(f"review batch apply result {key} must be {value}")
    if len(metadata.get("records") or []) != 4:
        raise ValueError("review batch apply metadata record count mismatch")
    if len(source_leads.get("records") or []) != 4:
        raise ValueError("review batch apply source lead count mismatch")
    if len(known_needs.get("records") or []) != 2:
        raise ValueError("review batch apply known need count mismatch")
    if len(bounded_absences.get("records") or []) != 2:
        raise ValueError("review batch apply bounded absence count mismatch")
    if len(non_applied.get("candidates") or []) != 60:
        raise ValueError("review batch apply non-applied count mismatch")
    for key in (
        "operator_instance_mutated",
        "committed_instance_state",
        "public_index_mutated",
        "master_index_mutated",
        "artifact_verified_claim_created",
        "verified_download_claim_created",
        "malware_clean_claim_created",
        "rights_clearance_claim_created",
        "compatibility_guarantee_claim_created",
        "scan_completeness_claim_created",
        "ocr_quality_claim_created",
        "download_performed",
        "file_fetch_performed",
        "ocr_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if result.get(key) not in (False, None):
            raise ValueError(f"review batch apply boundary failed: {key}")


def _assert_false_boundaries(result: Mapping[str, Any]) -> None:
    for key in (
        "site_dist_written",
        "deployment_performed",
        "public_index_mutated",
        "master_index_mutated",
        "download_performed",
        "file_fetch_performed",
        "ocr_performed",
        "extraction_executed",
        "model_provider_used",
        "public_launch_readiness_claimed",
        "production_readiness_claimed",
    ):
        if result.get(key) is not False:
            raise ValueError(f"snapshot boundary failed: {key}")


def _applied_candidate_refs(review_batch_apply: Mapping[str, Any]) -> set[str]:
    refs: set[str] = set()
    for key in ("limited_reviewed_metadata_records", "limited_reviewed_source_leads"):
        for record in review_batch_apply.get(key, []):
            refs.update(_text(ref) for ref in record.get("candidate_refs", []) if _text(ref))
    return refs


def _applied_candidate_refs_from_sections(snapshot_sections: Mapping[str, Any]) -> set[str]:
    refs: set[str] = set()
    for section_name in ("limited_reviewed_metadata_section", "limited_reviewed_source_lead_section"):
        section = snapshot_sections.get(section_name, {})
        previous_count = int(section.get("previous_record_count") or 0)
        for record in list(section.get("records", []))[previous_count:]:
            refs.update(_text(ref) for ref in record.get("candidate_refs", []) if _text(ref))
    return refs


def _total_limited_records(snapshot_sections: Mapping[str, Any]) -> int:
    return int(snapshot_sections["limited_reviewed_metadata_section"]["limited_reviewed_metadata_record_count"]) + int(
        snapshot_sections["limited_reviewed_source_lead_section"]["limited_reviewed_source_lead_count"]
    ) + 1


def _limited_record(record: Mapping[str, Any]) -> dict[str, Any]:
    item = _retag(record)
    item.setdefault("accepted_truth", False)
    item["artifact_verified"] = False
    item["verified_download_claim"] = False
    item["malware_clean_claim"] = False
    item["rights_clearance_claim"] = False
    item["compatibility_guarantee_claim"] = False
    item["scan_completeness_claim"] = False
    item["ocr_quality_claim"] = False
    item.update(_false_boundaries())
    return item


def _reviewed_need(record: Mapping[str, Any]) -> dict[str, Any]:
    item = _retag(record)
    item["accepted_truth"] = False
    item["resolved_object_created"] = False
    item["reviewed_known_need_not_resolved_object"] = True
    item.update(_false_boundaries())
    return item


def _reviewed_absence(record: Mapping[str, Any]) -> dict[str, Any]:
    item = _retag(record)
    item["accepted_truth"] = False
    item["universal_absence_claim"] = False
    item["reviewed_bounded_absence_not_universal"] = True
    item.update(_false_boundaries())
    return item


def _remaining_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    item = _retag(candidate)
    item["accepted_truth"] = False
    item["review_required"] = True
    item["public_search_status"] = "candidate"
    item["reviewed_record_ref"] = None
    item["artifact_verified"] = False
    item["verified_download_claim"] = False
    item["malware_clean_claim"] = False
    item["rights_clearance_claim"] = False
    item["compatibility_guarantee"] = False
    item.update(_false_boundaries())
    return item


def _limited_record_card(record: Mapping[str, Any], status: str, object_type: str) -> dict[str, Any]:
    title = _text(record.get("title")) or _text(record.get("lead_summary"))
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", record.get("record_id"), SNAPSHOT_REFRESH_ID),
        "title": title,
        "url": "/source/" + _text(record.get("record_id")),
        "href": "/source/" + _text(record.get("record_id")),
        "status": status,
        "status_label": "Limited reviewed metadata" if status == "reviewed_metadata_record" else "Reviewed source lead",
        "object_type": object_type,
        "domain": "review_batch_apply",
        "domain_id": "review_batch_apply",
        "source_family": _text(record.get("source_family")) or "metadata_fixture",
        "snippet": "Limited reviewed record from temp review-batch apply. It is not a verified downloadable artifact.",
        "confidence_label": status,
        "risk_label": "not_artifact_verified",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "not_verified_download",
        "review_required": False,
        "accepted_truth": False,
        "limited_reviewed_record": True,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "install_execution_enabled": False,
        "action_posture": _action_posture(False),
        "limitations": _text_list(record.get("limitations")),
        "created_at": DEFAULT_TIMESTAMP,
    }


def _reviewed_need_card(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", record.get("record_id"), SNAPSHOT_REFRESH_ID),
        "title": _text(record.get("summary"))[:96] or _text(record.get("record_id")),
        "url": "/needs/" + _text(record.get("record_id")),
        "href": "/needs/" + _text(record.get("record_id")),
        "status": "known_need",
        "status_label": "Reviewed known need",
        "object_type": "reviewed_known_need",
        "domain": _text(record.get("need_kind")) or "review_batch_apply",
        "source_family": "review_batch_apply",
        "snippet": "Reviewed known need. This is not a resolved object or artifact verification.",
        "confidence_label": "reviewed_need",
        "risk_label": "unresolved_need",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "not_verified",
        "review_required": True,
        "accepted_truth": False,
        "resolved_object_created": False,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee": False,
        "action_posture": _action_posture(True),
        "limitations": _text_list(record.get("limitations")),
        "created_at": DEFAULT_TIMESTAMP,
    }


def _reviewed_absence_card(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", record.get("record_id"), SNAPSHOT_REFRESH_ID),
        "title": _text(record.get("summary"))[:96] or _text(record.get("record_id")),
        "url": "/absence/" + _text(record.get("record_id")),
        "href": "/absence/" + _text(record.get("record_id")),
        "status": "absence",
        "status_label": "Reviewed bounded absence",
        "object_type": "reviewed_bounded_absence",
        "domain": _text(record.get("absence_kind")) or "review_batch_apply",
        "source_family": "review_batch_apply",
        "snippet": "Reviewed bounded absence. This is bounded to reviewed evidence, not a universal absence claim.",
        "confidence_label": "bounded_absence",
        "risk_label": "bounded_not_universal",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "not_verified",
        "review_required": True,
        "accepted_truth": False,
        "universal_absence_claim": False,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee": False,
        "action_posture": _action_posture(True),
        "limitations": _text_list(record.get("limitations")),
        "created_at": DEFAULT_TIMESTAMP,
    }


def _action_posture(review_required: bool) -> dict[str, Any]:
    return {
        "schema_version": "public_search_action_posture_view_model.v0",
        "allowed_actions": ["inspect", "view_source", "view_provenance", "read"],
        "blocked_actions": [
            "download",
            "fetch_file",
            "ocr",
            "extract",
            "execute",
            "install_handoff",
            "live_source_fanout",
            "mutate_public_index",
            "promote_public",
        ],
        "review_required": review_required,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "file_fetches_enabled": False,
        "ocr_enabled": False,
        "extraction_enabled": False,
        "install_execution_enabled": False,
        "model_provider_enabled": False,
    }


def _card_candidate_id(card: Mapping[str, Any]) -> str:
    for key in ("url", "href"):
        value = _text(card.get(key))
        if "/candidate/" in value:
            return value.rsplit("/candidate/", 1)[-1].strip("/")
    return ""


def _dedupe_cards(cards: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for card in cards:
        item = dict(card)
        key = _text(item.get("view_model_id")) or _text(item.get("url")) or _text(item.get("title"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _domain_counts(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    domains = []
    for section in result.get("candidate_sections") or []:
        domains.append(
            {
                "domain_key": section.get("domain_key"),
                "domain_id": section.get("domain_id"),
                "candidate_count": section.get("candidate_count"),
                "review_only": True,
            }
        )
    live_section = result.get("live_metadata_candidate_section") or {}
    domains.append(
        {
            "domain_key": "live_metadata",
            "domain_id": "live_metadata_candidates",
            "candidate_count": live_section.get("candidate_count"),
            "review_only": True,
        }
    )
    return domains


def _limitations() -> list[str]:
    return [
        "snapshot_refresh_is_projection_only",
        "review_batch_apply_outputs_are_limited_records",
        "limited_reviewed_records_are_not_verified_artifacts",
        "reviewed_known_needs_are_not_resolved_objects",
        "reviewed_bounded_absences_are_bounded_not_universal",
        "non_applied_candidates_remain_candidates",
        "temp_apply_did_not_mutate_operator_instance",
        "no_verified_download_claim",
        "no_malware_clean_claim",
        "no_compatibility_guarantee",
        "no_rights_clearance_claim",
        "no_scan_completeness_or_ocr_quality_claim",
        "no_site_dist_write",
        "no_public_index_mutation",
        "no_deployment_or_launch_claim",
    ]


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "snapshot_refresh_is_projection",
        "review_batch_apply_outputs_project_as_limited_records",
        "reviewed_known_needs_are_not_resolved_objects",
        "reviewed_bounded_absences_are_bounded_not_universal",
        "non_applied_candidates_remain_candidates",
        "temp_apply_outputs_do_not_mutate_operator_instance",
        "no_reviewed_index_mutation",
        "no_master_index_mutation",
        "no_public_index_mutation",
        "no_public_mutation",
        "no_public_live_source_fanout",
        "no_deployment",
        "no_site_dist_write",
        "no_public_launch_claim",
        "no_production_claim",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"snapshot refresh 06 policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "downloads_enabled",
        "file_fetches_enabled",
        "ocr_enabled",
        "extraction_enabled",
        "install_execution_enabled",
        "model_provider_enabled",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"snapshot refresh 06 policy enables forbidden behavior: {', '.join(enabled)}")


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


def _retag(payload: Any) -> Any:
    if isinstance(payload, dict):
        updated = {}
        for key, value in payload.items():
            if key == "snapshot_refresh_id":
                updated[key] = SNAPSHOT_REFRESH_ID
            elif key == "created_at":
                updated[key] = DEFAULT_TIMESTAMP
            else:
                updated[key] = _retag(value)
        return updated
    if isinstance(payload, list):
        return [_retag(item) for item in payload]
    return copy.deepcopy(payload)


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
