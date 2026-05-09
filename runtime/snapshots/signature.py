"""Snapshot signature-envelope posture.

Current D-BUNDLE-01 behavior validates unsigned/placeholder/malformed envelope
metadata only. It does not create real signatures or use private keys.
"""

from __future__ import annotations

from typing import Any, Mapping

from runtime.snapshots.manifest import detect_snapshot_boundary_violations, product_boundary, stable_id, truth_boundary


ENVELOPE_SCHEMA_VERSION = "snapshot_signature_envelope.v0"
REPORT_SCHEMA_VERSION = "snapshot_signature_verification_report.v0"
SIGNATURE_STATUSES = {"unsigned", "placeholder_only", "malformed", "verification_not_available", "verified_future"}


def build_unsigned_signature_envelope(snapshot: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot_ref = snapshot.get("snapshot_envelope_id") or snapshot.get("snapshot_manifest_id", "")
    return {
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "signature_envelope_id": stable_id("snapshot_signature_envelope", {"snapshot": snapshot_ref, "status": "unsigned"}),
        "snapshot_ref": snapshot_ref,
        "signature_status": "unsigned",
        "signature_kind": "none_current",
        "signer_ref": "",
        "public_key_ref_future": "",
        "signature_value_ref_future": "",
        "verification_method": "not_performed_unsigned_local",
        "verification_status": "verification_not_available",
        "limitations": ["Unsigned local snapshot envelope does not imply trust."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def build_placeholder_signature_envelope(snapshot: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    envelope = build_unsigned_signature_envelope(snapshot, policy)
    envelope.update(
        {
            "signature_envelope_id": stable_id("snapshot_signature_envelope", {"snapshot": envelope["snapshot_ref"], "status": "placeholder_only"}),
            "signature_status": "placeholder_only",
            "signature_kind": "placeholder_documentation_only",
            "verification_method": "placeholder_not_cryptographic",
            "verification_status": "verification_not_available",
            "limitations": ["Placeholder signature envelope is documentation only and does not imply trust."],
        }
    )
    return envelope


def validate_snapshot_signature_envelope(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "signature_envelope_id",
        "snapshot_ref",
        "signature_status",
        "signature_kind",
        "signer_ref",
        "public_key_ref_future",
        "signature_value_ref_future",
        "verification_method",
        "verification_status",
        "limitations",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in envelope:
            errors.append(f"missing snapshot signature field: {field}")
    if envelope.get("schema_version") != ENVELOPE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {ENVELOPE_SCHEMA_VERSION}")
    if envelope.get("signature_status") not in SIGNATURE_STATUSES:
        errors.append(f"signature_status is not allowed: {envelope.get('signature_status')}")
    if "private" in str(envelope.get("signer_ref", "")).casefold():
        errors.append("private key refs are forbidden")
    errors.extend(detect_snapshot_boundary_violations(envelope))
    return sorted(dict.fromkeys(errors))


def build_snapshot_signature_verification_report(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    validation_errors = validate_snapshot_signature_envelope(envelope, policy)
    status = "blocked_malformed_signature_envelope" if envelope.get("signature_status") == "malformed" or validation_errors else "unsigned_or_placeholder_only"
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "signature_verification_report_id": stable_id("snapshot_signature_verification_report", envelope),
        "signature_envelope_ref": envelope.get("signature_envelope_id", ""),
        "verification_status": status,
        "verification_performed": False,
        "verification_method": envelope.get("verification_method", "not_performed"),
        "private_key_used": False,
        "real_signature_created": False,
        "warnings": ["Real signature verification is future work."] if status != "blocked_malformed_signature_envelope" else [],
        "blockers": validation_errors if status == "blocked_malformed_signature_envelope" else [],
        "limitations": ["No private keys are used and no real signature is created in D-BUNDLE-01."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def validate_snapshot_signature_verification_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    for field in (
        "schema_version",
        "signature_verification_report_id",
        "signature_envelope_ref",
        "verification_status",
        "verification_performed",
        "verification_method",
        "private_key_used",
        "real_signature_created",
        "warnings",
        "blockers",
        "limitations",
        "truth_boundary",
        "product_boundary",
    ):
        if field not in report:
            errors.append(f"missing signature verification report field: {field}")
    if report.get("schema_version") != REPORT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {REPORT_SCHEMA_VERSION}")
    if report.get("private_key_used") is not False:
        errors.append("private_key_used must be false")
    if report.get("real_signature_created") is not False:
        errors.append("real_signature_created must be false")
    errors.extend(detect_snapshot_boundary_violations(report))
    return sorted(dict.fromkeys(errors))
