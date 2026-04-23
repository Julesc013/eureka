from __future__ import annotations

from typing import Any, Mapping


def format_decomposition(view_model: Mapping[str, Any]) -> str:
    lines = [
        "Decomposition",
        f"status: {view_model.get('decomposition_status', view_model.get('status', '(unknown)'))}",
        f"target_ref: {view_model.get('target_ref', '(unknown)')}",
        f"representation_id: {view_model.get('representation_id', '(unknown)')}",
    ]
    for key in (
        "resolved_resource_id",
        "representation_kind",
        "label",
        "filename",
        "content_type",
        "byte_length",
        "source_family",
        "source_label",
        "source_locator",
        "access_kind",
        "access_locator",
    ):
        value = view_model.get(key)
        if value is not None:
            lines.append(f"{key}: {value}")

    members = view_model.get("members")
    if isinstance(members, list) and members:
        lines.extend(["", "Members"])
        for index, member in enumerate(members, start=1):
            if not isinstance(member, Mapping):
                continue
            lines.append(f"{index}. {member.get('member_path', '(unknown)')}")
            lines.append(f"   member_kind: {member.get('member_kind', '(unknown)')}")
            byte_length = member.get("byte_length")
            if isinstance(byte_length, int):
                lines.append(f"   byte_length: {byte_length}")
            content_type = member.get("content_type")
            if isinstance(content_type, str) and content_type:
                lines.append(f"   content_type: {content_type}")
            sha256 = member.get("sha256")
            if isinstance(sha256, str) and sha256:
                lines.append(f"   sha256: {sha256}")
            text_hint = member.get("text_hint")
            if isinstance(text_hint, str) and text_hint:
                lines.append(f"   text_hint: {text_hint}")

    reason_codes = view_model.get("reason_codes")
    reason_messages = view_model.get("reason_messages")
    if isinstance(reason_codes, list) and isinstance(reason_messages, list) and reason_codes:
        lines.extend(["", "Reasons"])
        for reason_code, reason_message in zip(reason_codes, reason_messages):
            lines.append(f"- {reason_code}: {reason_message}")

    notices = view_model.get("notices")
    if isinstance(notices, list) and notices:
        lines.extend(["", "Notices"])
        for notice in notices:
            if not isinstance(notice, Mapping):
                continue
            line = f"- {notice.get('severity', '(unknown)')} {notice.get('code', '(unknown)')}"
            message = notice.get("message")
            if isinstance(message, str) and message:
                line += f": {message}"
            lines.append(line)

    return "\n".join(lines) + "\n"
