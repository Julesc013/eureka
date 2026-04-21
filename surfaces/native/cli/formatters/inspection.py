from __future__ import annotations

import json
from typing import Any, Mapping


def format_bundle_inspection(bundle_inspection: Mapping[str, Any]) -> str:
    source = bundle_inspection.get("source", {})
    lines = [
        "Bundle inspection",
        f"status: {bundle_inspection.get('status', '(unknown)')}",
        f"inspection_mode: {bundle_inspection.get('inspection_mode', '(unknown)')}",
        f"source_kind: {source.get('kind', '(unknown)')}",
        f"source_locator: {source.get('locator', '(unknown)')}",
    ]
    resolved_resource_id = bundle_inspection.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    bundle = bundle_inspection.get("bundle")
    if isinstance(bundle, Mapping):
        lines.extend(["", "Bundle"])
        if bundle.get("bundle_kind"):
            lines.append(f"bundle_kind: {bundle['bundle_kind']}")
        if bundle.get("bundle_version"):
            lines.append(f"bundle_version: {bundle['bundle_version']}")
        if bundle.get("target_ref"):
            lines.append(f"target_ref: {bundle['target_ref']}")
        member_list = bundle.get("member_list")
        if isinstance(member_list, list):
            lines.append(f"member_count: {len(member_list)}")
            if member_list:
                lines.extend(["", "Members"])
                lines.extend(f"- {member}" for member in member_list)

    primary_object = bundle_inspection.get("primary_object")
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

    normalized_record = bundle_inspection.get("normalized_record")
    if isinstance(normalized_record, Mapping):
        lines.extend(
            [
                "",
                "Normalized record",
                json.dumps(dict(normalized_record), indent=2, sort_keys=True),
            ]
        )

    notices = bundle_inspection.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

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
