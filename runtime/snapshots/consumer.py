"""Offline snapshot consumer reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from runtime.snapshots.fixity import validate_snapshot_fixity_report
from runtime.snapshots.manifest import (
    ensure_allowed_input_path,
    load_json,
    product_boundary,
    stable_id,
    truth_boundary,
    validate_snapshot_manifest,
)
from runtime.snapshots.signature import validate_snapshot_signature_envelope


SCHEMA_VERSION = "snapshot_consumer_report.v0"


def load_snapshot_bundle(paths: Mapping[str, str | Path], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    bundle: dict[str, Any] = {}
    for key in ("envelope", "manifest", "fixity", "signature"):
        if paths.get(key):
            bundle[key] = load_json(ensure_allowed_input_path(paths[key]))
    return bundle


def build_snapshot_consumer_report(bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest = bundle.get("manifest", {})
    fixity = bundle.get("fixity", {})
    signature = bundle.get("signature", {})
    manifest_errors = validate_snapshot_manifest(manifest, policy) if isinstance(manifest, Mapping) and manifest else ["manifest missing"]
    fixity_errors = validate_snapshot_fixity_report(fixity, policy) if isinstance(fixity, Mapping) and fixity else []
    signature_errors = validate_snapshot_signature_envelope(signature, policy) if isinstance(signature, Mapping) and signature else []
    blocked_actions = sorted(
        {
            action
            for record in manifest.get("records", []) if isinstance(record, Mapping)
            for action in record.get("render_fields", {}).get("blocked_actions", [])
        }
    ) if isinstance(manifest, Mapping) else []
    return {
        "schema_version": SCHEMA_VERSION,
        "consumer_report_id": stable_id("snapshot_consumer_report", bundle),
        "snapshot_ref": bundle.get("envelope", {}).get("snapshot_envelope_id", manifest.get("snapshot_manifest_id", "")) if isinstance(manifest, Mapping) else "",
        "consumer_mode": "local_fixture_offline",
        "records_loaded": manifest.get("record_count", 0) if isinstance(manifest, Mapping) else 0,
        "manifest_verified": not manifest_errors,
        "fixity_verified": not fixity_errors if fixity else False,
        "signature_status": signature.get("signature_status", "unsigned") if isinstance(signature, Mapping) else "unsigned",
        "render_targets_available": manifest.get("render_targets", []) if isinstance(manifest, Mapping) else [],
        "blocked_actions": blocked_actions,
        "limitations": ["Consumer report is local/offline only and does not activate relay, hosting, or public routes."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def validate_snapshot_consumer_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    for field in (
        "schema_version",
        "consumer_report_id",
        "snapshot_ref",
        "consumer_mode",
        "records_loaded",
        "manifest_verified",
        "fixity_verified",
        "signature_status",
        "render_targets_available",
        "blocked_actions",
        "limitations",
        "truth_boundary",
        "product_boundary",
    ):
        if field not in report:
            errors.append(f"missing consumer report field: {field}")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    from runtime.snapshots.manifest import detect_snapshot_boundary_violations

    errors.extend(detect_snapshot_boundary_violations(report))
    return sorted(dict.fromkeys(errors))
