"""File-tree style snapshot renderer."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.snapshots.manifest import product_boundary, stable_id, truth_boundary


def render_snapshot_file_tree_index(bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest = bundle.get("manifest", bundle)
    records = manifest.get("records", []) if isinstance(manifest, Mapping) else []
    entries = [
        {"path": "README.txt", "entry_type": "readme", "summary": "Snapshot limitations and no-claims."},
        {"path": "manifest.json", "entry_type": "manifest", "summary": manifest.get("snapshot_manifest_id", "") if isinstance(manifest, Mapping) else ""},
    ]
    lines = ["snapshot/", "|-- README.txt", "|-- manifest.json", "`-- records/"]
    for record in records:
        if not isinstance(record, Mapping):
            continue
        name = f"{record.get('record_type', 'record')}-{record.get('snapshot_record_id', 'record').split('.')[-3]}.json"
        entries.append({"path": f"records/{name}", "entry_type": "record", "summary": record.get("summary", "")})
        lines.append(f"    |-- {name} # identity/source posture/evidence posture/rights posture/risk posture/action posture/limitations-no-claims")
    text = "\n".join(lines) + "\n"
    return {
        "schema_version": "snapshot_file_tree_index.v0",
        "file_tree_index_id": stable_id("snapshot_file_tree_index", entries),
        "snapshot_ref": manifest.get("snapshot_manifest_id", "") if isinstance(manifest, Mapping) else "",
        "entries": entries,
        "readme_summary": "Offline fixture snapshot index. No live access, hosting, downloads, mirroring, execution, or truth acceptance.",
        "manifest_refs": [manifest.get("snapshot_manifest_id", "")] if isinstance(manifest, Mapping) else [],
        "record_refs": [record.get("snapshot_record_id", "") for record in records if isinstance(record, Mapping)],
        "content": text,
        "limitations": ["File-tree render is descriptive and does not create files unless explicitly written to an allowed output path."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }
