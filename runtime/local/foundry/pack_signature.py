"""Signature envelope validation for quarantined pack exports.

The current runtime validates envelope posture only. It does not use private
keys, create real signatures, or perform cryptographic verification.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from runtime.local.foundry.pack_fixity import pack_product_boundary


ENVELOPE_SCHEMA_VERSION = "pack_signature_envelope.v0"
REPORT_SCHEMA_VERSION = "pack_signature_verification_report.v0"
SIGNATURE_STATUSES = {
    "unsigned",
    "placeholder_only",
    "malformed",
    "verification_not_available",
    "verified_future",
}


def signature_truth_boundary() -> dict[str, bool]:
    return {
        "signature_placeholder_implies_trust": False,
        "quarantined_pack_is_accepted": False,
        "quarantined_pack_is_imported": False,
        "quarantined_pack_is_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def parse_pack_signature_envelope(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a normalized signature envelope without performing verification."""

    raw = pack.get("signature_envelope")
    pack_ref = _pack_ref(pack)
    if isinstance(raw, Mapping):
        envelope = deepcopy(dict(raw))
        envelope.setdefault("schema_version", ENVELOPE_SCHEMA_VERSION)
        envelope.setdefault("signature_envelope_id", f"pack_signature_envelope.{pack_ref}.v0")
        envelope.setdefault("pack_ref", pack_ref)
    else:
        signature_policy = pack.get("signature_policy", {})
        status = "unsigned"
        if isinstance(signature_policy, Mapping) and signature_policy.get("signature_status") in {
            "unsigned_placeholder_only",
            "placeholder_only",
        }:
            status = "placeholder_only"
        envelope = {
            "schema_version": ENVELOPE_SCHEMA_VERSION,
            "signature_envelope_id": f"pack_signature_envelope.{pack_ref}.v0",
            "pack_ref": pack_ref,
            "signature_status": status,
            "signature_kind": "none" if status == "unsigned" else "placeholder",
            "signer_ref": "",
            "public_key_ref_future": "",
            "signature_value_ref_future": "",
            "verification_method": "envelope_validation_only",
            "verification_status": "not_performed",
            "limitations": ["No real cryptographic verification is performed in this bundle."],
            "truth_boundary": signature_truth_boundary(),
            "product_boundary": pack_product_boundary(),
        }
    envelope.setdefault("signature_status", "malformed")
    envelope.setdefault("signature_kind", "unknown")
    envelope.setdefault("signer_ref", "")
    envelope.setdefault("public_key_ref_future", "")
    envelope.setdefault("signature_value_ref_future", "")
    envelope.setdefault("verification_method", "envelope_validation_only")
    envelope.setdefault("verification_status", "not_performed")
    envelope.setdefault("limitations", ["Envelope validation only; real verification is future policy work."])
    envelope.setdefault("truth_boundary", signature_truth_boundary())
    envelope.setdefault("product_boundary", pack_product_boundary())
    return envelope


def validate_signature_envelope(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "signature_envelope_id",
        "pack_ref",
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
            errors.append(f"missing signature envelope field: {field}")
    if envelope.get("schema_version") != ENVELOPE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {ENVELOPE_SCHEMA_VERSION}")
    if envelope.get("signature_status") not in SIGNATURE_STATUSES:
        errors.append(f"signature_status is not allowed: {envelope.get('signature_status')}")
    if envelope.get("signature_status") == "verified_future":
        errors.append("verified_future is not allowed in current runtime")
    text = str(envelope).casefold()
    if "private_key" in text or "private key" in text or "-----begin" in text:
        errors.append("private key material is forbidden")
    if envelope.get("verification_method") not in {"envelope_validation_only", "not_available", "future_crypto_verification"}:
        errors.append("verification_method must be envelope validation only or future/deferred")
    truth = envelope.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be an object")
    else:
        for key, expected in signature_truth_boundary().items():
            if truth.get(key) is not expected:
                errors.append(f"truth_boundary.{key} must be {str(expected).lower()}")
    return sorted(dict.fromkeys(errors))


def build_signature_verification_report(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = validate_signature_envelope(envelope, policy)
    status = str(envelope.get("signature_status", "malformed"))
    if errors or status == "malformed":
        verification_status = "malformed_envelope"
    elif status == "unsigned":
        verification_status = "unsigned_needs_review"
    elif status == "placeholder_only":
        verification_status = "placeholder_only"
    else:
        verification_status = "verification_deferred"
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "signature_verification_report_id": f"pack_signature_verification.{envelope.get('signature_envelope_id', 'unknown')}.v0",
        "signature_envelope_ref": envelope.get("signature_envelope_id", ""),
        "verification_status": verification_status,
        "verification_performed": False,
        "verification_method": envelope.get("verification_method", "envelope_validation_only"),
        "private_key_used": False,
        "real_signature_created": False,
        "warnings": errors or _warnings_for_status(status),
        "limitations": [
            "Signature verification is envelope validation only in this bundle.",
            "Unsigned or placeholder envelopes require review before any future import or trust decision.",
        ],
        "truth_boundary": signature_truth_boundary(),
        "product_boundary": pack_product_boundary(),
    }


def validate_signature_verification_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != REPORT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {REPORT_SCHEMA_VERSION}")
    if report.get("verification_performed") is not False:
        errors.append("verification_performed must be false")
    if report.get("private_key_used") is not False:
        errors.append("private_key_used must be false")
    if report.get("real_signature_created") is not False:
        errors.append("real_signature_created must be false")
    truth = report.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be an object")
    else:
        for key, expected in signature_truth_boundary().items():
            if truth.get(key) is not expected:
                errors.append(f"truth_boundary.{key} must be {str(expected).lower()}")
    return sorted(dict.fromkeys(errors))


def _warnings_for_status(status: str) -> list[str]:
    if status == "unsigned":
        return ["pack is unsigned and requires review"]
    if status == "placeholder_only":
        return ["placeholder envelope does not establish trust"]
    return ["real signature verification is deferred"]


def _pack_ref(pack: Mapping[str, Any]) -> str:
    return str(pack.get("pack_export_id") or pack.get("pack_id") or pack.get("pack_draft_id") or "unknown_pack")
