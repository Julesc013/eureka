from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_representations_html(
    representations_view_model: Mapping[str, Any],
    *,
    allow_payload_readback: bool = True,
) -> str:
    status = _require_string(representations_view_model.get("status"), "representations.status")
    target_ref = _require_string(representations_view_model.get("target_ref"), "representations.target_ref")
    representations = _representation_list(representations_view_model.get("representations"))
    notices = _notice_list(representations_view_model.get("notices"))

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Representations</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Representations</h1>",
        "      <p>Compatibility-first listing of bounded known representations and access paths for one resolved target.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Lookup Representations</h2>",
        "        <form method=\"get\" action=\"/representations\">",
        "          <label for=\"target_ref\">Target reference</label>",
        f"          <input id=\"target_ref\" name=\"target_ref\" type=\"text\" value=\"{escape(target_ref, quote=True)}\">",
        "          <button type=\"submit\">List representations</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>State</h2>",
        "        <dl>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Target ref</dt><dd>{escape(target_ref)}</dd>",
        "        </dl>",
        "      </section>",
        "      <section>",
        "        <h2>Known representations/access paths</h2>",
    ]
    if representations:
        parts.append("        <ul>")
        for representation in representations:
            parts.append("          <li>")
            parts.append(f"            <strong>{escape(_require_string(representation.get('label'), 'representation.label'))}</strong>")
            parts.append("            <dl>")
            parts.append(
                f"              <dt>Representation kind</dt><dd>{escape(_require_string(representation.get('representation_kind'), 'representation.representation_kind'))}</dd>"
            )
            parts.append(
                f"              <dt>Access kind</dt><dd>{escape(_require_string(representation.get('access_kind'), 'representation.access_kind'))}</dd>"
            )
            parts.append(
                f"              <dt>Source family</dt><dd>{escape(_require_string(representation.get('source_family'), 'representation.source_family'))}</dd>"
            )
            source_label = _optional_string(representation.get("source_label"), "representation.source_label")
            if source_label is not None:
                parts.append(f"              <dt>Source label</dt><dd>{escape(source_label)}</dd>")
            content_type = _optional_string(representation.get("content_type"), "representation.content_type")
            if content_type is not None:
                parts.append(f"              <dt>Content type</dt><dd>{escape(content_type)}</dd>")
            byte_length = _optional_non_negative_int(representation.get("byte_length"), "representation.byte_length")
            if byte_length is not None:
                parts.append(f"              <dt>Byte length</dt><dd>{byte_length}</dd>")
            access_locator = _optional_string(representation.get("access_locator"), "representation.access_locator")
            if access_locator is not None:
                parts.append(f"              <dt>Access locator</dt><dd>{escape(access_locator)}</dd>")
            source_locator = _optional_string(representation.get("source_locator"), "representation.source_locator")
            if source_locator is not None:
                parts.append(f"              <dt>Source locator</dt><dd>{escape(source_locator)}</dd>")
            filename = _optional_string(representation.get("filename"), "representation.filename")
            if filename is not None:
                parts.append(f"              <dt>Filename</dt><dd>{escape(filename)}</dd>")
            is_direct = representation.get("is_direct")
            if isinstance(is_direct, bool):
                parts.append(f"              <dt>Direct</dt><dd>{escape(str(is_direct).lower())}</dd>")
            is_fetchable = representation.get("is_fetchable")
            if isinstance(is_fetchable, bool):
                parts.append(
                    f"              <dt>Fetchable</dt><dd>{escape(str(is_fetchable).lower())}</dd>"
                )
                if is_fetchable and allow_payload_readback:
                    fetch_href = (
                        "/fetch?target_ref="
                        + quote(target_ref, safe="")
                        + "&representation_id="
                        + quote(
                            _require_string(
                                representation.get("representation_id"),
                                "representation.representation_id",
                            ),
                            safe="",
                        )
                    )
                    parts.append(
                        f"              <dt>Bounded fetch</dt><dd><a href=\"{escape(fetch_href, quote=True)}\">Retrieve local fixture payload</a></dd>"
                    )
                elif is_fetchable:
                    parts.append(
                        "              <dt>Bounded fetch</dt><dd>Disabled in public-alpha mode.</dd>"
                    )
            parts.append("            </dl>")
            parts.append("          </li>")
        parts.append("        </ul>")
    else:
        parts.append("        <p>No bounded representations are available for this target.</p>")
    parts.append("      </section>")

    if notices:
        parts.extend(
            [
                "      <section>",
                "        <h2>Notices</h2>",
                "        <ul>",
            ]
        )
        for notice in notices:
            code = _require_string(notice.get("code"), "notice.code")
            severity = _require_string(notice.get("severity"), "notice.severity")
            message = _optional_string(notice.get("message"), "notice.message")
            item = f"          <li><strong>{escape(code)}</strong> ({escape(severity)})"
            if message is not None:
                item += f": {escape(message)}"
            item += "</li>"
            parts.append(item)
        parts.extend(["        </ul>", "      </section>"])

    parts.extend(["    </main>", "  </body>", "</html>", ""])
    return "\n".join(parts)


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


def _optional_non_negative_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer when provided.")
    return value


def _representation_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("representations.representations must be a list.")
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"representations.representations[{index}] must be an object.")
        result.append(item)
    return result


def _notice_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("representations.notices must be a list when provided.")
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"representations.notices[{index}] must be an object.")
        result.append(item)
    return result
