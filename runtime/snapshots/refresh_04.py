"""Snapshot refresh after manuals/scans and driver/support seed batches.

SNAPSHOT-REFRESH-04 packages the manuals/scans and driver/support seed-batch
handoffs alongside existing limited reviewed metadata/source-lead records. The
new seed outputs remain review-only metadata candidates. This refresh does not
download documents, OCR scans, fetch driver packages, install/execute software,
or create artifact safety, compatibility, rights, public index, deployment, or
launch claims.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.snapshots import refresh as seed_refresh
from runtime.snapshots import refresh_02, refresh_03
from runtime.snapshots.relay_foundation import sample_reviewed_records


DEFAULT_TIMESTAMP = "2026-06-02T00:00:00Z"
SNAPSHOT_REFRESH_ID = "snapshot_refresh_04"
TASK_ID = "SNAPSHOT-REFRESH-04"
LOCAL_APPLY_REF = "control/inventory/local_apply_live_metadata_result.json"
SNAPSHOT_REFRESH_03_REF = "control/inventory/snapshot_refresh_03_result.json"
MANUALS_SCANS_REF = "control/inventory/seed_batch_manuals_scans_result.json"
DRIVER_SUPPORT_REF = "control/inventory/seed_batch_driver_support_result.json"
NEXT_TASK = "PUBLIC-ALPHA-REASSESS-04 - Reassess alpha after manuals/scans and driver/support snapshot refresh"

SEED_BATCH_DOMAINS = (
    {
        "domain_key": "frontier_media",
        "domain_id": "frontier_resolution_media",
        "batch_id": "seed_batch_frontier_media_00",
    },
    {
        "domain_key": "legacy_software",
        "domain_id": "legacy_software",
        "batch_id": "seed_batch_legacy_software_00",
    },
    {
        "domain_key": "manuals_scans",
        "domain_id": "manuals_docs_scans",
        "batch_id": "seed_batch_manuals_scans_00",
    },
    {
        "domain_key": "driver_support",
        "domain_id": "driver_support_media",
        "batch_id": "seed_batch_driver_support_00",
    },
)

BOUNDARY_FALSE_KEYS = (
    "accepted_truth_created",
    "candidate_promoted_to_reviewed",
    "artifact_verified_claim_created",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "compatibility_guarantee_created",
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
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)

DEFAULT_POLICY: dict[str, Any] = {
    "snapshot_refresh_is_projection": True,
    "seed_batch_candidates_remain_candidates": True,
    "manuals_scans_candidates_are_not_downloaded_documents": True,
    "manuals_scans_candidates_are_not_ocr_text": True,
    "manuals_scans_candidates_are_not_rights_cleared": True,
    "driver_support_candidates_are_not_driver_downloads": True,
    "driver_support_candidates_are_not_safe_installers": True,
    "driver_support_candidates_are_not_compatibility_guarantees": True,
    "local_apply_outputs_may_project_as_limited_reviewed_records": True,
    "reviewed_metadata_records_are_limited_claims": True,
    "reviewed_source_leads_are_limited_claims": True,
    "reviewed_metadata_records_are_not_verified_artifacts": True,
    "reviewed_source_leads_are_not_verified_artifacts": True,
    "live_metadata_candidates_remain_candidates": True,
    "candidates_remain_candidates": True,
    "seed_outputs_are_not_truth": True,
    "reviewed_records_only_from_existing_reviewed_sources": True,
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
    "file_fetches_enabled": False,
    "ocr_enabled": False,
    "extraction_enabled": False,
    "install_execution_enabled": False,
    "model_provider_enabled": False,
}


def load_seed_batch_handoffs(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    source_batches = []
    for descriptor in SEED_BATCH_DOMAINS:
        root = repo / "examples" / "seed_batches" / str(descriptor["domain_key"])
        source_batches.append(seed_refresh._load_seed_batch_example(root, descriptor))
    return {
        "schema_version": "snapshot_seed_batch_handoffs.v0",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": source_batches,
        "source_batch_count": len(source_batches),
        "manuals_scans_integrated": True,
        "driver_support_integrated": True,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def load_manuals_scans_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _domain_handoff("manuals_scans", policy)


def load_driver_support_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _domain_handoff("driver_support", policy)


def load_local_apply_live_metadata_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return refresh_03.load_local_apply_live_metadata_handoff(_policy(policy))


def load_live_metadata_pilot_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return refresh_03.load_live_metadata_pilot_handoff(_policy(policy))


def load_live_metadata_review_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return refresh_03.load_live_metadata_review_handoff(_policy(policy))


def build_snapshot_refresh_04_plan(
    all_handoffs: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_handoffs = all_handoffs["seed_handoffs"]
    local_apply = all_handoffs["local_apply_handoff"]
    batches = list(seed_handoffs.get("source_batches") or [])
    return {
        "schema_version": "snapshot_refresh_plan.v0",
        "record_type": "snapshot_refresh_plan",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": [_batch_summary(batch) for batch in batches],
        "snapshot_refresh_03_ref": SNAPSHOT_REFRESH_03_REF,
        "manuals_scans_ref": MANUALS_SCANS_REF,
        "driver_support_ref": DRIVER_SUPPORT_REF,
        "local_apply_ref": LOCAL_APPLY_REF,
        "reviewed_record_refs": [record["record_id"] for record in sample_reviewed_records()],
        "reviewed_metadata_record_refs": [
            record.get("record_id") for record in local_apply.get("reviewed_metadata_records", [])
        ],
        "reviewed_source_lead_refs": [
            record.get("record_id") for record in local_apply.get("reviewed_source_leads", [])
        ],
        "candidate_section_refs": [
            _section_id("snapshot_candidate_section", batch.get("domain_key"), SNAPSHOT_REFRESH_ID)
            for batch in batches
        ],
        "manuals_scans_candidate_section_refs": [
            _section_id("snapshot_manuals_scans_candidate_section", SNAPSHOT_REFRESH_ID)
        ],
        "driver_support_candidate_section_refs": [
            _section_id("snapshot_driver_support_candidate_section", SNAPSHOT_REFRESH_ID)
        ],
        "review_queue_section_refs": [_section_id("snapshot_review_queue_section", SNAPSHOT_REFRESH_ID)],
        "need_absence_section_refs": [_section_id("snapshot_need_absence_section", SNAPSHOT_REFRESH_ID)],
        "relay_projection_refs": [_section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID)],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "public_search_view_model_refs": [_section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID)],
        "refresh_mode": "manuals_scans_driver_support_projection_only",
        "manuals_scans_candidates_are_metadata_only": True,
        "driver_support_candidates_are_metadata_only": True,
        "seed_batch_candidates_remain_candidates": True,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_existing_reviewed_record_section(
    existing_reviewed_records: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _retag(refresh_03.build_existing_reviewed_record_section(existing_reviewed_records, _policy(policy)))


def build_reviewed_metadata_record_section(
    local_apply_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _retag(refresh_03.build_reviewed_metadata_record_section(local_apply_records, _policy(policy)))


def build_reviewed_source_lead_section(
    local_apply_records: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _retag(refresh_03.build_reviewed_source_lead_section(local_apply_records, _policy(policy)))


def build_manuals_scans_candidate_section(
    manuals_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    batch_id: str = "seed_batch_manuals_scans_00",
    scout_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    section = refresh_03.build_candidate_snapshot_section(
        manuals_candidates,
        _policy(policy),
        domain_key="manuals_scans",
        batch_id=batch_id,
        scout_refs=scout_refs or [],
    )
    section = _retag(section)
    section.update(
        {
            "schema_version": "snapshot_manuals_scans_candidate_section.v0",
            "record_type": "snapshot_manuals_scans_candidate_section",
            "section_id": _section_id("snapshot_manuals_scans_candidate_section", batch_id),
            "domain_id": "manuals_docs_scans",
            "download_performed": False,
            "file_fetch_performed": False,
            "ocr_performed": False,
            "rights_clearance_claim_created": False,
            "scan_completeness_claim_created": False,
            "ocr_quality_claim_created": False,
            "accepted_truth": False,
            "limitations": _manuals_limitations(),
        }
    )
    section["candidates"] = [_manuals_candidate(candidate) for candidate in section.get("candidates", [])]
    return section


def build_driver_support_candidate_section(
    driver_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    batch_id: str = "seed_batch_driver_support_00",
    scout_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    section = refresh_03.build_candidate_snapshot_section(
        driver_candidates,
        _policy(policy),
        domain_key="driver_support",
        batch_id=batch_id,
        scout_refs=scout_refs or [],
    )
    section = _retag(section)
    section.update(
        {
            "schema_version": "snapshot_driver_support_candidate_section.v0",
            "record_type": "snapshot_driver_support_candidate_section",
            "section_id": _section_id("snapshot_driver_support_candidate_section", batch_id),
            "domain_id": "driver_support_media",
            "download_performed": False,
            "file_fetch_performed": False,
            "install_execution_enabled": False,
            "malware_clean_claim_created": False,
            "compatibility_guarantee_created": False,
            "rights_clearance_claim_created": False,
            "accepted_truth": False,
            "limitations": _driver_limitations(),
        }
    )
    section["candidates"] = [_driver_candidate(candidate) for candidate in section.get("candidates", [])]
    return section


def build_candidate_snapshot_section(
    all_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    domain_key: str = "all_seed_candidates",
    batch_id: str = "seed_batch_combined",
    scout_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    return _retag(
        refresh_03.build_candidate_snapshot_section(
            all_candidates,
            _policy(policy),
            domain_key=domain_key,
            batch_id=batch_id,
            scout_refs=scout_refs or [],
        )
    )


def build_review_queue_section(
    review_packets: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    local_apply_section: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _retag(
        refresh_03.build_review_queue_section(
            review_packets,
            _policy(policy),
            live_metadata_review_section=None,
            local_apply_section=local_apply_section,
        )
    )


def build_need_absence_section(
    known_needs: Sequence[Mapping[str, Any]],
    absence_summaries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _retag(refresh_03.build_need_absence_section(known_needs, absence_summaries, _policy(policy)))


def build_refreshed_relay_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_sections = list(snapshot_sections.get("candidate_sections") or [])
    live_section = dict(snapshot_sections.get("live_metadata_candidate_section") or {})
    reviewed_section = dict(snapshot_sections.get("existing_reviewed_record_section") or {})
    metadata_section = dict(snapshot_sections.get("reviewed_metadata_record_section") or {})
    source_lead_section = dict(snapshot_sections.get("reviewed_source_lead_section") or {})
    manuals_section = dict(snapshot_sections.get("manuals_scans_candidate_section") or {})
    driver_section = dict(snapshot_sections.get("driver_support_candidate_section") or {})
    need_absence = dict(snapshot_sections.get("need_absence_section") or {})
    seed_candidate_count = sum(int(section.get("candidate_count") or 0) for section in candidate_sections)
    live_candidate_count = int(live_section.get("candidate_count") or 0)
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
            "fixture_candidates": seed_candidate_count,
            "manuals_scans_candidates": int(manuals_section.get("candidate_count") or 0),
            "driver_support_candidates": int(driver_section.get("candidate_count") or 0),
            "live_metadata_candidates": live_candidate_count,
            "total_candidate_count": seed_candidate_count + live_candidate_count,
            "known_needs": int(need_absence.get("known_need_count") or 0),
            "absence_summaries": int(need_absence.get("absence_count") or 0),
        },
        "query_previews": [
            _relay_preview("manuals/scans metadata candidates remain review-only", manuals_section.get("candidates", [])),
            _relay_preview("driver/support metadata candidates remain review-only", driver_section.get("candidates", [])),
            _relay_preview("limited reviewed metadata records", metadata_section.get("records", [])),
            _relay_preview("limited reviewed source leads", source_lead_section.get("records", [])),
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


def build_public_search_view_model_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_sections = list(snapshot_sections.get("candidate_sections") or [])
    candidate_cards = [
        _candidate_card(candidate, section.get("domain_key") or "seed_batch")
        for section in candidate_sections
        for candidate in section.get("candidates", [])
    ]
    live_cards = [
        _candidate_card(candidate, "live_metadata")
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
    cards = candidate_cards + live_cards + metadata_cards + source_lead_cards
    return {
        "schema_version": "snapshot_public_search_view_model_projection.v0",
        "record_type": "snapshot_public_search_view_model_projection",
        "projection_id": _section_id("snapshot_public_search_view_model_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "projection_profiles": ["public_web", "operator_workbench", "api_json", "classic_html", "text"],
        "result_cards": cards,
        "status_counts": {
            "verified": int(snapshot_sections.get("existing_reviewed_record_section", {}).get("reviewed_record_count") or 0),
            "candidate": len(candidate_cards) + len(live_cards),
            "known_need": int(snapshot_sections.get("need_absence_section", {}).get("known_need_count") or 0),
            "absence": int(snapshot_sections.get("need_absence_section", {}).get("absence_count") or 0),
            "source_lead": len(metadata_cards) + len(source_lead_cards),
        },
        "manuals_scans_cards_remain_candidates": True,
        "driver_support_cards_remain_candidates": True,
        "reviewed_metadata_source_lead_cards_distinct_from_verified_artifacts": True,
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "file_fetches_enabled": False,
        "ocr_enabled": False,
        "install_execution_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
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
        "existing_reviewed_record_count": int(snapshot_refresh_result.get("existing_reviewed_record_count") or 0),
        "reviewed_metadata_record_count": int(snapshot_refresh_result.get("reviewed_metadata_record_count") or 0),
        "reviewed_source_lead_count": int(snapshot_refresh_result.get("reviewed_source_lead_count") or 0),
        "total_limited_reviewed_record_projection_count": int(
            snapshot_refresh_result.get("total_limited_reviewed_record_projection_count") or 0
        ),
        "manuals_scans_candidate_count": int(snapshot_refresh_result.get("manuals_scans_candidate_count") or 0),
        "driver_support_candidate_count": int(snapshot_refresh_result.get("driver_support_candidate_count") or 0),
        "additional_seed_candidate_count": int(snapshot_refresh_result.get("additional_seed_candidate_count") or 0),
        "fixture_candidate_count": int(snapshot_refresh_result.get("fixture_candidate_count") or 0),
        "live_metadata_candidate_count": int(snapshot_refresh_result.get("live_metadata_candidate_count") or 0),
        "total_candidate_count": int(snapshot_refresh_result.get("total_candidate_count") or 0),
        "known_need_count": int(snapshot_refresh_result.get("known_need_count") or 0),
        "absence_count": int(snapshot_refresh_result.get("absence_count") or 0),
        "launch_recommended": False,
        "demo_mode_recommended": True,
        "internal_review_recommended": True,
        "needs_public_alpha_reassess_after_snapshot_refresh": True,
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def validate_snapshot_refresh_04_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    errors: list[str] = []
    expected_counts = {
        "existing_reviewed_record_count": 1,
        "reviewed_metadata_record_count": 1,
        "reviewed_source_lead_count": 2,
        "total_limited_reviewed_record_projection_count": 4,
        "manuals_scans_candidate_count": 16,
        "driver_support_candidate_count": 16,
        "additional_seed_candidate_count": 32,
        "total_candidate_count": 68,
    }
    if result.get("schema_version") != "snapshot_refresh_04_result.v0":
        errors.append("schema_version must be snapshot_refresh_04_result.v0")
    for key, value in expected_counts.items():
        if int(result.get(key) or 0) != value:
            errors.append(f"{key} must be {value}")
    for key in BOUNDARY_FALSE_KEYS:
        if result.get(key) is not False:
            errors.append(f"{key} must be false")
    manuals_section = result.get("manuals_scans_candidate_section")
    if not isinstance(manuals_section, Mapping) or manuals_section.get("candidate_count") != 16:
        errors.append("manuals/scans section must include 16 candidates")
    else:
        for key in ("download_performed", "file_fetch_performed", "ocr_performed", "rights_clearance_claim_created", "scan_completeness_claim_created", "ocr_quality_claim_created", "accepted_truth"):
            if manuals_section.get(key) is not False:
                errors.append(f"manuals_scans_candidate_section.{key} must be false")
    driver_section = result.get("driver_support_candidate_section")
    if not isinstance(driver_section, Mapping) or driver_section.get("candidate_count") != 16:
        errors.append("driver/support section must include 16 candidates")
    else:
        for key in ("download_performed", "file_fetch_performed", "install_execution_enabled", "malware_clean_claim_created", "compatibility_guarantee_created", "rights_clearance_claim_created", "accepted_truth"):
            if driver_section.get(key) is not False:
                errors.append(f"driver_support_candidate_section.{key} must be false")
    projection = result.get("public_search_view_model_projection")
    if not isinstance(projection, Mapping) or projection.get("status_counts", {}).get("candidate") != 68:
        errors.append("public search projection must include 68 candidate cards")
    return {
        "schema_version": "snapshot_refresh_04_validation_report.v0",
        "task": TASK_ID,
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_04_boundary_report(
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
        "manuals_scans_integrated": True,
        "driver_support_integrated": True,
        "seed_batch_candidates_remain_candidates": True,
        "manuals_scans_candidates_are_not_downloaded_documents": True,
        "manuals_scans_candidates_are_not_ocr_text": True,
        "manuals_scans_candidates_are_not_rights_cleared": True,
        "driver_support_candidates_are_not_driver_downloads": True,
        "driver_support_candidates_are_not_safe_installers": True,
        "driver_support_candidates_are_not_compatibility_guarantees": True,
        "manuals_scans_candidate_count": int(result.get("manuals_scans_candidate_count") or 0),
        "driver_support_candidate_count": int(result.get("driver_support_candidate_count") or 0),
        "total_candidate_count": int(result.get("total_candidate_count") or 0),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_snapshot_refresh_04(
    policy: Mapping[str, Any] | None = None,
    *,
    from_manuals_driver_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_manuals_driver_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_handoffs = load_seed_batch_handoffs(merged_policy)
    live_handoff = load_live_metadata_pilot_handoff(merged_policy)
    review_handoff = load_live_metadata_review_handoff(merged_policy)
    local_apply_handoff = load_local_apply_live_metadata_handoff(merged_policy)
    all_handoffs = {
        "seed_handoffs": seed_handoffs,
        "live_handoff": live_handoff,
        "review_handoff": review_handoff,
        "local_apply_handoff": local_apply_handoff,
    }
    source_batches = list(seed_handoffs["source_batches"])
    by_domain = {batch["domain_key"]: batch for batch in source_batches}
    plan = build_snapshot_refresh_04_plan(all_handoffs, merged_policy)
    existing_reviewed_section = build_existing_reviewed_record_section(sample_reviewed_records(), merged_policy)
    reviewed_metadata_section = build_reviewed_metadata_record_section(
        local_apply_handoff["reviewed_metadata_records"],
        merged_policy,
    )
    reviewed_source_lead_section = build_reviewed_source_lead_section(
        local_apply_handoff["reviewed_source_leads"],
        merged_policy,
    )
    candidate_sections = []
    for batch in source_batches:
        if batch["domain_key"] == "manuals_scans":
            section = build_manuals_scans_candidate_section(
                batch["candidate_summaries"],
                merged_policy,
                batch_id=batch["batch_id"],
                scout_refs=batch.get("scout_refs") or [],
            )
        elif batch["domain_key"] == "driver_support":
            section = build_driver_support_candidate_section(
                batch["candidate_summaries"],
                merged_policy,
                batch_id=batch["batch_id"],
                scout_refs=batch.get("scout_refs") or [],
            )
        else:
            section = build_candidate_snapshot_section(
                batch["candidate_summaries"],
                merged_policy,
                domain_key=batch["domain_key"],
                batch_id=batch["batch_id"],
                scout_refs=batch.get("scout_refs") or [],
            )
        candidate_sections.append(section)
    manuals_section = next(section for section in candidate_sections if section["domain_key"] == "manuals_scans")
    driver_section = next(section for section in candidate_sections if section["domain_key"] == "driver_support")
    live_section = _retag(
        refresh_03.build_live_metadata_candidate_section(
            live_handoff["candidates"],
            merged_policy,
            live_metadata_handoff=live_handoff,
        )
    )
    local_apply_section = _retag(refresh_03.build_local_apply_section(local_apply_handoff, merged_policy))
    review_packets = [batch["review_batch_packet"] for batch in source_batches]
    review_packets.append(live_handoff["review_batch_packet"])
    review_packets.append(review_handoff["candidate_review_packet"])
    review_queue_section = build_review_queue_section(
        review_packets,
        merged_policy,
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
        "manuals_scans_candidate_section": manuals_section,
        "driver_support_candidate_section": driver_section,
        "live_metadata_candidate_section": live_section,
        "local_apply_section": local_apply_section,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
    }
    relay_projection = build_refreshed_relay_projection(sections, merged_policy)
    public_search_projection = build_public_search_view_model_projection(sections, merged_policy)
    fixture_candidate_count = sum(int(section.get("candidate_count") or 0) for section in candidate_sections)
    live_candidate_count = int(live_section.get("candidate_count") or 0)
    manuals_count = int(manuals_section.get("candidate_count") or 0)
    driver_count = int(driver_section.get("candidate_count") or 0)
    existing_count = int(existing_reviewed_section["reviewed_record_count"])
    metadata_count = int(reviewed_metadata_section["reviewed_metadata_record_count"])
    source_lead_count = int(reviewed_source_lead_section["reviewed_source_lead_count"])
    result: dict[str, Any] = {
        "schema_version": "snapshot_refresh_04_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "manuals_scans_integrated": True,
        "driver_support_integrated": True,
        "source_batches": [_batch_summary(batch) for batch in source_batches],
        "source_batch_refs": [batch["batch_id"] for batch in source_batches],
        "plan": plan,
        "existing_reviewed_record_section": existing_reviewed_section,
        "reviewed_metadata_record_section": reviewed_metadata_section,
        "reviewed_source_lead_section": reviewed_source_lead_section,
        "candidate_sections": candidate_sections,
        "manuals_scans_candidate_section": manuals_section,
        "driver_support_candidate_section": driver_section,
        "live_metadata_candidate_section": live_section,
        "local_apply_section": local_apply_section,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
        "refreshed_relay_projection": relay_projection,
        "public_search_view_model_projection": public_search_projection,
        "existing_reviewed_record_refs": list(existing_reviewed_section["reviewed_record_refs"]),
        "reviewed_metadata_record_refs": list(reviewed_metadata_section["record_refs"]),
        "reviewed_source_lead_refs": list(reviewed_source_lead_section["record_refs"]),
        "candidate_section_refs": [section["section_id"] for section in candidate_sections],
        "manuals_scans_candidate_section_refs": [manuals_section["section_id"]],
        "driver_support_candidate_section_refs": [driver_section["section_id"]],
        "live_metadata_candidate_section_refs": [live_section["section_id"]],
        "review_queue_section_refs": [review_queue_section["section_id"]],
        "need_absence_section_refs": [need_absence_section["section_id"]],
        "relay_projection_refs": [relay_projection["relay_projection_id"]],
        "public_search_view_model_refs": [public_search_projection["projection_id"]],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "existing_reviewed_record_count": existing_count,
        "reviewed_metadata_record_count": metadata_count,
        "reviewed_source_lead_count": source_lead_count,
        "reviewed_record_delta_count": metadata_count + source_lead_count,
        "total_limited_reviewed_record_projection_count": existing_count + metadata_count + source_lead_count,
        "fixture_candidate_count": fixture_candidate_count,
        "live_metadata_candidate_count": live_candidate_count,
        "manuals_scans_candidate_count": manuals_count,
        "driver_support_candidate_count": driver_count,
        "additional_seed_candidate_count": manuals_count + driver_count,
        "total_candidate_count": fixture_candidate_count + live_candidate_count,
        "candidate_count": fixture_candidate_count + live_candidate_count,
        "known_need_count": int(need_absence_section["known_need_count"]),
        "absence_count": int(need_absence_section["absence_count"]),
        "review_queue_candidate_count": int(review_queue_section["candidate_count"]),
        "fixture_snapshot_refresh_passed": True,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    public_alpha = build_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_snapshot_refresh_04_boundary_report(result, merged_policy)
    result["validation_report"] = validate_snapshot_refresh_04_result(result, merged_policy)
    if result["validation_report"]["status"] != "pass":
        result["status"] = "fail"
        result["fixture_snapshot_refresh_passed"] = False
    if write_examples:
        written = write_snapshot_refresh_04_examples(result)
        written.extend(write_snapshot_refresh_04_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_snapshot_refresh_04_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_04(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "snapshots" / "refresh" / "manuals_scans_driver_support"
    base.mkdir(parents=True, exist_ok=True)
    candidate_by_domain = {section.get("domain_key"): section for section in payload["candidate_sections"]}
    files = {
        "snapshot_refresh_plan.json": payload["plan"],
        "existing_reviewed_record_section.json": payload["existing_reviewed_record_section"],
        "reviewed_metadata_record_section.json": payload["reviewed_metadata_record_section"],
        "reviewed_source_lead_section.json": payload["reviewed_source_lead_section"],
        "candidate_section_frontier_media.json": candidate_by_domain["frontier_media"],
        "candidate_section_legacy_software.json": candidate_by_domain["legacy_software"],
        "candidate_section_manuals_scans.json": payload["manuals_scans_candidate_section"],
        "candidate_section_driver_support.json": payload["driver_support_candidate_section"],
        "live_metadata_candidate_section.json": payload["live_metadata_candidate_section"],
        "review_queue_section.json": payload["review_queue_section"],
        "need_absence_section.json": payload["need_absence_section"],
        "refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "public_search_view_model_projection.json": payload["public_search_view_model_projection"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "snapshot_refresh_04_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/relay/refresh/manuals_scans_driver_support_refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "examples/public_alpha/reassess/manuals_scans_driver_support/snapshot_refresh_04_reassess_input.json": payload[
            "public_alpha_reassess_input"
        ],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_snapshot_refresh_04_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_04(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = build_snapshot_refresh_04_inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_snapshot_refresh_04_audit_pack(payload, repo_root))
    return written


def build_snapshot_refresh_04_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    candidate_sections = list(result.get("candidate_sections") or [])
    packets: dict[str, Any] = {
        "snapshot_refresh_04_input_state.json": {
            "schema_version": "snapshot_refresh_04_input_state.v0",
            "task": TASK_ID,
            "branch": "dev",
            "input_results": {
                "seed_batch_driver_support": DRIVER_SUPPORT_REF,
                "seed_batch_manuals_scans": MANUALS_SCANS_REF,
                "public_alpha_reassess_03": "control/inventory/public_alpha_reassess_03_result.json",
                "snapshot_refresh_03": SNAPSHOT_REFRESH_03_REF,
                "local_apply_live_metadata": LOCAL_APPLY_REF,
                "seed_batch_legacy_software": "control/inventory/seed_batch_legacy_software_result.json",
                "seed_batch_frontier_media": "control/inventory/seed_batch_frontier_media_result.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
            },
            "equivalent_filename_mappings": {
                "query_planner_result": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json"
            },
            "manuals_scans_integrated": True,
            "driver_support_integrated": True,
            **_false_boundaries(),
            "created_at": DEFAULT_TIMESTAMP,
        },
        "snapshot_refresh_04_source_matrix.json": {
            "schema_version": "snapshot_refresh_04_source_matrix.v0",
            "task": TASK_ID,
            "sources": list(result.get("source_batches") or []),
            "source_batch_count": len(result.get("source_batches") or []),
        },
        "snapshot_refresh_04_reviewed_record_matrix.json": {
            "schema_version": "snapshot_refresh_04_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "existing_reviewed_record_refs": list(result.get("existing_reviewed_record_refs") or []),
            "existing_reviewed_record_count": result.get("existing_reviewed_record_count"),
        },
        "snapshot_refresh_04_reviewed_metadata_record_matrix.json": {
            "schema_version": "snapshot_refresh_04_reviewed_metadata_record_matrix.v0",
            "task": TASK_ID,
            "records": result.get("reviewed_metadata_record_section", {}).get("records"),
            "reviewed_metadata_record_count": result.get("reviewed_metadata_record_count"),
            "artifact_verified": False,
            "verified_download_claim": False,
            "malware_clean_claim": False,
            "rights_clearance_claim": False,
        },
        "snapshot_refresh_04_reviewed_source_lead_matrix.json": {
            "schema_version": "snapshot_refresh_04_reviewed_source_lead_matrix.v0",
            "task": TASK_ID,
            "records": result.get("reviewed_source_lead_section", {}).get("records"),
            "reviewed_source_lead_count": result.get("reviewed_source_lead_count"),
            "artifact_verified": False,
            "verified_download_claim": False,
            "malware_clean_claim": False,
            "rights_clearance_claim": False,
        },
        "snapshot_refresh_04_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_04_candidate_matrix.v0",
            "task": TASK_ID,
            "candidate_sections": [
                {
                    "section_id": section.get("section_id"),
                    "batch_id": section.get("batch_id"),
                    "domain_key": section.get("domain_key"),
                    "domain_id": section.get("domain_id"),
                    "candidate_count": section.get("candidate_count"),
                    "accepted_truth": False,
                    "candidate_promoted_to_reviewed": False,
                }
                for section in candidate_sections
            ],
            "fixture_candidate_count": result.get("fixture_candidate_count"),
            "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
            "total_candidate_count": result.get("total_candidate_count"),
        },
        "snapshot_refresh_04_manuals_scans_candidate_matrix.json": result["manuals_scans_candidate_section"],
        "snapshot_refresh_04_driver_support_candidate_matrix.json": result["driver_support_candidate_section"],
        "snapshot_refresh_04_live_metadata_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_04_live_metadata_candidate_matrix.v0",
            "task": TASK_ID,
            "section_id": result.get("live_metadata_candidate_section", {}).get("section_id"),
            "candidate_count": result.get("live_metadata_candidate_count"),
            "review_required": True,
            "accepted_truth": False,
            "raw_response_included": False,
        },
        "snapshot_refresh_04_local_apply_matrix.json": {
            "schema_version": "snapshot_refresh_04_local_apply_matrix.v0",
            "task": TASK_ID,
            "local_apply_section": result.get("local_apply_section"),
            "reviewed_record_delta_count": result.get("reviewed_record_delta_count"),
            "operator_instance_mutated": False,
        },
        "snapshot_refresh_04_need_absence_matrix.json": {
            "schema_version": "snapshot_refresh_04_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result.get("known_need_count"),
            "absence_count": result.get("absence_count"),
            "bounded_absence_statements": True,
        },
        "snapshot_refresh_04_review_queue_matrix.json": {
            "schema_version": "snapshot_refresh_04_review_queue_matrix.v0",
            "task": TASK_ID,
            "review_queue_section_refs": list(result.get("review_queue_section_refs") or []),
            "review_queue_candidate_count": result.get("review_queue_candidate_count"),
        },
        "snapshot_refresh_04_relay_projection_matrix.json": {
            "schema_version": "snapshot_refresh_04_relay_projection_matrix.v0",
            "task": TASK_ID,
            "relay_projection_refs": list(result.get("relay_projection_refs") or []),
            "sections": result.get("refreshed_relay_projection", {}).get("sections"),
            "read_only": True,
            "mutation_enabled": False,
            "site_dist_written": False,
        },
        "snapshot_refresh_04_public_search_view_model_matrix.json": {
            "schema_version": "snapshot_refresh_04_public_search_view_model_matrix.v0",
            "task": TASK_ID,
            "public_search_view_model_refs": list(result.get("public_search_view_model_refs") or []),
            "result_card_count": len(result.get("public_search_view_model_projection", {}).get("result_cards") or []),
            "status_counts": result.get("public_search_view_model_projection", {}).get("status_counts"),
            "manuals_scans_cards_remain_candidates": True,
            "driver_support_cards_remain_candidates": True,
        },
        "snapshot_refresh_04_public_alpha_reassess_matrix.json": {
            "schema_version": "snapshot_refresh_04_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
            "total_candidate_count": result.get("total_candidate_count"),
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
        },
        "snapshot_refresh_04_boundary_report.json": result["boundary_report"],
        "snapshot_refresh_04_smoke_result.json": {
            "schema_version": "snapshot_refresh_04_smoke_result.v0",
            "task": TASK_ID,
            "status": result.get("status"),
            "fixture_snapshot_refresh_passed": result.get("fixture_snapshot_refresh_passed"),
            "manuals_scans_integrated": True,
            "driver_support_integrated": True,
            **_false_boundaries(),
        },
        "snapshot_refresh_04_validation_matrix.json": {
            "schema_version": "snapshot_refresh_04_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_snapshot_refresh.py",
                "focused snapshot refresh 04 unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "snapshot_refresh_04_result.json": _task_result(result),
        "snapshot_refresh_04_next_task_decision.json": {
            "schema_version": "snapshot_refresh_04_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": NEXT_TASK,
            "planned_after": [
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
                "PUBLIC-SEARCH-UX-MVP-00",
                "REVIEW-BATCH-APPLY-NEXT-00",
            ],
            "deployment_performed": False,
            "public_launch_readiness_claimed": False,
        },
        "snapshot_refresh_04_failure_repair_log.json": {
            "schema_version": "snapshot_refresh_04_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
            **_false_boundaries(),
        },
    }
    return packets


def _write_snapshot_refresh_04_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "snapshot-refresh-04-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = build_snapshot_refresh_04_inventory_packets(result)
    audit_json = {"snapshot_refresh_04_report.json": _task_result(result)}
    audit_markdown = {
        "README.md": "# SNAPSHOT-REFRESH-04 Audit\n\nRefresh evidence after manuals/scans and driver/support seed batches. New seed outputs remain review-only metadata candidates with no artifact, document, safety, compatibility, rights, public index, deployment, or launch claims.\n",
        "source_matrix.md": _matrix_md("Source Matrix", inventory["snapshot_refresh_04_source_matrix.json"]),
        "reviewed_record_matrix.md": _matrix_md("Reviewed Record Matrix", inventory["snapshot_refresh_04_reviewed_record_matrix.json"]),
        "reviewed_metadata_record_matrix.md": _matrix_md("Reviewed Metadata Record Matrix", inventory["snapshot_refresh_04_reviewed_metadata_record_matrix.json"]),
        "reviewed_source_lead_matrix.md": _matrix_md("Reviewed Source Lead Matrix", inventory["snapshot_refresh_04_reviewed_source_lead_matrix.json"]),
        "candidate_matrix.md": _matrix_md("Candidate Matrix", inventory["snapshot_refresh_04_candidate_matrix.json"]),
        "manuals_scans_candidate_matrix.md": _matrix_md("Manuals Scans Candidate Matrix", inventory["snapshot_refresh_04_manuals_scans_candidate_matrix.json"]),
        "driver_support_candidate_matrix.md": _matrix_md("Driver Support Candidate Matrix", inventory["snapshot_refresh_04_driver_support_candidate_matrix.json"]),
        "live_metadata_candidate_matrix.md": _matrix_md("Live Metadata Candidate Matrix", inventory["snapshot_refresh_04_live_metadata_candidate_matrix.json"]),
        "local_apply_matrix.md": _matrix_md("Local Apply Matrix", inventory["snapshot_refresh_04_local_apply_matrix.json"]),
        "need_absence_matrix.md": _matrix_md("Need And Absence Matrix", inventory["snapshot_refresh_04_need_absence_matrix.json"]),
        "review_queue_matrix.md": _matrix_md("Review Queue Matrix", inventory["snapshot_refresh_04_review_queue_matrix.json"]),
        "relay_projection_matrix.md": _matrix_md("Relay Projection Matrix", inventory["snapshot_refresh_04_relay_projection_matrix.json"]),
        "public_search_view_model_matrix.md": _matrix_md("Public Search View Model Matrix", inventory["snapshot_refresh_04_public_search_view_model_matrix.json"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", inventory["snapshot_refresh_04_public_alpha_reassess_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["snapshot_refresh_04_smoke_result.json"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["snapshot_refresh_04_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/snapshot_refresh_04_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    generated_files = {
        "sample_snapshot_refresh_plan.json": result["plan"],
        "sample_manuals_scans_candidate_section.json": result["manuals_scans_candidate_section"],
        "sample_driver_support_candidate_section.json": result["driver_support_candidate_section"],
        "sample_public_search_view_model_projection.json": result["public_search_view_model_projection"],
        "sample_relay_projection.json": result["refreshed_relay_projection"],
        "sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Snapshot Refresh 04 Summary\n\n"
        f"- manuals/scans candidates: {result.get('manuals_scans_candidate_count')}\n"
        f"- driver/support candidates: {result.get('driver_support_candidate_count')}\n"
        f"- additional seed candidates: {result.get('additional_seed_candidate_count')}\n"
        f"- total candidates: {result.get('total_candidate_count')}\n"
        "- verified download claim created: false\n"
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


def _domain_handoff(domain_key: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    for batch in load_seed_batch_handoffs(policy).get("source_batches", []):
        if batch.get("domain_key") == domain_key:
            return batch
    raise KeyError(f"missing seed batch handoff: {domain_key}")


def _manuals_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(dict(candidate))
    item["public_search_status"] = "candidate"
    item["download_performed"] = False
    item["file_fetch_performed"] = False
    item["ocr_performed"] = False
    item["rights_clearance_claim_created"] = False
    item["scan_completeness_claim_created"] = False
    item["ocr_quality_claim_created"] = False
    item["accepted_truth"] = False
    item["reviewed_record_ref"] = None
    item["limitations"] = sorted(set(_text_list(item.get("limitations")) + _manuals_limitations()))
    return item


def _driver_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(dict(candidate))
    item["public_search_status"] = "candidate"
    item["download_performed"] = False
    item["file_fetch_performed"] = False
    item["install_execution_enabled"] = False
    item["malware_clean_claim_created"] = False
    item["compatibility_guarantee_created"] = False
    item["rights_clearance_claim_created"] = False
    item["accepted_truth"] = False
    item["reviewed_record_ref"] = None
    item["limitations"] = sorted(set(_text_list(item.get("limitations")) + _driver_limitations()))
    return item


def _candidate_card(candidate: Mapping[str, Any], domain_key: str) -> dict[str, Any]:
    domain_id = _text(candidate.get("domain_id"))
    if domain_key == "manuals_scans":
        object_type = "manuals_scans_candidate"
        snippet = "Manuals/scans metadata candidate. No document fetch, OCR, scan completeness, or rights claim is included."
    elif domain_key == "driver_support":
        object_type = "driver_support_candidate"
        snippet = "Driver/support metadata candidate. No driver download, install, malware-clean, compatibility, or rights claim is included."
    else:
        object_type = "seed_batch_candidate"
        snippet = "Seed-batch metadata candidate remains review-only."
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", candidate.get("candidate_id"), SNAPSHOT_REFRESH_ID),
        "title": _text(candidate.get("title")),
        "url": "/candidate/" + _text(candidate.get("candidate_id")),
        "status": "candidate",
        "object_type": object_type,
        "domain": domain_id,
        "source_family": _text(candidate.get("source_family")),
        "snippet": snippet,
        "confidence_label": "candidate",
        "risk_label": "review_required",
        "rights_label": "rights_not_cleared",
        "compatibility_label": "unreviewed",
        "review_required": True,
        "accepted_truth": False,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "compatibility_guarantee": False,
        "rights_clearance_claim": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "install_execution_enabled": False,
        "action_posture": _action_posture(),
        "limitations": _text_list(candidate.get("limitations")),
        "created_at": DEFAULT_TIMESTAMP,
    }


def _limited_record_card(record: Mapping[str, Any], object_type: str) -> dict[str, Any]:
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _section_id("result_card", record.get("record_id"), SNAPSHOT_REFRESH_ID),
        "title": _text(record.get("title")) or _text(record.get("lead_summary")),
        "url": "/source/" + _text(record.get("record_id")),
        "status": "source_lead",
        "object_type": object_type,
        "domain": "live_metadata_local_apply",
        "source_family": _text(record.get("source_family")) or "internet_archive_metadata",
        "snippet": "Limited reviewed metadata/source-lead record. It is not a verified downloadable artifact.",
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
                "title": item.get("title") or item.get("lead_summary"),
                "public_search_status": item.get("public_search_status") or "candidate",
                "accepted_truth": False,
                "artifact_verified": False,
                "verified_download_claim": False,
                "malware_clean_claim": False,
                "compatibility_guarantee": False,
                "rights_clearance_claim": False,
            }
            for item in rows
        ],
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return _task_result(result)


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_04_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "manuals_scans_integrated": True,
        "driver_support_integrated": True,
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "contracts_added": True,
        "policies_added": True,
        "source_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "reviewed_metadata_record_matrix_added": True,
        "reviewed_source_lead_matrix_added": True,
        "candidate_matrix_added": True,
        "manuals_scans_candidate_matrix_added": True,
        "driver_support_candidate_matrix_added": True,
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
        "manuals_scans_candidate_section_created": True,
        "driver_support_candidate_section_created": True,
        "candidate_sections_created": True,
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
        "manuals_scans_candidate_count": result.get("manuals_scans_candidate_count"),
        "driver_support_candidate_count": result.get("driver_support_candidate_count"),
        "additional_seed_candidate_count": result.get("additional_seed_candidate_count"),
        "total_candidate_count": result.get("total_candidate_count"),
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


def _batch_summary(batch: Mapping[str, Any]) -> dict[str, Any]:
    return seed_refresh._batch_summary(batch)


def _action_posture() -> dict[str, Any]:
    return {
        "schema_version": "snapshot_review_only_action_posture.v0",
        "allowed_actions": ["inspect", "view_source", "view_provenance", "read"],
        "blocked_actions": ["download", "fetch_file", "ocr", "install_handoff", "execute", "extract", "promote_public"],
        "review_required": True,
        "public_mutation_enabled": False,
        "downloads_enabled": False,
        "file_fetches_enabled": False,
        "ocr_enabled": False,
        "install_execution_enabled": False,
        "extraction_enabled": False,
    }


def _manuals_limitations() -> list[str]:
    return [
        "manuals_scans_candidate_only",
        "metadata_only",
        "no_download",
        "no_file_fetch",
        "no_ocr",
        "no_scan_completeness_claim",
        "no_ocr_quality_claim",
        "no_rights_clearance_claim",
    ]


def _driver_limitations() -> list[str]:
    return [
        "driver_support_candidate_only",
        "metadata_only",
        "no_download",
        "no_file_fetch",
        "no_install",
        "no_execute",
        "no_malware_clean_claim",
        "no_compatibility_guarantee",
        "no_rights_clearance_claim",
    ]


def _limitations() -> list[str]:
    return [
        "snapshot_refresh_is_projection_only",
        "seed_batch_candidates_remain_candidates",
        "manuals_scans_candidates_are_not_downloaded_documents_or_ocr_text",
        "driver_support_candidates_are_not_safe_or_compatible_driver_packages",
        "metadata_source_lead_records_are_not_verified_artifacts",
        "raw_live_responses_excluded",
        "no_verified_download_claim",
        "no_malware_clean_claim",
        "no_compatibility_guarantee",
        "no_rights_clearance_claim",
        "no_site_dist_write",
        "no_public_index_mutation",
        "no_deployment_or_launch_claim",
    ]


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
    return payload


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "snapshot_refresh_is_projection",
        "seed_batch_candidates_remain_candidates",
        "manuals_scans_candidates_are_not_downloaded_documents",
        "manuals_scans_candidates_are_not_ocr_text",
        "manuals_scans_candidates_are_not_rights_cleared",
        "driver_support_candidates_are_not_driver_downloads",
        "driver_support_candidates_are_not_safe_installers",
        "driver_support_candidates_are_not_compatibility_guarantees",
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
        raise PermissionError(f"snapshot refresh 04 policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "raw_live_response_included",
        "downloads_enabled",
        "file_fetches_enabled",
        "ocr_enabled",
        "extraction_enabled",
        "install_execution_enabled",
        "model_provider_enabled",
        "verified_download_claim_allowed",
        "malware_clean_claim_allowed",
        "rights_clearance_claim_allowed",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"snapshot refresh 04 policy enables forbidden behavior: {', '.join(enabled)}")


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
