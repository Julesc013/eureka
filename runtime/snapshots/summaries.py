"""Snapshot summary helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


def summarize_snapshot_bundle(bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest = bundle.get("manifest", bundle)
    records = manifest.get("records", []) if isinstance(manifest, Mapping) else []
    counts = Counter(record.get("record_type", "unknown") for record in records if isinstance(record, Mapping))
    return {
        "schema_version": "snapshot_summary.v0",
        "snapshot_ref": bundle.get("envelope", {}).get("snapshot_envelope_id", manifest.get("snapshot_manifest_id", "")) if isinstance(manifest, Mapping) else "",
        "record_count": len(records),
        "record_type_counts": dict(sorted(counts.items())),
        "render_targets": manifest.get("render_targets", []) if isinstance(manifest, Mapping) else [],
        "relay_enabled": False,
        "hosting_enabled": False,
        "site_dist_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def summarize_snapshot_render_result(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_render_summary.v0",
        "render_result_id": result.get("render_result_id") or result.get("file_tree_index_id", ""),
        "render_profile": result.get("render_profile", "file_tree" if result.get("schema_version") == "snapshot_file_tree_index.v0" else ""),
        "semantic_fields_present": result.get("required_semantic_fields_present", True),
        "warning_count": len(result.get("warnings", [])) if isinstance(result.get("warnings"), list) else 0,
        "relay_enabled": False,
        "hosting_enabled": False,
        "site_dist_mutated": False,
    }


def format_snapshot_summary(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Snapshot Summary",
        "",
        f"- Snapshot: {summary.get('snapshot_ref', '')}",
        f"- Records: {summary.get('record_count', 0)}",
        f"- Relay enabled: {str(summary.get('relay_enabled', False)).lower()}",
        f"- Hosting enabled: {str(summary.get('hosting_enabled', False)).lower()}",
        f"- Site dist mutated: {str(summary.get('site_dist_mutated', False)).lower()}",
        f"- Public index mutated: {str(summary.get('public_index_mutated', False)).lower()}",
        f"- Master index mutated: {str(summary.get('master_index_mutated', False)).lower()}",
    ]
    return "\n".join(lines) + "\n"
