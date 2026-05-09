"""Source-pack helper functions for H0 Source OS."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


ALLOWED_PACK_STATUS = {"example_only", "fixture_only", "audit_only", "draft_only", "export_preview_only", "blocked_by_policy", "not_evaluable"}
FORBIDDEN_TRUE_KEYS = {
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "downloaded_file",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "public_index_mutated",
    "rights_clearance_claimed",
    "source_pack_can_mutate_master_index",
    "source_pack_can_mutate_public_index",
    "source_pack_is_accepted_truth",
    "source_pack_is_imported_state",
    "source_pack_is_submitted",
    "verified_installability_claimed",
}


def build_source_pack_manifest(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    pack_id = str(inputs.get("source_pack_manifest_id", "source_pack.generated.v0"))
    pack = {
        "schema_version": "source_pack_manifest.v0",
        "source_pack_manifest_id": pack_id,
        "pack_status": str(inputs.get("pack_status", "draft_only")),
        "source_records": list(inputs.get("source_records", [])),
        "source_families": list(inputs.get("source_families", [])),
        "source_capabilities": list(inputs.get("source_capabilities", [])),
        "source_policy_refs": list(inputs.get("source_policy_refs", [])),
        "connector_family_refs": list(inputs.get("connector_family_refs", [])),
        "coverage_records": list(inputs.get("coverage_records", [])),
        "connector_scorecards": list(inputs.get("connector_scorecards", [])),
        "limitations": list(inputs.get("limitations", ["draft source pack only"])),
        "review_posture": dict(inputs.get("review_posture", {"review_required_before_import_or_submission": True})),
        "no_live_access_posture": dict(inputs.get("no_live_access_posture", {"live_access_enabled": False, "source_sync_enabled": False})),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": list(inputs.get("notes", ["Source pack is not accepted truth."])),
    }
    validate_source_pack_manifest(pack, policy)
    return pack


def validate_source_pack_manifest(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    if pack.get("schema_version") != "source_pack_manifest.v0":
        raise ValueError("source pack manifest schema_version must be source_pack_manifest.v0")
    if pack.get("pack_status") not in ALLOWED_PACK_STATUS:
        raise ValueError(f"unknown pack_status: {pack.get('pack_status')}")
    violations = detect_source_pack_truth_boundary_violations(pack, policy)
    if violations:
        raise ValueError("; ".join(violations))


def summarize_source_pack_manifest(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    violations = detect_source_pack_truth_boundary_violations(pack, policy)
    return {
        "schema_version": "source_pack_summary.v0",
        "status": "pass" if not violations else "invalid",
        "source_pack_manifest_id": pack.get("source_pack_manifest_id"),
        "pack_status": pack.get("pack_status"),
        "source_record_count": len(pack.get("source_records", [])),
        "coverage_record_count": len(pack.get("coverage_records", [])),
        "connector_scorecard_count": len(pack.get("connector_scorecards", [])),
        "source_families": list(pack.get("source_families", [])),
        "connector_family_refs": list(pack.get("connector_family_refs", [])),
        "truth_boundary_violations": violations,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }


def build_source_pack_export(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    validate_source_pack_manifest(pack, policy)
    export = {
        "schema_version": "source_pack_export.v0",
        "source_pack_export_id": f"{pack.get('source_pack_manifest_id', 'source_pack')}.export_preview",
        "source_pack_manifest_ref": pack.get("source_pack_manifest_id"),
        "export_status": "export_preview_only",
        "export_mode": "export_preview",
        "included_record_refs": list(pack.get("source_records", [])),
        "included_scorecard_refs": list(pack.get("connector_scorecards", [])),
        "included_coverage_refs": list(pack.get("coverage_records", [])),
        "limitations": ["export preview only", "not imported", "not submitted"],
        "review_posture": {"review_required_before_import_or_submission": True},
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Source pack export remains a draft preview."],
    }
    violations = detect_source_pack_truth_boundary_violations(export, policy)
    if violations:
        raise ValueError("; ".join(violations))
    return export


def detect_source_pack_truth_boundary_violations(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"{path}=true is forbidden for source-pack artifacts"
        for path, key, value in _iter_key_values(pack)
        if key in FORBIDDEN_TRUE_KEYS and value is True
    ]


def _truth_boundary() -> dict[str, bool]:
    return {
        "source_pack_is_accepted_truth": False,
        "source_pack_is_imported_state": False,
        "source_pack_is_submitted": False,
        "source_pack_can_mutate_public_index": False,
        "source_pack_can_mutate_master_index": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from _iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_key_values(child, f"{prefix}[{index}]")
