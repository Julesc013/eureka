from __future__ import annotations

import json
from typing import Any, Mapping


def format_stored_exports_listing(stored_exports: Mapping[str, Any]) -> str:
    lines = [
        "Stored exports",
        f"target_ref: {stored_exports.get('target_ref', '(unknown)')}",
    ]
    resolved_resource_id = stored_exports.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    store_actions = stored_exports.get("store_actions", [])
    lines.extend(["", "Store actions"])
    available_actions = [
        action for action in store_actions if action.get("availability") == "available"
    ]
    unavailable_actions = [
        action for action in store_actions if action.get("availability") != "available"
    ]
    if available_actions:
        lines.extend(
            f"- available {action.get('action_id', '(unknown)')}: {action.get('label', '(unknown)')}"
            for action in available_actions
        )
    else:
        lines.append("(no available store actions)")
    for action in unavailable_actions:
        lines.append(
            f"- unavailable {action.get('action_id', '(unknown)')}: {action.get('label', '(unknown)')}"
        )

    artifacts = stored_exports.get("artifacts", [])
    lines.extend(["", "Artifacts"])
    if isinstance(artifacts, list) and artifacts:
        for artifact in artifacts:
            lines.append(
                f"- {artifact.get('artifact_kind', '(unknown)')} {artifact.get('artifact_id', '(unknown)')}"
            )
            lines.append(f"  content_type: {artifact.get('content_type', '(unknown)')}")
            lines.append(f"  byte_length: {artifact.get('byte_length', 0)}")
            if artifact.get("filename"):
                lines.append(f"  filename: {artifact['filename']}")
            if artifact.get("resolved_resource_id"):
                lines.append(f"  resolved_resource_id: {artifact['resolved_resource_id']}")
            source = artifact.get("source")
            if isinstance(source, Mapping):
                source_label = source.get("label") or source.get("family")
                if source_label:
                    lines.append(f"  source: {source_label}")
    else:
        lines.append("(no stored artifacts)")

    notices = stored_exports.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def format_stored_artifact_json(
    artifact: Mapping[str, Any],
    content: Mapping[str, Any],
) -> str:
    lines = _artifact_header_lines(artifact)
    lines.extend(
        [
            "",
            "Content",
            json.dumps(dict(content), indent=2, sort_keys=True),
        ]
    )
    return "\n".join(lines) + "\n"


def format_stored_artifact_bundle(
    artifact: Mapping[str, Any],
    bundle_inspection: Mapping[str, Any],
) -> str:
    lines = _artifact_header_lines(artifact)
    lines.extend(
        [
            "",
            "Bundle inspection",
            f"status: {bundle_inspection.get('status', '(unknown)')}",
            f"inspection_mode: {bundle_inspection.get('inspection_mode', '(unknown)')}",
        ]
    )
    bundle = bundle_inspection.get("bundle")
    if isinstance(bundle, Mapping):
        if bundle.get("bundle_kind"):
            lines.append(f"bundle_kind: {bundle['bundle_kind']}")
        if bundle.get("bundle_version"):
            lines.append(f"bundle_version: {bundle['bundle_version']}")
        if bundle.get("target_ref"):
            lines.append(f"bundle_target_ref: {bundle['target_ref']}")
        member_list = bundle.get("member_list")
        if isinstance(member_list, list):
            lines.append(f"member_count: {len(member_list)}")
            if member_list:
                lines.extend(["", "Members"])
                lines.extend(f"- {member}" for member in member_list)

    notices = bundle_inspection.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        lines.extend(_format_notice_lines(notices))

    return "\n".join(lines) + "\n"


def _artifact_header_lines(artifact: Mapping[str, Any]) -> list[str]:
    lines = [
        "Stored artifact",
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
    return lines


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
