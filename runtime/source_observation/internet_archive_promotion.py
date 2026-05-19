"""IA promotion preview helpers.

IA-06 promotion is a dry-run only. The helpers in this module build proposed
reviewed-record previews from approved IA review decisions without writing the
reviewed index or master index.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.source_observation.ids import stable_digest
from runtime.source_observation.internet_archive_metadata import SOURCE_ID
from runtime.source_observation.internet_archive_review import validate_ia_review_decision


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROMOTION_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_promotion_dry_run_policy.json"
DEFAULT_REVIEW_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_review_policy.json"


def load_ia_promotion_dry_run_policy(path: str | Path = DEFAULT_PROMOTION_POLICY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_ia_promotion_preview(
    review_decision: Mapping[str, Any],
    candidate: Mapping[str, Any] | None,
    policy: Mapping[str, Any],
) -> dict[str, Any] | None:
    _ensure_policy(policy)
    decision = dict(review_decision)
    review_policy = json.loads(DEFAULT_REVIEW_POLICY_PATH.read_text(encoding="utf-8"))
    decision_errors = validate_ia_review_decision(decision, review_policy)
    if decision_errors:
        raise ValueError("; ".join(decision_errors))
    if decision.get("decision") != "approve_for_reviewed_index_dry_run":
        return None
    source_candidate = dict(candidate or decision.get("candidate_snapshot", {}) or {})
    preview = {
        "schema_version": "ia_promotion_preview.v0",
        "promotion_preview_id": "iaprv_"
        + stable_digest({"review_decision_id": decision.get("review_decision_id"), "candidate_id": decision.get("candidate_id")}),
        "review_decision_id": str(decision.get("review_decision_id", "")),
        "review_item_id": str(decision.get("review_item_id", "")),
        "candidate_id": str(decision.get("candidate_id", "")),
        "source_id": SOURCE_ID,
        "proposed_reviewed_record_id": "iarprev_" + stable_digest({"candidate_id": decision.get("candidate_id", "")}),
        "proposed_title": _title(source_candidate),
        "proposed_summary": _summary(source_candidate),
        "source_locator": dict(source_candidate.get("source_locator", {}) or {}),
        "evidence_ids": list(source_candidate.get("evidence_ids", []) or []),
        "source_cache_record_ids": list(source_candidate.get("source_cache_record_ids", []) or []),
        "observation_ids": list(source_candidate.get("observation_ids", []) or []),
        "item_identifier": str(source_candidate.get("item_identifier", "")),
        "mediatype": str(source_candidate.get("mediatype", "")),
        "collection_refs": list(source_candidate.get("collection_refs", []) or []),
        "file_summary": dict(source_candidate.get("file_summary", {}) or {}),
        "checksum_summary": dict(source_candidate.get("checksum_summary", {}) or {}),
        "claim_summary": dict(source_candidate.get("claim_summary", {}) or {}),
        "provenance": dict(source_candidate.get("provenance", {}) or {}),
        "uncertainty": _uncertainty(source_candidate),
        "limitations": _limitations(source_candidate),
        "rights_flags": list(source_candidate.get("rights_flags", []) or []),
        "risk_flags": list(source_candidate.get("risk_flags", []) or []),
        "review_required": True,
        "promotion_dry_run_only": True,
        "reviewed_index_write_performed": False,
        "reviewed_index_mutation_performed": False,
        "master_index_write_performed": False,
        "master_index_mutation_performed": False,
        "accepted_truth": False,
        "raw_response_committed": False,
        "download_performed": False,
    }
    errors = validate_ia_promotion_preview(preview, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return preview


def build_ia_promotion_previews(
    review_decisions: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []
    for decision in review_decisions:
        preview = build_ia_promotion_preview(decision, None, policy)
        if preview is not None:
            previews.append(preview)
    return previews


def validate_ia_promotion_preview(preview: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if preview.get("schema_version") != "ia_promotion_preview.v0":
        errors.append("promotion preview schema mismatch")
    if preview.get("source_id") != SOURCE_ID:
        errors.append("source_id must be internet_archive_metadata")
    for key in (
        "promotion_preview_id",
        "review_decision_id",
        "candidate_id",
        "proposed_reviewed_record_id",
        "proposed_title",
        "proposed_summary",
        "source_locator",
        "evidence_ids",
        "source_cache_record_ids",
        "provenance",
        "uncertainty",
        "limitations",
        "rights_flags",
        "risk_flags",
    ):
        if key not in preview or preview.get(key) in ("", None, []):
            errors.append(f"{key} is required")
    if preview.get("review_required") is not True:
        errors.append("review_required must be true")
    if preview.get("promotion_dry_run_only") is not True:
        errors.append("promotion dry-run flag must be true")
    for key in (
        "accepted_truth",
        "reviewed_index_write_performed",
        "reviewed_index_mutation_performed",
        "master_index_write_performed",
        "master_index_mutation_performed",
        "raw_response_committed",
        "download_performed",
    ):
        if preview.get(key) is not False:
            errors.append(f"{key} must be false")
    if policy.get("promotion_dry_run_enabled") is not True:
        errors.append("promotion dry-run must be enabled")
    for key in (
        "reviewed_index_write_enabled",
        "master_index_write_enabled",
        "accepted_truth_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"policy expected false: {key}")
    return tuple(errors)


def build_ia_promotion_dry_run_report(previews: Sequence[Mapping[str, Any]], policy: Mapping[str, Any]) -> dict[str, Any]:
    _ensure_policy(policy)
    preview_list = [dict(preview) for preview in previews]
    errors = [error for preview in preview_list for error in validate_ia_promotion_preview(preview, policy)]
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "schema_version": "ia_promotion_dry_run_report.v0",
        "task": "IA-06",
        "status": "pass",
        "promotion_dry_run_only": True,
        "promotion_preview_count": len(preview_list),
        "promotion_preview_ids": [str(preview.get("promotion_preview_id", "")) for preview in preview_list],
        "promotion_previews": preview_list,
        "promotion_previews_created": bool(preview_list),
        "all_promotion_previews_dry_run_only": all(preview.get("promotion_dry_run_only") is True for preview in preview_list),
        "accepted_truth_created": any(preview.get("accepted_truth") is True for preview in preview_list),
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_ia_promotion_boundary_report(report: Mapping[str, Any]) -> dict[str, Any]:
    passed = (
        bool(report.get("all_promotion_previews_dry_run_only", True))
        and not bool(report.get("accepted_truth_created", False))
        and not bool(report.get("reviewed_index_mutated", False))
        and not bool(report.get("master_index_mutated", False))
    )
    return {
        "schema_version": "ia_promotion_boundary_report.v0",
        "task": "IA-06",
        "passed": passed,
        "violations": [] if passed else ["promotion_boundary_failed"],
        "promotion_dry_run_only": True,
        "promotion_previews_created": bool(report.get("promotion_previews_created", False)),
        "all_promotion_previews_dry_run_only": bool(report.get("all_promotion_previews_dry_run_only", True)),
        "accepted_truth_created": bool(report.get("accepted_truth_created", False)),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _ensure_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != "ia_promotion_dry_run_policy.v0":
        raise ValueError("IA promotion dry-run policy schema mismatch")
    if policy.get("promotion_dry_run_enabled") is not True:
        raise ValueError("IA promotion dry-run is not enabled for IA-06")
    if policy.get("reviewed_index_write_enabled") is not False:
        raise ValueError("reviewed index writes must remain disabled")
    if policy.get("master_index_write_enabled") is not False:
        raise ValueError("master index writes must remain disabled")
    if policy.get("accepted_truth_enabled") is not False:
        raise ValueError("accepted truth must remain disabled")


def _title(candidate: Mapping[str, Any]) -> str:
    return str(candidate.get("title") or candidate.get("candidate_title") or "IA reviewed-record preview")


def _summary(candidate: Mapping[str, Any]) -> str:
    value = str(candidate.get("summary") or candidate.get("candidate_summary") or "")
    if not value:
        return "Preview-only IA reviewed-record proposal; reviewed index was not written."
    return value + " Promotion remains preview-only and preserves uncertainty."


def _uncertainty(candidate: Mapping[str, Any]) -> list[str]:
    values = [str(item) for item in candidate.get("uncertainty", []) or [] if str(item)]
    for value in ("promotion is dry-run only", "reviewed index write is disabled", "master index write is disabled"):
        if value not in values:
            values.append(value)
    return values


def _limitations(candidate: Mapping[str, Any]) -> list[str]:
    values = [str(item) for item in candidate.get("limitations", []) or [] if str(item)]
    for value in (
        "preview is not a final reviewed record",
        "preview does not establish accepted truth",
        "no reviewed or master index mutation occurred",
    ):
        if value not in values:
            values.append(value)
    return values
