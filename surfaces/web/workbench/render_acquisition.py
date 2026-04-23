from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_acquisition_html(
    acquisition_view_model: Mapping[str, Any] | None,
    *,
    target_ref: str,
    representation_id: str,
    message: str | None = None,
) -> str:
    status = "(not evaluated)"
    reasons: list[str] = []
    notices: list[Mapping[str, Any]] = []
    metadata: list[tuple[str, str]] = []
    if acquisition_view_model is not None:
        status = _require_string(acquisition_view_model.get("acquisition_status"), "acquisition.acquisition_status")
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
            value = acquisition_view_model.get(key)
            if value is None:
                continue
            metadata.append((label, str(value)))
        reason_codes = _string_list(
            acquisition_view_model.get("reason_codes"),
            "acquisition.reason_codes",
        )
        reason_messages = _string_list(
            acquisition_view_model.get("reason_messages"),
            "acquisition.reason_messages",
        )
        reasons = [f"{code}: {message}" for code, message in zip(reason_codes, reason_messages)]
        notices = _notice_list(acquisition_view_model.get("notices"))

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Acquisition</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Acquisition</h1>",
        "      <p>Compatibility-first bounded payload retrieval for one explicit representation selection.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/representations\">List known representations</a>",
        "        <a href=\"/handoff\">Choose a bounded handoff fit</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Fetch representation</h2>",
        "        <form method=\"get\" action=\"/fetch\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <label for=\"representation_id\">Representation ID</label>",
        f"          <input id=\"representation_id\" name=\"representation_id\" type=\"text\" value=\"{escape(representation_id, quote=True)}\">",
        "          <button type=\"submit\">Fetch bounded payload</button>",
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
        ]
    )
    for label, value in metadata:
        parts.append(f"          <dt>{escape(label)}</dt><dd>{escape(value)}</dd>")
    parts.extend(["        </dl>", "      </section>"])
    if reasons:
        parts.extend(["      <section>", "        <h2>Reasons</h2>", "        <ul>"])
        for reason in reasons:
            parts.append(f"          <li>{escape(reason)}</li>")
        parts.extend(["        </ul>", "      </section>"])
    if notices:
        parts.extend(["      <section>", "        <h2>Notices</h2>", "        <ul>"])
        for notice in notices:
            code = _require_string(notice.get("code"), "acquisition.notice.code")
            severity = _require_string(notice.get("severity"), "acquisition.notice.severity")
            notice_message = _optional_string(notice.get("message"), "acquisition.notice.message")
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
        raise ValueError("acquisition.notices must be a list when provided.")
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"acquisition.notices[{index}] must be an object.")
        result.append(item)
    return result


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
