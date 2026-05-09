"""Plain text snapshot renderer."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.snapshots.manifest import product_boundary, stable_id, truth_boundary


def render_snapshot_text(bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest = bundle.get("manifest", bundle)
    records = manifest.get("records", []) if isinstance(manifest, Mapping) else []
    lines = ["Eureka Snapshot", "================", ""]
    lines.append(f"Manifest: {manifest.get('snapshot_manifest_id', '') if isinstance(manifest, Mapping) else ''}")
    lines.append("No live access, hosting, downloads, mirroring, execution, or truth acceptance.")
    lines.append("")
    for record in records:
        if not isinstance(record, Mapping):
            continue
        fields = record.get("render_fields", {})
        lines.extend(
            [
                f"Record: {record.get('canonical_ref', '')}",
                f"Identity: {fields.get('identity', record.get('canonical_ref', ''))}",
                f"Title: {fields.get('title', record.get('title', ''))}",
                f"Summary: {fields.get('summary', record.get('summary', ''))}",
                f"Source posture: {fields.get('source_posture', record.get('source_posture', ''))}",
                f"Evidence posture: {fields.get('evidence_posture', record.get('evidence_posture', ''))}",
                f"Compatibility posture: {fields.get('compatibility_posture', record.get('compatibility_posture', ''))}",
                f"Rights posture: {fields.get('rights_posture', record.get('rights_posture', ''))}",
                f"Risk posture: {fields.get('risk_posture', record.get('risk_posture', ''))}",
                f"Action posture: {fields.get('action_posture', record.get('action_posture', ''))}",
                "Limitations/no-claims: " + "; ".join(fields.get("limitations", []) + fields.get("no_claims", [])),
                "",
            ]
        )
    content = "\n".join(lines)
    return {
        "schema_version": "snapshot_render_result.v0",
        "render_result_id": stable_id("snapshot_render_result", {"profile": "text", "manifest": manifest.get("snapshot_manifest_id", "") if isinstance(manifest, Mapping) else ""}),
        "render_request_ref": "",
        "render_profile": "text",
        "output_summary": "Plain text snapshot summary.",
        "output_path_ref": "",
        "content": content,
        "required_semantic_fields_present": _required_fields_present(content),
        "omitted_fields": [],
        "warnings": [],
        "limitations": ["Text render is an offline projection and not a public route."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def _required_fields_present(content: str) -> bool:
    lowered = content.casefold()
    return all(phrase in lowered for phrase in ("identity", "source posture", "evidence posture", "rights posture", "risk posture", "action posture", "limitations/no-claims"))
