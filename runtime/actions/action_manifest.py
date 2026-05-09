"""Build and validate non-executing J0 action manifests."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.actions.action_policy import (
    FORBIDDEN_EFFECTS,
    action_product_boundary,
    action_truth_boundary,
    detect_action_boundary_violations,
    normalize_action_family,
    stable_id,
    subject_ref,
    subject_type,
    validate_action_allowed,
)
from runtime.actions.blocked_action import build_blocked_action_report


SCHEMA_VERSION = "action_manifest.v0"
RESULT_PREVIEW_SCHEMA_VERSION = "action_result_preview.v0"
ACTION_STATUSES = {
    "example_only",
    "manifest_only",
    "descriptive_only",
    "blocked_by_policy",
    "review_required",
    "not_evaluable",
}
ACTION_OUTPUTS = {
    "view": ["action_result_preview"],
    "inspect": ["action_result_preview"],
    "compare": ["compare_action_manifest_preview"],
    "cite": ["citation_bundle_preview"],
    "export": ["export_manifest_preview"],
    "preserve_manifest": ["preservation_manifest_preview"],
    "acquisition_manifest": ["acquisition_manifest_preview"],
    "blocked_action": ["blocked_action_report"],
}


def build_action_manifest(subject: Mapping[str, Any] | None, action_family: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    subject = subject or {}
    family = normalize_action_family(action_family)
    allowed, reasons = validate_action_allowed(family, policy)
    status = "manifest_only" if allowed else "blocked_by_policy"
    blocked_report = build_blocked_action_report(family, subject, policy) if not allowed else None
    return {
        "schema_version": SCHEMA_VERSION,
        "action_manifest_id": stable_id("action_manifest", {"family": family, "subject": subject_ref(subject), "allowed": allowed}),
        "action_family": family,
        "action_status": status,
        "subject_ref": subject_ref(subject),
        "subject_type": subject_type(subject),
        "action_label": _label_for(family, allowed),
        "action_summary": _summary_for(family, allowed),
        "allowed_effects": _allowed_effects(family) if allowed else ["blocked_action_report"],
        "forbidden_effects": FORBIDDEN_EFFECTS,
        "required_review_gates": _review_gates(family, allowed),
        "generated_outputs": ACTION_OUTPUTS.get(family, ["blocked_action_report"]),
        "blocked_reason": "; ".join(reasons),
        "blocked_action_report_ref": blocked_report.get("blocked_action_report_id") if blocked_report else "",
        "limitations": [
            "The manifest describes a safe action envelope only.",
            "No download, mirror, install, execution, emulation, public-index mutation, or truth acceptance is performed.",
        ],
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
        "notes": ["J0 action manifests are review-gated and non-executing."],
    }


def build_action_result_preview(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": RESULT_PREVIEW_SCHEMA_VERSION,
        "action_result_preview_id": stable_id("action_result_preview", manifest),
        "action_manifest_ref": manifest.get("action_manifest_id", ""),
        "preview_status": "preview_only",
        "preview_summary": f"Would present descriptive output for {manifest.get('action_family', 'unknown')} without executing an action.",
        "outputs_previewed": manifest.get("generated_outputs", []),
        "performed_effects": [],
        "forbidden_effects": manifest.get("forbidden_effects", FORBIDDEN_EFFECTS),
        "truth_boundary": action_truth_boundary(),
        "product_boundary": action_product_boundary(),
        "notes": ["Preview record is not proof that an action was performed."],
    }


def validate_action_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "action_manifest_id",
        "action_family",
        "action_status",
        "subject_ref",
        "subject_type",
        "action_label",
        "action_summary",
        "allowed_effects",
        "forbidden_effects",
        "required_review_gates",
        "generated_outputs",
        "blocked_reason",
        "limitations",
        "truth_boundary",
        "product_boundary",
        "notes",
    }
    for field in sorted(required):
        if field not in manifest:
            errors.append(f"missing action manifest field: {field}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("action_status") not in ACTION_STATUSES:
        errors.append(f"action_status is not allowed: {manifest.get('action_status')}")
    family = normalize_action_family(str(manifest.get("action_family", "")))
    allowed, _ = validate_action_allowed(family, policy)
    if allowed and manifest.get("action_status") == "blocked_by_policy":
        errors.append(f"safe action family should not be blocked: {family}")
    if not allowed and manifest.get("action_status") != "blocked_by_policy":
        errors.append(f"risky or unknown action family must be blocked: {family}")
    errors.extend(detect_action_boundary_violations(manifest))
    return sorted(dict.fromkeys(errors))


def summarize_action_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "action_summary.v0",
        "action_manifest_id": manifest.get("action_manifest_id", ""),
        "action_family": manifest.get("action_family", ""),
        "action_status": manifest.get("action_status", ""),
        "subject_ref": manifest.get("subject_ref", ""),
        "generated_output_count": len(manifest.get("generated_outputs", [])) if isinstance(manifest.get("generated_outputs"), list) else 0,
        "blocked": manifest.get("action_status") == "blocked_by_policy",
        "download_enabled": False,
        "mirror_enabled": False,
        "install_enabled": False,
        "execute_enabled": False,
        "emulate_enabled": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _label_for(family: str, allowed: bool) -> str:
    if not allowed:
        return f"{family.replace('_', ' ').title()} Blocked"
    labels = {
        "view": "View Metadata",
        "inspect": "Inspect Local Record",
        "compare": "Compare Records",
        "cite": "Build Citation Bundle",
        "export": "Build Export Manifest",
        "preserve_manifest": "Build Preservation Manifest",
        "acquisition_manifest": "Explain Acquisition Path",
        "blocked_action": "Explain Blocked Action",
    }
    return labels.get(family, family.replace("_", " ").title())


def _summary_for(family: str, allowed: bool) -> str:
    if not allowed:
        return f"{family} is disabled and represented only by a blocked action report."
    return f"Build a non-executing descriptive manifest for {family}."


def _allowed_effects(family: str) -> list[str]:
    if family == "view":
        return ["metadata_view_preview"]
    if family == "inspect":
        return ["local_record_inspection_preview"]
    if family == "compare":
        return ["comparison_manifest_preview"]
    if family == "cite":
        return ["citation_bundle_preview"]
    if family == "export":
        return ["export_manifest_preview"]
    if family == "preserve_manifest":
        return ["preservation_manifest_preview"]
    if family == "acquisition_manifest":
        return ["acquisition_manifest_preview"]
    return ["blocked_action_report"]


def _review_gates(family: str, allowed: bool) -> list[str]:
    gates = ["review_before_public_display", "review_before_downstream_action"]
    if not allowed:
        gates.extend(["future_risky_action_policy", "rights_review", "risk_review"])
    if family in {"acquisition_manifest", "preserve_manifest"}:
        gates.extend(["rights_review_before_any_future_download_or_mirror", "risk_review_before_any_future_execution"])
    return sorted(dict.fromkeys(gates))
