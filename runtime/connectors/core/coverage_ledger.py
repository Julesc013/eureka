"""Source coverage ledger helpers for H0 Source OS.

These helpers are pure local transformations. They do not call networks,
fetch URLs, mutate runtime state, or accept source observations as truth.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


CURRENT_COVERAGE_BASIS = {"example_only", "fixture_only", "audit_only", "local_dry_run"}
KNOWN_DEPTHS = {
    "D0_source_known",
    "D1_catalog_indexed",
    "D2_metadata_indexed",
    "D3_representation_indexed",
    "D4_content_indexed",
    "D5_action_indexed",
}
FORBIDDEN_TRUE_KEYS = {
    "accepted_candidate_truth",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "coverage_claims_exhaustive_global_coverage",
    "coverage_manifest_is_exhaustive_global_coverage",
    "coverage_record_can_claim_malware_safety",
    "coverage_record_can_claim_rights_clearance",
    "coverage_record_can_claim_verified_installability",
    "coverage_record_can_mutate_master_index",
    "coverage_record_can_mutate_public_index",
    "coverage_record_is_public_truth",
    "downloaded_file",
    "enabled_downloads",
    "enabled_live_probes",
    "enabled_source_sync",
    "exhaustive_global_coverage",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "public_index_mutated",
    "rights_clearance_claimed",
    "source_sync_enabled",
    "verified_installability_claimed",
}


def build_source_coverage_record(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a coverage record from explicit local inputs."""

    source_id = str(inputs.get("source_id", "unknown_source"))
    source_family = str(inputs.get("source_family", "unknown"))
    record = {
        "schema_version": "source_coverage_ledger.v0",
        "coverage_record_id": str(inputs.get("coverage_record_id", f"coverage.{source_id}.v0")),
        "source_id": source_id,
        "source_family": source_family,
        "source_record_ref": str(inputs.get("source_record_ref", "")),
        "connector_family_refs": list(inputs.get("connector_family_refs", [])),
        "coverage_status": str(inputs.get("coverage_status", "local_dry_run")),
        "coverage_depth_current": str(inputs.get("coverage_depth_current", "D0_source_known")),
        "coverage_depth_target_future": str(inputs.get("coverage_depth_target_future", "D2_metadata_indexed")),
        "coverage_scope": str(inputs.get("coverage_scope", "local coverage record")),
        "coverage_basis": str(inputs.get("coverage_basis", "local_dry_run")),
        "records_seen": int(inputs.get("records_seen", 0)),
        "records_normalized": int(inputs.get("records_normalized", 0)),
        "records_indexed_future": int(inputs.get("records_indexed_future", 0)),
        "source_cache_candidates": int(inputs.get("source_cache_candidates", 0)),
        "evidence_candidates": int(inputs.get("evidence_candidates", 0)),
        "review_queue_entries": int(inputs.get("review_queue_entries", 0)),
        "blocked_operations": list(inputs.get("blocked_operations", [])),
        "known_gaps": list(inputs.get("known_gaps", [])),
        "limitations": list(inputs.get("limitations", ["bounded local coverage only"])),
        "freshness_summary": dict(inputs.get("freshness_summary", {"basis": "local_input"})),
        "review_gates": dict(inputs.get("review_gates", {"human_review_required_for_public_claims": True})),
        "truth_boundary": _coverage_truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": list(inputs.get("notes", ["Coverage record is not public truth."])),
    }
    validate_source_coverage_record(record, policy)
    return record


def validate_source_coverage_record(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    """Validate H0 coverage invariants."""

    if record.get("schema_version") != "source_coverage_ledger.v0":
        raise ValueError("coverage record schema_version must be source_coverage_ledger.v0")
    if record.get("coverage_basis") not in CURRENT_COVERAGE_BASIS:
        raise ValueError(f"coverage basis is not approved for H0-BUNDLE-03: {record.get('coverage_basis')}")
    if record.get("coverage_depth_current") not in KNOWN_DEPTHS:
        raise ValueError(f"unknown coverage depth: {record.get('coverage_depth_current')}")
    if int(record.get("records_normalized", 0)) > int(record.get("records_seen", 0)):
        raise ValueError("records_normalized cannot exceed records_seen")
    violations = detect_coverage_truth_boundary_violations(record, policy)
    if violations:
        raise ValueError("; ".join(violations))


def build_source_coverage_manifest(records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a coverage manifest rollup from coverage records."""

    for record in records:
        validate_source_coverage_record(record, policy)
    family_counts = Counter(str(item.get("source_family", "unknown")) for item in records)
    depth_counts = Counter(str(item.get("coverage_depth_current", "unknown")) for item in records)
    connector_counts: Counter[str] = Counter()
    for record in records:
        connector_counts.update(str(item) for item in record.get("connector_family_refs", []) if item)
    manifest = {
        "schema_version": "source_coverage_manifest.v0",
        "coverage_manifest_id": "coverage_manifest.source_os_h0.v0",
        "manifest_status": "local_dry_run",
        "coverage_records": [{"coverage_record_id": item.get("coverage_record_id")} for item in records],
        "source_family_counts": dict(sorted(family_counts.items())),
        "trust_lane_counts": {"unknown": len(records)},
        "index_depth_counts": dict(sorted(depth_counts.items())),
        "connector_family_counts": dict(sorted(connector_counts.items())),
        "blocked_source_count": sum(1 for item in records if item.get("coverage_status") == "blocked_by_policy"),
        "unknown_source_count": sum(1 for item in records if item.get("source_id") in (None, "", "unknown_source")),
        "reviewed_source_count_future": 0,
        "limitations": ["Coverage manifest is a local H0 rollup, not exhaustive global coverage."],
        "truth_boundary": {
            "coverage_manifest_is_public_truth": False,
            "coverage_manifest_is_exhaustive_global_coverage": False,
            "coverage_manifest_can_mutate_public_index": False,
            "coverage_manifest_can_mutate_master_index": False,
        },
        "product_boundary": _product_boundary(),
        "notes": ["Manifest is review evidence only."],
    }
    violations = detect_coverage_truth_boundary_violations(manifest, policy)
    if violations:
        raise ValueError("; ".join(violations))
    return manifest


def summarize_source_coverage_manifest(manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a compact manifest summary."""

    violations = detect_coverage_truth_boundary_violations(manifest, policy)
    return {
        "schema_version": "source_coverage_summary.v0",
        "status": "pass" if not violations else "invalid",
        "coverage_record_count": len(manifest.get("coverage_records", [])),
        "source_family_counts": dict(manifest.get("source_family_counts", {})),
        "index_depth_counts": dict(manifest.get("index_depth_counts", {})),
        "connector_family_counts": dict(manifest.get("connector_family_counts", {})),
        "blocked_source_count": int(manifest.get("blocked_source_count", 0)),
        "truth_boundary_violations": violations,
        "truth_boundary": {
            "coverage_summary_is_public_truth": False,
            "coverage_summary_claims_exhaustive_global_coverage": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": _product_boundary(),
    }


def detect_coverage_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [
        f"{path}=true is forbidden for coverage artifacts"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_TRUE_KEYS and value is True
    ]


def _coverage_truth_boundary() -> dict[str, bool]:
    return {
        "coverage_record_is_public_truth": False,
        "coverage_claims_exhaustive_global_coverage": False,
        "coverage_record_can_mutate_public_index": False,
        "coverage_record_can_mutate_master_index": False,
        "coverage_record_can_claim_rights_clearance": False,
        "coverage_record_can_claim_malware_safety": False,
        "coverage_record_can_claim_verified_installability": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
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
