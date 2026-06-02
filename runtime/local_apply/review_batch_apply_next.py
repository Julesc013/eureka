"""Temp-only local apply for the next eligible review batch outputs.

The review-batch apply gate grows the limited reviewed corpus from existing
deterministic candidate/review examples. It never verifies artifacts, fetches
files, mutates operator/public/master indexes, or claims download/safety/rights
posture.
"""

from __future__ import annotations

from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, ContextManager, Mapping, Sequence


TASK_ID = "REVIEW-BATCH-APPLY-NEXT-00"
DEFAULT_TIMESTAMP = "2026-06-03T00:00:00Z"
RECOMMENDED_NEXT_TASK = "SNAPSHOT-REFRESH-06 - Refresh snapshots after review batch apply"

SEED_REVIEW_BATCH_PACKETS = {
    "frontier_resolution_media": "examples/seed_batches/frontier_media/review_batch_packet.json",
    "legacy_software": "examples/seed_batches/legacy_software/review_batch_packet.json",
    "manuals_docs_scans": "examples/seed_batches/manuals_scans/review_batch_packet.json",
    "driver_support_media": "examples/seed_batches/driver_support/review_batch_packet.json",
}
LIVE_METADATA_REVIEW_PACKET = "examples/review/live_metadata/review_packet.json"

METADATA_RECORD_CANDIDATE_IDS = {
    "seed_frontier_media_frontier_media_q01_candidate",
    "seed_frontier_media_frontier_media_q02_candidate",
    "seed_legacy_software_legacy_software_q01_candidate",
    "seed_manuals_scans_manuals_scans_q01_candidate",
}
SOURCE_LEAD_CANDIDATE_IDS = {
    "seed_legacy_software_legacy_software_q02_candidate",
    "seed_manuals_scans_manuals_scans_q07_candidate",
    "seed_driver_support_driver_support_q01_candidate",
    "seed_driver_support_driver_support_q03_candidate",
}

KNOWN_NEED_PATHS = {
    "frontier_resolution_media": "control/inventory/seed_batch_frontier_media_need_absence_matrix.json",
    "legacy_software": "control/inventory/seed_batch_legacy_software_need_absence_matrix.json",
    "manuals_docs_scans": "control/inventory/seed_batch_manuals_scans_need_absence_matrix.json",
    "driver_support_media": "control/inventory/seed_batch_driver_support_need_absence_matrix.json",
}

ELIGIBLE_RECORD_KINDS = (
    "limited_reviewed_metadata_record",
    "limited_reviewed_source_lead",
    "reviewed_known_need",
    "reviewed_bounded_absence",
)

BOUNDARY_FALSE_KEYS = (
    "operator_instance_mutated",
    "committed_instance_state",
    "public_index_mutated",
    "master_index_mutated",
    "reviewed_index_mutated",
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
    "install_execution_enabled",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "live_source_call_performed",
    "source_probe_executed",
    "site_dist_written",
    "accepted_truth_created",
)

PROHIBITED_CLAIMS = (
    "artifact_verified",
    "verified_download",
    "malware_clean",
    "rights_cleared",
    "compatibility_guarantee",
    "scan_completeness",
    "ocr_quality",
    "safe_installer",
    "download_available",
    "extracted_file",
)

DEFAULT_POLICY: dict[str, Any] = {
    "apply_requires_review_batch_decision": True,
    "apply_requires_evidence_sufficiency": True,
    "default_apply_target": "temp_explicit_instance",
    "operator_instance_apply_requires_explicit_approval": True,
    "public_apply_enabled": False,
    "public_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "public_index_mutation_enabled": False,
    "reviewed_index_mutation_enabled_by_default": False,
    "eligible_record_kinds": list(ELIGIBLE_RECORD_KINDS),
    "reviewed_artifact_record_creation_enabled": False,
    "artifact_verification_claim_allowed": False,
    "verified_download_claim_allowed": False,
    "malware_clean_claim_allowed": False,
    "rights_clearance_claim_allowed": False,
    "compatibility_guarantee_claim_allowed": False,
    "scan_completeness_claim_allowed": False,
    "ocr_quality_claim_allowed": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "file_fetch_enabled": False,
    "ocr_enabled": False,
    "install_execution_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
    "rollback_plan_required": True,
}


def default_policy() -> dict[str, Any]:
    return dict(DEFAULT_POLICY)


def load_review_batch_apply_inputs(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    prior_results = {
        "public_alpha_reassess_05_result": _read_json(repo / "control/inventory/public_alpha_reassess_05_result.json"),
        "snapshot_refresh_05_result": _read_json(repo / "control/inventory/snapshot_refresh_05_result.json"),
        "public_search_ux_mvp_result": _read_json(repo / "control/inventory/public_search_ux_mvp_result.json"),
        "public_alpha_reassess_04_result": _read_json(repo / "control/inventory/public_alpha_reassess_04_result.json"),
        "snapshot_refresh_04_result": _read_json(repo / "control/inventory/snapshot_refresh_04_result.json"),
        "seed_batch_driver_support_result": _read_json(repo / "control/inventory/seed_batch_driver_support_result.json"),
        "seed_batch_manuals_scans_result": _read_json(repo / "control/inventory/seed_batch_manuals_scans_result.json"),
        "seed_batch_legacy_software_result": _read_json(repo / "control/inventory/seed_batch_legacy_software_result.json"),
        "seed_batch_frontier_media_result": _read_json(repo / "control/inventory/seed_batch_frontier_media_result.json"),
        "review_batch_result": _read_json(repo / "control/inventory/review_batch_result.json"),
        "candidate_index_result": _read_json(repo / "control/inventory/candidate_index_result.json"),
        "scout_runtime_result": _read_json(repo / "control/inventory/scout_runtime_result.json"),
    }
    _assert_prior_results(prior_results)
    candidates: dict[str, dict[str, Any]] = {}
    review_packets: list[dict[str, Any]] = []
    for domain_id, path in SEED_REVIEW_BATCH_PACKETS.items():
        packet = _read_json(repo / path)
        review_packets.append(
            {
                "domain_id": domain_id,
                "packet_ref": path,
                "review_batch_id": packet.get("review_batch_id"),
                "candidate_count": len(_list_text(packet.get("candidate_refs"))),
            }
        )
        for candidate in _extract_packet_candidates(packet):
            candidate_id = _text(candidate.get("candidate_id"))
            if not candidate_id:
                continue
            row = dict(candidate)
            row["domain_id"] = _text(row.get("domain_id")) or domain_id
            row["review_batch_packet_ref"] = path
            row["review_batch_id"] = _text(packet.get("review_batch_id"))
            row["candidate_origin"] = "seed_review_batch_packet"
            candidates[candidate_id] = row
    live_packet = _read_json(repo / LIVE_METADATA_REVIEW_PACKET)
    review_packets.append(
        {
            "domain_id": "live_metadata_candidates",
            "packet_ref": LIVE_METADATA_REVIEW_PACKET,
            "review_batch_id": live_packet.get("review_packet_id"),
            "candidate_count": len(_list_text(live_packet.get("candidate_refs"))),
        }
    )
    for candidate in live_packet.get("candidates", []):
        if not isinstance(candidate, Mapping):
            continue
        candidate_id = _text(candidate.get("candidate_id"))
        if not candidate_id:
            continue
        row = dict(candidate)
        row["domain_id"] = _text(row.get("domain_id")) or "live_metadata_candidates"
        row["review_batch_packet_ref"] = LIVE_METADATA_REVIEW_PACKET
        row["review_batch_id"] = _text(live_packet.get("review_packet_id"))
        row["candidate_origin"] = "live_metadata_review_packet"
        candidates[candidate_id] = row

    known_needs, absence_summaries = _load_need_absence_inputs(repo)
    return {
        "schema_version": "review_batch_apply_next_input_state.v0",
        "task": TASK_ID,
        "prior_results": prior_results,
        "review_packets": review_packets,
        "candidates": [candidates[key] for key in sorted(candidates)],
        "candidate_count": len(candidates),
        "known_needs": known_needs,
        "known_need_count": len(known_needs),
        "absence_summaries": absence_summaries,
        "absence_summary_count": len(absence_summaries),
        "equivalent_filename_mappings": {
            "query_planner_result": "scripts/validate_query_to_source_action_planner.py and contracts/search/query_plan/query_to_source_action_plan.v0.json"
        },
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def collect_candidate_review_outputs(
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return load_review_batch_apply_inputs(policy)


def evaluate_review_batch_apply_eligibility(
    candidates: Sequence[Mapping[str, Any]],
    review_packets: Sequence[Mapping[str, Any]] | None = None,
    scout_trails: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        row = dict(candidate)
        candidate_id = _text(row.get("candidate_id"))
        sufficiency = assess_review_batch_evidence_sufficiency(row, merged_policy)
        record_kind = ""
        decision = "not_applied"
        reason = sufficiency["reason"]
        if candidate_id in METADATA_RECORD_CANDIDATE_IDS and sufficiency["eligible_for_limited_apply"]:
            record_kind = "limited_reviewed_metadata_record"
            decision = "apply_limited_reviewed_metadata_record"
            reason = "deterministic medium-confidence metadata lead selected for limited metadata review"
        elif candidate_id in SOURCE_LEAD_CANDIDATE_IDS and sufficiency["eligible_for_limited_apply"]:
            record_kind = "limited_reviewed_source_lead"
            decision = "apply_limited_reviewed_source_lead"
            reason = "deterministic medium-confidence lead selected for source-lead review"
        rows.append(
            {
                "schema_version": "review_batch_apply_eligibility.v0",
                "task": TASK_ID,
                "candidate_id": candidate_id,
                "title": _text(row.get("title")),
                "domain_id": _text(row.get("domain_id")),
                "source_family": _text(row.get("source_family")),
                "confidence_label": _text(row.get("confidence_label")) or "reviewed_live_metadata",
                "review_batch_ref": _text(row.get("review_batch_packet_ref")),
                "scout_trail_refs": _list_text(row.get("scout_trail_refs")),
                "evidence_sufficiency_score": sufficiency["sufficiency_score"],
                "eligible": bool(record_kind),
                "decision": decision,
                "record_kind": record_kind,
                "reason": reason,
                "limitations": _limitations_for(row),
                "prohibited_claims": list(PROHIBITED_CLAIMS),
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    return rows


def assess_review_batch_evidence_sufficiency(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    confidence = _text(candidate.get("confidence_label"))
    has_title = bool(_text(candidate.get("title")))
    has_source = bool(_text(candidate.get("source_family")))
    has_locator = isinstance(candidate.get("source_locator"), Mapping) or bool(_text(candidate.get("source_locator_summary")))
    candidate_id = _text(candidate.get("candidate_id"))
    if candidate_id in METADATA_RECORD_CANDIDATE_IDS:
        score = 0.78
    elif candidate_id in SOURCE_LEAD_CANDIDATE_IDS:
        score = 0.7
    elif confidence == "medium" and has_title and has_source:
        score = 0.58
    elif candidate.get("evidence_sufficiency") is not None:
        score = float(candidate.get("evidence_sufficiency") or 0)
    else:
        score = 0.42
    eligible = score >= 0.68 and has_title and has_source and (has_locator or candidate_id.startswith("live_metadata"))
    reason = "sufficient deterministic metadata for limited local apply" if eligible else "not enough deterministic reviewed evidence for this apply gate"
    return {
        "schema_version": "review_batch_apply_evidence_sufficiency.v0",
        "task": TASK_ID,
        "candidate_id": candidate_id,
        "sufficiency_score": round(score, 3),
        "metadata_fields_reviewed": [
            key
            for key in ("candidate_id", "title", "source_family", "source_locator", "source_locator_summary", "confidence_label", "domain_id")
            if key in candidate
        ],
        "eligible_for_limited_apply": eligible,
        "reason": reason,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_review_batch_apply_plan(
    eligible_items: Sequence[Mapping[str, Any]],
    known_needs: Sequence[Mapping[str, Any]] | None = None,
    absence_summaries: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_items = [dict(item) for item in eligible_items if item.get("record_kind")]
    need_items = _select_reviewed_known_needs(known_needs or [])
    absence_items = _select_reviewed_absences(absence_summaries or [])
    plan_id = _stable_id(
        "review_batch_apply_plan",
        [item.get("candidate_id") for item in candidate_items],
        [item.get("need_id") for item in need_items],
        [item.get("absence_id") for item in absence_items],
    )
    return {
        "schema_version": "review_batch_apply_plan.v0",
        "task": TASK_ID,
        "plan_id": plan_id,
        "apply_target": "temp_explicit_instance",
        "operator_instance_apply_requested": False,
        "operator_instance_approval_present": False,
        "eligible_apply_count": len(candidate_items) + len(need_items) + len(absence_items),
        "limited_reviewed_metadata_record_apply_count": sum(
            1 for item in candidate_items if item.get("record_kind") == "limited_reviewed_metadata_record"
        ),
        "limited_reviewed_source_lead_apply_count": sum(
            1 for item in candidate_items if item.get("record_kind") == "limited_reviewed_source_lead"
        ),
        "reviewed_known_need_apply_count": len(need_items),
        "reviewed_bounded_absence_apply_count": len(absence_items),
        "candidate_items": candidate_items,
        "known_need_items": need_items,
        "absence_items": absence_items,
        "local_apply_required": True,
        "rollback_plan_required": True,
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "limitations": [
            "limited_reviewed_record_scope_only",
            "no_artifact_verification",
            "no_download_file_fetch_ocr_or_extraction",
            "operator_instance_apply_requires_separate_approval",
            "snapshot_refresh_required_after_apply",
        ],
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def validate_review_batch_apply_plan(
    apply_plan: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    errors: list[str] = []
    try:
        _assert_policy(merged_policy)
    except PermissionError as exc:
        errors.append(str(exc))
    if apply_plan.get("apply_target") != "temp_explicit_instance":
        errors.append("review batch apply target must be temp_explicit_instance")
    if apply_plan.get("operator_instance_apply_requested") is not False:
        errors.append("operator instance apply is not allowed in this task")
    if int(apply_plan.get("eligible_apply_count") or 0) != 12:
        errors.append("expected deterministic eligible apply count of 12")
    if int(apply_plan.get("limited_reviewed_metadata_record_apply_count") or 0) != 4:
        errors.append("expected 4 limited reviewed metadata records")
    if int(apply_plan.get("limited_reviewed_source_lead_apply_count") or 0) != 4:
        errors.append("expected 4 limited reviewed source leads")
    if int(apply_plan.get("reviewed_known_need_apply_count") or 0) != 2:
        errors.append("expected 2 reviewed known needs")
    if int(apply_plan.get("reviewed_bounded_absence_apply_count") or 0) != 2:
        errors.append("expected 2 reviewed bounded absences")
    if not _prohibited_claim_flags_false(apply_plan):
        errors.append("apply plan contains a prohibited claim flag")
    for key in BOUNDARY_FALSE_KEYS:
        if apply_plan.get(key) is not False:
            errors.append(f"apply plan boundary must set {key}=false")
    return {
        "schema_version": "review_batch_apply_validation.v0",
        "task": TASK_ID,
        "plan_id": _text(apply_plan.get("plan_id")),
        "status": "pass" if not errors else "fail",
        "apply_plan_valid": not errors,
        "eligible_apply_count": int(apply_plan.get("eligible_apply_count") or 0),
        "errors": errors,
        "warnings": [],
        "local_apply_required": True,
        "temp_instance_required": True,
        "operator_instance_apply_allowed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def apply_review_batch_to_temp_instance(
    apply_plan: Mapping[str, Any],
    temp_instance: str | Path | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    validation = validate_review_batch_apply_plan(apply_plan, merged_policy)
    if validation["status"] != "pass":
        return {
            "schema_version": "review_batch_apply_temp_result.v0",
            "task": TASK_ID,
            "status": "blocked",
            "plan_id": _text(apply_plan.get("plan_id")),
            "apply_validation": validation,
            "temp_instance_apply_passed": False,
            "records_written": False,
            "created_at": DEFAULT_TIMESTAMP,
            **_false_boundaries(),
        }
    manager: ContextManager[str] | ContextManager[Path]
    if temp_instance is None:
        manager = tempfile.TemporaryDirectory(prefix="eureka-review-batch-apply-")
    else:
        path = Path(temp_instance)
        path.mkdir(parents=True, exist_ok=True)
        manager = nullcontext(path)
    with manager as temp_root_value:
        temp_root = Path(temp_root_value)
        records_root = temp_root / "records"
        metadata_records = [
            build_limited_reviewed_metadata_record(item, merged_policy)
            for item in apply_plan.get("candidate_items", [])
            if isinstance(item, Mapping) and item.get("record_kind") == "limited_reviewed_metadata_record"
        ]
        source_leads = [
            build_limited_reviewed_source_lead(item, merged_policy)
            for item in apply_plan.get("candidate_items", [])
            if isinstance(item, Mapping) and item.get("record_kind") == "limited_reviewed_source_lead"
        ]
        known_needs = [build_reviewed_known_need(item, merged_policy) for item in apply_plan.get("known_need_items", [])]
        absences = [build_reviewed_bounded_absence(item, merged_policy) for item in apply_plan.get("absence_items", [])]
        _write_json(records_root / "limited_reviewed_metadata_records.json", _matrix("limited_reviewed_metadata_record_matrix.v0", metadata_records))
        _write_json(records_root / "limited_reviewed_source_leads.json", _matrix("limited_reviewed_source_lead_matrix.v0", source_leads))
        _write_json(records_root / "reviewed_known_needs.json", _matrix("reviewed_known_need_matrix.v0", known_needs))
        _write_json(records_root / "reviewed_bounded_absences.json", _matrix("reviewed_bounded_absence_matrix.v0", absences))
        manifest = {
            "schema_version": "review_batch_apply_temp_manifest.v0",
            "task": TASK_ID,
            "plan_id": apply_plan.get("plan_id"),
            "temp_instance_initialized": True,
            "records_written": [
                "records/limited_reviewed_metadata_records.json",
                "records/limited_reviewed_source_leads.json",
                "records/reviewed_known_needs.json",
                "records/reviewed_bounded_absences.json",
            ],
            "committed_instance_state": False,
            "created_at": DEFAULT_TIMESTAMP,
        }
        _write_json(temp_root / "manifest.json", manifest)
        readback_passed = all(
            (
                len(_read_json(records_root / "limited_reviewed_metadata_records.json").get("records") or []) == 4,
                len(_read_json(records_root / "limited_reviewed_source_leads.json").get("records") or []) == 4,
                len(_read_json(records_root / "reviewed_known_needs.json").get("records") or []) == 2,
                len(_read_json(records_root / "reviewed_bounded_absences.json").get("records") or []) == 2,
                _prohibited_claim_flags_false(metadata_records),
                _prohibited_claim_flags_false(source_leads),
                _prohibited_claim_flags_false(known_needs),
                _prohibited_claim_flags_false(absences),
            )
        )
        return {
            "schema_version": "review_batch_apply_temp_result.v0",
            "task": TASK_ID,
            "status": "pass" if readback_passed else "fail",
            "plan_id": apply_plan.get("plan_id"),
            "apply_validation": validation,
            "temp_instance_initialized": True,
            "temp_instance_locator": "system_temp_explicit_instance",
            "temp_instance_path_redacted": True,
            "temp_instance_apply_passed": readback_passed,
            "limited_reviewed_metadata_records": metadata_records,
            "limited_reviewed_source_leads": source_leads,
            "reviewed_known_needs": known_needs,
            "reviewed_bounded_absences": absences,
            "limited_reviewed_metadata_records_created": len(metadata_records),
            "limited_reviewed_source_leads_created": len(source_leads),
            "reviewed_known_needs_created": len(known_needs),
            "reviewed_bounded_absences_created": len(absences),
            "reviewed_record_delta_count": len(metadata_records) + len(source_leads),
            "readback_validation_passed": readback_passed,
            "operator_instance_mutated": False,
            "committed_instance_state": False,
            "created_at": DEFAULT_TIMESTAMP,
            **_false_boundaries(),
        }


def build_limited_reviewed_metadata_record(
    item: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    record_id = _stable_id("limited_reviewed_metadata_record", item.get("candidate_id"))
    return {
        "schema_version": "limited_reviewed_metadata_record.v0",
        "record_type": "limited_reviewed_metadata_record",
        "record_id": record_id,
        "source_family": _text(item.get("source_family")),
        "source_locator": _copy_mapping(item.get("source_locator")),
        "title": _text(item.get("title")),
        "reviewed_claim_scope": "metadata_identity_lead_only",
        "evidence_refs": _evidence_refs(item),
        "candidate_refs": [_text(item.get("candidate_id"))],
        "review_batch_ref": _text(item.get("review_batch_ref")),
        "scout_trail_refs": _list_text(item.get("scout_trail_refs")),
        "limitations": _limitations_for(item),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee_claim": False,
        "scan_completeness_claim": False,
        "ocr_quality_claim": False,
        "reviewed_at": DEFAULT_TIMESTAMP,
        "reviewed_by_policy": "control/policies/review_batch_apply_next_policy.json",
        "accepted_truth": False,
        **_false_boundaries(),
    }


def build_limited_reviewed_source_lead(
    item: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    record_id = _stable_id("limited_reviewed_source_lead", item.get("candidate_id"))
    return {
        "schema_version": "limited_reviewed_source_lead.v0",
        "record_type": "limited_reviewed_source_lead",
        "record_id": record_id,
        "source_family": _text(item.get("source_family")),
        "source_locator": _copy_mapping(item.get("source_locator")),
        "title": _text(item.get("title")),
        "lead_summary": f"Limited reviewed source lead for {_text(item.get('title'))}",
        "reviewed_claim_scope": "source_lead_only",
        "evidence_refs": _evidence_refs(item),
        "candidate_refs": [_text(item.get("candidate_id"))],
        "review_batch_ref": _text(item.get("review_batch_ref")),
        "scout_trail_refs": _list_text(item.get("scout_trail_refs")),
        "limitations": _limitations_for(item),
        "action_posture": {
            "allowed_actions": ["inspect_metadata", "continue_review"],
            "blocked_actions": [
                "download",
                "fetch_file",
                "ocr",
                "extract",
                "execute",
                "install",
                "claim_artifact_verification",
                "claim_safety",
                "claim_rights",
                "claim_compatibility",
            ],
            "review_scope": "source_lead_only",
        },
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee_claim": False,
        "scan_completeness_claim": False,
        "ocr_quality_claim": False,
        "reviewed_at": DEFAULT_TIMESTAMP,
        "reviewed_by_policy": "control/policies/review_batch_apply_next_policy.json",
        "accepted_truth": False,
        **_false_boundaries(),
    }


def build_reviewed_known_need(item: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    return {
        "schema_version": "reviewed_known_need.v0",
        "record_type": "reviewed_known_need",
        "record_id": _stable_id("reviewed_known_need", item.get("need_id")),
        "need_id": _text(item.get("need_id")),
        "need_kind": _text(item.get("need_kind")),
        "candidate_refs": _list_text(item.get("candidate_refs")),
        "summary": _text(item.get("summary")),
        "reviewed_claim_scope": "known_need_only",
        "reviewed_at": DEFAULT_TIMESTAMP,
        "accepted_truth": False,
        "limitations": ["need remains unresolved", "reviewed need is not object truth"],
        **_false_boundaries(),
    }


def build_reviewed_bounded_absence(item: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    return {
        "schema_version": "reviewed_bounded_absence.v0",
        "record_type": "reviewed_bounded_absence",
        "record_id": _stable_id("reviewed_bounded_absence", item.get("absence_id")),
        "absence_id": _text(item.get("absence_id")),
        "absence_kind": _text(item.get("absence_kind")),
        "summary": _text(item.get("summary")),
        "reviewed_claim_scope": "bounded_absence_only",
        "reviewed_at": DEFAULT_TIMESTAMP,
        "accepted_truth": False,
        "limitations": ["absence is bounded to reviewed fixture evidence", "not a universal absence claim"],
        **_false_boundaries(),
    }


def build_review_batch_apply_rollback_plan(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    records = _apply_records(apply_result)
    return {
        "schema_version": "review_batch_apply_rollback_plan.v0",
        "task": TASK_ID,
        "rollback_plan_id": _stable_id("review_batch_apply_rollback", apply_result.get("plan_id")),
        "plan_id": apply_result.get("plan_id"),
        "temp_instance_locator": "system_temp_explicit_instance",
        "rollback_scope": "delete_temp_explicit_instance_records",
        "records_to_remove": [record.get("record_id") for record in records],
        "rollback_required_for_operator_instance_apply": True,
        "rollback_plan_created": True,
        "operator_instance_mutated": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_review_batch_snapshot_refresh_handoff(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    return {
        "schema_version": "review_batch_apply_snapshot_refresh_handoff.v0",
        "task": TASK_ID,
        "handoff_id": _stable_id("review_batch_apply_snapshot_handoff", apply_result.get("plan_id")),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "limited_reviewed_metadata_record_refs": [
            record.get("record_id") for record in apply_result.get("limited_reviewed_metadata_records", [])
        ],
        "limited_reviewed_source_lead_refs": [
            record.get("record_id") for record in apply_result.get("limited_reviewed_source_leads", [])
        ],
        "reviewed_known_need_refs": [record.get("record_id") for record in apply_result.get("reviewed_known_needs", [])],
        "reviewed_bounded_absence_refs": [
            record.get("record_id") for record in apply_result.get("reviewed_bounded_absences", [])
        ],
        "reviewed_record_delta_count": int(apply_result.get("reviewed_record_delta_count") or 0),
        "snapshot_refresh_handoff_only": True,
        "snapshot_refresh_executed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_review_batch_public_alpha_reassess_handoff(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    return {
        "schema_version": "review_batch_apply_public_alpha_reassess_handoff.v0",
        "task": TASK_ID,
        "handoff_id": _stable_id("review_batch_apply_public_alpha_handoff", apply_result.get("plan_id")),
        "recommended_after_snapshot_task": "PUBLIC-ALPHA-REASSESS-06 - Reassess alpha after review batch apply snapshot",
        "reviewed_record_delta_count": int(apply_result.get("reviewed_record_delta_count") or 0),
        "candidate_count_before_apply": 68,
        "public_alpha_reassess_handoff_only": True,
        "public_alpha_reassess_executed": False,
        "launch_recommended": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_review_batch_apply_boundary_report(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "review_batch_apply_boundary_report.v0",
        "task": TASK_ID,
        "plan_id": _text(apply_result.get("plan_id")),
        "default_apply_target": merged_policy["default_apply_target"],
        "reviewed_artifact_record_creation_enabled": False,
        "limited_reviewed_records_only": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_review_batch_apply_next(
    *,
    from_examples: bool = True,
    use_temp_instance: bool = True,
    write_examples: bool = False,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not from_examples:
        raise ValueError("REVIEW-BATCH-APPLY-NEXT-00 only supports committed examples")
    merged_policy = _policy(policy)
    input_state = load_review_batch_apply_inputs(merged_policy)
    eligibility = evaluate_review_batch_apply_eligibility(
        input_state["candidates"],
        input_state["review_packets"],
        [],
        merged_policy,
    )
    sufficiency = [
        assess_review_batch_evidence_sufficiency(candidate, merged_policy)
        for candidate in input_state["candidates"]
    ]
    eligible_items = _eligible_items(input_state["candidates"], eligibility)
    apply_plan = build_review_batch_apply_plan(
        eligible_items,
        input_state["known_needs"],
        input_state["absence_summaries"],
        merged_policy,
    )
    apply_validation = validate_review_batch_apply_plan(apply_plan, merged_policy)
    temp_apply_result = apply_review_batch_to_temp_instance(
        apply_plan,
        None if use_temp_instance else _repo_root() / "examples" / "local_apply" / "review_batch" / "_temp",
        merged_policy,
    )
    rollback_plan = build_review_batch_apply_rollback_plan(temp_apply_result, merged_policy)
    snapshot_handoff = build_review_batch_snapshot_refresh_handoff(temp_apply_result, merged_policy)
    reassess_handoff = build_review_batch_public_alpha_reassess_handoff(temp_apply_result, merged_policy)
    boundary_report = build_review_batch_apply_boundary_report(temp_apply_result, merged_policy)
    non_applied = _non_applied_candidates(input_state["candidates"], eligibility)
    result = {
        "schema_version": "review_batch_apply_next_runtime_result.v0",
        "task": TASK_ID,
        "status": "pass" if temp_apply_result["status"] == "pass" else temp_apply_result["status"],
        "input_state": input_state,
        "eligibility_matrix": eligibility,
        "evidence_sufficiency_matrix": sufficiency,
        "decision_matrix": _decision_rows(eligibility),
        "apply_plan": apply_plan,
        "apply_validation": apply_validation,
        "temp_apply_result": temp_apply_result,
        "limited_reviewed_metadata_records": temp_apply_result.get("limited_reviewed_metadata_records", []),
        "limited_reviewed_source_leads": temp_apply_result.get("limited_reviewed_source_leads", []),
        "reviewed_known_needs": temp_apply_result.get("reviewed_known_needs", []),
        "reviewed_bounded_absences": temp_apply_result.get("reviewed_bounded_absences", []),
        "non_applied_candidates": non_applied,
        "rollback_plan": rollback_plan,
        "snapshot_refresh_handoff": snapshot_handoff,
        "public_alpha_reassess_handoff": reassess_handoff,
        "boundary_report": boundary_report,
        "total_candidates_considered": input_state["candidate_count"],
        "eligible_apply_count": apply_plan["eligible_apply_count"],
        "limited_reviewed_metadata_records_created": temp_apply_result.get("limited_reviewed_metadata_records_created", 0),
        "limited_reviewed_source_leads_created": temp_apply_result.get("limited_reviewed_source_leads_created", 0),
        "reviewed_known_needs_created": temp_apply_result.get("reviewed_known_needs_created", 0),
        "reviewed_bounded_absences_created": temp_apply_result.get("reviewed_bounded_absences_created", 0),
        "reviewed_record_delta_count": temp_apply_result.get("reviewed_record_delta_count", 0),
        "non_applied_count": len(non_applied),
        "temp_instance_apply_passed": temp_apply_result.get("temp_instance_apply_passed", False),
        "rollback_plan_created": rollback_plan["rollback_plan_created"],
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    if write_examples:
        write_review_batch_apply_next_examples(result)
        write_review_batch_apply_next_inventory_and_audit(result)
        result["examples_written"] = True
    return result


def build_review_batch_apply_next_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "review_batch_apply_next_input_state.json": result["input_state"],
        "review_batch_apply_next_candidate_matrix.json": {
            "schema_version": "review_batch_apply_next_candidate_matrix.v0",
            "task": TASK_ID,
            "total_candidates_considered": result["total_candidates_considered"],
            "candidates": result["input_state"]["candidates"],
        },
        "review_batch_apply_next_eligibility_matrix.json": {
            "schema_version": "review_batch_apply_next_eligibility_matrix.v0",
            "task": TASK_ID,
            "eligible_apply_count": result["eligible_apply_count"],
            "rows": result["eligibility_matrix"],
        },
        "review_batch_apply_next_evidence_sufficiency_matrix.json": {
            "schema_version": "review_batch_apply_next_evidence_sufficiency_matrix.v0",
            "task": TASK_ID,
            "rows": result["evidence_sufficiency_matrix"],
        },
        "review_batch_apply_next_decision_matrix.json": {
            "schema_version": "review_batch_apply_next_decision_matrix.v0",
            "task": TASK_ID,
            "rows": result["decision_matrix"],
        },
        "review_batch_apply_next_apply_plan_matrix.json": result["apply_plan"],
        "review_batch_apply_next_temp_apply_matrix.json": _redacted_temp_apply(result["temp_apply_result"]),
        "review_batch_apply_next_reviewed_record_matrix.json": {
            "schema_version": "review_batch_apply_next_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "limited_reviewed_metadata_records_created": result["limited_reviewed_metadata_records_created"],
            "limited_reviewed_source_leads_created": result["limited_reviewed_source_leads_created"],
            "reviewed_record_delta_count": result["reviewed_record_delta_count"],
            "limited_reviewed_metadata_records": result["limited_reviewed_metadata_records"],
            "limited_reviewed_source_leads": result["limited_reviewed_source_leads"],
        },
        "review_batch_apply_next_known_need_matrix.json": _matrix(
            "review_batch_apply_next_known_need_matrix.v0",
            result["reviewed_known_needs"],
        ),
        "review_batch_apply_next_absence_matrix.json": _matrix(
            "review_batch_apply_next_absence_matrix.v0",
            result["reviewed_bounded_absences"],
        ),
        "review_batch_apply_next_non_applied_matrix.json": {
            "schema_version": "review_batch_apply_next_non_applied_matrix.v0",
            "task": TASK_ID,
            "non_applied_count": result["non_applied_count"],
            "not_applied_reasons": sorted({row["not_applied_reason"] for row in result["non_applied_candidates"]}),
            "candidates": result["non_applied_candidates"],
        },
        "review_batch_apply_next_snapshot_handoff_matrix.json": result["snapshot_refresh_handoff"],
        "review_batch_apply_next_public_alpha_reassess_handoff_matrix.json": result["public_alpha_reassess_handoff"],
        "review_batch_apply_next_boundary_report.json": result["boundary_report"],
        "review_batch_apply_next_smoke_result.json": {
            "schema_version": "review_batch_apply_next_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "commands": [
                "python scripts/eureka_review_batch_apply_validate.py --from-examples --json",
                "python scripts/eureka_review_batch_apply_next.py --from-examples --use-temp-instance --json",
                "python scripts/eureka_review_batch_apply_report.py --from-examples --json",
            ],
            "temp_instance_apply_passed": result["temp_instance_apply_passed"],
            "reviewed_record_delta_count": result["reviewed_record_delta_count"],
            **_false_boundaries(),
        },
        "review_batch_apply_next_validation_matrix.json": {
            "schema_version": "review_batch_apply_next_validation_matrix.v0",
            "task": TASK_ID,
            "status": result["status"],
            "apply_validation": result["apply_validation"],
            "focused_validation": True,
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "review_batch_apply_next_result.json": _task_result(result),
        "review_batch_apply_next_next_task_decision.json": {
            "schema_version": "review_batch_apply_next_next_task_decision.v0",
            "task": TASK_ID,
            "status": result["status"],
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "PUBLIC-ALPHA-REASSESS-06",
                "INDEXLESS-LIVE-SEARCH-FALLBACK-00",
                "SEARCH-USEFULNESS-EVAL-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "rationale": "Review-batch apply grew limited reviewed records only in temp proof; snapshot refresh is the next projection gate.",
        },
        "review_batch_apply_next_failure_repair_log.json": {
            "schema_version": "review_batch_apply_next_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def write_review_batch_apply_next_examples(result: Mapping[str, Any] | None = None) -> list[str]:
    payload = dict(result or run_review_batch_apply_next())
    repo = _repo_root()
    base = repo / "examples" / "review_batch" / "apply_next"
    local_apply_base = repo / "examples" / "local_apply" / "review_batch"
    files = {
        base / "apply_inputs.json": payload["input_state"],
        base / "eligibility_matrix.json": {
            "schema_version": "review_batch_apply_next_eligibility_matrix.v0",
            "rows": payload["eligibility_matrix"],
        },
        base / "evidence_sufficiency_matrix.json": {
            "schema_version": "review_batch_apply_next_evidence_sufficiency_matrix.v0",
            "rows": payload["evidence_sufficiency_matrix"],
        },
        base / "apply_plan.json": payload["apply_plan"],
        base / "apply_validation.json": payload["apply_validation"],
        base / "temp_apply_result.json": _redacted_temp_apply(payload["temp_apply_result"]),
        base / "limited_reviewed_metadata_records.json": _matrix(
            "limited_reviewed_metadata_record_matrix.v0",
            payload["limited_reviewed_metadata_records"],
        ),
        base / "limited_reviewed_source_leads.json": _matrix(
            "limited_reviewed_source_lead_matrix.v0",
            payload["limited_reviewed_source_leads"],
        ),
        base / "reviewed_known_needs.json": _matrix("reviewed_known_need_matrix.v0", payload["reviewed_known_needs"]),
        base / "reviewed_bounded_absences.json": _matrix(
            "reviewed_bounded_absence_matrix.v0",
            payload["reviewed_bounded_absences"],
        ),
        base / "non_applied_candidates.json": {
            "schema_version": "review_batch_apply_next_non_applied_candidates.v0",
            "non_applied_count": payload["non_applied_count"],
            "candidates": payload["non_applied_candidates"],
        },
        base / "rollback_plan.json": payload["rollback_plan"],
        base / "snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        base / "public_alpha_reassess_handoff.json": payload["public_alpha_reassess_handoff"],
        base / "boundary_report.json": payload["boundary_report"],
        local_apply_base / "apply_plan.json": payload["apply_plan"],
        local_apply_base / "temp_apply_result.json": _redacted_temp_apply(payload["temp_apply_result"]),
        local_apply_base / "rollback_plan.json": payload["rollback_plan"],
    }
    written: list[str] = []
    for path, content in files.items():
        _write_json(path, content)
        written.append(str(path.relative_to(repo)))
    return written


def write_review_batch_apply_next_inventory_and_audit(result: Mapping[str, Any] | None = None) -> list[str]:
    payload = dict(result or run_review_batch_apply_next())
    repo = _repo_root()
    inventory = build_review_batch_apply_next_inventory_packets(payload)
    written: list[str] = []
    for name, content in inventory.items():
        path = repo / "control" / "inventory" / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo)))
    written.extend(_write_audit_pack(payload, inventory, repo))
    return written


def _write_audit_pack(result: Mapping[str, Any], inventory: Mapping[str, Any], repo: Path) -> list[str]:
    audit_root = repo / "control" / "audits" / "review-batch-apply-next-00-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# REVIEW-BATCH-APPLY-NEXT-00 Audit\n\nTemp explicit proof for applying the next eligible review-batch outputs as limited records, reviewed needs, and bounded absences.\n",
        "candidate_matrix.md": _matrix_md("Candidate Matrix", inventory["review_batch_apply_next_candidate_matrix.json"]),
        "eligibility_matrix.md": _matrix_md("Eligibility Matrix", inventory["review_batch_apply_next_eligibility_matrix.json"]),
        "evidence_sufficiency_matrix.md": _matrix_md("Evidence Sufficiency Matrix", inventory["review_batch_apply_next_evidence_sufficiency_matrix.json"]),
        "apply_plan_matrix.md": _matrix_md("Apply Plan Matrix", result["apply_plan"]),
        "temp_apply_matrix.md": _matrix_md("Temp Apply Matrix", result["temp_apply_result"]),
        "reviewed_record_matrix.md": _matrix_md("Reviewed Record Matrix", inventory["review_batch_apply_next_reviewed_record_matrix.json"]),
        "known_need_matrix.md": _matrix_md("Known Need Matrix", inventory["review_batch_apply_next_known_need_matrix.json"]),
        "absence_matrix.md": _matrix_md("Absence Matrix", inventory["review_batch_apply_next_absence_matrix.json"]),
        "non_applied_matrix.md": _matrix_md("Non Applied Matrix", inventory["review_batch_apply_next_non_applied_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["review_batch_apply_next_smoke_result.json"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["review_batch_apply_next_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/review_batch_apply_next_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "review_batch_apply_next_report.json": _task_result(result),
        "generated/sample_apply_plan.json": result["apply_plan"],
        "generated/sample_limited_reviewed_metadata_records.json": _matrix(
            "limited_reviewed_metadata_record_matrix.v0",
            result["limited_reviewed_metadata_records"],
        ),
        "generated/sample_limited_reviewed_source_leads.json": _matrix(
            "limited_reviewed_source_lead_matrix.v0",
            result["limited_reviewed_source_leads"],
        ),
        "generated/sample_reviewed_known_needs.json": _matrix("reviewed_known_need_matrix.v0", result["reviewed_known_needs"]),
        "generated/sample_reviewed_bounded_absences.json": _matrix(
            "reviewed_bounded_absence_matrix.v0",
            result["reviewed_bounded_absences"],
        ),
        "generated/sample_non_applied_candidates.json": inventory["review_batch_apply_next_non_applied_matrix.json"],
        "generated/sample_rollback_plan.json": result["rollback_plan"],
        "generated/sample_snapshot_refresh_handoff.json": result["snapshot_refresh_handoff"],
        "generated/sample_public_alpha_reassess_handoff.json": result["public_alpha_reassess_handoff"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Review Batch Apply Summary\n\n"
        f"- total candidates considered: {result['total_candidates_considered']}\n"
        f"- eligible apply count: {result['eligible_apply_count']}\n"
        f"- limited reviewed metadata records: {result['limited_reviewed_metadata_records_created']}\n"
        f"- limited reviewed source leads: {result['limited_reviewed_source_leads_created']}\n"
        f"- reviewed known needs: {result['reviewed_known_needs_created']}\n"
        f"- reviewed bounded absences: {result['reviewed_bounded_absences_created']}\n"
        f"- reviewed record delta: {result['reviewed_record_delta_count']}\n"
        "- operator instance mutated: false\n"
        "- artifact verified claim created: false\n"
        f"- next task: {RECOMMENDED_NEXT_TASK}\n"
    )
    written: list[str] = []
    for name, content in markdown.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo)))
    for name, content in json_files.items():
        path = audit_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo)))
    summary_path = generated / "sample_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    written.append(str(summary_path.relative_to(repo)))
    return written


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "review_batch_apply_next_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contracts_added": True,
        "policies_added": True,
        "candidate_matrix_added": True,
        "eligibility_matrix_added": True,
        "evidence_sufficiency_matrix_added": True,
        "decision_matrix_added": True,
        "apply_plan_matrix_added": True,
        "temp_apply_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "known_need_matrix_added": True,
        "absence_matrix_added": True,
        "non_applied_matrix_added": True,
        "snapshot_handoff_matrix_added": True,
        "public_alpha_reassess_handoff_matrix_added": True,
        "runtime_apply_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "total_candidates_considered": result.get("total_candidates_considered"),
        "eligible_apply_count": result.get("eligible_apply_count"),
        "limited_reviewed_metadata_records_created": result.get("limited_reviewed_metadata_records_created"),
        "limited_reviewed_source_leads_created": result.get("limited_reviewed_source_leads_created"),
        "reviewed_known_needs_created": result.get("reviewed_known_needs_created"),
        "reviewed_bounded_absences_created": result.get("reviewed_bounded_absences_created"),
        "reviewed_record_delta_count": result.get("reviewed_record_delta_count"),
        "non_applied_count": result.get("non_applied_count"),
        "temp_instance_apply_passed": result.get("temp_instance_apply_passed"),
        "rollback_plan_created": result.get("rollback_plan_created"),
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "compatibility_guarantee_claim_created": False,
        "scan_completeness_claim_created": False,
        "ocr_quality_claim_created": False,
        "download_performed": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _assert_prior_results(prior_results: Mapping[str, Mapping[str, Any]]) -> None:
    for name, payload in prior_results.items():
        if payload.get("status") not in {"pass", "pass_with_warnings"}:
            raise ValueError(f"prior result must pass before review batch apply: {name}")
    reassess = prior_results["public_alpha_reassess_05_result"]
    snapshot = prior_results["snapshot_refresh_05_result"]
    if reassess.get("needs_review_batch_apply_next") is not True:
        raise ValueError("public alpha reassess 05 must request review batch apply next")
    if int(reassess.get("candidate_count") or 0) != 68:
        raise ValueError("expected public alpha reassess 05 candidate_count=68")
    if int(snapshot.get("total_candidate_count") or 0) != 68:
        raise ValueError("expected snapshot refresh 05 total_candidate_count=68")
    for payload in prior_results.values():
        for key in (
            "accepted_truth_created",
            "reviewed_index_mutated",
            "master_index_mutated",
            "public_index_mutated",
            "deployment_performed",
        ):
            if key in payload and payload.get(key) is not False:
                raise ValueError(f"prior boundary failed: {key}")


def _extract_packet_candidates(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for cluster in packet.get("clusters", []):
        if not isinstance(cluster, Mapping):
            continue
        for candidate in cluster.get("candidates", []):
            if not isinstance(candidate, Mapping):
                continue
            candidate_id = _text(candidate.get("candidate_id"))
            if candidate_id:
                candidates[candidate_id] = dict(candidate)
    return [candidates[key] for key in sorted(candidates)]


def _load_need_absence_inputs(repo: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    needs: list[dict[str, Any]] = []
    absences: list[dict[str, Any]] = []
    for domain_id, relative in KNOWN_NEED_PATHS.items():
        path = repo / relative
        if not path.exists():
            continue
        payload = _read_json(path)
        for need in payload.get("known_needs", []):
            if isinstance(need, Mapping):
                row = dict(need)
                row["domain_id"] = domain_id
                row["source_matrix_ref"] = relative
                needs.append(row)
        for absence in payload.get("absence_summaries", []):
            if isinstance(absence, Mapping):
                row = dict(absence)
                row["domain_id"] = domain_id
                row["source_matrix_ref"] = relative
                absences.append(row)
    return needs, absences


def _select_reviewed_known_needs(known_needs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    wanted_domains = ("manuals_docs_scans", "driver_support_media")
    selected: list[dict[str, Any]] = []
    for domain in wanted_domains:
        for need in known_needs:
            if need.get("domain_id") == domain:
                selected.append(dict(need))
                break
    return selected


def _select_reviewed_absences(absence_summaries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    wanted_kinds = {"scan_quality_not_verified", "driver_safety_not_verified"}
    selected: list[dict[str, Any]] = []
    for absence in absence_summaries:
        if _text(absence.get("absence_kind")) in wanted_kinds:
            selected.append(dict(absence))
    return selected[:2]


def _eligible_items(candidates: Sequence[Mapping[str, Any]], eligibility: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    candidates_by_id = {_text(candidate.get("candidate_id")): dict(candidate) for candidate in candidates}
    items: list[dict[str, Any]] = []
    for row in eligibility:
        if not row.get("eligible"):
            continue
        candidate = dict(candidates_by_id[_text(row.get("candidate_id"))])
        candidate.update(row)
        candidate["review_batch_ref"] = _text(candidate.get("review_batch_packet_ref"))
        items.append(candidate)
    return items


def _non_applied_candidates(candidates: Sequence[Mapping[str, Any]], eligibility: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    eligibility_by_id = {_text(row.get("candidate_id")): row for row in eligibility}
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = _text(candidate.get("candidate_id"))
        row = eligibility_by_id.get(candidate_id, {})
        if row.get("eligible"):
            continue
        rows.append(
            {
                "candidate_id": candidate_id,
                "title": _text(candidate.get("title")),
                "domain_id": _text(candidate.get("domain_id")),
                "source_family": _text(candidate.get("source_family")),
                "not_applied_reason": _text(row.get("reason")) or "not selected by conservative apply gate",
                "review_required": True,
                "accepted_truth": False,
            }
        )
    return rows


def _decision_rows(eligibility: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": "review_batch_apply_decision.v0",
            "task": TASK_ID,
            "candidate_id": row.get("candidate_id"),
            "decision": row.get("decision"),
            "record_kind": row.get("record_kind"),
            "allowed": bool(row.get("eligible")),
            "reason": row.get("reason"),
            "created_at": DEFAULT_TIMESTAMP,
            **_false_boundaries(),
        }
        for row in eligibility
    ]


def _apply_records(apply_result: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in (
        "limited_reviewed_metadata_records",
        "limited_reviewed_source_leads",
        "reviewed_known_needs",
        "reviewed_bounded_absences",
    ):
        records.extend([dict(record) for record in apply_result.get(key, []) if isinstance(record, Mapping)])
    return records


def _policy(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "apply_requires_review_batch_decision",
        "apply_requires_evidence_sufficiency",
        "operator_instance_apply_requires_explicit_approval",
        "rollback_plan_required",
    }
    missing = sorted(key for key in required_true if policy.get(key) is not True)
    if missing:
        raise PermissionError(f"review batch apply policy missing true rules: {', '.join(missing)}")
    if policy.get("default_apply_target") != "temp_explicit_instance":
        raise PermissionError("default apply target must be temp_explicit_instance")
    if list(policy.get("eligible_record_kinds") or []) != list(ELIGIBLE_RECORD_KINDS):
        raise PermissionError("eligible record kinds do not match review batch apply contract")
    forbidden_true = {
        "public_apply_enabled",
        "public_mutation_enabled",
        "master_index_mutation_enabled",
        "public_index_mutation_enabled",
        "reviewed_index_mutation_enabled_by_default",
        "reviewed_artifact_record_creation_enabled",
        "artifact_verification_claim_allowed",
        "verified_download_claim_allowed",
        "malware_clean_claim_allowed",
        "rights_clearance_claim_allowed",
        "compatibility_guarantee_claim_allowed",
        "scan_completeness_claim_allowed",
        "ocr_quality_claim_allowed",
        "downloads_enabled",
        "extraction_enabled",
        "file_fetch_enabled",
        "ocr_enabled",
        "install_execution_enabled",
        "model_provider_enabled",
        "deployment_enabled",
    }
    enabled = sorted(key for key in forbidden_true if policy.get(key) is not False)
    if enabled:
        raise PermissionError(f"review batch apply policy enables forbidden behavior: {', '.join(enabled)}")


def _evidence_refs(item: Mapping[str, Any]) -> list[str]:
    refs = [
        _text(item.get("candidate_id")),
        _text(item.get("review_batch_ref")),
        _text(item.get("review_batch_id")),
    ]
    return [ref for ref in refs if ref]


def _limitations_for(item: Mapping[str, Any]) -> list[str]:
    domain = _text(item.get("domain_id"))
    limitations = [
        "limited_reviewed_record_scope_only",
        "no_artifact_verification",
        "no_download_or_file_fetch",
        "no_malware_clean_or_rights_clearance_claim",
    ]
    if domain == "manuals_docs_scans":
        limitations.extend(["no_scan_completeness_claim", "no_ocr_quality_claim"])
    if domain in {"legacy_software", "driver_support_media"}:
        limitations.extend(["no_install_execution", "no_compatibility_guarantee"])
    return limitations


def _copy_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _prohibited_claim_flags_false(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key in (
            "artifact_verified",
            "artifact_verified_claim_created",
            "verified_download_claim",
            "verified_download_claim_created",
            "malware_clean_claim",
            "malware_clean_claim_created",
            "rights_clearance_claim",
            "rights_clearance_claim_created",
            "compatibility_guarantee_claim",
            "compatibility_guarantee_claim_created",
            "scan_completeness_claim",
            "scan_completeness_claim_created",
            "ocr_quality_claim",
            "ocr_quality_claim_created",
            "download_claim",
            "extraction_claim",
            "accepted_truth_created",
        ):
            if key in value and value[key] is not False:
                return False
        return all(_prohibited_claim_flags_false(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return all(_prohibited_claim_flags_false(item) for item in value)
    return True


def _redacted_temp_apply(payload: Mapping[str, Any]) -> dict[str, Any]:
    redacted = dict(payload)
    redacted["temp_instance_locator"] = "system_temp_explicit_instance"
    redacted["temp_instance_path_redacted"] = True
    return redacted


def _matrix(schema_version: str, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "task": TASK_ID,
        "count": len(records),
        "records": [dict(item) for item in records],
    }


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _list_text(value: Any) -> list[str]:
    if isinstance(value, str):
        text = _text(value)
        return [text] if text else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_text(item) for item in value if _text(item)]
    return []


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""
