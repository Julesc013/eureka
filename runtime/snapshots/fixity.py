"""Snapshot fixity reports."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from runtime.snapshots.manifest import (
    detect_snapshot_boundary_violations,
    product_boundary,
    stable_id,
    stable_hash,
    truth_boundary,
)


SCHEMA_VERSION = "snapshot_fixity_report.v0"


def compute_snapshot_sha256(data: Any, policy: Mapping[str, Any] | None = None) -> str:
    if isinstance(data, bytes):
        payload = data
    elif isinstance(data, str):
        payload = data.encode("utf-8")
    else:
        payload = json.dumps(data, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_snapshot_fixity_report(
    envelope: Mapping[str, Any],
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    snapshot_ref = envelope.get("snapshot_envelope_id") or manifest.get("snapshot_manifest_id", "")
    record_list = list(records or manifest.get("records", []))
    return {
        "schema_version": SCHEMA_VERSION,
        "fixity_report_id": stable_id("snapshot_fixity_report", {"snapshot": snapshot_ref, "manifest": manifest}),
        "snapshot_ref": snapshot_ref,
        "canonical_serialization_policy": "json_sort_keys_compact_utf8",
        "hash_algorithm": "sha256",
        "record_hashes": [
            {
                "record_ref": record.get("snapshot_record_id", stable_id("snapshot_record", record)),
                "hash_algorithm": "sha256",
                "hash_value": stable_hash(record),
            }
            for record in record_list
        ],
        "manifest_hash": stable_hash(manifest),
        "envelope_hash": stable_hash(envelope),
        "deterministic": True,
        "verification_status": "local_fixity_recorded",
        "limitations": ["Fixity means local snapshot identity, not source authenticity or trust."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def validate_snapshot_fixity_report(report: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "fixity_report_id",
        "snapshot_ref",
        "canonical_serialization_policy",
        "hash_algorithm",
        "record_hashes",
        "manifest_hash",
        "envelope_hash",
        "deterministic",
        "verification_status",
        "limitations",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in report:
            errors.append(f"missing snapshot fixity field: {field}")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if report.get("hash_algorithm") != "sha256":
        errors.append("hash_algorithm must be sha256")
    if report.get("deterministic") is not True:
        errors.append("deterministic must be true")
    errors.extend(detect_snapshot_boundary_violations(report))
    return sorted(dict.fromkeys(errors))
