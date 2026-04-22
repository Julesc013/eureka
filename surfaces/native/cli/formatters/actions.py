from __future__ import annotations

import json
from typing import Any, Mapping


def format_manifest_export(manifest: Mapping[str, Any]) -> str:
    lines = [
        "Manifest export",
        f"manifest_kind: {manifest.get('manifest_kind', '(unknown)')}",
        f"manifest_version: {manifest.get('manifest_version', '(unknown)')}",
        f"target_ref: {manifest.get('target_ref', '(unknown)')}",
    ]
    resolved_resource_id = manifest.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")
    source = manifest.get("source")
    if isinstance(source, Mapping):
        source_label = source.get("label") or source.get("family")
        if source_label:
            lines.append(f"source: {source_label}")
        if source.get("locator"):
            lines.append(f"source_origin: {source['locator']}")

    primary_object = manifest.get("primary_object")
    if isinstance(primary_object, Mapping):
        lines.extend(
            [
                "",
                "Primary object",
                f"id: {primary_object.get('id', '(unknown)')}",
            ]
        )
        if primary_object.get("kind"):
            lines.append(f"kind: {primary_object['kind']}")
        if primary_object.get("label"):
            lines.append(f"label: {primary_object['label']}")

    notices = manifest.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def format_bundle_export_summary(bundle_export: Mapping[str, Any]) -> str:
    inspection = bundle_export.get("bundle_inspection", {})
    bundle = inspection.get("bundle", {}) if isinstance(inspection, Mapping) else {}
    lines = [
        "Bundle export",
        f"status: {bundle_export.get('status', '(unknown)')}",
        f"target_ref: {bundle_export.get('target_ref', bundle.get('target_ref', '(unknown)'))}",
        f"filename: {bundle_export.get('filename', '(unknown)')}",
        f"content_type: {bundle_export.get('content_type', '(unknown)')}",
        f"byte_length: {bundle_export.get('byte_length', 0)}",
    ]
    resolved_resource_id = bundle_export.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    if isinstance(bundle, Mapping):
        if bundle.get("bundle_kind"):
            lines.append(f"bundle_kind: {bundle['bundle_kind']}")
        if bundle.get("bundle_version"):
            lines.append(f"bundle_version: {bundle['bundle_version']}")
        member_list = bundle.get("member_list")
        if isinstance(member_list, list):
            lines.append(f"member_count: {len(member_list)}")
            if member_list:
                lines.extend(["", "Members"])
                lines.extend(f"- {member}" for member in member_list)

    notices = inspection.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def format_store_result(store_result: Mapping[str, Any]) -> str:
    if store_result.get("status") != "stored":
        return format_blocked_response(store_result, title="Store result")

    artifact = store_result.get("artifact", {})
    lines = [
        "Store result",
        f"status: {store_result.get('status', '(unknown)')}",
        f"artifact_id: {artifact.get('artifact_id', '(unknown)')}",
        f"artifact_kind: {artifact.get('artifact_kind', '(unknown)')}",
        f"target_ref: {artifact.get('target_ref', '(unknown)')}",
        f"content_type: {artifact.get('content_type', '(unknown)')}",
        f"byte_length: {artifact.get('byte_length', 0)}",
    ]
    if artifact.get("resolved_resource_id"):
        lines.append(f"resolved_resource_id: {artifact['resolved_resource_id']}")
    source = artifact.get("source")
    if isinstance(source, Mapping):
        source_label = source.get("label") or source.get("family")
        if source_label:
            lines.append(f"source: {source_label}")
    if artifact.get("filename"):
        lines.append(f"filename: {artifact['filename']}")
    if artifact.get("store_path"):
        lines.append(f"store_path: {artifact['store_path']}")
    if artifact.get("source_action"):
        lines.append(f"source_action: {artifact['source_action']}")

    notices = store_result.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def format_blocked_response(response: Mapping[str, Any], *, title: str = "Blocked result") -> str:
    lines = [
        title,
        f"status: {response.get('status', 'blocked')}",
    ]
    for field_name in ("target_ref", "artifact_id", "action_id", "code", "message"):
        value = response.get(field_name)
        if isinstance(value, str) and value:
            lines.append(f"{field_name}: {value}")

    notices = response.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    extra_fields = {
        key: value
        for key, value in response.items()
        if key not in {"status", "target_ref", "artifact_id", "action_id", "code", "message", "notices"}
    }
    if extra_fields:
        lines.extend(
            [
                "",
                "Details",
                json.dumps(extra_fields, indent=2, sort_keys=True),
            ]
        )

    return "\n".join(lines) + "\n"


def _format_notice_lines(notices: list[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for notice in notices:
        code = notice.get("code", "(unknown)")
        severity = notice.get("severity", "(unknown)")
        message = notice.get("message")
        line = f"- {severity} {code}"
        if isinstance(message, str) and message:
            line += f": {message}"
        lines.append(line)
    return lines
