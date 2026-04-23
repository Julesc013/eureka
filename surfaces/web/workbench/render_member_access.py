from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_member_access_html(
    member_access_view_model: Mapping[str, Any] | None,
    *,
    target_ref: str,
    representation_id: str,
    member_path: str,
    message: str | None = None,
) -> str:
    status = "(not evaluated)"
    reasons: list[str] = []
    notices: list[Mapping[str, Any]] = []
    metadata: list[tuple[str, str]] = []
    text_preview: str | None = None
    if member_access_view_model is not None:
        status = _require_string(
            member_access_view_model.get("member_access_status"),
            "member_access.member_access_status",
        )
        for key, label in (
            ("representation_kind", "Representation kind"),
            ("label", "Label"),
            ("filename", "Filename"),
            ("source_family", "Source family"),
            ("source_label", "Source label"),
            ("source_locator", "Source locator"),
            ("access_kind", "Access kind"),
            ("access_locator", "Access locator"),
            ("member_kind", "Member kind"),
            ("content_type", "Content type"),
            ("byte_length", "Byte length"),
            ("sha256", "SHA-256"),
            ("resolved_resource_id", "Resolved resource ID"),
        ):
            value = member_access_view_model.get(key)
            if value is None:
                continue
            metadata.append((label, str(value)))
        text_preview = _optional_string(
            member_access_view_model.get("text_preview"),
            "member_access.text_preview",
        )
        reason_codes = _string_list(
            member_access_view_model.get("reason_codes"),
            "member_access.reason_codes",
        )
        reason_messages = _string_list(
            member_access_view_model.get("reason_messages"),
            "member_access.reason_messages",
        )
        reasons = [f"{code}: {detail}" for code, detail in zip(reason_codes, reason_messages)]
        notices = _notice_list(member_access_view_model.get("notices"))

    raw_href = (
        "/member?target_ref="
        + quote(target_ref, safe="")
        + "&representation_id="
        + quote(representation_id, safe="")
        + "&member_path="
        + quote(member_path, safe="")
        + "&raw=1"
    )
    decompose_href = (
        "/decompose?target_ref="
        + quote(target_ref, safe="")
        + "&representation_id="
        + quote(representation_id, safe="")
    )

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Member Access</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Member Access</h1>",
        "      <p>Read one bounded package member through the same public boundary used for fetch and decomposition.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/decompose\">Inspect bounded package members</a>",
        "        <a href=\"/fetch\">Fetch a bounded payload</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Read member</h2>",
        "        <form method=\"get\" action=\"/member\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <label for=\"representation_id\">Representation ID</label>",
        f"          <input id=\"representation_id\" name=\"representation_id\" type=\"text\" value=\"{escape(representation_id, quote=True)}\">",
        "          <label for=\"member_path\">Member path</label>",
        f"          <input id=\"member_path\" name=\"member_path\" type=\"text\" value=\"{escape(member_path, quote=True)}\">",
        "          <button type=\"submit\">Read bounded member</button>",
        "        </form>",
        "      </section>",
    ]
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
            f"          <dt>Member path</dt><dd>{escape(member_path)}</dd>",
        ]
    )
    for label, value in metadata:
        parts.append(f"          <dt>{escape(label)}</dt><dd>{escape(value)}</dd>")
    parts.extend(["        </dl>", "      </section>"])

    if member_access_view_model is not None and status in {"previewed", "read"}:
        parts.extend(
            [
                "      <section>",
                "        <h2>Readback</h2>",
                f"        <p><a href=\"{escape(raw_href, quote=True)}\">Return raw member bytes</a></p>",
                f"        <p><a href=\"{escape(decompose_href, quote=True)}\">Back to bounded member listing</a></p>",
                "      </section>",
            ]
        )

    if text_preview is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Text preview</h2>",
                f"        <pre>{escape(text_preview)}</pre>",
                "      </section>",
            ]
        )

    if reasons:
        parts.extend(["      <section>", "        <h2>Reasons</h2>", "        <ul>"])
        for reason in reasons:
            parts.append(f"          <li>{escape(reason)}</li>")
        parts.extend(["        </ul>", "      </section>"])

    if notices:
        parts.extend(["      <section>", "        <h2>Notices</h2>", "        <ul>"])
        for notice in notices:
            code = _require_string(notice.get("code"), "member_access.notice.code")
            severity = _require_string(notice.get("severity"), "member_access.notice.severity")
            notice_message = _optional_string(notice.get("message"), "member_access.notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if notice_message is not None:
                item += f": {escape(notice_message)}"
            item += "</li>"
            parts.append(item)
        parts.extend(["        </ul>", "      </section>"])

    parts.extend(["    </main>", "  </body>", "</html>", ""])
    return "\n".join(parts)


def _notice_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("member_access.notices must be a list when provided.")
    notices: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"member_access.notices[{index}] must be an object.")
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
