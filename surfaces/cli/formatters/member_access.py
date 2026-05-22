from __future__ import annotations

from typing import Any, Mapping


def format_member_access(
    member_access: Mapping[str, Any],
    *,
    output_path: str | None = None,
) -> str:
    lines = [
        "Member access",
        f"status: {member_access.get('member_access_status', member_access.get('status', '(unknown)'))}",
        f"target_ref: {member_access.get('target_ref', '(unknown)')}",
        f"representation_id: {member_access.get('representation_id', '(unknown)')}",
        f"member_path: {member_access.get('member_path', '(unknown)')}",
    ]
    for key in (
        "resolved_resource_id",
        "representation_kind",
        "label",
        "filename",
        "source_family",
        "source_label",
        "source_locator",
        "access_kind",
        "access_locator",
        "member_kind",
        "content_type",
        "byte_length",
        "sha256",
    ):
        value = member_access.get(key)
        if value is not None:
            lines.append(f"{key}: {value}")

    text_preview = member_access.get("text_preview")
    if isinstance(text_preview, str) and text_preview:
        lines.extend(["", "Preview", text_preview])

    if output_path is not None:
        lines.append(f"output_path: {output_path}")
    elif member_access.get("member_access_status") in {"read", "previewed"}:
        lines.append("payload: read (not written; use --output to persist member bytes)")

    reason_codes = member_access.get("reason_codes")
    reason_messages = member_access.get("reason_messages")
    if isinstance(reason_codes, list) and isinstance(reason_messages, list) and reason_codes:
        lines.extend(["", "Reasons"])
        for reason_code, reason_message in zip(reason_codes, reason_messages):
            lines.append(f"- {reason_code}: {reason_message}")

    notices = member_access.get("notices")
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
