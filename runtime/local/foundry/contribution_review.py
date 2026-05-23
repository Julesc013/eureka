"""Contribution review and trust preview helpers for pack quarantine."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.local.foundry.pack_fixity import pack_product_boundary


REVIEW_SEED_SCHEMA_VERSION = "contribution_review_seed.v0"
TRUST_PREVIEW_SCHEMA_VERSION = "pack_trust_revocation_preview.v0"


def review_truth_boundary() -> dict[str, bool]:
    return {
        "review_seed_is_review_decision": False,
        "quarantined_pack_is_accepted": False,
        "quarantined_pack_is_imported": False,
        "quarantined_pack_is_submitted": False,
        "accepted_evidence": False,
        "accepted_candidate": False,
        "accepted_public_record": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def trust_truth_boundary() -> dict[str, bool]:
    truth = review_truth_boundary()
    truth.update(
        {
            "signature_placeholder_implies_trust": False,
            "trust_preview_creates_trust": False,
            "revocation_preview_revokes_pack": False,
        }
    )
    return truth


def build_contribution_review_seed(
    pack: Mapping[str, Any],
    quarantine_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    blockers = list(quarantine_result.get("blocker_summary", {}).get("blockers", []))
    pack_ref = quarantine_result.get("input_pack_ref") or pack.get("pack_export_id", "")
    return {
        "schema_version": REVIEW_SEED_SCHEMA_VERSION,
        "contribution_review_seed_id": f"contribution_review_seed.{quarantine_result.get('quarantine_result_id', 'unknown')}.v0",
        "input_pack_ref": pack_ref,
        "review_subject_type": quarantine_result.get("input_pack_type", "exported_pack_draft"),
        "review_reason": "pack_quarantine_requires_review",
        "proposed_review_entry": {
            "subject_ref": pack_ref,
            "subject_type": quarantine_result.get("input_pack_type", "exported_pack_draft"),
            "review_status": "seed_only",
            "review_decision_created": False,
            "automatic_acceptance_allowed": False,
        },
        "missing_evidence": _missing_evidence(quarantine_result),
        "policy_blockers": blockers,
        "rights_risk_blockers": _rights_risk_blockers(quarantine_result),
        "trust_notes": [
            "Unsigned or placeholder signature posture requires human review.",
            "Fixity does not create authenticity or trust.",
        ],
        "limitations": [
            "Review seed is not a review decision.",
            "No pack import, submission, publication, upload, acceptance, or trust mutation occurs.",
        ],
        "truth_boundary": review_truth_boundary(),
        "product_boundary": pack_product_boundary(),
    }


def build_pack_trust_preview(
    pack: Mapping[str, Any],
    quarantine_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": TRUST_PREVIEW_SCHEMA_VERSION,
        "trust_preview_id": f"pack_trust_preview.{quarantine_result.get('quarantine_result_id', 'unknown')}.v0",
        "pack_ref": quarantine_result.get("input_pack_ref") or pack.get("pack_export_id", ""),
        "trust_status": "preview_only_no_trust_created",
        "trust_inputs": {
            "fixity_report_ref": quarantine_result.get("fixity_report_ref", ""),
            "signature_verification_report_ref": quarantine_result.get("signature_verification_report_ref", ""),
            "provenance_summary_available": bool(quarantine_result.get("provenance_summary")),
        },
        "revocation_status": "not_revoked_preview_only",
        "revocation_reasons": [],
        "dispute_or_takedown_refs_future": [],
        "limitations": [
            "Trust preview does not create trust.",
            "Revocation preview does not revoke anything.",
        ],
        "truth_boundary": trust_truth_boundary(),
        "product_boundary": pack_product_boundary(),
    }


def build_pack_revocation_preview(
    pack: Mapping[str, Any],
    quarantine_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    preview = build_pack_trust_preview(pack, quarantine_result, policy)
    preview["trust_preview_id"] = f"pack_revocation_preview.{quarantine_result.get('quarantine_result_id', 'unknown')}.v0"
    preview["trust_status"] = "revocation_preview_only_no_trust_change"
    preview["revocation_status"] = "preview_only_no_revocation"
    preview["revocation_reasons"] = list(quarantine_result.get("blocker_summary", {}).get("blockers", []))
    return preview


def validate_contribution_review_seed(seed: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if seed.get("schema_version") != REVIEW_SEED_SCHEMA_VERSION:
        errors.append(f"schema_version must be {REVIEW_SEED_SCHEMA_VERSION}")
    truth = seed.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be an object")
    else:
        for key, expected in review_truth_boundary().items():
            if truth.get(key) is not expected:
                errors.append(f"truth_boundary.{key} must be {str(expected).lower()}")
    proposed = seed.get("proposed_review_entry", {})
    if isinstance(proposed, Mapping) and proposed.get("review_decision_created") is not False:
        errors.append("proposed_review_entry.review_decision_created must be false")
    return sorted(dict.fromkeys(errors))


def validate_pack_trust_preview(preview: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if preview.get("schema_version") != TRUST_PREVIEW_SCHEMA_VERSION:
        errors.append(f"schema_version must be {TRUST_PREVIEW_SCHEMA_VERSION}")
    truth = preview.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be an object")
    else:
        for key, expected in trust_truth_boundary().items():
            if truth.get(key) is not expected:
                errors.append(f"truth_boundary.{key} must be {str(expected).lower()}")
    return sorted(dict.fromkeys(errors))


def _missing_evidence(quarantine_result: Mapping[str, Any]) -> list[str]:
    missing = ["human_review_decision", "future_import_policy_approval"]
    if quarantine_result.get("signature_verification_report_ref"):
        missing.append("real_signature_verification_future")
    return missing


def _rights_risk_blockers(quarantine_result: Mapping[str, Any]) -> list[str]:
    text = str(quarantine_result.get("limitations", [])).casefold()
    blockers: list[str] = []
    if "rights" in text:
        blockers.append("rights_review_required")
    if "risk" in text:
        blockers.append("risk_review_required")
    return blockers
