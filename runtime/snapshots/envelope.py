"""Snapshot envelope builder."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from runtime.snapshots.manifest import (
    build_snapshot_manifest,
    detect_snapshot_boundary_violations,
    no_claims,
    product_boundary,
    stable_id,
    truth_boundary,
    validate_snapshot_manifest,
)


SCHEMA_VERSION = "snapshot_envelope.v0"
SNAPSHOT_STATUSES = {
    "example_only",
    "fixture_only",
    "local_generated",
    "verified_local",
    "unsigned_local",
    "policy_blocked",
    "incomplete",
    "not_evaluable",
}


def build_snapshot_envelope(input_records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest = build_snapshot_manifest(input_records, policy)
    source_refs = manifest["source_summary"]["source_refs"]
    evidence_refs = manifest["evidence_summary"]["evidence_refs"]
    action_refs = manifest["action_summary"]["action_refs"]
    snapshot_kind = "policy_blocked" if any(record.get("record_type") == "policy_blocked_record" for record in manifest["records"]) else "fixture_bundle"
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_envelope_id": stable_id("snapshot_envelope", manifest["snapshot_manifest_id"]),
        "snapshot_status": "policy_blocked" if snapshot_kind == "policy_blocked" else "unsigned_local",
        "snapshot_kind": snapshot_kind,
        "snapshot_label": "Eureka fixture snapshot bundle",
        "snapshot_scope": {
            "fixture_only": True,
            "offline_only": True,
            "record_count": manifest["record_count"],
            "render_profiles": manifest["render_targets"],
        },
        "manifest_ref": manifest["snapshot_manifest_id"],
        "records_ref": [record["snapshot_record_id"] for record in manifest["records"]],
        "fixity_report_ref": "",
        "signature_envelope_ref": "",
        "verification_report_ref": "",
        "render_result_refs": [],
        "source_refs": source_refs,
        "evidence_refs": evidence_refs,
        "action_refs": action_refs,
        "limitation_summary": manifest["limitations"],
        "no_claims": no_claims(),
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
        "notes": ["Snapshot envelope is local, unsigned by default, and does not publish or host anything."],
    }


def validate_snapshot_envelope(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "snapshot_envelope_id",
        "snapshot_status",
        "snapshot_kind",
        "snapshot_label",
        "snapshot_scope",
        "manifest_ref",
        "records_ref",
        "fixity_report_ref",
        "signature_envelope_ref",
        "verification_report_ref",
        "render_result_refs",
        "source_refs",
        "evidence_refs",
        "action_refs",
        "limitation_summary",
        "no_claims",
        "truth_boundary",
        "product_boundary",
        "notes",
    }
    for field in sorted(required):
        if field not in envelope:
            errors.append(f"missing snapshot envelope field: {field}")
    if envelope.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if envelope.get("snapshot_status") not in SNAPSHOT_STATUSES:
        errors.append(f"snapshot_status is not allowed: {envelope.get('snapshot_status')}")
    errors.extend(detect_snapshot_boundary_violations(envelope))
    return sorted(dict.fromkeys(errors))


def summarize_snapshot_envelope(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    scope = envelope.get("snapshot_scope", {})
    return {
        "schema_version": "snapshot_summary.v0",
        "snapshot_envelope_id": envelope.get("snapshot_envelope_id", ""),
        "snapshot_status": envelope.get("snapshot_status", ""),
        "snapshot_kind": envelope.get("snapshot_kind", ""),
        "record_count": scope.get("record_count", len(envelope.get("records_ref", []))),
        "fixture_only": scope.get("fixture_only", True),
        "relay_enabled": False,
        "hosting_enabled": False,
        "site_dist_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def build_envelope_for_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors = validate_snapshot_manifest(manifest, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_envelope_id": stable_id("snapshot_envelope", manifest["snapshot_manifest_id"]),
        "snapshot_status": "unsigned_local",
        "snapshot_kind": "fixture_bundle",
        "snapshot_label": "Eureka fixture snapshot bundle",
        "snapshot_scope": {
            "fixture_only": True,
            "offline_only": True,
            "record_count": manifest["record_count"],
            "render_profiles": manifest["render_targets"],
        },
        "manifest_ref": manifest["snapshot_manifest_id"],
        "records_ref": [record["snapshot_record_id"] for record in manifest["records"]],
        "fixity_report_ref": "",
        "signature_envelope_ref": "",
        "verification_report_ref": "",
        "render_result_refs": [],
        "source_refs": manifest["source_summary"]["source_refs"],
        "evidence_refs": manifest["evidence_summary"]["evidence_refs"],
        "action_refs": manifest["action_summary"]["action_refs"],
        "limitation_summary": manifest["limitations"],
        "no_claims": no_claims(),
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
        "notes": ["Envelope generated from an explicit manifest."],
    }
