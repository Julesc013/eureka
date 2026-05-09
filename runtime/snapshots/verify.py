"""Snapshot bundle verification reports."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.snapshots.envelope import validate_snapshot_envelope
from runtime.snapshots.fixity import validate_snapshot_fixity_report
from runtime.snapshots.manifest import (
    detect_snapshot_boundary_violations,
    product_boundary,
    stable_id,
    truth_boundary,
    validate_snapshot_manifest,
)
from runtime.snapshots.signature import (
    build_snapshot_signature_verification_report,
    validate_snapshot_signature_envelope,
)


SCHEMA_VERSION = "snapshot_verification_report.v0"


def verify_snapshot_bundle(
    envelope: Mapping[str, Any],
    manifest: Mapping[str, Any],
    records_or_policy: Any | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = {"envelope": envelope, "manifest": manifest}
    return build_snapshot_verification_report(inputs, policy or (records_or_policy if isinstance(records_or_policy, Mapping) else None))


def build_snapshot_verification_report(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    envelope = inputs.get("envelope", {})
    manifest = inputs.get("manifest", {})
    fixity = inputs.get("fixity_report", {})
    signature = inputs.get("signature_envelope", {})
    render_results = inputs.get("render_results", [])
    envelope_errors = validate_snapshot_envelope(envelope, policy) if isinstance(envelope, Mapping) else ["envelope missing"]
    manifest_errors = validate_snapshot_manifest(manifest, policy) if isinstance(manifest, Mapping) else ["manifest missing"]
    fixity_errors = validate_snapshot_fixity_report(fixity, policy) if isinstance(fixity, Mapping) and fixity else []
    signature_errors = validate_snapshot_signature_envelope(signature, policy) if isinstance(signature, Mapping) and signature else []
    signature_report = build_snapshot_signature_verification_report(signature, policy) if isinstance(signature, Mapping) and signature else {}
    blockers = envelope_errors + manifest_errors + fixity_errors + signature_errors
    if signature.get("signature_status") == "malformed":
        blockers.append("malformed_signature_envelope")
    return {
        "schema_version": SCHEMA_VERSION,
        "verification_report_id": stable_id("snapshot_verification_report", {"envelope": envelope, "manifest": manifest, "fixity": fixity, "signature": signature}),
        "snapshot_ref": envelope.get("snapshot_envelope_id", manifest.get("snapshot_manifest_id", "")) if isinstance(envelope, Mapping) else "",
        "manifest_valid": not manifest_errors,
        "records_valid": not manifest_errors,
        "fixity_valid": not fixity_errors if fixity else False,
        "signature_envelope_valid": not signature_errors and signature.get("signature_status") != "malformed" if signature else False,
        "render_outputs_valid": all(isinstance(item, Mapping) and not detect_snapshot_boundary_violations(item) for item in render_results) if isinstance(render_results, list) else False,
        "semantic_parity_checked": True,
        "verification_status": "verified_local" if not blockers else "blocked_by_policy_or_validation",
        "signature_verification_ref": signature_report.get("signature_verification_report_id", ""),
        "warnings": ["Unsigned or placeholder signatures do not imply trust."] if signature and not blockers else [],
        "blockers": sorted(dict.fromkeys(blockers)),
        "limitations": ["Verification is local/offline and does not create public truth or source authenticity."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def validate_snapshot_verification_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    for field in (
        "schema_version",
        "verification_report_id",
        "snapshot_ref",
        "manifest_valid",
        "records_valid",
        "fixity_valid",
        "signature_envelope_valid",
        "render_outputs_valid",
        "semantic_parity_checked",
        "verification_status",
        "warnings",
        "blockers",
        "limitations",
        "truth_boundary",
        "product_boundary",
    ):
        if field not in report:
            errors.append(f"missing verification report field: {field}")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    errors.extend(detect_snapshot_boundary_violations(report))
    return sorted(dict.fromkeys(errors))
