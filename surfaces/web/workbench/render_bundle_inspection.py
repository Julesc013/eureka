from __future__ import annotations

import json
from html import escape
from typing import Any, Mapping


def render_bundle_inspection_html(bundle_inspection: Mapping[str, Any]) -> str:
    status = _require_string(bundle_inspection.get("status"), "bundle_inspection.status")
    inspection_mode = _require_string(
        bundle_inspection.get("inspection_mode"),
        "bundle_inspection.inspection_mode",
    )
    source = _require_mapping(bundle_inspection.get("source"), "bundle_inspection.source")
    source_kind = _require_string(source.get("kind"), "bundle_inspection.source.kind")
    source_locator = _require_string(source.get("locator"), "bundle_inspection.source.locator")
    resolved_resource_id = _optional_string(
        bundle_inspection.get("resolved_resource_id"),
        "bundle_inspection.resolved_resource_id",
    )
    notices = _notice_list(bundle_inspection.get("notices"))
    bundle_summary = _optional_mapping(bundle_inspection.get("bundle"), "bundle_inspection.bundle")
    primary_object = _optional_mapping(bundle_inspection.get("primary_object"), "bundle_inspection.primary_object")
    evidence = _evidence_list(bundle_inspection.get("evidence"))
    normalized_record = _optional_mapping(
        bundle_inspection.get("normalized_record"),
        "bundle_inspection.normalized_record",
    )

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Bundle Inspection</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Bundle Inspection</h1>",
        "      <p>Compatibility-first local inspection of a previously exported deterministic bundle.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/compare\">Compare two targets</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Inspect a Bundle</h2>",
        "        <form method=\"get\" action=\"/inspect/bundle\">",
        "          <label for=\"bundle_path\">Local bundle path</label>",
        f"          <input id=\"bundle_path\" name=\"bundle_path\" type=\"text\" value=\"{escape(source_locator, quote=True)}\">",
        "          <button type=\"submit\">Inspect</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Inspection State</h2>",
        "        <dl>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Mode</dt><dd>{escape(inspection_mode)}</dd>",
        f"          <dt>Source kind</dt><dd>{escape(source_kind)}</dd>",
        f"          <dt>Source locator</dt><dd>{escape(source_locator)}</dd>",
    ]
    if resolved_resource_id is not None:
        parts.append(f"          <dt>Resolved resource ID</dt><dd>{escape(resolved_resource_id)}</dd>")
    parts.extend(
        [
            "        </dl>",
            "      </section>",
        ]
    )

    if bundle_summary is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Bundle Summary</h2>",
                "        <dl>",
            ]
        )
        bundle_kind = _optional_string(bundle_summary.get("bundle_kind"), "bundle.bundle_kind")
        if bundle_kind is not None:
            parts.append(f"          <dt>Bundle kind</dt><dd>{escape(bundle_kind)}</dd>")
        bundle_version = _optional_string(bundle_summary.get("bundle_version"), "bundle.bundle_version")
        if bundle_version is not None:
            parts.append(f"          <dt>Bundle version</dt><dd>{escape(bundle_version)}</dd>")
        target_ref = _optional_string(bundle_summary.get("target_ref"), "bundle.target_ref")
        if target_ref is not None:
            parts.append(f"          <dt>Target ref</dt><dd>{escape(target_ref)}</dd>")
        member_list = _string_list(bundle_summary.get("member_list"), "bundle.member_list")
        parts.append(f"          <dt>Member count</dt><dd>{len(member_list)}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
                "      <section>",
                "        <h2>Bundle Members</h2>",
            ]
        )
        if member_list:
            parts.append("        <ul>")
            for member in member_list:
                parts.append(f"          <li>{escape(member)}</li>")
            parts.append("        </ul>")
        else:
            parts.append("        <p>No bundle members were reported.</p>")
        parts.append("      </section>")
    else:
        parts.extend(
            [
                "      <section>",
                "        <h2>Bundle Summary</h2>",
                "        <p>No bundle summary is available for this inspection result.</p>",
                "      </section>",
            ]
        )

    if primary_object is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Primary Object</h2>",
                "        <dl>",
                f"          <dt>ID</dt><dd>{escape(_require_string(primary_object.get('id'), 'primary_object.id'))}</dd>",
            ]
        )
        object_kind = _optional_string(primary_object.get("kind"), "primary_object.kind")
        if object_kind is not None:
            parts.append(f"          <dt>Kind</dt><dd>{escape(object_kind)}</dd>")
        object_label = _optional_string(primary_object.get("label"), "primary_object.label")
        if object_label is not None:
            parts.append(f"          <dt>Label</dt><dd>{escape(object_label)}</dd>")
        parts.extend(
            [
                "        </dl>",
                "      </section>",
            ]
        )

    if evidence:
        parts.extend(
            [
                "      <section>",
                "        <h2>Evidence</h2>",
                "        <ul>",
            ]
        )
        for entry in evidence:
            parts.append(f"          <li>{escape(_evidence_text(entry))}</li>")
        parts.extend(
            [
                "        </ul>",
                "      </section>",
            ]
        )

    if normalized_record is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Normalized Record Summary</h2>",
                f"        <pre>{escape(json.dumps(dict(normalized_record), indent=2, sort_keys=True))}</pre>",
                "      </section>",
            ]
        )

    if notices:
        parts.extend(
            [
                "      <section>",
                "        <h2>Notices</h2>",
                "        <ul>",
            ]
        )
        for notice in notices:
            code = _require_string(notice.get("code"), "notice.code")
            severity = _require_string(notice.get("severity"), "notice.severity")
            message = _optional_string(notice.get("message"), "notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if message is not None:
                item += f": {escape(message)}"
            item += "</li>"
            parts.append(item)
        parts.extend(
            [
                "        </ul>",
                "      </section>",
            ]
        )

    parts.extend(
        [
            "    </main>",
            "  </body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object when provided.")
    return value


def _notice_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("bundle_inspection.notices must be a list when provided.")
    notices: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"bundle_inspection.notices[{index}] must be an object.")
        notices.append(item)
    return notices


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_string(item, f"{field_name}[{index}]"))
    return result


def _evidence_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("bundle_inspection.evidence must be a list when provided.")
    evidence: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"bundle_inspection.evidence[{index}] must be an object.")
        evidence.append(item)
    return evidence


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string when provided.")
    return value


def _evidence_text(entry: Mapping[str, Any]) -> str:
    claim_kind = _require_string(entry.get("claim_kind"), "evidence.claim_kind")
    claim_value = _require_string(entry.get("claim_value"), "evidence.claim_value")
    asserted_by = _optional_string(entry.get("asserted_by_label"), "evidence.asserted_by_label") or _require_string(
        entry.get("asserted_by_family"),
        "evidence.asserted_by_family",
    )
    evidence_kind = _require_string(entry.get("evidence_kind"), "evidence.evidence_kind")
    evidence_locator = _require_string(entry.get("evidence_locator"), "evidence.evidence_locator")
    text = f"{claim_kind} = {claim_value} ({asserted_by}, {evidence_kind}, {evidence_locator})"
    asserted_at = _optional_string(entry.get("asserted_at"), "evidence.asserted_at")
    if asserted_at is not None:
        text += f" @ {asserted_at}"
    return text
