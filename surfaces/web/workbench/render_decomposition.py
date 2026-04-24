from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_decomposition_html(
    decomposition_view_model: Mapping[str, Any] | None,
    *,
    target_ref: str,
    representation_id: str,
    message: str | None = None,
    allow_member_readback: bool = True,
) -> str:
    status = "(not evaluated)"
    reasons: list[str] = []
    notices: list[Mapping[str, Any]] = []
    members: list[Mapping[str, Any]] = []
    metadata: list[tuple[str, str]] = []
    if decomposition_view_model is not None:
        status = _require_string(
            decomposition_view_model.get("decomposition_status"),
            "decomposition.decomposition_status",
        )
        for key, label in (
            ("representation_kind", "Representation kind"),
            ("label", "Label"),
            ("filename", "Filename"),
            ("content_type", "Content type"),
            ("byte_length", "Byte length"),
            ("source_family", "Source family"),
            ("source_label", "Source label"),
            ("source_locator", "Source locator"),
            ("access_kind", "Access kind"),
            ("access_locator", "Access locator"),
            ("resolved_resource_id", "Resolved resource ID"),
        ):
            value = decomposition_view_model.get(key)
            if value is None:
                continue
            metadata.append((label, str(value)))
        reason_codes = _string_list(
            decomposition_view_model.get("reason_codes"),
            "decomposition.reason_codes",
        )
        reason_messages = _string_list(
            decomposition_view_model.get("reason_messages"),
            "decomposition.reason_messages",
        )
        reasons = [f"{code}: {detail}" for code, detail in zip(reason_codes, reason_messages)]
        notices = _notice_list(decomposition_view_model.get("notices"))
        members = _member_list(decomposition_view_model.get("members"))

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Bounded Decomposition</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Bounded Decomposition</h1>",
        "      <p>Inspect one fetched bounded representation into a compact member listing when the format is supported.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/representations\">List known representations</a>",
    ]
    if allow_member_readback:
        parts.append("        <a href=\"/fetch\">Fetch a bounded payload</a>")
    else:
        parts.append("        <span>Payload readback disabled in public-alpha mode</span>")
    parts.extend(
        [
            "      </nav>",
            "    </header>",
            "    <main>",
            "      <section>",
            "        <h2>Inspect representation members</h2>",
            "        <form method=\"get\" action=\"/decompose\">",
            "          <label for=\"target_ref\">Target reference</label>",
            f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
            "          <label for=\"representation_id\">Representation ID</label>",
            f"          <input id=\"representation_id\" name=\"representation_id\" type=\"text\" value=\"{escape(representation_id, quote=True)}\">",
            "          <button type=\"submit\">Inspect bounded members</button>",
            "        </form>",
            "      </section>",
        ]
    )
    if message is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Message</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    parts.extend(
        [
            "      <section>",
            "        <h2>Summary</h2>",
            "        <dl>",
            f"          <dt>Status</dt><dd>{escape(status)}</dd>",
            f"          <dt>Target ref</dt><dd>{escape(target_ref)}</dd>",
            f"          <dt>Representation ID</dt><dd>{escape(representation_id)}</dd>",
        ]
    )
    for label, value in metadata:
        parts.append(f"          <dt>{escape(label)}</dt><dd>{escape(value)}</dd>")
    parts.extend(["        </dl>", "      </section>"])

    parts.extend(["      <section>", "        <h2>Members</h2>"])
    if members:
        parts.append("        <ul>")
        for member in members:
            member_path = _require_string(member.get("member_path"), "decomposition.member.member_path")
            member_kind = _require_string(member.get("member_kind"), "decomposition.member.member_kind")
            parts.append(f"          <li><strong>{escape(member_path)}</strong>")
            parts.append("            <dl>")
            parts.append(f"              <dt>Member kind</dt><dd>{escape(member_kind)}</dd>")
            byte_length = member.get("byte_length")
            if isinstance(byte_length, int):
                parts.append(f"              <dt>Byte length</dt><dd>{byte_length}</dd>")
            content_type = _optional_string(member.get("content_type"), "decomposition.member.content_type")
            if content_type is not None:
                parts.append(f"              <dt>Content type</dt><dd>{escape(content_type)}</dd>")
            sha256 = _optional_string(member.get("sha256"), "decomposition.member.sha256")
            if sha256 is not None:
                parts.append(f"              <dt>SHA-256</dt><dd>{escape(sha256)}</dd>")
            text_hint = _optional_string(member.get("text_hint"), "decomposition.member.text_hint")
            if text_hint is not None:
                parts.append(f"              <dt>Text hint</dt><dd>{escape(text_hint)}</dd>")
            if allow_member_readback:
                member_href = (
                    "/member?target_ref="
                    + quote(target_ref, safe="")
                    + "&representation_id="
                    + quote(representation_id, safe="")
                    + "&member_path="
                    + quote(member_path, safe="")
                )
                parts.append(
                    f"              <dt>Read member</dt><dd><a href=\"{escape(member_href, quote=True)}\">Open bounded member preview</a></dd>"
                )
            else:
                parts.append(
                    "              <dt>Read member</dt><dd>Disabled in public-alpha mode.</dd>"
                )
            parts.append("            </dl>")
            parts.append("          </li>")
        parts.append("        </ul>")
    else:
        parts.append("        <p>No bounded member listing is available for this representation.</p>")
    parts.append("      </section>")

    if reasons:
        parts.extend(["      <section>", "        <h2>Reasons</h2>", "        <ul>"])
        for reason in reasons:
            parts.append(f"          <li>{escape(reason)}</li>")
        parts.extend(["        </ul>", "      </section>"])

    if notices:
        parts.extend(["      <section>", "        <h2>Notices</h2>", "        <ul>"])
        for notice in notices:
            code = _require_string(notice.get("code"), "decomposition.notice.code")
            severity = _require_string(notice.get("severity"), "decomposition.notice.severity")
            notice_message = _optional_string(notice.get("message"), "decomposition.notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if notice_message is not None:
                item += f": {escape(notice_message)}"
            item += "</li>"
            parts.append(item)
        parts.extend(["        </ul>", "      </section>"])

    parts.extend(["    </main>", "  </body>", "</html>", ""])
    return "\n".join(parts)


def _member_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("decomposition.members must be a list when provided.")
    members: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"decomposition.members[{index}] must be an object.")
        members.append(item)
    return members


def _notice_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("decomposition.notices must be a list when provided.")
    notices: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"decomposition.notices[{index}] must be an object.")
        notices.append(item)
    return notices


def _string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


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
