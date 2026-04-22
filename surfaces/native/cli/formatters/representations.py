from __future__ import annotations

from typing import Any, Mapping


def format_representations(view_model: Mapping[str, Any]) -> str:
    lines = [
        "Representations",
        f"status: {view_model.get('status', '(unknown)')}",
        f"target_ref: {view_model.get('target_ref', '(unknown)')}",
    ]
    resolved_resource_id = view_model.get("resolved_resource_id")
    if isinstance(resolved_resource_id, str) and resolved_resource_id:
        lines.append(f"resolved_resource_id: {resolved_resource_id}")

    primary_object = view_model.get("primary_object")
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

    source = view_model.get("source")
    if isinstance(source, Mapping):
        lines.extend(
            [
                "",
                "Source",
                f"family: {source.get('family', '(unknown)')}",
            ]
        )
        if source.get("label"):
            lines.append(f"label: {source['label']}")
        if source.get("locator"):
            lines.append(f"origin: {source['locator']}")

    representations = view_model.get("representations")
    if isinstance(representations, list) and representations:
        lines.extend(["", "Known representations/access paths"])
        lines.extend(format_representation_lines(representations))
    else:
        lines.extend(["", "Known representations/access paths", "(none)"])

    notices = view_model.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        for notice in notices:
            if not isinstance(notice, Mapping):
                continue
            line = f"- {notice.get('severity', '(unknown)')} {notice.get('code', '(unknown)')}"
            if notice.get("message"):
                line += f": {notice['message']}"
            lines.append(line)
    return "\n".join(lines) + "\n"


def format_representation_lines(representations: list[Any]) -> list[str]:
    lines: list[str] = []
    for index, item in enumerate(representations, start=1):
        if not isinstance(item, Mapping):
            continue
        label = item.get("label", "(unknown)")
        kind = item.get("representation_kind", "(unknown)")
        access_kind = item.get("access_kind", "(unknown)")
        source_family = item.get("source_family", "(unknown)")
        lines.append(f"{index}. {label}")
        lines.append(f"   representation_kind: {kind}")
        lines.append(f"   access_kind: {access_kind}")
        lines.append(f"   source_family: {source_family}")
        source_label = item.get("source_label")
        if source_label:
            lines.append(f"   source_label: {source_label}")
        content_type = item.get("content_type")
        if content_type:
            lines.append(f"   content_type: {content_type}")
        byte_length = item.get("byte_length")
        if isinstance(byte_length, int):
            lines.append(f"   byte_length: {byte_length}")
        access_locator = item.get("access_locator")
        if access_locator:
            lines.append(f"   access_locator: {access_locator}")
        source_locator = item.get("source_locator")
        if source_locator:
            lines.append(f"   source_locator: {source_locator}")
        is_direct = item.get("is_direct")
        if isinstance(is_direct, bool):
            lines.append(f"   is_direct: {str(is_direct).lower()}")
    return lines
