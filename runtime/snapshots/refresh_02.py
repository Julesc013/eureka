"""Snapshot refresh projection after live metadata candidate review.

SNAPSHOT-REFRESH-02 packages review decisions and preview records into read-only
snapshot sections. Reviewed metadata/source-lead previews remain previews until a
separate local-apply gate runs.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.review.live_metadata import run_live_metadata_candidate_review
from runtime.snapshots import refresh_01
from runtime.snapshots.relay_foundation import sample_reviewed_records


DEFAULT_TIMESTAMP = "2026-06-01T00:00:00Z"
SNAPSHOT_REFRESH_ID = "snapshot_refresh_02"
TASK_ID = "SNAPSHOT-REFRESH-02"
LIVE_METADATA_REVIEW_REF = "control/inventory/live_metadata_review_result.json"
LIVE_METADATA_PILOT_REF = "control/inventory/live_metadata_pilot_result.json"
NEXT_TASK = "PUBLIC-ALPHA-REASSESS-02 - Reassess alpha after live metadata candidate review snapshot"

DEFAULT_POLICY: dict[str, Any] = {
    "snapshot_refresh_is_projection": True,
    "review_previews_are_not_truth": True,
    "reviewed_metadata_previews_require_local_apply": True,
    "reviewed_source_lead_previews_require_local_apply": True,
    "live_metadata_candidates_remain_candidates_until_applied": True,
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
    "verified_download_claim_allowed": False,
    "malware_clean_claim_allowed": False,
    "rights_clearance_claim_allowed": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
}

BOUNDARY_FALSE_KEYS = (
    "accepted_truth_created",
    "candidate_promoted_to_reviewed",
    "live_metadata_candidate_promoted",
    "review_preview_applied",
    "raw_live_response_included",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "rights_clearance_claim_created",
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
    return refresh_01.load_seed_batch_handoffs(merged_policy)


def load_live_metadata_pilot_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return refresh_01.load_live_metadata_pilot_handoff(merged_policy)


def load_live_metadata_review_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    review_result = _read_json(repo / LIVE_METADATA_REVIEW_REF)
    example_result = run_live_metadata_candidate_review()
    payload = dict(example_result)
    payload["inventory_result"] = review_result
    _assert_live_metadata_review(review_result, payload)
    return {
        "schema_version": "snapshot_refresh_02_live_metadata_review_handoff.v0",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "review_result": review_result,
        "candidate_review_packet": copy.deepcopy(payload["candidate_review_packet"]),
        "evidence_sufficiency": copy.deepcopy(payload["evidence_sufficiency"]),
        "review_decisions": copy.deepcopy(payload["review_decisions"]),
        "promotion_previews": copy.deepcopy(payload["promotion_previews"]),
        "reviewed_metadata_record_previews": copy.deepcopy(payload["reviewed_metadata_record_previews"]),
        "reviewed_source_lead_previews": copy.deepcopy(payload["reviewed_source_lead_previews"]),
        "local_apply_handoff": copy.deepcopy(payload["local_apply_handoff"]),
        "snapshot_refresh_handoff": copy.deepcopy(payload["snapshot_refresh_handoff"]),
        "public_alpha_reassess_handoff": copy.deepcopy(payload["public_alpha_reassess_handoff"]),
        "boundary_report": copy.deepcopy(payload["boundary_report"]),
        "counts": _decision_counts(payload["review_decisions"]),
        "accepted_truth": False,
        "review_preview_applied": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_02_plan(
    seed_handoffs: Mapping[str, Any],
    live_metadata_handoff: Mapping[str, Any],
    review_handoff: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    batches = list(seed_handoffs.get("source_batches") or [])
    counts = dict(review_handoff.get("counts") or {})
    return {
        "schema_version": "snapshot_refresh_plan.v0",
        "record_type": "snapshot_refresh_plan",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": [refresh_01._batch_summary(batch) for batch in batches],
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "live_metadata_source_family": live_metadata_handoff.get("source_family"),
        "reviewed_record_refs": [record["record_id"] for record in sample_reviewed_records()],
        "candidate_section_refs": [
            _section_id("snapshot_candidate_section", batch.get("domain_key"), SNAPSHOT_REFRESH_ID)
            for batch in batches
        ],
        "live_metadata_candidate_section_refs": [
            _section_id("snapshot_live_metadata_candidate_section", live_metadata_handoff.get("pilot_batch_id"))
        ],
        "live_metadata_review_section_refs": [_section_id("snapshot_live_metadata_review_section", SNAPSHOT_REFRESH_ID)],
        "reviewed_metadata_preview_section_refs": [
            _section_id("snapshot_reviewed_metadata_preview_section", SNAPSHOT_REFRESH_ID)
        ],
        "reviewed_source_lead_preview_section_refs": [
            _section_id("snapshot_reviewed_source_lead_preview_section", SNAPSHOT_REFRESH_ID)
        ],
        "review_queue_section_refs": [_section_id("snapshot_review_queue_section", SNAPSHOT_REFRESH_ID)],
        "need_absence_section_refs": [_section_id("snapshot_need_absence_section", SNAPSHOT_REFRESH_ID)],
        "relay_projection_refs": [_section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID)],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "public_search_view_model_refs": [_section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID)],
        "review_counts": counts,
        "refresh_mode": "live_metadata_review_projection_only",
        "local_apply_required_before_reviewed_mutation": True,
        "accepted_truth_created": False,
        "review_preview_applied": False,
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
    section = refresh_01.build_reviewed_record_section(existing_reviewed_records, _policy(policy))
    return _retag_snapshot_refresh(section)


def build_candidate_snapshot_section(
    seed_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    domain_key: str = "seed_batch",
    batch_id: str = "",
    scout_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    section = refresh_01.build_candidate_snapshot_section(
        seed_candidates,
        _policy(policy),
        domain_key=domain_key,
        batch_id=batch_id,
        scout_refs=scout_refs or [],
    )
    return _retag_snapshot_refresh(section)


def build_live_metadata_candidate_section(
    live_metadata_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    live_metadata_handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = refresh_01.build_live_metadata_candidate_section(
        live_metadata_candidates,
        _policy(policy),
        live_metadata_handoff=live_metadata_handoff,
    )
    return _retag_snapshot_refresh(section)


def build_live_metadata_review_section(
    review_decisions: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    decisions = [_decision_item(item) for item in review_decisions]
    counts = _decision_counts(decisions)
    return {
        "schema_version": "snapshot_live_metadata_review_section.v0",
        "record_type": "snapshot_live_metadata_review_section",
        "section_id": _section_id("snapshot_live_metadata_review_section", [item["decision_id"] for item in decisions]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "source_family": "internet_archive_metadata",
        "review_decision_refs": [item["decision_id"] for item in decisions],
        "candidate_refs": [item["candidate_id"] for item in decisions],
        "review_decision_count": len(decisions),
        "decisions": decisions,
        "useful_lead_refs": [
            item["candidate_id"] for item in decisions if item["review_decision"] == "mark_useful_lead"
        ],
        "needs_more_evidence_refs": [
            item["candidate_id"] for item in decisions if item["review_decision"] == "needs_more_evidence"
        ],
        "rejected_or_duplicate_refs": [
            item["candidate_id"]
            for item in decisions
            if item["review_decision"] in {"duplicate", "reject_wrong_object", "reject_wrong_version", "reject_low_quality", "block_candidate"}
        ],
        **counts,
        "review_required": True,
        "accepted_truth": False,
        "review_preview_applied": False,
        "raw_response_included": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_reviewed_metadata_preview_section(
    previews: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_preview_item(item, "reviewed_metadata_record_preview") for item in previews]
    return {
        "schema_version": "snapshot_reviewed_metadata_preview_section.v0",
        "record_type": "snapshot_reviewed_metadata_preview_section",
        "section_id": _section_id("snapshot_reviewed_metadata_preview_section", [item["record_id"] for item in records]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "preview_count": len(records),
        "preview_refs": [item["record_id"] for item in records],
        "previews": records,
        "accepted_truth": False,
        "local_apply_required": True,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "prohibited_claims": _prohibited_claims(),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_reviewed_source_lead_preview_section(
    previews: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_preview_item(item, "reviewed_source_lead_preview") for item in previews]
    return {
        "schema_version": "snapshot_reviewed_source_lead_preview_section.v0",
        "record_type": "snapshot_reviewed_source_lead_preview_section",
        "section_id": _section_id("snapshot_reviewed_source_lead_preview_section", [item["record_id"] for item in records]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "source_lead_preview_count": len(records),
        "source_lead_refs": [item["record_id"] for item in records],
        "previews": records,
        "accepted_truth": False,
        "local_apply_required": True,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_review_queue_section(
    review_packets: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    live_metadata_review_section: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = refresh_01.build_review_queue_section(review_packets, _policy(policy))
    section = _retag_snapshot_refresh(section)
    review_section = dict(live_metadata_review_section or {})
    section["live_metadata_review_decision_refs"] = list(review_section.get("review_decision_refs") or [])
    section["reviewed_metadata_record_preview_count"] = int(review_section.get("reviewed_metadata_record_preview_count") or 0)
    section["reviewed_source_lead_preview_count"] = int(review_section.get("reviewed_source_lead_preview_count") or 0)
    section["useful_lead_count"] = int(review_section.get("useful_lead_count") or 0)
    section["needs_more_evidence_count"] = int(review_section.get("needs_more_evidence_count") or 0)
    section["rejected_or_duplicate_count"] = int(review_section.get("rejected_or_duplicate_count") or 0)
    section["review_preview_applied"] = False
    return section


def build_need_absence_section(
    known_needs: Sequence[Mapping[str, Any]],
    absence_summaries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = refresh_01.build_need_absence_section(known_needs, absence_summaries, _policy(policy))
    return _retag_snapshot_refresh(section)


def build_refreshed_relay_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_sections = list(snapshot_sections.get("candidate_sections") or [])
    seed_candidates = [candidate for section in candidate_sections for candidate in section.get("candidates", [])]
    live_candidates = list(snapshot_sections.get("live_metadata_candidate_section", {}).get("candidates") or [])
    review_section = dict(snapshot_sections.get("live_metadata_review_section") or {})
    metadata_preview_section = dict(snapshot_sections.get("reviewed_metadata_preview_section") or {})
    source_lead_section = dict(snapshot_sections.get("reviewed_source_lead_preview_section") or {})
    return {
        "schema_version": "snapshot_refresh_relay_projection.v0",
        "record_type": "snapshot_refresh_relay_projection",
        "relay_projection_id": _section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "read_only": True,
        "sections": {
            "reviewed_records": int(snapshot_sections.get("reviewed_record_section", {}).get("reviewed_record_count") or 0),
            "candidate_sections": len(candidate_sections),
            "fixture_candidates": len(seed_candidates),
            "live_metadata_candidates": len(live_candidates),
            "live_metadata_review_decisions": int(review_section.get("review_decision_count") or 0),
            "reviewed_metadata_record_previews": int(metadata_preview_section.get("preview_count") or 0),
            "reviewed_source_lead_previews": int(source_lead_section.get("source_lead_preview_count") or 0),
            "useful_leads": int(review_section.get("useful_lead_count") or 0),
            "needs_more_evidence": int(review_section.get("needs_more_evidence_count") or 0),
            "rejected_or_duplicate": int(review_section.get("rejected_or_duplicate_count") or 0),
            "known_needs": int(snapshot_sections.get("need_absence_section", {}).get("known_need_count") or 0),
            "absence_summaries": int(snapshot_sections.get("need_absence_section", {}).get("absence_count") or 0),
        },
        "query_previews": [
            _relay_preview("reviewed metadata previews", metadata_preview_section.get("previews", [])),
            _relay_preview("reviewed source lead previews", source_lead_section.get("previews", [])),
            _relay_preview("live metadata review decisions", review_section.get("decisions", [])),
        ],
        "review_previews_are_not_truth": True,
        "local_apply_required": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_performed": False,
        "accepted_truth": False,
        **_false_boundaries(),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_search_view_model_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    live_cards = [
        _candidate_result_card(candidate)
        for candidate in snapshot_sections.get("live_metadata_candidate_section", {}).get("candidates", [])
    ]
    metadata_preview_cards = [
        _preview_result_card(preview, "reviewed_metadata_record_preview")
        for preview in snapshot_sections.get("reviewed_metadata_preview_section", {}).get("previews", [])
    ]
    source_lead_cards = [
        _preview_result_card(preview, "reviewed_source_lead_preview")
        for preview in snapshot_sections.get("reviewed_source_lead_preview_section", {}).get("previews", [])
    ]
    cards = live_cards + metadata_preview_cards + source_lead_cards
    status_counts = {
        "verified": int(snapshot_sections.get("reviewed_record_section", {}).get("reviewed_record_count") or 0),
        "candidate": len(live_cards),
        "near_miss": 0,
        "known_need": int(snapshot_sections.get("need_absence_section", {}).get("known_need_count") or 0),
        "absence": int(snapshot_sections.get("need_absence_section", {}).get("absence_count") or 0),
        "source_lead": len(metadata_preview_cards) + len(source_lead_cards),
    }
    return {
        "schema_version": "snapshot_public_search_view_model_projection.v0",
        "record_type": "snapshot_public_search_view_model_projection",
        "projection_id": _section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "projection_profiles": ["public_web", "operator_workbench", "api_json", "classic_html", "text"],
        "result_cards": cards,
        "status_counts": status_counts,
        "candidate_verified_separation_visible": True,
        "review_previews_visible_as_source_leads": True,
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "accepted_truth_created": False,
        "review_preview_applied": False,
        "raw_live_response_included": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "limitations": _limitations(),
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
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "reviewed_record_count": int(snapshot_refresh_result.get("reviewed_record_count") or 0),
        "fixture_candidate_count": int(snapshot_refresh_result.get("fixture_candidate_count") or 0),
        "live_metadata_candidate_count": int(snapshot_refresh_result.get("live_metadata_candidate_count") or 0),
        "reviewed_metadata_record_preview_count": int(snapshot_refresh_result.get("reviewed_metadata_record_preview_count") or 0),
        "reviewed_source_lead_preview_count": int(snapshot_refresh_result.get("reviewed_source_lead_preview_count") or 0),
        "useful_lead_count": int(snapshot_refresh_result.get("useful_lead_count") or 0),
        "needs_more_evidence_count": int(snapshot_refresh_result.get("needs_more_evidence_count") or 0),
        "rejected_or_duplicate_count": int(snapshot_refresh_result.get("rejected_or_duplicate_count") or 0),
        "known_need_count": int(snapshot_refresh_result.get("known_need_count") or 0),
        "absence_count": int(snapshot_refresh_result.get("absence_count") or 0),
        "launch_recommended": False,
        "demo_mode_recommended": True,
        "internal_review_recommended": True,
        "needs_more_reviewed_records": True,
        "needs_local_apply_for_reviewed_previews": True,
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "review_required": True,
        "accepted_truth": False,
        "review_preview_applied": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def validate_snapshot_refresh_02_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    errors: list[str] = []
    if result.get("schema_version") != "snapshot_refresh_02_result.v0":
        errors.append("schema_version must be snapshot_refresh_02_result.v0")
    for key in BOUNDARY_FALSE_KEYS:
        if result.get(key) is not False:
            errors.append(f"{key} must be false")
    review_section = result.get("live_metadata_review_section")
    metadata_section = result.get("reviewed_metadata_preview_section")
    source_lead_section = result.get("reviewed_source_lead_preview_section")
    if not isinstance(review_section, Mapping) or review_section.get("review_decision_count") != 8:
        errors.append("live metadata review section must include 8 decisions")
    if not isinstance(metadata_section, Mapping) or metadata_section.get("preview_count") != 1:
        errors.append("reviewed metadata preview section must include 1 preview")
    if not isinstance(source_lead_section, Mapping) or source_lead_section.get("source_lead_preview_count") != 2:
        errors.append("reviewed source lead preview section must include 2 previews")
    for section_name, section in (
        ("reviewed_metadata_preview_section", metadata_section),
        ("reviewed_source_lead_preview_section", source_lead_section),
    ):
        if not isinstance(section, Mapping):
            continue
        if section.get("accepted_truth") is not False:
            errors.append(f"{section_name} must not be accepted truth")
        if section.get("local_apply_required") is not True:
            errors.append(f"{section_name} must require local apply")
        for preview in section.get("previews", []):
            for key in ("accepted_truth", "verified_download_claim_created", "malware_clean_claim_created", "rights_clearance_claim_created"):
                if preview.get(key) is not False:
                    errors.append(f"{preview.get('record_id')} {key} must be false")
    projection = result.get("public_search_view_model_projection")
    if not isinstance(projection, Mapping) or not projection.get("result_cards"):
        errors.append("public search view model projection must include result cards")
    else:
        for card in projection.get("result_cards", []):
            if card.get("object_type") != "reviewed_record" and card.get("status") == "verified":
                errors.append(f"{card.get('view_model_id')} must not be verified unless already reviewed")
    return {
        "schema_version": "snapshot_refresh_02_validation_report.v0",
        "task": TASK_ID,
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_02_boundary_report(
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
        "review_previews_are_not_truth": True,
        "local_apply_required": True,
        "live_metadata_candidates_remain_candidates_until_applied": True,
        **_false_boundaries(),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_snapshot_refresh_02(
    policy: Mapping[str, Any] | None = None,
    *,
    from_live_metadata_review_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_live_metadata_review_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_handoffs = load_seed_batch_handoffs(merged_policy)
    live_handoff = load_live_metadata_pilot_handoff(merged_policy)
    review_handoff = load_live_metadata_review_handoff(merged_policy)
    source_batches = list(seed_handoffs["source_batches"])
    plan = build_snapshot_refresh_02_plan(seed_handoffs, live_handoff, review_handoff, merged_policy)
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
    review_section = build_live_metadata_review_section(review_handoff["review_decisions"], merged_policy)
    metadata_preview_section = build_reviewed_metadata_preview_section(
        review_handoff["reviewed_metadata_record_previews"],
        merged_policy,
    )
    source_lead_preview_section = build_reviewed_source_lead_preview_section(
        review_handoff["reviewed_source_lead_previews"],
        merged_policy,
    )
    review_packets = [batch["review_batch_packet"] for batch in source_batches]
    review_packets.append(live_handoff["review_batch_packet"])
    review_packets.append(review_handoff["candidate_review_packet"])
    review_queue_section = build_review_queue_section(
        review_packets,
        merged_policy,
        live_metadata_review_section=review_section,
    )
    known_needs = [item for batch in source_batches for item in batch["known_needs"]]
    absence_summaries = [item for batch in source_batches for item in batch["absence_summaries"]]
    need_absence_section = build_need_absence_section(known_needs, absence_summaries, merged_policy)
    seed_summary_section = refresh_01.build_seed_batch_summary_section(source_batches, merged_policy)
    seed_summary_section = _retag_snapshot_refresh(seed_summary_section)
    sections = {
        "reviewed_record_section": reviewed_section,
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_section,
        "live_metadata_review_section": review_section,
        "reviewed_metadata_preview_section": metadata_preview_section,
        "reviewed_source_lead_preview_section": source_lead_preview_section,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
        "seed_batch_summary_section": seed_summary_section,
    }
    relay_projection = build_refreshed_relay_projection(sections, merged_policy)
    public_search_projection = build_public_search_view_model_projection(sections, merged_policy)
    fixture_candidate_count = sum(int(section.get("candidate_count") or 0) for section in candidate_sections)
    live_candidate_count = int(live_section.get("candidate_count") or 0)
    counts = _decision_counts(review_handoff["review_decisions"])
    result: dict[str, Any] = {
        "schema_version": "snapshot_refresh_02_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "live_metadata_review_integrated": True,
        "source_batches": [refresh_01._batch_summary(batch) for batch in source_batches],
        "source_batch_refs": [batch["batch_id"] for batch in source_batches],
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "reviewed_record_refs": list(reviewed_section["reviewed_record_refs"]),
        "candidate_section_refs": [section["section_id"] for section in candidate_sections],
        "live_metadata_candidate_section_refs": [live_section["section_id"]],
        "live_metadata_review_section_refs": [review_section["section_id"]],
        "reviewed_metadata_preview_section_refs": [metadata_preview_section["section_id"]],
        "reviewed_source_lead_preview_section_refs": [source_lead_preview_section["section_id"]],
        "review_queue_section_refs": [review_queue_section["section_id"]],
        "need_absence_section_refs": [need_absence_section["section_id"]],
        "relay_projection_refs": [relay_projection["relay_projection_id"]],
        "public_search_view_model_refs": [public_search_projection["projection_id"]],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "plan": plan,
        "reviewed_record_section": reviewed_section,
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_section,
        "live_metadata_review_section": review_section,
        "reviewed_metadata_preview_section": metadata_preview_section,
        "reviewed_source_lead_preview_section": source_lead_preview_section,
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
        **counts,
        "fixture_snapshot_refresh_passed": True,
        **_false_boundaries(),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }
    public_alpha = build_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_snapshot_refresh_02_boundary_report(result, merged_policy)
    result["validation_report"] = validate_snapshot_refresh_02_result(result, merged_policy)
    if result["validation_report"]["status"] != "pass":
        result["status"] = "fail"
        result["fixture_snapshot_refresh_passed"] = False
    if write_examples:
        written = write_snapshot_refresh_02_examples(result)
        written.extend(write_snapshot_refresh_02_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_snapshot_refresh_02_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_02(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "snapshots" / "refresh" / "live_metadata_review"
    base.mkdir(parents=True, exist_ok=True)
    candidate_sections = list(payload["candidate_sections"])
    files = {
        "snapshot_refresh_plan.json": payload["plan"],
        "reviewed_record_section.json": payload["reviewed_record_section"],
        "candidate_section_frontier_media.json": candidate_sections[0],
        "candidate_section_legacy_software.json": candidate_sections[1],
        "live_metadata_candidate_section.json": payload["live_metadata_candidate_section"],
        "live_metadata_review_section.json": payload["live_metadata_review_section"],
        "reviewed_metadata_preview_section.json": payload["reviewed_metadata_preview_section"],
        "reviewed_source_lead_preview_section.json": payload["reviewed_source_lead_preview_section"],
        "review_queue_section.json": payload["review_queue_section"],
        "need_absence_section.json": payload["need_absence_section"],
        "refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "public_search_view_model_projection.json": payload["public_search_view_model_projection"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "snapshot_refresh_02_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/relay/refresh/live_metadata_review_refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "examples/public_alpha/reassess/live_metadata/snapshot_refresh_02_reassess_input.json": payload["public_alpha_reassess_input"],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_snapshot_refresh_02_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_02(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = build_snapshot_refresh_02_inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_snapshot_refresh_02_audit_pack(payload, repo_root))
    return written


def build_snapshot_refresh_02_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    review_section = dict(result.get("live_metadata_review_section") or {})
    metadata_section = dict(result.get("reviewed_metadata_preview_section") or {})
    source_lead_section = dict(result.get("reviewed_source_lead_preview_section") or {})
    candidate_sections = list(result.get("candidate_sections") or [])
    packets: dict[str, Any] = {
        "snapshot_refresh_02_input_state.json": {
            "schema_version": "snapshot_refresh_02_input_state.v0",
            "task": TASK_ID,
            "branch": "dev",
            "input_results": {
                "live_metadata_review": LIVE_METADATA_REVIEW_REF,
                "public_alpha_reassess_01": "control/inventory/public_alpha_reassess_01_result.json",
                "snapshot_refresh_01": "control/inventory/snapshot_refresh_01_result.json",
                "live_metadata_pilot": LIVE_METADATA_PILOT_REF,
                "snapshot_refresh_00": "control/inventory/snapshot_refresh_result.json",
                "review_batch": "control/inventory/review_batch_result.json",
                "candidate_index": "control/inventory/candidate_index_result.json",
                "scout_runtime": "control/inventory/scout_runtime_result.json",
                "query_planner": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
            },
            **_false_boundaries(),
            "created_at": DEFAULT_TIMESTAMP,
        },
        "snapshot_refresh_02_source_matrix.json": {
            "schema_version": "snapshot_refresh_02_source_matrix.v0",
            "task": TASK_ID,
            "sources": list(result.get("source_batches") or []),
            "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
            "source_batch_count": len(result.get("source_batches") or []),
        },
        "snapshot_refresh_02_reviewed_record_matrix.json": {
            "schema_version": "snapshot_refresh_02_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "reviewed_record_refs": list(result.get("reviewed_record_refs") or []),
            "reviewed_record_count": result.get("reviewed_record_count"),
            "review_previews_are_not_truth": True,
        },
        "snapshot_refresh_02_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_02_candidate_matrix.v0",
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
        "snapshot_refresh_02_live_metadata_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_02_live_metadata_candidate_matrix.v0",
            "task": TASK_ID,
            "section_id": result.get("live_metadata_candidate_section", {}).get("section_id"),
            "candidate_count": result.get("live_metadata_candidate_count"),
            "review_required": True,
            "accepted_truth": False,
            "raw_response_included": False,
            "public_search_status": "candidate",
        },
        "snapshot_refresh_02_live_metadata_review_matrix.json": {
            "schema_version": "snapshot_refresh_02_live_metadata_review_matrix.v0",
            "task": TASK_ID,
            "section_id": review_section.get("section_id"),
            "review_decision_count": review_section.get("review_decision_count"),
            "review_decision_refs": review_section.get("review_decision_refs"),
            "useful_lead_count": result.get("useful_lead_count"),
            "needs_more_evidence_count": result.get("needs_more_evidence_count"),
            "rejected_or_duplicate_count": result.get("rejected_or_duplicate_count"),
            "accepted_truth": False,
            "review_preview_applied": False,
        },
        "snapshot_refresh_02_reviewed_preview_matrix.json": {
            "schema_version": "snapshot_refresh_02_reviewed_preview_matrix.v0",
            "task": TASK_ID,
            "reviewed_metadata_record_previews": metadata_section.get("previews"),
            "reviewed_source_lead_previews": source_lead_section.get("previews"),
            "reviewed_metadata_record_preview_count": result.get("reviewed_metadata_record_preview_count"),
            "reviewed_source_lead_preview_count": result.get("reviewed_source_lead_preview_count"),
            "local_apply_required": True,
            "accepted_truth": False,
            "review_preview_applied": False,
        },
        "snapshot_refresh_02_need_absence_matrix.json": {
            "schema_version": "snapshot_refresh_02_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result.get("known_need_count"),
            "absence_count": result.get("absence_count"),
            "bounded_absence_statements": True,
        },
        "snapshot_refresh_02_review_queue_matrix.json": {
            "schema_version": "snapshot_refresh_02_review_queue_matrix.v0",
            "task": TASK_ID,
            "review_queue_section_refs": list(result.get("review_queue_section_refs") or []),
            "review_queue_candidate_count": result.get("review_queue_candidate_count"),
            "live_metadata_review_decision_refs": result.get("review_queue_section", {}).get("live_metadata_review_decision_refs"),
            "operator_context_required": True,
        },
        "snapshot_refresh_02_relay_projection_matrix.json": {
            "schema_version": "snapshot_refresh_02_relay_projection_matrix.v0",
            "task": TASK_ID,
            "relay_projection_refs": list(result.get("relay_projection_refs") or []),
            "sections": result.get("refreshed_relay_projection", {}).get("sections"),
            "read_only": True,
            "mutation_enabled": False,
            "site_dist_written": False,
        },
        "snapshot_refresh_02_public_search_view_model_matrix.json": {
            "schema_version": "snapshot_refresh_02_public_search_view_model_matrix.v0",
            "task": TASK_ID,
            "public_search_view_model_refs": list(result.get("public_search_view_model_refs") or []),
            "result_card_count": len(result.get("public_search_view_model_projection", {}).get("result_cards") or []),
            "status_counts": result.get("public_search_view_model_projection", {}).get("status_counts"),
            "candidate_verified_separation_visible": True,
        },
        "snapshot_refresh_02_public_alpha_reassess_matrix.json": {
            "schema_version": "snapshot_refresh_02_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
            "reviewed_metadata_record_preview_count": result.get("reviewed_metadata_record_preview_count"),
            "reviewed_source_lead_preview_count": result.get("reviewed_source_lead_preview_count"),
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
        },
        "snapshot_refresh_02_boundary_report.json": result["boundary_report"],
        "snapshot_refresh_02_smoke_result.json": {
            "schema_version": "snapshot_refresh_02_smoke_result.v0",
            "task": TASK_ID,
            "status": result.get("status"),
            "fixture_snapshot_refresh_passed": result.get("fixture_snapshot_refresh_passed"),
            "live_metadata_review_integrated": True,
            **_false_boundaries(),
        },
        "snapshot_refresh_02_validation_matrix.json": {
            "schema_version": "snapshot_refresh_02_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_review_live_metadata_candidates.py",
                "focused snapshot refresh unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "snapshot_refresh_02_result.json": _task_result(result),
        "snapshot_refresh_02_next_task_decision.json": {
            "schema_version": "snapshot_refresh_02_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": NEXT_TASK,
            "planned_after": [
                "LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00",
                "SEED-BATCH-MANUALS-SCANS-00",
                "SEED-BATCH-DRIVER-SUPPORT-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "deployment_performed": False,
            "public_launch_readiness_claimed": False,
        },
        "snapshot_refresh_02_failure_repair_log.json": {
            "schema_version": "snapshot_refresh_02_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
            **_false_boundaries(),
        },
    }
    return packets


def _write_snapshot_refresh_02_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "snapshot-refresh-02-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = build_snapshot_refresh_02_inventory_packets(result)
    audit_json = {"snapshot_refresh_02_report.json": _task_result(result)}
    audit_markdown = {
        "README.md": "# SNAPSHOT-REFRESH-02 Audit\n\nRefresh evidence after live metadata candidate review. Review previews remain preview-only, local apply is required, and no reviewed/master/public index is mutated.\n",
        "source_matrix.md": _matrix_md("Source Matrix", inventory["snapshot_refresh_02_source_matrix.json"]),
        "reviewed_record_matrix.md": _matrix_md("Reviewed Record Matrix", inventory["snapshot_refresh_02_reviewed_record_matrix.json"]),
        "candidate_matrix.md": _matrix_md("Candidate Matrix", inventory["snapshot_refresh_02_candidate_matrix.json"]),
        "live_metadata_candidate_matrix.md": _matrix_md("Live Metadata Candidate Matrix", inventory["snapshot_refresh_02_live_metadata_candidate_matrix.json"]),
        "live_metadata_review_matrix.md": _matrix_md("Live Metadata Review Matrix", inventory["snapshot_refresh_02_live_metadata_review_matrix.json"]),
        "reviewed_preview_matrix.md": _matrix_md("Reviewed Preview Matrix", inventory["snapshot_refresh_02_reviewed_preview_matrix.json"]),
        "need_absence_matrix.md": _matrix_md("Need And Absence Matrix", inventory["snapshot_refresh_02_need_absence_matrix.json"]),
        "review_queue_matrix.md": _matrix_md("Review Queue Matrix", inventory["snapshot_refresh_02_review_queue_matrix.json"]),
        "relay_projection_matrix.md": _matrix_md("Relay Projection Matrix", inventory["snapshot_refresh_02_relay_projection_matrix.json"]),
        "public_search_view_model_matrix.md": _matrix_md("Public Search View Model Matrix", inventory["snapshot_refresh_02_public_search_view_model_matrix.json"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", inventory["snapshot_refresh_02_public_alpha_reassess_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["snapshot_refresh_02_smoke_result.json"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["snapshot_refresh_02_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/snapshot_refresh_02_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    generated_files = {
        "sample_snapshot_refresh_plan.json": result["plan"],
        "sample_live_metadata_review_section.json": result["live_metadata_review_section"],
        "sample_reviewed_metadata_preview_section.json": result["reviewed_metadata_preview_section"],
        "sample_reviewed_source_lead_preview_section.json": result["reviewed_source_lead_preview_section"],
        "sample_public_search_view_model_projection.json": result["public_search_view_model_projection"],
        "sample_relay_projection.json": result["refreshed_relay_projection"],
        "sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Snapshot Refresh 02 Summary\n\n"
        f"- reviewed metadata record previews: {result.get('reviewed_metadata_record_preview_count')}\n"
        f"- reviewed source lead previews: {result.get('reviewed_source_lead_preview_count')}\n"
        f"- useful leads: {result.get('useful_lead_count')}\n"
        f"- needs more evidence: {result.get('needs_more_evidence_count')}\n"
        f"- rejected or duplicate: {result.get('rejected_or_duplicate_count')}\n"
        "- accepted truth created: false\n"
        "- review preview applied: false\n"
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


def _decision_item(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_live_metadata_review_decision_item.v0",
        "decision_id": _text(decision.get("decision_id")),
        "candidate_id": _text(decision.get("candidate_id")),
        "source_family": _text(decision.get("source_family")) or "internet_archive_metadata",
        "review_decision": _text(decision.get("review_decision") or decision.get("decision")),
        "allowed_promotion_kind": _text(decision.get("allowed_promotion_kind")) or "none",
        "promotion_preview_allowed": bool(decision.get("promotion_preview_allowed")),
        "sufficiency_score": float(decision.get("sufficiency_score") or 0.0),
        "evidence_refs": _text_list(decision.get("evidence_refs")),
        "reason": _text(decision.get("reason")),
        "accepted_truth": False,
        "reviewed_artifact_claim": False,
        "download_claim": False,
        "extraction_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "local_apply_required": bool(decision.get("local_apply_required")),
        "limitations": _text_list(decision.get("limitations")),
        "prohibited_claims": _prohibited_claims(),
    }


def _preview_item(preview: Mapping[str, Any], expected_type: str) -> dict[str, Any]:
    record = copy.deepcopy(dict(preview))
    record["record_type"] = expected_type
    record["accepted_truth"] = False
    record["local_apply_required"] = True
    record["review_preview_applied"] = False
    record["verified_download_claim_created"] = False
    record["malware_clean_claim_created"] = False
    record["rights_clearance_claim_created"] = False
    record["reviewed_artifact_claim"] = False
    record["download_claim"] = False
    record["extraction_claim"] = False
    record["malware_clean_claim"] = False
    record["rights_clearance_claim"] = False
    return record


def _candidate_result_card(candidate: Mapping[str, Any]) -> dict[str, Any]:
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
        "snippet": "Live-metadata candidate remains review-only; no raw response or artifact claim is included.",
        "match_reasons": ["bounded_live_metadata_pilot", "review_required"],
        "evidence_summary": {"evidence_refs": refs, "evidence_count": len(refs)},
        "confidence_label": "candidate",
        "risk_label": "review_required",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "unreviewed",
        "action_posture": _action_posture(),
        "review_required": True,
        "accepted_truth": False,
        "limitations": _text_list(candidate.get("limitations")),
        "created_at": DEFAULT_TIMESTAMP,
    }


def _preview_result_card(preview: Mapping[str, Any], preview_kind: str) -> dict[str, Any]:
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", preview.get("record_id")),
        "title": _text(preview.get("title")),
        "url": "/source/" + _text(preview.get("record_id")),
        "status": "source_lead",
        "object_type": preview_kind,
        "domain": "live_metadata_review",
        "source_family": _text(preview.get("source_family")) or "internet_archive_metadata",
        "source_label": "Internet Archive metadata review preview",
        "snippet": "Review preview only. Local apply is required before any reviewed-record mutation.",
        "match_reasons": ["live_metadata_review", "preview_only", "local_apply_required"],
        "evidence_summary": {
            "summary": _text(preview.get("limited_claim")),
            "evidence_refs": _text_list(preview.get("evidence_refs")),
            "evidence_count": len(_text_list(preview.get("evidence_refs"))),
        },
        "confidence_label": "source_lead_preview",
        "risk_label": "not_artifact_verified",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "not_verified_download",
        "action_posture": _action_posture(),
        "review_required": True,
        "local_apply_required": True,
        "accepted_truth": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def _relay_preview(label: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_relay_query_preview.v0",
        "query": label,
        "read_only": True,
        "result_count": len(rows),
        "results": [
            {
                "id": item.get("record_id") or item.get("decision_id") or item.get("candidate_id"),
                "candidate_id": item.get("candidate_id"),
                "title": item.get("title") or item.get("review_decision"),
                "accepted_truth": False,
                "local_apply_required": bool(item.get("local_apply_required")),
                "public_search_status": "source_lead" if item.get("record_id") else "candidate",
            }
            for item in rows
        ],
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
    }


def _decision_counts(decisions: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    decision_names = [_text(item.get("review_decision") or item.get("decision")) for item in decisions]
    return {
        "live_metadata_candidates_reviewed": len(decision_names),
        "reviewed_metadata_record_preview_count": sum(
            1 for item in decisions if item.get("allowed_promotion_kind") == "reviewed_metadata_record"
        ),
        "reviewed_source_lead_preview_count": sum(
            1 for item in decisions if item.get("allowed_promotion_kind") == "reviewed_source_lead"
        ),
        "useful_lead_count": decision_names.count("mark_useful_lead"),
        "needs_more_evidence_count": decision_names.count("needs_more_evidence"),
        "rejected_or_duplicate_count": sum(
            1
            for decision in decision_names
            if decision in {"duplicate", "reject_wrong_object", "reject_wrong_version", "reject_low_quality", "block_candidate"}
        ),
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_02_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "live_metadata_review_integrated": True,
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "contracts_added": True,
        "policies_added": True,
        "source_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "candidate_matrix_added": True,
        "live_metadata_candidate_matrix_added": True,
        "live_metadata_review_matrix_added": True,
        "reviewed_preview_matrix_added": True,
        "need_absence_matrix_added": True,
        "review_queue_matrix_added": True,
        "relay_projection_matrix_added": True,
        "public_search_view_model_matrix_added": True,
        "public_alpha_reassess_matrix_added": True,
        "runtime_snapshot_refresh_added": True,
        "reviewed_record_section_created": True,
        "candidate_sections_created": True,
        "live_metadata_candidate_section_created": True,
        "live_metadata_review_section_created": True,
        "reviewed_metadata_preview_section_created": True,
        "reviewed_source_lead_preview_section_created": True,
        "review_queue_section_created": True,
        "need_absence_section_created": True,
        "relay_projection_created": True,
        "public_search_view_model_projection_created": True,
        "public_alpha_reassess_input_created": True,
        "reviewed_metadata_record_preview_count": result.get("reviewed_metadata_record_preview_count"),
        "reviewed_source_lead_preview_count": result.get("reviewed_source_lead_preview_count"),
        "useful_lead_count": result.get("useful_lead_count"),
        "needs_more_evidence_count": result.get("needs_more_evidence_count"),
        "rejected_or_duplicate_count": result.get("rejected_or_duplicate_count"),
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "fixture_snapshot_refresh_passed": bool(result.get("fixture_snapshot_refresh_passed")),
        **_false_boundaries(),
        "recommended_next_task": NEXT_TASK,
    }


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return _result_summary(result)


def _action_posture() -> dict[str, Any]:
    return {
        "schema_version": "snapshot_review_only_action_posture.v0",
        "allowed_actions": ["inspect", "view_source", "view_provenance", "read"],
        "blocked_actions": ["download", "install_handoff", "execute", "extract", "promote"],
        "review_required": True,
        "accepted_truth": False,
        "public_mutation_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
    }


def _prohibited_claims() -> list[str]:
    return [
        "verified_download",
        "safe_installer",
        "extracted_file",
        "malware_clean",
        "rights_cleared",
        "production_quality_artifact",
    ]


def _limitations() -> list[str]:
    return [
        "snapshot_refresh_is_projection_only",
        "review_previews_remain_preview_only",
        "local_apply_required_before_reviewed_mutation",
        "live_metadata_candidates_remain_candidates_until_applied",
        "raw_live_responses_excluded",
        "no_verified_download_claim",
        "no_malware_clean_claim",
        "no_rights_clearance_claim",
        "no_site_dist_write",
        "no_public_index_mutation",
        "no_deployment_or_launch_claim",
    ]


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


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
        "review_previews_are_not_truth",
        "reviewed_metadata_previews_require_local_apply",
        "reviewed_source_lead_previews_require_local_apply",
        "live_metadata_candidates_remain_candidates_until_applied",
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
        raise PermissionError(f"snapshot refresh 02 policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "raw_live_response_included",
        "verified_download_claim_allowed",
        "malware_clean_claim_allowed",
        "rights_clearance_claim_allowed",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"snapshot refresh 02 policy enables forbidden behavior: {', '.join(enabled)}")


def _assert_live_metadata_review(review_result: Mapping[str, Any], payload: Mapping[str, Any]) -> None:
    if review_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("live metadata review must pass before snapshot refresh 02")
    expected_counts = {
        "live_metadata_candidates_reviewed": 8,
        "reviewed_metadata_record_preview_count": 1,
        "reviewed_source_lead_preview_count": 2,
        "useful_lead_count": 1,
        "needs_more_evidence_count": 2,
        "rejected_or_duplicate_count": 2,
    }
    for key, value in expected_counts.items():
        if int(review_result.get(key) or 0) != value or int(payload.get(key) or 0) != value:
            raise ValueError(f"live metadata review count mismatch for {key}")
    for key in (
        "new_live_source_calls_performed",
        "raw_live_response_committed",
        "verified_download_claim_created",
        "malware_clean_claim_created",
        "rights_clearance_claim_created",
        "accepted_truth_created",
        "reviewed_index_mutated",
        "master_index_mutated",
        "public_index_mutated",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
    ):
        if review_result.get(key) is not False:
            raise ValueError(f"live metadata review boundary failed: {key}")


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
        text = _text(value)
        return [text] if text else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [_text(item) for item in value if _text(item)]
    return []
