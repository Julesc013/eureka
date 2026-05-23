"""Deterministic local fixity reports for quarantined pack exports.

Fixity is local content identity only. It is not source authenticity, a real
signature, pack acceptance, evidence acceptance, or public truth.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Mapping


SCHEMA_VERSION = "pack_fixity_report.v0"


def fixity_truth_boundary() -> dict[str, bool]:
    return {
        "fixity_implies_authenticity": False,
        "quarantined_pack_is_accepted": False,
        "quarantined_pack_is_imported": False,
        "quarantined_pack_is_submitted": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def pack_product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_pack_import_runtime": False,
        "enabled_pack_submission_runtime": False,
        "enabled_hosted_upload_runtime": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def canonicalize_pack_for_hash(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> bytes:
    """Return deterministic JSON bytes used for local SHA-256 fixity."""

    payload = deepcopy(dict(pack))
    for volatile in (
        "fixity_report",
        "signature_verification_report",
        "quarantine_result",
        "import_preview",
        "contribution_review_seed",
    ):
        payload.pop(volatile, None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def compute_pack_sha256(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    return hashlib.sha256(canonicalize_pack_for_hash(pack, policy)).hexdigest()


def build_pack_fixity_report(pack: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    pack_ref = _pack_ref(pack)
    hash_value = compute_pack_sha256(pack, policy)
    return {
        "schema_version": SCHEMA_VERSION,
        "fixity_report_id": f"pack_fixity.{hash_value[:16]}.v0",
        "pack_ref": pack_ref,
        "canonical_serialization_policy": {
            "format": "json",
            "sort_keys": True,
            "separators": [",", ":"],
            "encoding": "utf-8",
            "volatile_fields_removed": [
                "fixity_report",
                "signature_verification_report",
                "quarantine_result",
                "import_preview",
                "contribution_review_seed",
            ],
        },
        "hash_algorithm": "sha256",
        "hash_value": hash_value,
        "hash_input_summary": {
            "pack_ref": pack_ref,
            "pack_schema_version": pack.get("schema_version", ""),
            "pack_type": _pack_type(pack),
            "local_content_identity_only": True,
            "source_authenticity_claimed": False,
        },
        "deterministic": True,
        "verification_status": "computed_local",
        "limitations": [
            "SHA-256 fixity identifies this local serialized content only.",
            "Fixity does not establish source authenticity, trust, acceptance, rights, safety, or installability.",
        ],
        "truth_boundary": fixity_truth_boundary(),
        "product_boundary": pack_product_boundary(),
    }


def validate_pack_fixity_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "fixity_report_id",
        "pack_ref",
        "canonical_serialization_policy",
        "hash_algorithm",
        "hash_value",
        "hash_input_summary",
        "deterministic",
        "verification_status",
        "limitations",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in report:
            errors.append(f"missing fixity report field: {field}")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if report.get("hash_algorithm") != "sha256":
        errors.append("hash_algorithm must be sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", str(report.get("hash_value", ""))):
        errors.append("hash_value must be a lowercase SHA-256 hex digest")
    if report.get("deterministic") is not True:
        errors.append("deterministic must be true")
    truth = report.get("truth_boundary", {})
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be an object")
    else:
        for key, expected in fixity_truth_boundary().items():
            if truth.get(key) is not expected:
                errors.append(f"truth_boundary.{key} must be {str(expected).lower()}")
    product = report.get("product_boundary", {})
    if not isinstance(product, Mapping):
        errors.append("product_boundary must be an object")
    else:
        for key, expected in pack_product_boundary().items():
            if product.get(key) is not expected:
                errors.append(f"product_boundary.{key} must be {str(expected).lower()}")
    return sorted(dict.fromkeys(errors))


def _pack_ref(pack: Mapping[str, Any]) -> str:
    for key in ("pack_export_id", "pack_id", "quarantine_request_id", "pack_draft_id"):
        if pack.get(key):
            return str(pack[key])
    digest = hashlib.sha256(canonicalize_pack_for_hash(pack)).hexdigest()[:16]
    return f"pack.local.{digest}.v0"


def _pack_type(pack: Mapping[str, Any]) -> str:
    return str(pack.get("export_pack_type") or pack.get("input_pack_type") or pack.get("pack_type") or "unknown_pack")
