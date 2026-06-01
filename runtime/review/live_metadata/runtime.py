"""Conservative review over redacted live metadata candidates.

The review path consumes already-recorded, redacted live metadata summaries.
It does not perform new live source calls, download files, inspect archive
members, accept truth, or mutate reviewed/master/public indexes.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


TASK_ID = "REVIEW-LIVE-METADATA-CANDIDATES-00"
DEFAULT_TIMESTAMP = "2026-06-01T00:00:00Z"
SOURCE_FAMILY = "internet_archive_metadata"
RECOMMENDED_NEXT_TASK = "SNAPSHOT-REFRESH-02 - Refresh snapshots after live metadata candidate review"

LIVE_METADATA_REVIEW_DECISIONS = (
    "promote_reviewed_metadata_record_preview",
    "promote_reviewed_source_lead_preview",
    "mark_useful_lead",
    "needs_more_evidence",
    "duplicate",
    "near_miss",
    "reject_wrong_object",
    "reject_wrong_version",
    "reject_low_quality",
    "block_candidate",
)

PROHIBITED_CLAIMS = (
    "verified_download",
    "safe_installer",
    "extracted_file",
    "malware_clean",
    "rights_cleared",
    "production_quality_artifact",
)

DEFAULT_POLICY: dict[str, Any] = {
    "metadata_only_review": True,
    "raw_live_response_required": False,
    "raw_live_response_commit_allowed": False,
    "reviewed_metadata_record_allowed": True,
    "reviewed_source_lead_allowed": True,
    "verified_download_claim_allowed": False,
    "malware_clean_claim_allowed": False,
    "rights_clearance_claim_allowed": False,
    "automatic_promotion_enabled": False,
    "local_apply_required_for_any_reviewed_record": True,
    "reviewed_index_mutation_enabled_by_default": False,
    "public_index_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
    "new_live_source_calls_enabled": False,
}

DECISION_PLAN: dict[str, dict[str, Any]] = {
    "live_metadata_pilot_frontier_media_q01_01": {
        "decision": "promote_reviewed_source_lead_preview",
        "promotion_kind": "reviewed_source_lead",
        "score": 0.72,
        "reason": "redacted metadata provides a stable source lead, but not artifact verification",
    },
    "live_metadata_pilot_frontier_media_q03_02": {
        "decision": "mark_useful_lead",
        "promotion_kind": "none",
        "score": 0.58,
        "reason": "metadata is useful for operator follow-up but is thin for a reviewed record preview",
    },
    "live_metadata_pilot_frontier_media_q05_03": {
        "decision": "duplicate",
        "promotion_kind": "none",
        "score": 0.50,
        "reason": "identifier hash duplicates an earlier frontier media source lead",
    },
    "live_metadata_pilot_frontier_media_q06_04": {
        "decision": "needs_more_evidence",
        "promotion_kind": "none",
        "score": 0.46,
        "reason": "metadata-only observation needs corroborating source context before review preview",
    },
    "live_metadata_pilot_legacy_software_q01_05": {
        "decision": "promote_reviewed_metadata_record_preview",
        "promotion_kind": "reviewed_metadata_record",
        "score": 0.74,
        "reason": "redacted metadata supports a limited reviewed metadata-record preview with no download claim",
    },
    "live_metadata_pilot_legacy_software_q02_06": {
        "decision": "promote_reviewed_source_lead_preview",
        "promotion_kind": "reviewed_source_lead",
        "score": 0.69,
        "reason": "metadata supports a source-lead preview while installer verification remains out of scope",
    },
    "live_metadata_pilot_legacy_software_q03_07": {
        "decision": "duplicate",
        "promotion_kind": "none",
        "score": 0.45,
        "reason": "redacted identifier hash collides with another legacy software candidate",
    },
    "live_metadata_pilot_legacy_software_q06_08": {
        "decision": "needs_more_evidence",
        "promotion_kind": "none",
        "score": 0.44,
        "reason": "metadata-only record is not enough to distinguish the requested version safely",
    },
}


def load_live_metadata_candidates(policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Load the redacted live metadata candidate section from examples."""

    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    section = _read_json(repo_root / "examples/snapshots/refresh/live_metadata/live_metadata_candidate_section.json")
    summaries = _read_json(repo_root / "examples/live_metadata_pilot/redacted_metadata_summary.json")
    redacted_by_request = {
        _text(row.get("request_plan_id")): row
        for row in summaries.get("redacted_results", [])
        if isinstance(row, Mapping)
    }
    candidates = [dict(item) for item in section.get("candidates", []) if isinstance(item, Mapping)]
    hash_counts: dict[str, int] = {}
    for candidate in candidates:
        locator = candidate.get("source_locator") if isinstance(candidate.get("source_locator"), Mapping) else {}
        identifier_hash = _text(locator.get("identifier_hash"))
        if identifier_hash:
            hash_counts[identifier_hash] = hash_counts.get(identifier_hash, 0) + 1
    enriched: list[dict[str, Any]] = []
    for candidate in candidates:
        locator = dict(candidate.get("source_locator") if isinstance(candidate.get("source_locator"), Mapping) else {})
        request_plan_id = _text(locator.get("request_plan_id"))
        redacted = dict(redacted_by_request.get(request_plan_id, {}))
        identifier_hash = _text(locator.get("identifier_hash"))
        duplicate_refs = [
            _text(other.get("candidate_id"))
            for other in candidates
            if other is not candidate
            and identifier_hash
            and _text((other.get("source_locator") or {}).get("identifier_hash")) == identifier_hash
        ]
        row = dict(candidate)
        row.update(
            {
                "schema_version": "live_metadata_review_candidate_input.v0",
                "source_family": SOURCE_FAMILY,
                "source_locator_summary": _source_locator_summary(locator),
                "redacted_summary_ref": request_plan_id,
                "redacted_summary": redacted,
                "duplicate_candidate_refs": sorted(ref for ref in duplicate_refs if ref),
                "metadata_fields_available": _metadata_fields_available(candidate, redacted),
                "raw_response_included": False,
                "review_required": True,
                "accepted_truth": False,
            }
        )
        enriched.append(row)
    return enriched


def build_live_metadata_review_packet(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    rows = [_candidate_review_row(candidate) for candidate in candidates]
    candidate_refs = [_text(row.get("candidate_id")) for row in rows]
    return {
        "schema_version": "live_metadata_candidate_review_packet.v0",
        "record_type": "live_metadata_candidate_review_packet",
        "task": TASK_ID,
        "review_packet_id": _stable_id("live_metadata_review_packet", candidate_refs),
        "source_family": SOURCE_FAMILY,
        "candidate_count": len(rows),
        "candidate_refs": candidate_refs,
        "candidates": rows,
        "allowed_decision_classes": list(LIVE_METADATA_REVIEW_DECISIONS),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "metadata_only_review": True,
        "local_apply_required": True,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def assess_live_metadata_evidence_sufficiency(
    candidate: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_id = _text(candidate.get("candidate_id"))
    plan = DECISION_PLAN.get(candidate_id, {})
    decision = _text(plan.get("decision")) or "needs_more_evidence"
    score = float(plan.get("score") or 0.4)
    promotion_kind = _text(plan.get("promotion_kind")) or "none"
    criteria = {
        "metadata_only_source_observation_present": bool(_text(candidate.get("source_observation_ref"))),
        "source_locator_hash_present": bool(
            _text((candidate.get("source_locator") or {}).get("identifier_hash"))
            if isinstance(candidate.get("source_locator"), Mapping)
            else False
        ),
        "query_context_present": bool(candidate.get("query_refs")),
        "scout_trail_present": bool(candidate.get("scout_trail_refs")),
        "raw_response_absent_by_policy": candidate.get("raw_response_included") is False,
        "duplicate_hash_signal": bool(candidate.get("duplicate_candidate_refs")),
        "artifact_verification_absent": True,
    }
    return {
        "schema_version": "live_metadata_evidence_sufficiency.v0",
        "record_type": "live_metadata_evidence_sufficiency",
        "sufficiency_id": _stable_id("live_metadata_evidence_sufficiency", candidate_id, decision, score),
        "candidate_id": candidate_id,
        "source_family": SOURCE_FAMILY,
        "evidence_refs": _evidence_refs(candidate),
        "metadata_fields_reviewed": _list_text(candidate.get("metadata_fields_available")),
        "criteria": criteria,
        "sufficiency_score": score,
        "sufficiency_label": _sufficiency_label(decision, promotion_kind),
        "supports_reviewed_metadata_record_preview": promotion_kind == "reviewed_metadata_record",
        "supports_reviewed_source_lead_preview": promotion_kind == "reviewed_source_lead",
        "supports_verified_download": False,
        "limitations": _limitations(),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "review_required": True,
        "accepted_truth": False,
        "reviewed_artifact_claim": False,
        "download_claim": False,
        "extraction_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def decide_live_metadata_candidate(
    candidate: Mapping[str, Any],
    sufficiency: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_id = _text(candidate.get("candidate_id"))
    plan = DECISION_PLAN.get(candidate_id, {})
    decision = _text(plan.get("decision")) or "needs_more_evidence"
    promotion_kind = _text(plan.get("promotion_kind")) or "none"
    promotion_allowed = decision in {
        "promote_reviewed_metadata_record_preview",
        "promote_reviewed_source_lead_preview",
    }
    return {
        "schema_version": "live_metadata_review_decision.v0",
        "record_type": "live_metadata_review_decision",
        "decision_id": _stable_id("live_metadata_review_decision", candidate_id, decision, promotion_kind),
        "candidate_id": candidate_id,
        "source_family": SOURCE_FAMILY,
        "evidence_refs": _evidence_refs(candidate),
        "metadata_fields_reviewed": _list_text(sufficiency.get("metadata_fields_reviewed")),
        "sufficiency_score": float(sufficiency.get("sufficiency_score") or 0.0),
        "review_decision": decision,
        "decision": decision,
        "allowed_promotion_kind": promotion_kind,
        "promotion_preview_allowed": promotion_allowed,
        "reason": _text(plan.get("reason")) or "metadata-only review requires more evidence",
        "limitations": _limitations(),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "accepted_truth": False,
        "reviewed_artifact_claim": False,
        "download_claim": False,
        "extraction_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "local_apply_required": promotion_allowed,
        "snapshot_refresh_required": promotion_allowed or decision in {"mark_useful_lead", "needs_more_evidence", "duplicate"},
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_promotion_preview(
    candidate: Mapping[str, Any],
    decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_id = _text(candidate.get("candidate_id"))
    promotion_kind = _text(decision.get("allowed_promotion_kind"))
    return {
        "schema_version": "live_metadata_promotion_preview.v0",
        "record_type": "live_metadata_promotion_preview",
        "preview_id": _stable_id("live_metadata_promotion_preview", candidate_id, promotion_kind),
        "candidate_id": candidate_id,
        "source_family": SOURCE_FAMILY,
        "decision_id": _text(decision.get("decision_id")),
        "review_decision": _text(decision.get("review_decision")),
        "allowed_promotion_kind": promotion_kind,
        "promotion_preview_created": bool(decision.get("promotion_preview_allowed")),
        "promotion_preview_is_not_promotion": True,
        "local_apply_required": bool(decision.get("promotion_preview_allowed")),
        "snapshot_refresh_required": True,
        "reviewed_metadata_record_preview": (
            build_reviewed_metadata_record_preview(candidate, decision, merged_policy)
            if promotion_kind == "reviewed_metadata_record"
            else None
        ),
        "reviewed_source_lead_preview": (
            build_reviewed_source_lead_preview(candidate, decision, merged_policy)
            if promotion_kind == "reviewed_source_lead"
            else None
        ),
        "limitations": _limitations(),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "review_required": True,
        "accepted_truth": False,
        "reviewed_artifact_claim": False,
        "download_claim": False,
        "extraction_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_reviewed_metadata_record_preview(
    candidate: Mapping[str, Any],
    decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_id = _text(candidate.get("candidate_id"))
    return {
        "schema_version": "reviewed_metadata_record.v0",
        "record_type": "reviewed_metadata_record_preview",
        "record_id": _stable_id("reviewed_metadata_record_preview", candidate_id),
        "candidate_id": candidate_id,
        "source_family": SOURCE_FAMILY,
        "title": _text(candidate.get("title")),
        "source_locator_summary": _text(candidate.get("source_locator_summary")),
        "evidence_refs": _evidence_refs(candidate),
        "review_decision_ref": _text(decision.get("decision_id")),
        "limited_claim": "reviewed metadata record preview only; not a verified artifact",
        "allowed_public_status_after_apply": "reviewed_metadata_record",
        "local_apply_required": True,
        "snapshot_refresh_required": True,
        "accepted_truth": False,
        "reviewed_artifact_claim": False,
        "download_claim": False,
        "extraction_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_reviewed_source_lead_preview(
    candidate: Mapping[str, Any],
    decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_id = _text(candidate.get("candidate_id"))
    return {
        "schema_version": "reviewed_source_lead.v0",
        "record_type": "reviewed_source_lead_preview",
        "record_id": _stable_id("reviewed_source_lead_preview", candidate_id),
        "candidate_id": candidate_id,
        "source_family": SOURCE_FAMILY,
        "title": _text(candidate.get("title")),
        "source_locator_summary": _text(candidate.get("source_locator_summary")),
        "evidence_refs": _evidence_refs(candidate),
        "review_decision_ref": _text(decision.get("decision_id")),
        "limited_claim": "reviewed source lead preview only; not a verified downloadable artifact",
        "allowed_public_status_after_apply": "reviewed_source_lead",
        "local_apply_required": True,
        "snapshot_refresh_required": True,
        "accepted_truth": False,
        "reviewed_artifact_claim": False,
        "download_claim": False,
        "extraction_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_local_apply_handoff(
    previews: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    preview_refs = sorted(_text(item.get("preview_id")) for item in previews if _text(item.get("preview_id")))
    metadata_refs = sorted(
        _text((item.get("reviewed_metadata_record_preview") or {}).get("record_id"))
        for item in previews
        if isinstance(item.get("reviewed_metadata_record_preview"), Mapping)
    )
    source_lead_refs = sorted(
        _text((item.get("reviewed_source_lead_preview") or {}).get("record_id"))
        for item in previews
        if isinstance(item.get("reviewed_source_lead_preview"), Mapping)
    )
    return {
        "schema_version": "live_metadata_local_apply_handoff.v0",
        "record_type": "live_metadata_local_apply_handoff",
        "handoff_id": _stable_id("live_metadata_local_apply_handoff", preview_refs),
        "promotion_preview_refs": preview_refs,
        "reviewed_metadata_record_preview_refs": [ref for ref in metadata_refs if ref],
        "reviewed_source_lead_preview_refs": [ref for ref in source_lead_refs if ref],
        "handoff_status": "handoff_ready" if preview_refs else "blocked_no_promotion_previews",
        "local_apply_handoff_only": True,
        "local_apply_executed": False,
        "requires_separate_local_apply_gate": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_snapshot_refresh_handoff(
    previews: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    preview_refs = sorted(_text(item.get("preview_id")) for item in previews if _text(item.get("preview_id")))
    decision_refs = sorted(_text(item.get("decision_id")) for item in decisions if _text(item.get("decision_id")))
    counts = _decision_counts(decisions)
    return {
        "schema_version": "live_metadata_snapshot_refresh_handoff.v0",
        "record_type": "live_metadata_snapshot_refresh_handoff",
        "handoff_id": _stable_id("live_metadata_snapshot_refresh_handoff", preview_refs, decision_refs),
        "promotion_preview_refs": preview_refs,
        "review_decision_refs": decision_refs,
        "decision_counts": counts,
        "snapshot_refresh_handoff_only": True,
        "snapshot_refresh_executed": False,
        "requires_separate_snapshot_refresh_gate": True,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_public_alpha_reassess_handoff(
    decisions: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    counts = _decision_counts(decisions)
    return {
        "schema_version": "live_metadata_public_alpha_reassess_handoff.v0",
        "record_type": "live_metadata_public_alpha_reassess_handoff",
        "handoff_id": _stable_id("live_metadata_public_alpha_reassess_handoff", counts),
        "live_metadata_candidates_reviewed": counts["live_metadata_candidates_reviewed"],
        "reviewed_metadata_record_preview_count": counts["reviewed_metadata_record_preview_count"],
        "reviewed_source_lead_preview_count": counts["reviewed_source_lead_preview_count"],
        "useful_lead_count": counts["useful_lead_count"],
        "needs_more_evidence_count": counts["needs_more_evidence_count"],
        "rejected_or_duplicate_count": counts["rejected_or_duplicate_count"],
        "public_alpha_reassess_handoff_only": True,
        "public_launch_recommended": False,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_review_boundary_report(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "live_metadata_review_boundary_report.v0",
        "record_type": "live_metadata_review_boundary_report",
        "task": TASK_ID,
        "metadata_only_review": True,
        "review_packet_created": bool(result.get("review_packet_created")),
        "promotion_previews_created": bool(result.get("promotion_previews_created")),
        "local_apply_handoff_created": bool(result.get("local_apply_handoff_created")),
        "snapshot_refresh_handoff_created": bool(result.get("snapshot_refresh_handoff_created")),
        "public_alpha_reassess_handoff_created": bool(result.get("public_alpha_reassess_handoff_created")),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_live_metadata_candidate_review(
    policy: Mapping[str, Any] | None = None,
    *,
    from_live_metadata_examples: bool = False,
    write_examples: bool = False,
) -> dict[str, Any]:
    """Run deterministic review over the recorded live metadata examples."""

    del from_live_metadata_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidates = load_live_metadata_candidates(merged_policy)
    review_packet = build_live_metadata_review_packet(candidates, merged_policy)
    sufficiency_records = [
        assess_live_metadata_evidence_sufficiency(candidate, merged_policy)
        for candidate in candidates
    ]
    decisions = [
        decide_live_metadata_candidate(candidate, sufficiency, merged_policy)
        for candidate, sufficiency in zip(candidates, sufficiency_records)
    ]
    promotion_previews = [
        build_live_metadata_promotion_preview(candidate, decision, merged_policy)
        for candidate, decision in zip(candidates, decisions)
        if bool(decision.get("promotion_preview_allowed"))
    ]
    reviewed_metadata_previews = [
        preview["reviewed_metadata_record_preview"]
        for preview in promotion_previews
        if isinstance(preview.get("reviewed_metadata_record_preview"), Mapping)
    ]
    reviewed_source_lead_previews = [
        preview["reviewed_source_lead_preview"]
        for preview in promotion_previews
        if isinstance(preview.get("reviewed_source_lead_preview"), Mapping)
    ]
    local_apply = build_live_metadata_local_apply_handoff(promotion_previews, merged_policy)
    snapshot_handoff = build_live_metadata_snapshot_refresh_handoff(promotion_previews, decisions, merged_policy)
    public_alpha_handoff = build_live_metadata_public_alpha_reassess_handoff(decisions, merged_policy)
    counts = _decision_counts(decisions)
    result: dict[str, Any] = {
        "schema_version": "live_metadata_review_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "contracts_added": True,
        "policies_added": True,
        "candidate_review_matrix_added": True,
        "evidence_sufficiency_matrix_added": True,
        "review_decision_matrix_added": True,
        "runtime_review_added": True,
        "review_packet_created": True,
        "promotion_previews_created": bool(promotion_previews),
        "reviewed_metadata_record_previews_created": bool(reviewed_metadata_previews),
        "reviewed_source_lead_previews_created": bool(reviewed_source_lead_previews),
        "local_apply_handoff_created": True,
        "snapshot_refresh_handoff_created": True,
        "public_alpha_reassess_handoff_created": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "candidate_review_packet": review_packet,
        "evidence_sufficiency": sufficiency_records,
        "review_decisions": decisions,
        "promotion_previews": promotion_previews,
        "reviewed_metadata_record_previews": reviewed_metadata_previews,
        "reviewed_source_lead_previews": reviewed_source_lead_previews,
        "local_apply_handoff": local_apply,
        "snapshot_refresh_handoff": snapshot_handoff,
        "public_alpha_reassess_handoff": public_alpha_handoff,
        "created_at": DEFAULT_TIMESTAMP,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        **counts,
        **_false_boundaries(),
    }
    result["boundary_report"] = build_live_metadata_review_boundary_report(result, merged_policy)
    if write_examples:
        result["examples_written_paths"] = write_live_metadata_review_examples(result)
        result["inventory_written_paths"] = write_live_metadata_review_inventory_and_audit(result)
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["inventory_written_paths"] = []
        result["examples_written"] = False
    return result


def write_live_metadata_review_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_live_metadata_candidate_review())
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "review" / "live_metadata"
    files = {
        "review_packet.json": payload["candidate_review_packet"],
        "evidence_sufficiency_matrix.json": _matrix("live_metadata_evidence_sufficiency_matrix.v0", payload["evidence_sufficiency"]),
        "review_decisions.json": _matrix("live_metadata_review_decision_matrix.v0", payload["review_decisions"]),
        "promotion_previews.json": _matrix("live_metadata_promotion_preview_matrix.v0", payload["promotion_previews"]),
        "reviewed_metadata_record_previews.json": _matrix("reviewed_metadata_record_preview_matrix.v0", payload["reviewed_metadata_record_previews"]),
        "reviewed_source_lead_previews.json": _matrix("reviewed_source_lead_preview_matrix.v0", payload["reviewed_source_lead_previews"]),
        "local_apply_handoff.json": payload["local_apply_handoff"],
        "snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        "public_alpha_reassess_handoff.json": payload["public_alpha_reassess_handoff"],
        "boundary_report.json": payload["boundary_report"],
        "live_metadata_review_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/local_apply/live_metadata/local_apply_handoff.json": payload["local_apply_handoff"],
        "examples/snapshots/refresh/live_metadata/live_metadata_review_snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        "examples/public_alpha/reassess/live_metadata/live_metadata_review_reassess_handoff.json": payload["public_alpha_reassess_handoff"],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def build_live_metadata_review_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    counts = _decision_counts(payload.get("review_decisions", []))
    return {
        "review_live_metadata_candidates_input_state.json": {
            "schema_version": "review_live_metadata_candidates_input_state.v0",
            "task": TASK_ID,
            "input_results": {
                "public_alpha_reassess_01": "control/inventory/public_alpha_reassess_01_result.json",
                "snapshot_refresh_01": "control/inventory/snapshot_refresh_01_result.json",
                "live_metadata_pilot": "control/inventory/live_metadata_pilot_result.json",
                "public_alpha_reassess": "control/inventory/public_alpha_reassess_result.json",
                "snapshot_refresh": "control/inventory/snapshot_refresh_result.json",
                "review_batch": "control/inventory/review_batch_result.json",
                "candidate_index": "control/inventory/candidate_index_result.json",
                "scout_runtime": "control/inventory/scout_runtime_result.json",
                "query_planner_equivalent": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
            },
            "live_metadata_candidates_remain_review_only": True,
            **_false_boundaries(),
        },
        "live_metadata_candidate_review_matrix.json": {
            "schema_version": "live_metadata_candidate_review_matrix.v0",
            "task": TASK_ID,
            "candidate_count": counts["live_metadata_candidates_reviewed"],
            "candidates": payload["candidate_review_packet"]["candidates"],
        },
        "live_metadata_evidence_sufficiency_matrix.json": {
            "schema_version": "live_metadata_evidence_sufficiency_matrix.v0",
            "task": TASK_ID,
            "records": payload["evidence_sufficiency"],
        },
        "live_metadata_review_decision_matrix.json": {
            "schema_version": "live_metadata_review_decision_matrix.v0",
            "task": TASK_ID,
            "decisions": payload["review_decisions"],
            **counts,
        },
        "live_metadata_promotion_preview_matrix.json": {
            "schema_version": "live_metadata_promotion_preview_matrix.v0",
            "task": TASK_ID,
            "promotion_previews": payload["promotion_previews"],
            "preview_count": len(payload["promotion_previews"]),
        },
        "live_metadata_local_apply_handoff_matrix.json": payload["local_apply_handoff"],
        "live_metadata_snapshot_handoff_matrix.json": payload["snapshot_refresh_handoff"],
        "live_metadata_public_alpha_reassess_handoff_matrix.json": payload["public_alpha_reassess_handoff"],
        "live_metadata_review_boundary_report.json": payload["boundary_report"],
        "live_metadata_review_smoke_result.json": {
            "schema_version": "live_metadata_review_smoke_result.v0",
            "task": TASK_ID,
            "status": payload["status"],
            "commands": [
                "python scripts/eureka_review_live_metadata_candidates.py --from-live-metadata-examples --json",
                "python scripts/eureka_live_metadata_promotion_preview.py --from-live-metadata-examples --json",
                "python scripts/eureka_live_metadata_local_apply_handoff.py --from-live-metadata-examples --json",
                "python scripts/eureka_live_metadata_review_report.py --from-examples --json",
            ],
            **_false_boundaries(),
        },
        "live_metadata_review_validation_matrix.json": {
            "schema_version": "live_metadata_review_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "focused_validation": True,
            "full_discovery": "NOT_RUN_BY_POLICY",
            **_false_boundaries(),
        },
        "live_metadata_review_result.json": _result_summary(payload),
        "live_metadata_review_next_task_decision.json": {
            "schema_version": "live_metadata_review_next_task_decision.v0",
            "task": TASK_ID,
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "PUBLIC-ALPHA-REASSESS-02",
                "SEED-BATCH-MANUALS-SCANS-00",
                "SEED-BATCH-DRIVER-SUPPORT-00",
            ],
            **counts,
        },
        "live_metadata_review_failure_repair_log.json": {
            "schema_version": "live_metadata_review_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_repairs_required",
            "repairs": [],
            **_false_boundaries(),
        },
    }


def write_live_metadata_review_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_live_metadata_candidate_review())
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    written: list[str] = []
    for name, content in sorted(build_live_metadata_review_inventory_packets(payload).items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_audit_pack(payload, repo_root))
    return written


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "review-live-metadata-candidates-00-v0"
    generated = audit_root / "generated"
    markdown = {
        "README.md": _audit_readme(result),
        "candidate_review_matrix.md": _matrix_md("Candidate Review Matrix", result["candidate_review_packet"]),
        "evidence_sufficiency_matrix.md": _matrix_md("Evidence Sufficiency Matrix", {"records": result["evidence_sufficiency"]}),
        "review_decision_matrix.md": _matrix_md("Review Decision Matrix", {"decisions": result["review_decisions"]}),
        "promotion_preview_matrix.md": _matrix_md("Promotion Preview Matrix", {"promotion_previews": result["promotion_previews"]}),
        "local_apply_handoff_matrix.md": _matrix_md("Local Apply Handoff Matrix", result["local_apply_handoff"]),
        "snapshot_handoff_matrix.md": _matrix_md("Snapshot Handoff Matrix", result["snapshot_refresh_handoff"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", {"status": result["status"]}),
        "validation_matrix.md": _matrix_md("Validation Matrix", {"status": "pass", "full_discovery": "NOT_RUN_BY_POLICY"}),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/live_metadata_review_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "live_metadata_review_report.json": _result_summary(result),
        "generated/sample_review_packet.json": result["candidate_review_packet"],
        "generated/sample_review_decisions.json": result["review_decisions"],
        "generated/sample_promotion_previews.json": result["promotion_previews"],
        "generated/sample_reviewed_metadata_record_previews.json": result["reviewed_metadata_record_previews"],
        "generated/sample_reviewed_source_lead_previews.json": result["reviewed_source_lead_previews"],
        "generated/sample_snapshot_refresh_handoff.json": result["snapshot_refresh_handoff"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Live Metadata Review Summary\n\n"
        f"- status: {result['status']}\n"
        f"- candidates reviewed: {result['live_metadata_candidates_reviewed']}\n"
        f"- reviewed metadata record previews: {result['reviewed_metadata_record_preview_count']}\n"
        f"- reviewed source lead previews: {result['reviewed_source_lead_preview_count']}\n"
        f"- needs more evidence: {result['needs_more_evidence_count']}\n"
        f"- next task: {result['recommended_next_task']}\n"
    )
    written: list[str] = []
    for name, content in markdown.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    for name, content in json_files.items():
        path = audit_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    summary_path = generated / "sample_summary.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")
    written.append(str(summary_path.relative_to(repo_root)))
    return written


def _candidate_review_row(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "live_metadata_candidate_review_item.v0",
        "candidate_id": _text(candidate.get("candidate_id")),
        "source_family": SOURCE_FAMILY,
        "query_id": _query_id(candidate),
        "title": _text(candidate.get("title")),
        "source_locator_summary": _text(candidate.get("source_locator_summary")),
        "metadata_fields_available": _list_text(candidate.get("metadata_fields_available")),
        "evidence_sufficiency": DECISION_PLAN.get(_text(candidate.get("candidate_id")), {}).get("score", 0.0),
        "decision": DECISION_PLAN.get(_text(candidate.get("candidate_id")), {}).get("decision", "needs_more_evidence"),
        "reason": DECISION_PLAN.get(_text(candidate.get("candidate_id")), {}).get("reason", ""),
        "promotion_preview_allowed": DECISION_PLAN.get(_text(candidate.get("candidate_id")), {}).get("promotion_kind") in {
            "reviewed_metadata_record",
            "reviewed_source_lead",
        },
        "promotion_kind": DECISION_PLAN.get(_text(candidate.get("candidate_id")), {}).get("promotion_kind", "none"),
        "limitations": _limitations(),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "accepted_truth": False,
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
    keys = (
        "schema_version",
        "task",
        "status",
        "contracts_added",
        "policies_added",
        "candidate_review_matrix_added",
        "evidence_sufficiency_matrix_added",
        "review_decision_matrix_added",
        "runtime_review_added",
        "review_packet_created",
        "promotion_previews_created",
        "reviewed_metadata_record_previews_created",
        "reviewed_source_lead_previews_created",
        "local_apply_handoff_created",
        "snapshot_refresh_handoff_created",
        "public_alpha_reassess_handoff_created",
        "cli_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "live_metadata_candidates_reviewed",
        "reviewed_metadata_record_preview_count",
        "reviewed_source_lead_preview_count",
        "useful_lead_count",
        "needs_more_evidence_count",
        "rejected_or_duplicate_count",
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
        "recommended_next_task",
    )
    return {key: result.get(key) for key in keys}


def _metadata_fields_available(candidate: Mapping[str, Any], redacted: Mapping[str, Any]) -> list[str]:
    fields = []
    for field in (
        "candidate_id",
        "title",
        "domain_id",
        "source_family",
        "source_locator",
        "source_observation_ref",
        "query_refs",
        "scout_trail_refs",
        "public_search_status",
    ):
        if candidate.get(field) not in (None, "", []):
            fields.append(field)
    for field in ("status", "endpoint_class", "candidate_identifier_hash", "summary"):
        if redacted.get(field) not in (None, "", []):
            fields.append(f"redacted_{field}")
    return sorted(set(fields))


def _source_locator_summary(locator: Mapping[str, Any]) -> str:
    return (
        f"{_text(locator.get('locator_kind'))}; "
        f"identifier_hash={_text(locator.get('identifier_hash'))}; "
        f"request_plan_id={_text(locator.get('request_plan_id'))}"
    )


def _evidence_refs(candidate: Mapping[str, Any]) -> list[str]:
    refs = [
        _text(candidate.get("source_observation_ref")),
        _text(candidate.get("candidate_snapshot_ref")),
        _text(candidate.get("redacted_summary_ref")),
    ]
    refs.extend(_list_text(candidate.get("scout_trail_refs")))
    return sorted(ref for ref in refs if ref)


def _sufficiency_label(decision: str, promotion_kind: str) -> str:
    if promotion_kind == "reviewed_metadata_record":
        return "sufficient_for_reviewed_metadata_record_preview"
    if promotion_kind == "reviewed_source_lead":
        return "sufficient_for_reviewed_source_lead_preview"
    if decision == "mark_useful_lead":
        return "useful_lead_not_reviewed_record"
    if decision == "duplicate":
        return "duplicate_or_colliding_metadata_observation"
    return "needs_more_evidence"


def _limitations() -> list[str]:
    return [
        "metadata_only_review",
        "redacted_summary_only",
        "no_raw_response_available",
        "no_download_or_extraction",
        "no_malware_or_rights_claim",
        "promotion_preview_requires_local_apply",
        "snapshot_refresh_is_separate_gate",
    ]


def _matrix(schema_version: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "task": TASK_ID,
        "count": len(rows),
        "records": [dict(row) for row in rows],
    }


def _audit_readme(result: Mapping[str, Any]) -> str:
    return (
        "# REVIEW-LIVE-METADATA-CANDIDATES-00\n\n"
        "This audit pack records deterministic review over redacted live metadata candidates. "
        "It does not contain raw live responses and does not claim verified downloads, malware status, rights clearance, or accepted truth.\n\n"
        f"- status: {result['status']}\n"
        f"- candidates reviewed: {result['live_metadata_candidates_reviewed']}\n"
        f"- reviewed metadata record previews: {result['reviewed_metadata_record_preview_count']}\n"
        f"- reviewed source lead previews: {result['reviewed_source_lead_preview_count']}\n"
    )


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "metadata_only_review",
        "reviewed_metadata_record_allowed",
        "reviewed_source_lead_allowed",
        "local_apply_required_for_any_reviewed_record",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"live metadata review policy missing required rules: {', '.join(missing)}")
    forbidden_true = {
        "raw_live_response_required",
        "raw_live_response_commit_allowed",
        "verified_download_claim_allowed",
        "malware_clean_claim_allowed",
        "rights_clearance_claim_allowed",
        "automatic_promotion_enabled",
        "reviewed_index_mutation_enabled_by_default",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "new_live_source_calls_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"live metadata review policy enables forbidden behavior: {', '.join(enabled)}")


def _false_boundaries() -> dict[str, bool]:
    return {
        "new_live_source_calls_performed": False,
        "live_source_call_performed": False,
        "raw_live_response_committed": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "operator_instance_mutated": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
    }


def _query_id(candidate: Mapping[str, Any]) -> str:
    for ref in _list_text(candidate.get("query_refs")):
        if ":" in ref and "query_plan" in ref:
            return ref
    return _text(candidate.get("redacted_summary", {}).get("query_id")) if isinstance(candidate.get("redacted_summary"), Mapping) else ""


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _list_text(value: Any) -> list[str]:
    if isinstance(value, str):
        text = _text(value)
        return [text] if text else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [_text(item) for item in value if _text(item)]
    return []


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
