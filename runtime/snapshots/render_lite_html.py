"""Lite HTML snapshot renderer."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from runtime.snapshots.manifest import product_boundary, stable_id, truth_boundary


def render_snapshot_lite_html(bundle: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest = bundle.get("manifest", bundle)
    records = manifest.get("records", []) if isinstance(manifest, Mapping) else []
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head><meta charset=\"utf-8\"><title>Eureka Snapshot</title></head>",
        "<body>",
        "<h1>Eureka Snapshot</h1>",
        "<p>No live access, hosting, downloads, mirroring, execution, or truth acceptance.</p>",
    ]
    for record in records:
        if not isinstance(record, Mapping):
            continue
        fields = record.get("render_fields", {})
        parts.append("<section>")
        parts.append(f"<h2>{escape(str(fields.get('title', record.get('title', 'Snapshot Record'))))}</h2>")
        for label, key in (
            ("Identity", "identity"),
            ("Summary", "summary"),
            ("Source posture", "source_posture"),
            ("Evidence posture", "evidence_posture"),
            ("Compatibility posture", "compatibility_posture"),
            ("Rights posture", "rights_posture"),
            ("Risk posture", "risk_posture"),
            ("Action posture", "action_posture"),
        ):
            parts.append(f"<p><strong>{label}:</strong> {escape(str(fields.get(key, '')))}</p>")
        claims = "; ".join(fields.get("limitations", []) + fields.get("no_claims", []))
        parts.append(f"<p><strong>Limitations/no-claims:</strong> {escape(claims)}</p>")
        parts.append("</section>")
    parts.extend(["</body>", "</html>", ""])
    content = "\n".join(parts)
    return {
        "schema_version": "snapshot_render_result.v0",
        "render_result_id": stable_id("snapshot_render_result", {"profile": "lite_html", "manifest": manifest.get("snapshot_manifest_id", "") if isinstance(manifest, Mapping) else ""}),
        "render_request_ref": "",
        "render_profile": "lite_html",
        "output_summary": "Lite HTML snapshot fragment.",
        "output_path_ref": "",
        "content": content,
        "required_semantic_fields_present": _required_fields_present(content),
        "omitted_fields": [],
        "warnings": [],
        "limitations": ["Lite HTML render is a static fragment and not hosting or route activation."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }


def _required_fields_present(content: str) -> bool:
    lowered = content.casefold()
    return all(phrase in lowered for phrase in ("identity", "source posture", "evidence posture", "rights posture", "risk posture", "action posture", "limitations/no-claims"))
