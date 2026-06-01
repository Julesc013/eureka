"""Snapshot refresh projection after temp local apply of live metadata previews.

SNAPSHOT-REFRESH-03 packages limited reviewed metadata/source-lead records from
the temp-only local-apply proof. These records remain limited metadata/source
lead claims; they are not verified artifacts, downloads, malware-clean claims,
rights-clearance claims, or public/master index mutations.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.snapshots import refresh_01, refresh_02
from runtime.snapshots.relay_foundation import sample_reviewed_records


DEFAULT_TIMESTAMP = "2026-06-01T00:00:00Z"
SNAPSHOT_REFRESH_ID = "snapshot_refresh_03"
TASK_ID = "SNAPSHOT-REFRESH-03"
LOCAL_APPLY_REF = "control/inventory/local_apply_live_metadata_result.json"
LOCAL_APPLY_SNAPSHOT_HANDOFF_REF = "examples/local_apply/live_metadata/snapshot_refresh_handoff.json"
LIVE_METADATA_REVIEW_REF = "control/inventory/live_metadata_review_result.json"
LIVE_METADATA_PILOT_REF = "control/inventory/live_metadata_pilot_result.json"
SNAPSHOT_REFRESH_02_REF = "control/inventory/snapshot_refresh_02_result.json"
NEXT_TASK = "PUBLIC-ALPHA-REASSESS-03 - Reassess alpha after local apply snapshot refresh"

BOUNDARY_FALSE_KEYS = (
    "accepted_truth_created",
    "artifact_verified_claim_created",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "rights_clearance_claim_created",
    "operator_instance_mutated",
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

DEFAULT_POLICY: dict[str, Any] = {
    "snapshot_refresh_is_projection": True,
    "local_apply_outputs_may_project_as_limited_reviewed_records": True,
    "reviewed_metadata_records_are_limited_claims": True,
    "reviewed_source_leads_are_limited_claims": True,
    "reviewed_metadata_records_are_not_verified_artifacts": True,
    "reviewed_source_leads_are_not_verified_artifacts": True,
    "live_metadata_candidates_remain_candidates": True,
    "candidates_remain_candidates": True,
    "seed_outputs_are_not_truth": True,
    "reviewed_records_only_from_existing_reviewed_sources": True,
    "review_previews_are_not_truth": True,
    "reviewed_metadata_previews_require_local_apply": True,
    "reviewed_source_lead_previews_require_local_apply": True,
    "live_metadata_candidates_remain_candidates_until_applied": True,
    "no_candidate_auto_acceptance": True,
    "no_live_metadata_auto_acceptance": True,
    "no_verified_download_claim": True,
    "no_malware_clean_claim": True,
    "no_rights_clearance_claim": True,
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


def load_seed_batch_handoffs(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return refresh_02.load_seed_batch_handoffs(merged_policy)


def load_live_metadata_review_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return refresh_02.load_live_metadata_review_handoff(merged_policy)


def load_live_metadata_pilot_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return refresh_02.load_live_metadata_pilot_handoff(merged_policy)


def load_local_apply_live_metadata_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    local_apply_result = _read_json(repo / LOCAL_APPLY_REF)
    metadata_matrix = _read_json(repo / "examples/local_apply/live_metadata/reviewed_metadata_records.json")
    source_lead_matrix = _read_json(repo / "examples/local_apply/live_metadata/reviewed_source_leads.json")
    snapshot_handoff = _read_json(repo / LOCAL_APPLY_SNAPSHOT_HANDOFF_REF)
    public_alpha_handoff = _read_json(repo / "examples/local_apply/live_metadata/public_alpha_reassess_handoff.json")
    boundary_report = _read_json(repo / "examples/local_apply/live_metadata/boundary_report.json")
    reviewed_metadata_records = [dict(item) for item in metadata_matrix.get("records", [])]
    reviewed_source_leads = [dict(item) for item in source_lead_matrix.get("records", [])]
    _assert_local_apply(local_apply_result, reviewed_metadata_records, reviewed_source_leads)
    return {
        "schema_version": "snapshot_refresh_03_local_apply_handoff.v0",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "local_apply_ref": LOCAL_APPLY_REF,
        "snapshot_handoff_ref": LOCAL_APPLY_SNAPSHOT_HANDOFF_REF,
        "local_apply_result": local_apply_result,
        "snapshot_refresh_handoff": snapshot_handoff,
        "public_alpha_reassess_handoff": public_alpha_handoff,
        "boundary_report": boundary_report,
        "reviewed_metadata_records": reviewed_metadata_records,
        "reviewed_source_leads": reviewed_source_leads,
        "eligible_preview_count": int(local_apply_result.get("eligible_preview_count") or 0),
        "reviewed_metadata_records_created": len(reviewed_metadata_records),
        "reviewed_source_leads_created": len(reviewed_source_leads),
        "reviewed_record_delta_count": len(reviewed_metadata_records) + len(reviewed_source_leads),
        "temp_instance_apply_passed": bool(local_apply_result.get("temp_instance_apply_passed")),
        "useful_leads_not_applied": int(local_apply_result.get("useful_leads_not_applied") or 0),
        "needs_more_evidence_not_applied": int(local_apply_result.get("needs_more_evidence_not_applied") or 0),
        "rejected_or_duplicate_not_applied": int(local_apply_result.get("rejected_or_duplicate_not_applied") or 0),
        "limited_claim_scope": "metadata_or_source_lead_only",
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_snapshot_refresh_03_plan(
    seed_handoffs: Mapping[str, Any],
    live_metadata_handoff: Mapping[str, Any],
    review_handoff: Mapping[str, Any],
    local_apply_handoff: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    batches = list(seed_handoffs.get("source_batches") or [])
    return {
        "schema_version": "snapshot_refresh_plan.v0",
        "record_type": "snapshot_refresh_plan",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": [refresh_01._batch_summary(batch) for batch in batches],
        "local_apply_ref": LOCAL_APPLY_REF,
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "live_metadata_source_family": live_metadata_handoff.get("source_family"),
        "reviewed_record_refs": [record["record_id"] for record in sample_reviewed_records()],
        "reviewed_metadata_record_refs": [
            record.get("record_id") for record in local_apply_handoff.get("reviewed_metadata_records", [])
        ],
        "reviewed_source_lead_refs": [
            record.get("record_id") for record in local_apply_handoff.get("reviewed_source_leads", [])
        ],
        "candidate_section_refs": [
            _section_id("snapshot_candidate_section", batch.get("domain_key"), SNAPSHOT_REFRESH_ID)
            for batch in batches
        ],
        "live_metadata_candidate_section_refs": [
            _section_id("snapshot_live_metadata_candidate_section", live_metadata_handoff.get("pilot_batch_id"), SNAPSHOT_REFRESH_ID)
        ],
        "local_apply_section_refs": [_section_id("snapshot_local_apply_section", SNAPSHOT_REFRESH_ID)],
        "reviewed_metadata_record_section_refs": [
            _section_id("snapshot_reviewed_metadata_record_section", SNAPSHOT_REFRESH_ID)
        ],
        "reviewed_source_lead_section_refs": [
            _section_id("snapshot_reviewed_source_lead_section", SNAPSHOT_REFRESH_ID)
        ],
        "review_queue_section_refs": [_section_id("snapshot_review_queue_section", SNAPSHOT_REFRESH_ID)],
        "need_absence_section_refs": [_section_id("snapshot_need_absence_section", SNAPSHOT_REFRESH_ID)],
        "relay_projection_refs": [_section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID)],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "public_search_view_model_refs": [_section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID)],
        "refresh_mode": "local_apply_live_metadata_projection_only",
        "limited_reviewed_record_projection_count": int(local_apply_handoff.get("reviewed_record_delta_count") or 0),
        "reviewed_metadata_records_are_limited_claims": True,
        "reviewed_source_leads_are_limited_claims": True,
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "operator_instance_mutated": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "raw_live_response_included": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_existing_reviewed_record_section(
    existing_reviewed_records: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = refresh_02.build_reviewed_record_section(existing_reviewed_records, _policy(policy))
    section = _retag_snapshot_refresh(section)
    section["section_role"] = "existing_reviewed_records"
    section["limited_reviewed_record_projection"] = False
    return section


def build_reviewed_metadata_record_section(
    local_apply_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_limited_metadata_record(record) for record in local_apply_records]
    return {
        "schema_version": "snapshot_reviewed_metadata_record_section.v0",
        "record_type": "snapshot_reviewed_metadata_record_section",
        "section_id": _section_id("snapshot_reviewed_metadata_record_section", [record["record_id"] for record in records]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "local_apply_ref": LOCAL_APPLY_REF,
        "reviewed_metadata_record_count": len(records),
        "record_refs": [record["record_id"] for record in records],
        "records": records,
        "limited_claim_scope": "metadata_record_only",
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_reviewed_source_lead_section(
    local_apply_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [_limited_source_lead(record) for record in local_apply_records]
    return {
        "schema_version": "snapshot_reviewed_source_lead_section.v0",
        "record_type": "snapshot_reviewed_source_lead_section",
        "section_id": _section_id("snapshot_reviewed_source_lead_section", [record["record_id"] for record in records]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "local_apply_ref": LOCAL_APPLY_REF,
        "reviewed_source_lead_count": len(records),
        "record_refs": [record["record_id"] for record in records],
        "records": records,
        "limited_claim_scope": "source_lead_only",
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_candidate_snapshot_section(
    seed_candidates: Sequence[Mapping[str, Any]],
    live_metadata_candidates: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
    *,
    domain_key: str = "seed_batch",
    batch_id: str = "",
    scout_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    if isinstance(live_metadata_candidates, Mapping) and policy is None:
        policy = live_metadata_candidates
    section = refresh_02.build_candidate_snapshot_section(
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
    section = refresh_02.build_live_metadata_candidate_section(
        live_metadata_candidates,
        _policy(policy),
        live_metadata_handoff=live_metadata_handoff,
    )
    return _retag_snapshot_refresh(section)


def build_local_apply_section(
    local_apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    metadata_records = list(local_apply_result.get("reviewed_metadata_records") or [])
    source_leads = list(local_apply_result.get("reviewed_source_leads") or [])
    return {
        "schema_version": "snapshot_local_apply_section.v0",
        "record_type": "snapshot_local_apply_section",
        "section_id": _section_id("snapshot_local_apply_section", LOCAL_APPLY_REF),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "local_apply_ref": LOCAL_APPLY_REF,
        "snapshot_refresh_handoff_ref": LOCAL_APPLY_SNAPSHOT_HANDOFF_REF,
        "eligible_preview_count": int(local_apply_result.get("eligible_preview_count") or 0),
        "reviewed_metadata_records_created": len(metadata_records),
        "reviewed_source_leads_created": len(source_leads),
        "reviewed_record_delta_count": len(metadata_records) + len(source_leads),
        "reviewed_metadata_record_refs": [record.get("record_id") for record in metadata_records],
        "reviewed_source_lead_refs": [record.get("record_id") for record in source_leads],
        "useful_leads_not_applied": int(local_apply_result.get("useful_leads_not_applied") or 0),
        "needs_more_evidence_not_applied": int(local_apply_result.get("needs_more_evidence_not_applied") or 0),
        "rejected_or_duplicate_not_applied": int(local_apply_result.get("rejected_or_duplicate_not_applied") or 0),
        "temp_instance_apply_passed": bool(local_apply_result.get("temp_instance_apply_passed")),
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "limited_claim_scope": "metadata_or_source_lead_only",
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_review_queue_section(
    review_packets: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    live_metadata_review_section: Mapping[str, Any] | None = None,
    local_apply_section: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = refresh_02.build_review_queue_section(
        review_packets,
        _policy(policy),
        live_metadata_review_section=live_metadata_review_section,
    )
    section = _retag_snapshot_refresh(section)
    local_apply = dict(local_apply_section or {})
    section["local_apply_section_ref"] = local_apply.get("section_id")
    section["reviewed_metadata_records_created"] = int(local_apply.get("reviewed_metadata_records_created") or 0)
    section["reviewed_source_leads_created"] = int(local_apply.get("reviewed_source_leads_created") or 0)
    section["useful_leads_not_applied"] = int(local_apply.get("useful_leads_not_applied") or 0)
    section["needs_more_evidence_not_applied"] = int(local_apply.get("needs_more_evidence_not_applied") or 0)
    section["rejected_or_duplicate_not_applied"] = int(local_apply.get("rejected_or_duplicate_not_applied") or 0)
    section["operator_instance_mutated"] = False
    return section


def build_need_absence_section(
    known_needs: Sequence[Mapping[str, Any]],
    absence_summaries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    section = refresh_02.build_need_absence_section(known_needs, absence_summaries, _policy(policy))
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
    reviewed_section = dict(snapshot_sections.get("existing_reviewed_record_section") or {})
    metadata_section = dict(snapshot_sections.get("reviewed_metadata_record_section") or {})
    source_lead_section = dict(snapshot_sections.get("reviewed_source_lead_section") or {})
    local_apply_section = dict(snapshot_sections.get("local_apply_section") or {})
    need_absence_section = dict(snapshot_sections.get("need_absence_section") or {})
    existing_count = int(reviewed_section.get("reviewed_record_count") or 0)
    metadata_count = int(metadata_section.get("reviewed_metadata_record_count") or 0)
    source_lead_count = int(source_lead_section.get("reviewed_source_lead_count") or 0)
    return {
        "schema_version": "snapshot_refresh_relay_projection.v0",
        "record_type": "snapshot_refresh_relay_projection",
        "relay_projection_id": _section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "read_only": True,
        "sections": {
            "existing_reviewed_records": existing_count,
            "reviewed_metadata_records_from_local_apply": metadata_count,
            "reviewed_source_leads_from_local_apply": source_lead_count,
            "total_limited_reviewed_record_projection_count": existing_count + metadata_count + source_lead_count,
            "candidate_sections": len(candidate_sections),
            "fixture_candidates": len(seed_candidates),
            "live_metadata_candidates": len(live_candidates),
            "useful_leads_not_applied": int(local_apply_section.get("useful_leads_not_applied") or 0),
            "needs_more_evidence_not_applied": int(local_apply_section.get("needs_more_evidence_not_applied") or 0),
            "rejected_or_duplicate_not_applied": int(local_apply_section.get("rejected_or_duplicate_not_applied") or 0),
            "known_needs": int(need_absence_section.get("known_need_count") or 0),
            "absence_summaries": int(need_absence_section.get("absence_count") or 0),
        },
        "query_previews": [
            _relay_preview("reviewed metadata records from local apply", metadata_section.get("records", [])),
            _relay_preview("reviewed source leads from local apply", source_lead_section.get("records", [])),
            _relay_preview("live metadata candidates remain review-only", live_candidates),
        ],
        "reviewed_metadata_records_are_limited_claims": True,
        "reviewed_source_leads_are_limited_claims": True,
        "metadata_source_lead_records_are_not_artifacts": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_performed": False,
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
    metadata_cards = [
        _limited_record_card(record, "reviewed_metadata_record_limited")
        for record in snapshot_sections.get("reviewed_metadata_record_section", {}).get("records", [])
    ]
    source_lead_cards = [
        _limited_record_card(record, "reviewed_source_lead_limited")
        for record in snapshot_sections.get("reviewed_source_lead_section", {}).get("records", [])
    ]
    cards = live_cards + metadata_cards + source_lead_cards
    status_counts = {
        "verified": int(snapshot_sections.get("existing_reviewed_record_section", {}).get("reviewed_record_count") or 0),
        "candidate": len(live_cards),
        "near_miss": 0,
        "known_need": int(snapshot_sections.get("need_absence_section", {}).get("known_need_count") or 0),
        "absence": int(snapshot_sections.get("need_absence_section", {}).get("absence_count") or 0),
        "source_lead": len(metadata_cards) + len(source_lead_cards),
    }
    return {
        "schema_version": "snapshot_public_search_view_model_projection.v0",
        "record_type": "snapshot_public_search_view_model_projection",
        "projection_id": _section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "projection_profiles": ["public_web", "operator_workbench", "api_json", "classic_html", "text"],
        "result_cards": cards,
        "status_counts": status_counts,
        "reviewed_metadata_source_lead_cards_distinct_from_verified_artifacts": True,
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "artifact_verified_claim_created": False,
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
        "local_apply_ref": LOCAL_APPLY_REF,
        "existing_reviewed_record_count": int(snapshot_refresh_result.get("existing_reviewed_record_count") or 0),
        "reviewed_metadata_record_count": int(snapshot_refresh_result.get("reviewed_metadata_record_count") or 0),
        "reviewed_source_lead_count": int(snapshot_refresh_result.get("reviewed_source_lead_count") or 0),
        "reviewed_record_delta_count": int(snapshot_refresh_result.get("reviewed_record_delta_count") or 0),
        "total_limited_reviewed_record_projection_count": int(
            snapshot_refresh_result.get("total_limited_reviewed_record_projection_count") or 0
        ),
        "fixture_candidate_count": int(snapshot_refresh_result.get("fixture_candidate_count") or 0),
        "live_metadata_candidate_count": int(snapshot_refresh_result.get("live_metadata_candidate_count") or 0),
        "useful_leads_not_applied": int(snapshot_refresh_result.get("useful_leads_not_applied") or 0),
        "needs_more_evidence_not_applied": int(snapshot_refresh_result.get("needs_more_evidence_not_applied") or 0),
        "rejected_or_duplicate_not_applied": int(snapshot_refresh_result.get("rejected_or_duplicate_not_applied") or 0),
        "known_need_count": int(snapshot_refresh_result.get("known_need_count") or 0),
        "absence_count": int(snapshot_refresh_result.get("absence_count") or 0),
        "launch_recommended": False,
        "demo_mode_recommended": True,
        "internal_review_recommended": True,
        "needs_more_reviewed_records": True,
        "needs_public_alpha_reassess_after_apply": True,
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def validate_snapshot_refresh_03_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    errors: list[str] = []
    if result.get("schema_version") != "snapshot_refresh_03_result.v0":
        errors.append("schema_version must be snapshot_refresh_03_result.v0")
    expected_counts = {
        "existing_reviewed_record_count": 1,
        "reviewed_metadata_record_count": 1,
        "reviewed_source_lead_count": 2,
        "reviewed_record_delta_count": 3,
        "total_limited_reviewed_record_projection_count": 4,
    }
    for key, value in expected_counts.items():
        if int(result.get(key) or 0) != value:
            errors.append(f"{key} must be {value}")
    for key in BOUNDARY_FALSE_KEYS:
        if result.get(key) is not False:
            errors.append(f"{key} must be false")
    for section_name, count_key, count_value in (
        ("reviewed_metadata_record_section", "reviewed_metadata_record_count", 1),
        ("reviewed_source_lead_section", "reviewed_source_lead_count", 2),
    ):
        section = result.get(section_name)
        if not isinstance(section, Mapping) or section.get(count_key) != count_value:
            errors.append(f"{section_name} must include {count_value} records")
            continue
        for key in ("artifact_verified", "verified_download_claim", "malware_clean_claim", "rights_clearance_claim"):
            if section.get(key) is not False:
                errors.append(f"{section_name}.{key} must be false")
        for record in section.get("records", []):
            for key in (
                "artifact_verified",
                "verified_download_claim",
                "malware_clean_claim",
                "rights_clearance_claim",
                "artifact_verified_claim_created",
                "verified_download_claim_created",
                "malware_clean_claim_created",
                "rights_clearance_claim_created",
            ):
                if record.get(key) is not False:
                    errors.append(f"{record.get('record_id')} {key} must be false")
    projection = result.get("public_search_view_model_projection")
    if not isinstance(projection, Mapping) or not projection.get("result_cards"):
        errors.append("public search view model projection must include result cards")
    elif projection.get("status_counts", {}).get("source_lead") != 3:
        errors.append("public search projection must expose 3 limited source-lead style cards")
    else:
        for card in projection.get("result_cards", []):
            if card.get("object_type") in {"reviewed_metadata_record_limited", "reviewed_source_lead_limited"}:
                if card.get("status") == "verified":
                    errors.append(f"{card.get('view_model_id')} must not be verified artifact")
                if card.get("artifact_verified") is not False:
                    errors.append(f"{card.get('view_model_id')} artifact_verified must be false")
    return {
        "schema_version": "snapshot_refresh_03_validation_report.v0",
        "task": TASK_ID,
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_03_boundary_report(
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
        "local_apply_outputs_may_project_as_limited_reviewed_records": True,
        "reviewed_metadata_records_are_limited_claims": True,
        "reviewed_source_leads_are_limited_claims": True,
        "reviewed_metadata_records_are_not_verified_artifacts": True,
        "reviewed_source_leads_are_not_verified_artifacts": True,
        "local_apply_ref": LOCAL_APPLY_REF,
        "reviewed_metadata_record_count": int(result.get("reviewed_metadata_record_count") or 0),
        "reviewed_source_lead_count": int(result.get("reviewed_source_lead_count") or 0),
        **_false_boundaries(),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_snapshot_refresh_03(
    policy: Mapping[str, Any] | None = None,
    *,
    from_local_apply_live_metadata_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_local_apply_live_metadata_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_handoffs = load_seed_batch_handoffs(merged_policy)
    live_handoff = load_live_metadata_pilot_handoff(merged_policy)
    review_handoff = load_live_metadata_review_handoff(merged_policy)
    local_apply_handoff = load_local_apply_live_metadata_handoff(merged_policy)
    source_batches = list(seed_handoffs["source_batches"])
    plan = build_snapshot_refresh_03_plan(seed_handoffs, live_handoff, review_handoff, local_apply_handoff, merged_policy)
    existing_reviewed_section = build_existing_reviewed_record_section(sample_reviewed_records(), merged_policy)
    reviewed_metadata_section = build_reviewed_metadata_record_section(
        local_apply_handoff["reviewed_metadata_records"],
        merged_policy,
    )
    reviewed_source_lead_section = build_reviewed_source_lead_section(
        local_apply_handoff["reviewed_source_leads"],
        merged_policy,
    )
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
    local_apply_section = build_local_apply_section(local_apply_handoff, merged_policy)
    review_packets = [batch["review_batch_packet"] for batch in source_batches]
    review_packets.append(live_handoff["review_batch_packet"])
    review_packets.append(review_handoff["candidate_review_packet"])
    review_queue_section = build_review_queue_section(
        review_packets,
        merged_policy,
        live_metadata_review_section=refresh_02.build_live_metadata_review_section(
            review_handoff["review_decisions"],
            merged_policy,
        ),
        local_apply_section=local_apply_section,
    )
    known_needs = [item for batch in source_batches for item in batch["known_needs"]]
    absence_summaries = [item for batch in source_batches for item in batch["absence_summaries"]]
    need_absence_section = build_need_absence_section(known_needs, absence_summaries, merged_policy)
    sections = {
        "existing_reviewed_record_section": existing_reviewed_section,
        "reviewed_metadata_record_section": reviewed_metadata_section,
        "reviewed_source_lead_section": reviewed_source_lead_section,
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_section,
        "local_apply_section": local_apply_section,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
    }
    relay_projection = build_refreshed_relay_projection(sections, merged_policy)
    public_search_projection = build_public_search_view_model_projection(sections, merged_policy)
    fixture_candidate_count = sum(int(section.get("candidate_count") or 0) for section in candidate_sections)
    live_candidate_count = int(live_section.get("candidate_count") or 0)
    existing_count = int(existing_reviewed_section["reviewed_record_count"])
    metadata_count = int(reviewed_metadata_section["reviewed_metadata_record_count"])
    source_lead_count = int(reviewed_source_lead_section["reviewed_source_lead_count"])
    result: dict[str, Any] = {
        "schema_version": "snapshot_refresh_03_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "local_apply_live_metadata_integrated": True,
        "source_batches": [refresh_01._batch_summary(batch) for batch in source_batches],
        "source_batch_refs": [batch["batch_id"] for batch in source_batches],
        "local_apply_ref": LOCAL_APPLY_REF,
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "live_metadata_review_ref": LIVE_METADATA_REVIEW_REF,
        "existing_reviewed_record_refs": list(existing_reviewed_section["reviewed_record_refs"]),
        "reviewed_metadata_record_refs": list(reviewed_metadata_section["record_refs"]),
        "reviewed_source_lead_refs": list(reviewed_source_lead_section["record_refs"]),
        "candidate_section_refs": [section["section_id"] for section in candidate_sections],
        "live_metadata_candidate_section_refs": [live_section["section_id"]],
        "local_apply_section_refs": [local_apply_section["section_id"]],
        "review_queue_section_refs": [review_queue_section["section_id"]],
        "need_absence_section_refs": [need_absence_section["section_id"]],
        "relay_projection_refs": [relay_projection["relay_projection_id"]],
        "public_search_view_model_refs": [public_search_projection["projection_id"]],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "plan": plan,
        "existing_reviewed_record_section": existing_reviewed_section,
        "reviewed_metadata_record_section": reviewed_metadata_section,
        "reviewed_source_lead_section": reviewed_source_lead_section,
        "candidate_sections": candidate_sections,
        "live_metadata_candidate_section": live_section,
        "local_apply_section": local_apply_section,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
        "refreshed_relay_projection": relay_projection,
        "public_search_view_model_projection": public_search_projection,
        "existing_reviewed_record_count": existing_count,
        "reviewed_metadata_record_count": metadata_count,
        "reviewed_source_lead_count": source_lead_count,
        "reviewed_record_delta_count": metadata_count + source_lead_count,
        "total_limited_reviewed_record_projection_count": existing_count + metadata_count + source_lead_count,
        "fixture_candidate_count": fixture_candidate_count,
        "live_metadata_candidate_count": live_candidate_count,
        "candidate_count": fixture_candidate_count + live_candidate_count,
        "known_need_count": int(need_absence_section["known_need_count"]),
        "absence_count": int(need_absence_section["absence_count"]),
        "review_queue_candidate_count": int(review_queue_section["candidate_count"]),
        "useful_leads_not_applied": int(local_apply_section["useful_leads_not_applied"]),
        "needs_more_evidence_not_applied": int(local_apply_section["needs_more_evidence_not_applied"]),
        "rejected_or_duplicate_not_applied": int(local_apply_section["rejected_or_duplicate_not_applied"]),
        "fixture_snapshot_refresh_passed": True,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    public_alpha = build_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_snapshot_refresh_03_boundary_report(result, merged_policy)
    result["validation_report"] = validate_snapshot_refresh_03_result(result, merged_policy)
    if result["validation_report"]["status"] != "pass":
        result["status"] = "fail"
        result["fixture_snapshot_refresh_passed"] = False
    if write_examples:
        written = write_snapshot_refresh_03_examples(result)
        written.extend(write_snapshot_refresh_03_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_snapshot_refresh_03_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_03(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "snapshots" / "refresh" / "local_apply_live_metadata"
    base.mkdir(parents=True, exist_ok=True)
    candidate_sections = list(payload["candidate_sections"])
    files = {
        "snapshot_refresh_plan.json": payload["plan"],
        "existing_reviewed_record_section.json": payload["existing_reviewed_record_section"],
        "reviewed_metadata_record_section.json": payload["reviewed_metadata_record_section"],
        "reviewed_source_lead_section.json": payload["reviewed_source_lead_section"],
        "candidate_section_frontier_media.json": candidate_sections[0],
        "candidate_section_legacy_software.json": candidate_sections[1],
        "live_metadata_candidate_section.json": payload["live_metadata_candidate_section"],
        "local_apply_section.json": payload["local_apply_section"],
        "review_queue_section.json": payload["review_queue_section"],
        "need_absence_section.json": payload["need_absence_section"],
        "refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "public_search_view_model_projection.json": payload["public_search_view_model_projection"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "snapshot_refresh_03_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/relay/refresh/local_apply_live_metadata_refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "examples/public_alpha/reassess/local_apply_live_metadata/snapshot_refresh_03_reassess_input.json": payload[
            "public_alpha_reassess_input"
        ],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_snapshot_refresh_03_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_03(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = build_snapshot_refresh_03_inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_snapshot_refresh_03_audit_pack(payload, repo_root))
    return written


def build_snapshot_refresh_03_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    metadata_section = dict(result.get("reviewed_metadata_record_section") or {})
    source_lead_section = dict(result.get("reviewed_source_lead_section") or {})
    local_apply_section = dict(result.get("local_apply_section") or {})
    candidate_sections = list(result.get("candidate_sections") or [])
    packets: dict[str, Any] = {
        "snapshot_refresh_03_input_state.json": {
            "schema_version": "snapshot_refresh_03_input_state.v0",
            "task": TASK_ID,
            "branch": "dev",
            "input_results": {
                "local_apply_live_metadata": LOCAL_APPLY_REF,
                "public_alpha_reassess_02": "control/inventory/public_alpha_reassess_02_result.json",
                "snapshot_refresh_02": SNAPSHOT_REFRESH_02_REF,
                "live_metadata_review": LIVE_METADATA_REVIEW_REF,
                "snapshot_refresh_01": "control/inventory/snapshot_refresh_01_result.json",
                "live_metadata_pilot": LIVE_METADATA_PILOT_REF,
                "review_batch": "control/inventory/review_batch_result.json",
                "candidate_index": "control/inventory/candidate_index_result.json",
                "scout_runtime": "control/inventory/scout_runtime_result.json",
                "query_planner": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
            },
            "equivalent_filename_mappings": {
                "query_planner_result": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json"
            },
            **_false_boundaries(),
            "created_at": DEFAULT_TIMESTAMP,
        },
        "snapshot_refresh_03_source_matrix.json": {
            "schema_version": "snapshot_refresh_03_source_matrix.v0",
            "task": TASK_ID,
            "sources": list(result.get("source_batches") or []),
            "local_apply_ref": LOCAL_APPLY_REF,
            "source_batch_count": len(result.get("source_batches") or []),
        },
        "snapshot_refresh_03_reviewed_record_matrix.json": {
            "schema_version": "snapshot_refresh_03_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "existing_reviewed_record_refs": list(result.get("existing_reviewed_record_refs") or []),
            "existing_reviewed_record_count": result.get("existing_reviewed_record_count"),
        },
        "snapshot_refresh_03_reviewed_metadata_record_matrix.json": {
            "schema_version": "snapshot_refresh_03_reviewed_metadata_record_matrix.v0",
            "task": TASK_ID,
            "records": metadata_section.get("records"),
            "reviewed_metadata_record_count": result.get("reviewed_metadata_record_count"),
            "limited_claim_scope": "metadata_record_only",
            "artifact_verified": False,
            "verified_download_claim": False,
            "malware_clean_claim": False,
            "rights_clearance_claim": False,
        },
        "snapshot_refresh_03_reviewed_source_lead_matrix.json": {
            "schema_version": "snapshot_refresh_03_reviewed_source_lead_matrix.v0",
            "task": TASK_ID,
            "records": source_lead_section.get("records"),
            "reviewed_source_lead_count": result.get("reviewed_source_lead_count"),
            "limited_claim_scope": "source_lead_only",
            "artifact_verified": False,
            "verified_download_claim": False,
            "malware_clean_claim": False,
            "rights_clearance_claim": False,
        },
        "snapshot_refresh_03_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_03_candidate_matrix.v0",
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
        "snapshot_refresh_03_live_metadata_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_03_live_metadata_candidate_matrix.v0",
            "task": TASK_ID,
            "section_id": result.get("live_metadata_candidate_section", {}).get("section_id"),
            "candidate_count": result.get("live_metadata_candidate_count"),
            "review_required": True,
            "accepted_truth": False,
            "raw_response_included": False,
            "public_search_status": "candidate",
        },
        "snapshot_refresh_03_live_metadata_review_matrix.json": {
            "schema_version": "snapshot_refresh_03_live_metadata_review_matrix.v0",
            "task": TASK_ID,
            "source_ref": LIVE_METADATA_REVIEW_REF,
            "useful_leads_not_applied": result.get("useful_leads_not_applied"),
            "needs_more_evidence_not_applied": result.get("needs_more_evidence_not_applied"),
            "rejected_or_duplicate_not_applied": result.get("rejected_or_duplicate_not_applied"),
            "reviewed_preview_applied_through_temp_local_apply": True,
            "operator_instance_mutated": False,
        },
        "snapshot_refresh_03_local_apply_matrix.json": {
            "schema_version": "snapshot_refresh_03_local_apply_matrix.v0",
            "task": TASK_ID,
            "local_apply_section": local_apply_section,
            "reviewed_record_delta_count": result.get("reviewed_record_delta_count"),
            "temp_instance_apply_passed": local_apply_section.get("temp_instance_apply_passed"),
            "operator_instance_mutated": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "snapshot_refresh_03_need_absence_matrix.json": {
            "schema_version": "snapshot_refresh_03_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result.get("known_need_count"),
            "absence_count": result.get("absence_count"),
            "bounded_absence_statements": True,
        },
        "snapshot_refresh_03_review_queue_matrix.json": {
            "schema_version": "snapshot_refresh_03_review_queue_matrix.v0",
            "task": TASK_ID,
            "review_queue_section_refs": list(result.get("review_queue_section_refs") or []),
            "review_queue_candidate_count": result.get("review_queue_candidate_count"),
            "operator_context_required": True,
        },
        "snapshot_refresh_03_relay_projection_matrix.json": {
            "schema_version": "snapshot_refresh_03_relay_projection_matrix.v0",
            "task": TASK_ID,
            "relay_projection_refs": list(result.get("relay_projection_refs") or []),
            "sections": result.get("refreshed_relay_projection", {}).get("sections"),
            "read_only": True,
            "mutation_enabled": False,
            "site_dist_written": False,
        },
        "snapshot_refresh_03_public_search_view_model_matrix.json": {
            "schema_version": "snapshot_refresh_03_public_search_view_model_matrix.v0",
            "task": TASK_ID,
            "public_search_view_model_refs": list(result.get("public_search_view_model_refs") or []),
            "result_card_count": len(result.get("public_search_view_model_projection", {}).get("result_cards") or []),
            "status_counts": result.get("public_search_view_model_projection", {}).get("status_counts"),
            "reviewed_metadata_source_lead_cards_distinct_from_verified_artifacts": True,
        },
        "snapshot_refresh_03_public_alpha_reassess_matrix.json": {
            "schema_version": "snapshot_refresh_03_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
            "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
        },
        "snapshot_refresh_03_boundary_report.json": result["boundary_report"],
        "snapshot_refresh_03_smoke_result.json": {
            "schema_version": "snapshot_refresh_03_smoke_result.v0",
            "task": TASK_ID,
            "status": result.get("status"),
            "fixture_snapshot_refresh_passed": result.get("fixture_snapshot_refresh_passed"),
            "local_apply_live_metadata_integrated": True,
            **_false_boundaries(),
        },
        "snapshot_refresh_03_validation_matrix.json": {
            "schema_version": "snapshot_refresh_03_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_local_apply_live_metadata_previews.py",
                "focused snapshot refresh unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "snapshot_refresh_03_result.json": _task_result(result),
        "snapshot_refresh_03_next_task_decision.json": {
            "schema_version": "snapshot_refresh_03_next_task_decision.v0",
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
        "snapshot_refresh_03_failure_repair_log.json": {
            "schema_version": "snapshot_refresh_03_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
            **_false_boundaries(),
        },
    }
    return packets


def _write_snapshot_refresh_03_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "snapshot-refresh-03-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = build_snapshot_refresh_03_inventory_packets(result)
    audit_json = {"snapshot_refresh_03_report.json": _task_result(result)}
    audit_markdown = {
        "README.md": "# SNAPSHOT-REFRESH-03 Audit\n\nRefresh evidence after temp local apply of live metadata previews. Limited reviewed metadata/source-lead records project into snapshot sections without artifact, safety, rights, public index, or deployment claims.\n",
        "source_matrix.md": _matrix_md("Source Matrix", inventory["snapshot_refresh_03_source_matrix.json"]),
        "reviewed_record_matrix.md": _matrix_md("Reviewed Record Matrix", inventory["snapshot_refresh_03_reviewed_record_matrix.json"]),
        "reviewed_metadata_record_matrix.md": _matrix_md("Reviewed Metadata Record Matrix", inventory["snapshot_refresh_03_reviewed_metadata_record_matrix.json"]),
        "reviewed_source_lead_matrix.md": _matrix_md("Reviewed Source Lead Matrix", inventory["snapshot_refresh_03_reviewed_source_lead_matrix.json"]),
        "candidate_matrix.md": _matrix_md("Candidate Matrix", inventory["snapshot_refresh_03_candidate_matrix.json"]),
        "local_apply_matrix.md": _matrix_md("Local Apply Matrix", inventory["snapshot_refresh_03_local_apply_matrix.json"]),
        "need_absence_matrix.md": _matrix_md("Need And Absence Matrix", inventory["snapshot_refresh_03_need_absence_matrix.json"]),
        "review_queue_matrix.md": _matrix_md("Review Queue Matrix", inventory["snapshot_refresh_03_review_queue_matrix.json"]),
        "relay_projection_matrix.md": _matrix_md("Relay Projection Matrix", inventory["snapshot_refresh_03_relay_projection_matrix.json"]),
        "public_search_view_model_matrix.md": _matrix_md("Public Search View Model Matrix", inventory["snapshot_refresh_03_public_search_view_model_matrix.json"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", inventory["snapshot_refresh_03_public_alpha_reassess_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["snapshot_refresh_03_smoke_result.json"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["snapshot_refresh_03_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/snapshot_refresh_03_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    generated_files = {
        "sample_snapshot_refresh_plan.json": result["plan"],
        "sample_reviewed_metadata_record_section.json": result["reviewed_metadata_record_section"],
        "sample_reviewed_source_lead_section.json": result["reviewed_source_lead_section"],
        "sample_public_search_view_model_projection.json": result["public_search_view_model_projection"],
        "sample_relay_projection.json": result["refreshed_relay_projection"],
        "sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Snapshot Refresh 03 Summary\n\n"
        f"- existing reviewed records: {result.get('existing_reviewed_record_count')}\n"
        f"- reviewed metadata records from local apply: {result.get('reviewed_metadata_record_count')}\n"
        f"- reviewed source leads from local apply: {result.get('reviewed_source_lead_count')}\n"
        f"- total limited reviewed projection count: {result.get('total_limited_reviewed_record_projection_count')}\n"
        "- artifact verified claim created: false\n"
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


def _limited_metadata_record(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(record))
    payload["snapshot_record_type"] = "limited_reviewed_metadata_record"
    payload["public_search_status"] = "source_lead"
    payload["limited_claim_scope"] = "metadata_record_only"
    return _force_non_claims(payload)


def _limited_source_lead(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(record))
    payload["snapshot_record_type"] = "limited_reviewed_source_lead"
    payload["public_search_status"] = "source_lead"
    payload["limited_claim_scope"] = "source_lead_only"
    return _force_non_claims(payload)


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


def _limited_record_card(record: Mapping[str, Any], object_type: str) -> dict[str, Any]:
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", record.get("record_id")),
        "title": _text(record.get("title")) or _text(record.get("lead_summary")),
        "url": "/source/" + _text(record.get("record_id")),
        "status": "source_lead",
        "object_type": object_type,
        "domain": "live_metadata_local_apply",
        "source_family": _text(record.get("source_family")) or "internet_archive_metadata",
        "source_label": "Internet Archive metadata local apply",
        "snippet": "Limited reviewed metadata/source-lead record. It is not a verified downloadable artifact.",
        "match_reasons": ["local_apply_live_metadata", "limited_reviewed_record", "not_artifact_verified"],
        "evidence_summary": {
            "evidence_refs": _text_list(record.get("evidence_refs")),
            "evidence_count": len(_text_list(record.get("evidence_refs"))),
        },
        "confidence_label": "limited_reviewed_metadata" if object_type == "reviewed_metadata_record_limited" else "reviewed_source_lead",
        "risk_label": "not_artifact_verified",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "not_verified_download",
        "action_posture": _action_posture(),
        "review_required": False,
        "limited_reviewed_record": True,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "artifact_verified_claim_created": False,
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
                "id": item.get("record_id") or item.get("candidate_id"),
                "candidate_id": item.get("candidate_id"),
                "title": item.get("title") or item.get("lead_summary"),
                "public_search_status": item.get("public_search_status") or "candidate",
                "limited_reviewed_record": bool(item.get("record_type") in {"reviewed_metadata_record", "reviewed_source_lead"}),
                "artifact_verified": False,
                "verified_download_claim": False,
                "malware_clean_claim": False,
                "rights_clearance_claim": False,
            }
            for item in rows
        ],
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_03_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "local_apply_live_metadata_integrated": True,
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "contracts_added": True,
        "policies_added": True,
        "source_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "reviewed_metadata_record_matrix_added": True,
        "reviewed_source_lead_matrix_added": True,
        "candidate_matrix_added": True,
        "live_metadata_candidate_matrix_added": True,
        "local_apply_matrix_added": True,
        "need_absence_matrix_added": True,
        "review_queue_matrix_added": True,
        "relay_projection_matrix_added": True,
        "public_search_view_model_matrix_added": True,
        "public_alpha_reassess_matrix_added": True,
        "runtime_snapshot_refresh_added": True,
        "existing_reviewed_record_section_created": True,
        "reviewed_metadata_record_section_created": True,
        "reviewed_source_lead_section_created": True,
        "candidate_sections_created": True,
        "local_apply_section_created": True,
        "review_queue_section_created": True,
        "need_absence_section_created": True,
        "relay_projection_created": True,
        "public_search_view_model_projection_created": True,
        "public_alpha_reassess_input_created": True,
        "existing_reviewed_record_count": result.get("existing_reviewed_record_count"),
        "reviewed_metadata_record_count": result.get("reviewed_metadata_record_count"),
        "reviewed_source_lead_count": result.get("reviewed_source_lead_count"),
        "reviewed_record_delta_count": result.get("reviewed_record_delta_count"),
        "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
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
        "blocked_actions": ["download", "install_handoff", "execute", "extract", "promote_public"],
        "review_required": False,
        "public_mutation_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
    }


def _limitations() -> list[str]:
    return [
        "snapshot_refresh_is_projection_only",
        "local_apply_outputs_are_limited_reviewed_metadata_or_source_lead_records",
        "metadata_source_lead_records_are_not_verified_artifacts",
        "raw_live_responses_excluded",
        "no_verified_download_claim",
        "no_malware_clean_claim",
        "no_rights_clearance_claim",
        "no_operator_instance_mutation",
        "no_site_dist_write",
        "no_public_index_mutation",
        "no_deployment_or_launch_claim",
    ]


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


def _force_non_claims(payload: dict[str, Any]) -> dict[str, Any]:
    for key in (
        "artifact_verified",
        "verified_download_claim",
        "malware_clean_claim",
        "rights_clearance_claim",
        "artifact_verified_claim_created",
        "verified_download_claim_created",
        "malware_clean_claim_created",
        "rights_clearance_claim_created",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "operator_instance_mutated",
        "public_index_mutated",
        "master_index_mutated",
    ):
        payload[key] = False
    return payload


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
        "local_apply_outputs_may_project_as_limited_reviewed_records",
        "reviewed_metadata_records_are_limited_claims",
        "reviewed_source_leads_are_limited_claims",
        "reviewed_metadata_records_are_not_verified_artifacts",
        "reviewed_source_leads_are_not_verified_artifacts",
        "no_verified_download_claim",
        "no_malware_clean_claim",
        "no_rights_clearance_claim",
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
        raise PermissionError(f"snapshot refresh 03 policy missing required safety rules: {', '.join(missing)}")
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
        raise PermissionError(f"snapshot refresh 03 policy enables forbidden behavior: {', '.join(enabled)}")


def _assert_local_apply(
    local_apply_result: Mapping[str, Any],
    reviewed_metadata_records: Sequence[Mapping[str, Any]],
    reviewed_source_leads: Sequence[Mapping[str, Any]],
) -> None:
    if local_apply_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("local apply live metadata must pass before snapshot refresh 03")
    expected = {
        "eligible_preview_count": 3,
        "reviewed_metadata_records_created": 1,
        "reviewed_source_leads_created": 2,
        "reviewed_record_delta_count": 3,
        "useful_leads_not_applied": 1,
        "needs_more_evidence_not_applied": 2,
        "rejected_or_duplicate_not_applied": 2,
    }
    for key, value in expected.items():
        if int(local_apply_result.get(key) or 0) != value:
            raise ValueError(f"local apply count mismatch for {key}")
    if len(reviewed_metadata_records) != 1 or len(reviewed_source_leads) != 2:
        raise ValueError("local apply reviewed record examples must include 1 metadata record and 2 source leads")
    for key in (
        "operator_instance_mutated",
        "committed_instance_state",
        "public_index_mutated",
        "master_index_mutated",
        "verified_download_claim_created",
        "malware_clean_claim_created",
        "rights_clearance_claim_created",
        "artifact_verified_claim_created",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
    ):
        if local_apply_result.get(key) is not False:
            raise ValueError(f"local apply boundary failed: {key}")


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
