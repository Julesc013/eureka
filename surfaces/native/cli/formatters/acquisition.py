from __future__ import annotations

from typing import Any, Mapping


def format_acquisition(
    acquisition: Mapping[str, Any],
    *,
    output_path: str | None = None,
) -> str:
    lines = [
        "Acquisition",
        f"status: {acquisition.get('acquisition_status', acquisition.get('status', '(unknown)'))}",
        f"target_ref: {acquisition.get('target_ref', '(unknown)')}",
        f"representation_id: {acquisition.get('representation_id', '(unknown)')}",
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
        value = acquisition.get(key)
        if value is not None:
            lines.append(f"{key}: {value}")

    if output_path is not None:
        lines.append(f"output_path: {output_path}")
    elif acquisition.get("acquisition_status") == "fetched":
        lines.append("payload: fetched (not written; use --output to persist bytes)")

    reason_codes = acquisition.get("reason_codes")
    reason_messages = acquisition.get("reason_messages")
    if isinstance(reason_codes, list) and isinstance(reason_messages, list) and reason_codes:
        lines.extend(["", "Reasons"])
        for reason_code, reason_message in zip(reason_codes, reason_messages):
            lines.append(f"- {reason_code}: {reason_message}")

    notices = acquisition.get("notices")
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
