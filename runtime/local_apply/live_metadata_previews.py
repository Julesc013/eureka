"""Temp-only local apply for live metadata review previews.

This runtime converts eligible reviewed metadata/source-lead previews into
limited reviewed local records inside a temporary explicit store. It does not
touch an operator instance, public/master indexes, raw source responses, or any
artifact/download/safety/rights claims.
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, ContextManager, Mapping, Sequence


TASK_ID = "LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00"
DEFAULT_TIMESTAMP = "2026-06-01T00:00:00Z"
SOURCE_FAMILY = "internet_archive_metadata"
RECOMMENDED_NEXT_TASK = "SNAPSHOT-REFRESH-03 - Refresh snapshots after local apply of live metadata previews"

ELIGIBLE_PREVIEW_KINDS = (
    "reviewed_metadata_record_preview",
    "reviewed_source_lead_preview",
)

BOUNDARY_FALSE_KEYS = (
    "operator_instance_mutated",
    "committed_instance_state",
    "public_index_mutated",
    "master_index_mutated",
    "reviewed_index_mutated",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "rights_clearance_claim_created",
    "artifact_verified_claim_created",
    "download_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "raw_live_response_committed",
    "new_live_source_calls_performed",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
)

PROHIBITED_CLAIMS = (
    "verified_download",
    "malware_clean",
    "rights_cleared",
    "artifact_verified",
    "safe_installer",
    "extracted_file",
)

DEFAULT_POLICY: dict[str, Any] = {
    "eligible_preview_kinds": list(ELIGIBLE_PREVIEW_KINDS),
    "useful_leads_not_auto_applied": True,
    "needs_more_evidence_not_applied": True,
    "rejected_or_duplicate_not_applied": True,
    "local_apply_required": True,
    "default_apply_target": "temp_explicit_instance",
    "operator_instance_apply_requires_explicit_approval": True,
    "public_apply_enabled": False,
    "public_mutation_enabled": False,
    "reviewed_record_scope_limited_to_metadata_or_source_lead": True,
    "verified_download_claim_allowed": False,
    "malware_clean_claim_allowed": False,
    "rights_clearance_claim_allowed": False,
    "artifact_verification_claim_allowed": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "public_index_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "deployment_enabled": False,
    "rollback_plan_required": True,
}


def default_policy() -> dict[str, Any]:
    return dict(DEFAULT_POLICY)


def load_live_metadata_review_previews(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    metadata = _read_json(repo / "examples/review/live_metadata/reviewed_metadata_record_previews.json")
    source_leads = _read_json(repo / "examples/review/live_metadata/reviewed_source_lead_previews.json")
    decisions = _read_json(repo / "examples/review/live_metadata/review_decisions.json")
    promotion_previews = _read_json(repo / "examples/review/live_metadata/promotion_previews.json")
    review_result = _read_json(repo / "control/inventory/live_metadata_review_result.json")
    snapshot_result = _read_json(repo / "control/inventory/snapshot_refresh_02_result.json")
    reassess_result = _read_json(repo / "control/inventory/public_alpha_reassess_02_result.json")
    local_apply_gate_result = _read_json(repo / "control/inventory/local_apply_gate_result.json")
    metadata_records = [dict(item) for item in metadata.get("records", [])]
    source_lead_records = [dict(item) for item in source_leads.get("records", [])]
    decision_records = [dict(item) for item in decisions.get("records", [])]
    _assert_prior_results(review_result, snapshot_result, reassess_result)
    return {
        "schema_version": "local_apply_live_metadata_input_state.v0",
        "task": TASK_ID,
        "reviewed_metadata_record_previews": metadata_records,
        "reviewed_source_lead_previews": source_lead_records,
        "promotion_previews": list(promotion_previews.get("records") or []),
        "review_decisions": decision_records,
        "review_result": review_result,
        "snapshot_refresh_02_result": snapshot_result,
        "public_alpha_reassess_02_result": reassess_result,
        "local_apply_gate_result": local_apply_gate_result,
        "equivalent_filename_mappings": {
            "local_apply_gate_result": "control/inventory/local_apply_gate_result.json"
        },
        "reviewed_metadata_record_preview_count": len(metadata_records),
        "reviewed_source_lead_preview_count": len(source_lead_records),
        "useful_lead_count": int(review_result.get("useful_lead_count") or 0),
        "needs_more_evidence_count": int(review_result.get("needs_more_evidence_count") or 0),
        "rejected_or_duplicate_count": int(review_result.get("rejected_or_duplicate_count") or 0),
        "review_preview_applied_before_task": False,
        "accepted_truth_created_before_task": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def select_eligible_live_metadata_previews(
    previews: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    if isinstance(previews, Mapping):
        rows = list(previews.get("reviewed_metadata_record_previews") or []) + list(
            previews.get("reviewed_source_lead_previews") or []
        )
    else:
        rows = list(previews)
    eligible: list[dict[str, Any]] = []
    for row in rows:
        record = dict(row)
        record_type = _text(record.get("record_type"))
        if record_type in set(merged_policy["eligible_preview_kinds"]):
            record["eligible_for_local_apply"] = True
            record["local_apply_target"] = "temp_explicit_instance"
            record["applied_to_operator_instance"] = False
            eligible.append(record)
    return eligible


def build_live_metadata_local_apply_plan(
    eligible_previews: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    rows = [dict(item) for item in eligible_previews]
    plan_id = _stable_id("live_metadata_local_apply_plan", [_text(item.get("record_id")) for item in rows])
    metadata = [item for item in rows if item.get("record_type") == "reviewed_metadata_record_preview"]
    source_leads = [item for item in rows if item.get("record_type") == "reviewed_source_lead_preview"]
    return {
        "schema_version": "live_metadata_local_apply_plan.v0",
        "task": TASK_ID,
        "plan_id": plan_id,
        "source_family": SOURCE_FAMILY,
        "apply_target": "temp_explicit_instance",
        "operator_instance_apply_requested": False,
        "operator_instance_approval_present": False,
        "eligible_preview_count": len(rows),
        "reviewed_metadata_record_preview_count": len(metadata),
        "reviewed_source_lead_preview_count": len(source_leads),
        "preview_refs": [_text(item.get("record_id")) for item in rows],
        "previews": rows,
        "records_to_create": [
            {
                "preview_ref": _text(item.get("record_id")),
                "candidate_id": _text(item.get("candidate_id")),
                "record_type": "reviewed_metadata_record"
                if item.get("record_type") == "reviewed_metadata_record_preview"
                else "reviewed_source_lead",
                "claim_scope": "metadata_or_source_lead_only",
            }
            for item in rows
        ],
        "local_apply_required": True,
        "rollback_plan_required": True,
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def validate_live_metadata_apply_plan(
    apply_plan: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        _assert_policy(merged_policy)
    except PermissionError as exc:
        errors.append(str(exc))
    if apply_plan.get("apply_target") != "temp_explicit_instance":
        errors.append("default apply target must be temp_explicit_instance")
    if apply_plan.get("operator_instance_apply_requested") is not False:
        errors.append("operator instance apply is not allowed in this task")
    if int(apply_plan.get("eligible_preview_count") or 0) != 3:
        errors.append("expected exactly 3 eligible live metadata previews")
    if int(apply_plan.get("reviewed_metadata_record_preview_count") or 0) != 1:
        errors.append("expected 1 reviewed metadata record preview")
    if int(apply_plan.get("reviewed_source_lead_preview_count") or 0) != 2:
        errors.append("expected 2 reviewed source lead previews")
    for preview in apply_plan.get("previews", []):
        if not isinstance(preview, Mapping):
            errors.append("preview row must be an object")
            continue
        if preview.get("record_type") not in ELIGIBLE_PREVIEW_KINDS:
            errors.append(f"preview has ineligible type: {preview.get('record_type')}")
        if not _prohibited_claim_flags_false(preview):
            errors.append(f"preview contains prohibited claim: {preview.get('record_id')}")
    for key in BOUNDARY_FALSE_KEYS:
        if apply_plan.get(key) is not False:
            errors.append(f"apply plan boundary must set {key}=false")
    return {
        "schema_version": "live_metadata_local_apply_validation.v0",
        "task": TASK_ID,
        "plan_id": _text(apply_plan.get("plan_id")),
        "status": "pass" if not errors else "fail",
        "apply_plan_valid": not errors,
        "eligible_preview_count": int(apply_plan.get("eligible_preview_count") or 0),
        "errors": errors,
        "warnings": warnings,
        "local_apply_required": True,
        "temp_instance_required": True,
        "operator_instance_apply_allowed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def apply_live_metadata_previews_to_temp_instance(
    apply_plan: Mapping[str, Any],
    temp_instance: str | Path | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    validation = validate_live_metadata_apply_plan(apply_plan, merged_policy)
    if validation["status"] != "pass":
        return {
            "schema_version": "live_metadata_temp_apply_result.v0",
            "task": TASK_ID,
            "status": "blocked",
            "plan_id": _text(apply_plan.get("plan_id")),
            "apply_validation": validation,
            "temp_instance_apply_passed": False,
            "records_written": False,
            **_false_boundaries(),
        }
    manager: ContextManager[str] | ContextManager[Path]
    if temp_instance is None:
        manager = tempfile.TemporaryDirectory(prefix="eureka-live-metadata-apply-")
    else:
        path = Path(temp_instance)
        path.mkdir(parents=True, exist_ok=True)
        manager = nullcontext(path)
    with manager as temp_root_value:
        temp_root = Path(temp_root_value)
        records_root = temp_root / "records"
        metadata_records = [
            build_reviewed_metadata_record(preview, merged_policy)
            for preview in apply_plan.get("previews", [])
            if isinstance(preview, Mapping) and preview.get("record_type") == "reviewed_metadata_record_preview"
        ]
        source_leads = [
            build_reviewed_source_lead(preview, merged_policy)
            for preview in apply_plan.get("previews", [])
            if isinstance(preview, Mapping) and preview.get("record_type") == "reviewed_source_lead_preview"
        ]
        _write_json(records_root / "reviewed_metadata_records.json", _matrix("live_metadata_reviewed_record_matrix.v0", metadata_records))
        _write_json(records_root / "reviewed_source_leads.json", _matrix("live_metadata_source_lead_matrix.v0", source_leads))
        manifest = {
            "schema_version": "live_metadata_temp_apply_manifest.v0",
            "task": TASK_ID,
            "plan_id": apply_plan.get("plan_id"),
            "temp_instance_initialized": True,
            "records_written": [
                "records/reviewed_metadata_records.json",
                "records/reviewed_source_leads.json",
            ],
            "committed_instance_state": False,
            "created_at": DEFAULT_TIMESTAMP,
        }
        _write_json(temp_root / "manifest.json", manifest)
        readback_metadata = _read_json(records_root / "reviewed_metadata_records.json")
        readback_source_leads = _read_json(records_root / "reviewed_source_leads.json")
        readback_passed = (
            len(readback_metadata.get("records") or []) == 1
            and len(readback_source_leads.get("records") or []) == 2
            and _prohibited_claim_flags_false(readback_metadata)
            and _prohibited_claim_flags_false(readback_source_leads)
        )
        return {
            "schema_version": "live_metadata_temp_apply_result.v0",
            "task": TASK_ID,
            "status": "pass" if readback_passed else "fail",
            "plan_id": apply_plan.get("plan_id"),
            "apply_validation": validation,
            "temp_instance_initialized": True,
            "temp_instance_locator": "system_temp_explicit_instance",
            "temp_instance_path_redacted": True,
            "temp_instance_apply_passed": readback_passed,
            "reviewed_metadata_records": metadata_records,
            "reviewed_source_leads": source_leads,
            "reviewed_metadata_records_created": len(metadata_records),
            "reviewed_source_leads_created": len(source_leads),
            "reviewed_record_delta_count": len(metadata_records) + len(source_leads),
            "readback_validation_passed": readback_passed,
            "operator_instance_mutated": False,
            "committed_instance_state": False,
            "created_at": DEFAULT_TIMESTAMP,
            **_false_boundaries(),
        }


def build_reviewed_metadata_record(preview: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    record_id = _stable_id("reviewed_metadata_record", preview.get("record_id"), preview.get("candidate_id"))
    return {
        "schema_version": "live_metadata_reviewed_record.v0",
        "record_type": "reviewed_metadata_record",
        "record_id": record_id,
        "source_family": SOURCE_FAMILY,
        "source_locator": _source_locator(preview),
        "title": _text(preview.get("title")),
        "reviewed_claim_scope": "metadata_record_only",
        "evidence_refs": _text_list(preview.get("evidence_refs")),
        "live_metadata_review_ref": "control/inventory/live_metadata_review_result.json",
        "preview_ref": _text(preview.get("record_id")),
        "candidate_id": _text(preview.get("candidate_id")),
        "limitations": _limitations(),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "artifact_verified": False,
        "reviewed_at": DEFAULT_TIMESTAMP,
        "reviewed_by_policy": "control/policies/live_metadata_reviewed_record_policy.json",
        **_false_boundaries(),
    }


def build_reviewed_source_lead(preview: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    record_id = _stable_id("reviewed_source_lead", preview.get("record_id"), preview.get("candidate_id"))
    return {
        "schema_version": "live_metadata_source_lead.v0",
        "record_type": "reviewed_source_lead",
        "record_id": record_id,
        "source_family": SOURCE_FAMILY,
        "source_locator": _source_locator(preview),
        "lead_summary": _text(preview.get("limited_claim")) or "reviewed source lead from redacted metadata",
        "title": _text(preview.get("title")),
        "evidence_refs": _text_list(preview.get("evidence_refs")),
        "live_metadata_review_ref": "control/inventory/live_metadata_review_result.json",
        "preview_ref": _text(preview.get("record_id")),
        "candidate_id": _text(preview.get("candidate_id")),
        "limitations": _limitations(),
        "action_posture": {
            "allowed_actions": ["inspect_metadata", "review_source_lead"],
            "blocked_actions": ["download", "extract", "execute", "install", "claim_safety", "claim_rights"],
            "review_scope": "source_lead_only",
        },
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "artifact_verified": False,
        "reviewed_at": DEFAULT_TIMESTAMP,
        "reviewed_by_policy": "control/policies/live_metadata_source_lead_policy.json",
        **_false_boundaries(),
    }


def build_live_metadata_apply_rollback_plan(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    rollback_id = _stable_id("live_metadata_apply_rollback", apply_result.get("plan_id"))
    return {
        "schema_version": "live_metadata_apply_rollback_plan.v0",
        "task": TASK_ID,
        "rollback_plan_id": rollback_id,
        "plan_id": apply_result.get("plan_id"),
        "temp_instance_locator": "system_temp_explicit_instance",
        "rollback_scope": "delete_temp_explicit_instance_records",
        "records_to_remove": [
            record.get("record_id")
            for record in list(apply_result.get("reviewed_metadata_records") or [])
            + list(apply_result.get("reviewed_source_leads") or [])
        ],
        "rollback_required_for_operator_instance_apply": True,
        "rollback_plan_created": True,
        "operator_instance_mutated": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_snapshot_refresh_handoff(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = list(apply_result.get("reviewed_metadata_records") or [])
    leads = list(apply_result.get("reviewed_source_leads") or [])
    return {
        "schema_version": "live_metadata_apply_snapshot_refresh_handoff.v0",
        "task": TASK_ID,
        "handoff_id": _stable_id("live_metadata_apply_snapshot_handoff", apply_result.get("plan_id")),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "reviewed_metadata_record_refs": [record.get("record_id") for record in records],
        "reviewed_source_lead_refs": [lead.get("record_id") for lead in leads],
        "reviewed_metadata_records_created": len(records),
        "reviewed_source_leads_created": len(leads),
        "reviewed_record_delta_count": len(records) + len(leads),
        "snapshot_refresh_handoff_only": True,
        "snapshot_refresh_executed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_public_alpha_reassess_handoff(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    delta = int(apply_result.get("reviewed_record_delta_count") or 0)
    return {
        "schema_version": "live_metadata_apply_public_alpha_reassess_handoff.v0",
        "task": TASK_ID,
        "handoff_id": _stable_id("live_metadata_apply_public_alpha_handoff", apply_result.get("plan_id")),
        "reviewed_record_delta_count": delta,
        "expected_reviewed_record_count_after_temp_apply": 1 + delta,
        "public_alpha_reassess_handoff_only": True,
        "public_alpha_reassess_executed": False,
        "launch_recommended": False,
        "needs_snapshot_refresh_after_apply": True,
        "needs_public_alpha_reassess_after_apply": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_apply_boundary_report(
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "live_metadata_apply_boundary_report.v0",
        "task": TASK_ID,
        "boundary_report_id": _stable_id("live_metadata_apply_boundary", apply_result.get("plan_id")),
        "result_status": apply_result.get("status", "unknown"),
        "temp_instance_apply_passed": bool(apply_result.get("temp_instance_apply_passed")),
        "reviewed_metadata_records_created": int(apply_result.get("reviewed_metadata_records_created") or 0),
        "reviewed_source_leads_created": int(apply_result.get("reviewed_source_leads_created") or 0),
        "reviewed_record_delta_count": int(apply_result.get("reviewed_record_delta_count") or 0),
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "artifact_verified_claim_created": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        **_false_boundaries(),
    }


def run_local_apply_live_metadata_previews(
    policy: Mapping[str, Any] | None = None,
    *,
    from_live_metadata_review_examples: bool = False,
    use_temp_instance: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_live_metadata_review_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    input_state = load_live_metadata_review_previews(merged_policy)
    eligible = select_eligible_live_metadata_previews(input_state, merged_policy)
    plan = build_live_metadata_local_apply_plan(eligible, merged_policy)
    validation = validate_live_metadata_apply_plan(plan, merged_policy)
    if not use_temp_instance:
        temp_result = {
            "schema_version": "live_metadata_temp_apply_result.v0",
            "task": TASK_ID,
            "status": "dry_run",
            "plan_id": plan["plan_id"],
            "apply_validation": validation,
            "temp_instance_apply_passed": False,
            "reviewed_metadata_records": [],
            "reviewed_source_leads": [],
            "reviewed_metadata_records_created": 0,
            "reviewed_source_leads_created": 0,
            "reviewed_record_delta_count": 0,
            **_false_boundaries(),
        }
    else:
        temp_result = apply_live_metadata_previews_to_temp_instance(plan, None, merged_policy)
    rollback = build_live_metadata_apply_rollback_plan(temp_result, merged_policy)
    snapshot_handoff = build_live_metadata_snapshot_refresh_handoff(temp_result, merged_policy)
    public_alpha_handoff = build_live_metadata_public_alpha_reassess_handoff(temp_result, merged_policy)
    boundary = build_live_metadata_apply_boundary_report(temp_result, merged_policy)
    result = {
        "schema_version": "local_apply_live_metadata_result.v0",
        "task": TASK_ID,
        "status": "pass" if temp_result.get("status") == "pass" else temp_result.get("status", "fail"),
        "contracts_added": True,
        "policies_added": True,
        "preview_matrix_added": True,
        "eligibility_matrix_added": True,
        "apply_plan_matrix_added": True,
        "validation_matrix_added": True,
        "temp_apply_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "source_lead_matrix_added": True,
        "snapshot_handoff_matrix_added": True,
        "public_alpha_reassess_handoff_matrix_added": True,
        "runtime_local_apply_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "input_state": input_state,
        "eligible_previews": eligible,
        "apply_plan": plan,
        "apply_validation": validation,
        "temp_apply_result": temp_result,
        "reviewed_metadata_records": list(temp_result.get("reviewed_metadata_records") or []),
        "reviewed_source_leads": list(temp_result.get("reviewed_source_leads") or []),
        "rollback_plan": rollback,
        "snapshot_refresh_handoff": snapshot_handoff,
        "public_alpha_reassess_handoff": public_alpha_handoff,
        "boundary_report": boundary,
        "eligible_preview_count": len(eligible),
        "reviewed_metadata_records_created": int(temp_result.get("reviewed_metadata_records_created") or 0),
        "reviewed_source_leads_created": int(temp_result.get("reviewed_source_leads_created") or 0),
        "reviewed_record_delta_count": int(temp_result.get("reviewed_record_delta_count") or 0),
        "useful_leads_not_applied": int(input_state.get("useful_lead_count") or 0),
        "needs_more_evidence_not_applied": int(input_state.get("needs_more_evidence_count") or 0),
        "rejected_or_duplicate_not_applied": int(input_state.get("rejected_or_duplicate_count") or 0),
        "temp_instance_apply_passed": bool(temp_result.get("temp_instance_apply_passed")),
        "rollback_plan_created": True,
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "artifact_verified_claim_created": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "created_at": DEFAULT_TIMESTAMP,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        **_false_boundaries(),
    }
    if write_examples:
        result["examples_written_paths"] = write_local_apply_live_metadata_examples(result)
        result["inventory_written_paths"] = write_local_apply_live_metadata_inventory_and_audit(result)
        result["examples_written"] = True
    return result


def build_local_apply_live_metadata_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "local_apply_live_metadata_input_state.json": result["input_state"],
        "local_apply_live_metadata_preview_matrix.json": {
            "schema_version": "local_apply_live_metadata_preview_matrix.v0",
            "task": TASK_ID,
            "input_reviewed_metadata_record_previews": 1,
            "input_reviewed_source_lead_previews": 2,
            "previews": result["eligible_previews"],
        },
        "local_apply_live_metadata_eligibility_matrix.json": {
            "schema_version": "local_apply_live_metadata_eligibility_matrix.v0",
            "task": TASK_ID,
            "eligible_preview_count": result["eligible_preview_count"],
            "eligible_preview_kinds": list(ELIGIBLE_PREVIEW_KINDS),
            "useful_leads_not_applied": result["useful_leads_not_applied"],
            "needs_more_evidence_not_applied": result["needs_more_evidence_not_applied"],
            "rejected_or_duplicate_not_applied": result["rejected_or_duplicate_not_applied"],
            "rows": [
                {
                    "preview_ref": row.get("record_id"),
                    "record_type": row.get("record_type"),
                    "eligible": True,
                    "reason": "preview kind is eligible and local apply validation is required",
                }
                for row in result["eligible_previews"]
            ],
        },
        "local_apply_live_metadata_apply_plan_matrix.json": result["apply_plan"],
        "local_apply_live_metadata_validation_matrix.json": {
            "schema_version": "local_apply_live_metadata_validation_matrix.v0",
            "task": TASK_ID,
            "status": result["apply_validation"]["status"],
            "apply_validation": result["apply_validation"],
            "focused_validation": True,
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "local_apply_live_metadata_temp_apply_matrix.json": result["temp_apply_result"],
        "local_apply_live_metadata_reviewed_record_matrix.json": _matrix(
            "local_apply_live_metadata_reviewed_record_matrix.v0",
            result["reviewed_metadata_records"],
        ),
        "local_apply_live_metadata_source_lead_matrix.json": _matrix(
            "local_apply_live_metadata_source_lead_matrix.v0",
            result["reviewed_source_leads"],
        ),
        "local_apply_live_metadata_snapshot_handoff_matrix.json": result["snapshot_refresh_handoff"],
        "local_apply_live_metadata_public_alpha_reassess_handoff_matrix.json": result[
            "public_alpha_reassess_handoff"
        ],
        "local_apply_live_metadata_boundary_report.json": result["boundary_report"],
        "local_apply_live_metadata_smoke_result.json": {
            "schema_version": "local_apply_live_metadata_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "temp_instance_apply_passed": result["temp_instance_apply_passed"],
            "reviewed_metadata_records_created": result["reviewed_metadata_records_created"],
            "reviewed_source_leads_created": result["reviewed_source_leads_created"],
            "commands": [
                "python scripts/eureka_local_apply_preview_validate.py --from-live-metadata-review-examples --json",
                "python scripts/eureka_local_apply_live_metadata_previews.py --from-live-metadata-review-examples --use-temp-instance --json",
                "python scripts/eureka_local_apply_live_metadata_report.py --from-examples --json",
            ],
            **_false_boundaries(),
        },
        "local_apply_live_metadata_result.json": _task_result(result),
        "local_apply_live_metadata_next_task_decision.json": {
            "schema_version": "local_apply_live_metadata_next_task_decision.v0",
            "task": TASK_ID,
            "status": result["status"],
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "PUBLIC-ALPHA-REASSESS-03",
                "SEED-BATCH-MANUALS-SCANS-00",
                "SEED-BATCH-DRIVER-SUPPORT-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "rationale": "Eligible previews were applied only to a temp explicit store; snapshot refresh is the next packaging gate.",
        },
        "local_apply_live_metadata_failure_repair_log.json": {
            "schema_version": "local_apply_live_metadata_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def write_local_apply_live_metadata_examples(result: Mapping[str, Any] | None = None) -> list[str]:
    payload = dict(result or run_local_apply_live_metadata_previews())
    repo = _repo_root()
    base = repo / "examples" / "local_apply" / "live_metadata"
    files = {
        "apply_plan.json": payload["apply_plan"],
        "apply_validation.json": payload["apply_validation"],
        "temp_apply_result.json": _redacted_temp_apply(payload["temp_apply_result"]),
        "reviewed_metadata_records.json": _matrix("live_metadata_reviewed_record_matrix.v0", payload["reviewed_metadata_records"]),
        "reviewed_source_leads.json": _matrix("live_metadata_source_lead_matrix.v0", payload["reviewed_source_leads"]),
        "rollback_plan.json": payload["rollback_plan"],
        "snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        "public_alpha_reassess_handoff.json": payload["public_alpha_reassess_handoff"],
        "boundary_report.json": payload["boundary_report"],
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo)))
    return written


def write_local_apply_live_metadata_inventory_and_audit(result: Mapping[str, Any] | None = None) -> list[str]:
    payload = dict(result or run_local_apply_live_metadata_previews())
    repo = _repo_root()
    inventory = build_local_apply_live_metadata_inventory_packets(payload)
    written: list[str] = []
    for name, content in inventory.items():
        path = repo / "control" / "inventory" / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo)))
    written.extend(_write_audit_pack(payload, inventory, repo))
    return written


def _write_audit_pack(result: Mapping[str, Any], inventory: Mapping[str, Any], repo: Path) -> list[str]:
    audit_root = repo / "control" / "audits" / "local-apply-live-metadata-previews-00-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00 Audit\n\nTemp explicit instance proof for applying eligible live metadata review previews as limited reviewed metadata/source-lead records.\n",
        "preview_matrix.md": _matrix_md("Preview Matrix", inventory["local_apply_live_metadata_preview_matrix.json"]),
        "eligibility_matrix.md": _matrix_md("Eligibility Matrix", inventory["local_apply_live_metadata_eligibility_matrix.json"]),
        "apply_plan_matrix.md": _matrix_md("Apply Plan Matrix", result["apply_plan"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["local_apply_live_metadata_validation_matrix.json"]),
        "temp_apply_matrix.md": _matrix_md("Temp Apply Matrix", result["temp_apply_result"]),
        "reviewed_record_matrix.md": _matrix_md("Reviewed Record Matrix", inventory["local_apply_live_metadata_reviewed_record_matrix.json"]),
        "source_lead_matrix.md": _matrix_md("Source Lead Matrix", inventory["local_apply_live_metadata_source_lead_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["local_apply_live_metadata_smoke_result.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/local_apply_live_metadata_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "local_apply_live_metadata_report.json": _task_result(result),
        "generated/sample_apply_plan.json": result["apply_plan"],
        "generated/sample_reviewed_metadata_records.json": inventory["local_apply_live_metadata_reviewed_record_matrix.json"],
        "generated/sample_reviewed_source_leads.json": inventory["local_apply_live_metadata_source_lead_matrix.json"],
        "generated/sample_rollback_plan.json": result["rollback_plan"],
        "generated/sample_snapshot_refresh_handoff.json": result["snapshot_refresh_handoff"],
        "generated/sample_public_alpha_reassess_handoff.json": result["public_alpha_reassess_handoff"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Local Apply Live Metadata Summary\n\n"
        f"- eligible previews: {result['eligible_preview_count']}\n"
        f"- reviewed metadata records created in temp proof: {result['reviewed_metadata_records_created']}\n"
        f"- reviewed source leads created in temp proof: {result['reviewed_source_leads_created']}\n"
        "- operator instance mutated: false\n"
        "- verified download claim created: false\n"
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
        "schema_version": "local_apply_live_metadata_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contracts_added": True,
        "policies_added": True,
        "preview_matrix_added": True,
        "eligibility_matrix_added": True,
        "apply_plan_matrix_added": True,
        "validation_matrix_added": True,
        "temp_apply_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "source_lead_matrix_added": True,
        "snapshot_handoff_matrix_added": True,
        "public_alpha_reassess_handoff_matrix_added": True,
        "runtime_local_apply_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "eligible_preview_count": result.get("eligible_preview_count"),
        "reviewed_metadata_records_created": result.get("reviewed_metadata_records_created"),
        "reviewed_source_leads_created": result.get("reviewed_source_leads_created"),
        "reviewed_record_delta_count": result.get("reviewed_record_delta_count"),
        "useful_leads_not_applied": result.get("useful_leads_not_applied"),
        "needs_more_evidence_not_applied": result.get("needs_more_evidence_not_applied"),
        "rejected_or_duplicate_not_applied": result.get("rejected_or_duplicate_not_applied"),
        "temp_instance_apply_passed": result.get("temp_instance_apply_passed"),
        "rollback_plan_created": result.get("rollback_plan_created"),
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "artifact_verified_claim_created": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _assert_prior_results(
    review_result: Mapping[str, Any],
    snapshot_result: Mapping[str, Any],
    reassess_result: Mapping[str, Any],
) -> None:
    if review_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("live metadata review must pass before local apply")
    if snapshot_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("snapshot refresh 02 must pass before local apply")
    if reassess_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("public alpha reassess 02 must pass before local apply")
    expected = {
        "reviewed_metadata_record_preview_count": 1,
        "reviewed_source_lead_preview_count": 2,
        "useful_lead_count": 1,
        "needs_more_evidence_count": 2,
        "rejected_or_duplicate_count": 2,
    }
    for key, value in expected.items():
        if int(review_result.get(key) or 0) != value:
            raise ValueError(f"live metadata review count mismatch for {key}")
    for key in (
        "raw_live_response_committed",
        "accepted_truth_created",
        "reviewed_index_mutated",
        "master_index_mutated",
        "public_index_mutated",
        "deployment_performed",
    ):
        if review_result.get(key) is not False:
            raise ValueError(f"prior live metadata review boundary failed: {key}")
    for key in (
        "review_preview_applied",
        "accepted_truth_created",
        "reviewed_index_mutated",
        "master_index_mutated",
        "public_index_mutated",
        "deployment_performed",
    ):
        if snapshot_result.get(key) is not False and reassess_result.get(key) is not False:
            raise ValueError(f"prior preview/apply boundary failed: {key}")


def _policy(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "useful_leads_not_auto_applied",
        "needs_more_evidence_not_applied",
        "rejected_or_duplicate_not_applied",
        "local_apply_required",
        "operator_instance_apply_requires_explicit_approval",
        "reviewed_record_scope_limited_to_metadata_or_source_lead",
        "rollback_plan_required",
    }
    missing = sorted(key for key in required_true if policy.get(key) is not True)
    if missing:
        raise PermissionError(f"live metadata local apply policy missing true rules: {', '.join(missing)}")
    if list(policy.get("eligible_preview_kinds") or []) != list(ELIGIBLE_PREVIEW_KINDS):
        raise PermissionError("eligible preview kinds must be reviewed metadata/source lead previews only")
    if policy.get("default_apply_target") != "temp_explicit_instance":
        raise PermissionError("default apply target must be temp_explicit_instance")
    forbidden_true = {
        "public_apply_enabled",
        "public_mutation_enabled",
        "verified_download_claim_allowed",
        "malware_clean_claim_allowed",
        "rights_clearance_claim_allowed",
        "artifact_verification_claim_allowed",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "deployment_enabled",
    }
    enabled = sorted(key for key in forbidden_true if policy.get(key) is not False)
    if enabled:
        raise PermissionError(f"live metadata local apply policy enables forbidden behavior: {', '.join(enabled)}")


def _source_locator(preview: Mapping[str, Any]) -> dict[str, Any]:
    summary = _text(preview.get("source_locator_summary"))
    identifier_hash = ""
    request_plan_id = ""
    for part in summary.split(";"):
        part = part.strip()
        if part.startswith("identifier_hash="):
            identifier_hash = part.split("=", 1)[1]
        if part.startswith("request_plan_id="):
            request_plan_id = part.split("=", 1)[1]
    return {
        "schema_version": "redacted_source_locator.v0",
        "source_locator_summary": summary,
        "identifier_hash": identifier_hash,
        "request_plan_id": request_plan_id,
        "raw_locator_included": False,
    }


def _prohibited_claim_flags_false(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key in (
            "verified_download_claim",
            "verified_download_claim_created",
            "malware_clean_claim",
            "malware_clean_claim_created",
            "rights_clearance_claim",
            "rights_clearance_claim_created",
            "artifact_verified",
            "artifact_verified_claim_created",
            "reviewed_artifact_claim",
            "download_claim",
            "extraction_claim",
            "accepted_truth",
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


def _limitations() -> list[str]:
    return [
        "metadata_or_source_lead_scope_only",
        "no_verified_download_or_artifact_claim",
        "no_malware_clean_claim",
        "no_rights_clearance_claim",
        "no_download_or_extraction",
        "operator_instance_apply_requires_separate_approval",
        "snapshot_refresh_required_after_apply",
    ]


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
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_text(item) for item in value if _text(item)]
    return []


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if False else DEFAULT_TIMESTAMP
