"""Render relay response models as old-browser-safe and text outputs."""

from __future__ import annotations

from html import escape
import json
from typing import Any, Mapping, Sequence


def render_relay_text(response_model: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    body = response_model.get("body")
    if isinstance(body, str):
        return body
    lines = [
        "Eureka Relay",
        "============",
        f"Status: {response_model.get('status_code', '')}",
        f"Summary: {response_model.get('body_summary', '')}",
        "No live access, downloads, uploads, execution, accounts, telemetry, or index mutation.",
        "",
    ]
    for record in _records_from_body(body):
        lines.extend(_record_text_lines(record))
        lines.append("")
    if not _records_from_body(body):
        lines.append(json.dumps(body, indent=2, sort_keys=True) if body is not None else "")
    return "\n".join(lines).rstrip() + "\n"


def render_relay_lite_html(response_model: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    body = response_model.get("body")
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        '<head><meta charset="utf-8"><title>Eureka Relay</title></head>',
        "<body>",
        "<h1>Eureka Relay</h1>",
        f"<p>Status: {escape(str(response_model.get('status_code', '')))}</p>",
        f"<p>{escape(str(response_model.get('body_summary', 'Fixture response')))}</p>",
        "<p>No live access, downloads, uploads, execution, accounts, telemetry, or index mutation.</p>",
    ]
    records = _records_from_body(body)
    if records:
        for record in records:
            parts.append("<section>")
            parts.append(f"<h2>{escape(str(record.get('title', record.get('canonical_ref', 'Record'))))}</h2>")
            for label, key in (
                ("Identity", "canonical_ref"),
                ("Summary", "summary"),
                ("Source posture", "source_posture"),
                ("Evidence posture", "evidence_posture"),
                ("Rights posture", "rights_posture"),
                ("Risk posture", "risk_posture"),
                ("Action posture", "action_posture"),
            ):
                parts.append(f"<p><strong>{label}:</strong> {escape(str(record.get(key, '')))}</p>")
            parts.append("<p><strong>Limitations/no-claims:</strong> no public truth; no download; no execution; no index mutation</p>")
            parts.append("</section>")
    else:
        parts.append("<pre>")
        parts.append(escape(json.dumps(body, indent=2, sort_keys=True) if body is not None else ""))
        parts.append("</pre>")
    parts.extend(["</body>", "</html>", ""])
    return "\n".join(parts)


def render_relay_file_tree(response_model: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    body = response_model.get("body", {})
    records = _records_from_body(body)
    lines = ["snapshot/", "  manifest.json"]
    for record in records:
        record_type = str(record.get("record_type", "record"))
        record_id = str(record.get("canonical_ref", record.get("snapshot_record_id", "record"))).replace(":", "_")
        lines.append(f"  records/{record_type}/{record_id}.json")
    lines.append("  README.txt")
    lines.append("")
    lines.append("Read-only fixture tree. No files are downloaded, mirrored, installed, or executed.")
    return "\n".join(lines) + "\n"


def render_relay_json_manifest(response_model: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    return json.dumps(response_model.get("body", response_model), indent=2, sort_keys=True) + "\n"


def render_relay_native_fixture_json(response_model: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> str:
    payload = {
        "schema_version": "native_fixture_response.v0",
        "status_code": response_model.get("status_code", 200),
        "render_profile": "native_fixture_json",
        "body_summary": response_model.get("body_summary", ""),
        "body": response_model.get("body"),
        "read_only": True,
        "write_allowed": False,
        "download_allowed": False,
        "action_execution_allowed": False,
        "telemetry_allowed": False,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _records_from_body(body: Any) -> list[Mapping[str, Any]]:
    if isinstance(body, Mapping):
        if isinstance(body.get("records"), list):
            return [record for record in body["records"] if isinstance(record, Mapping)]
        if isinstance(body.get("record"), Mapping):
            return [body["record"]]
        if body.get("schema_version") == "snapshot_record.v0":
            return [body]
    if isinstance(body, list):
        return [record for record in body if isinstance(record, Mapping)]
    return []


def _record_text_lines(record: Mapping[str, Any]) -> list[str]:
    return [
        f"Record: {record.get('canonical_ref', '')}",
        f"Title: {record.get('title', '')}",
        f"Summary: {record.get('summary', '')}",
        f"Source posture: {record.get('source_posture', '')}",
        f"Evidence posture: {record.get('evidence_posture', '')}",
        f"Rights posture: {record.get('rights_posture', '')}",
        f"Risk posture: {record.get('risk_posture', '')}",
        f"Action posture: {record.get('action_posture', '')}",
        "Limitations/no-claims: no public truth; no download; no execution; no index mutation",
    ]

