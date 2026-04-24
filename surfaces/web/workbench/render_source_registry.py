from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_source_registry_html(source_registry: Mapping[str, Any]) -> str:
    status = _require_string(source_registry.get("status"), "source_registry.status")
    source_count = _require_int(source_registry.get("source_count"), "source_registry.source_count")
    sources = _source_list(source_registry.get("sources"))
    applied_filters = _optional_mapping(
        source_registry.get("applied_filters"),
        "source_registry.applied_filters",
    )
    selected_source_id = _optional_string(
        source_registry.get("selected_source_id"),
        "source_registry.selected_source_id",
    )
    notices = _optional_notice_list(source_registry.get("notices"), "source_registry.notices")

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Source Registry</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Source Registry</h1>",
        "      <p>Compatibility-first, inventory-backed source metadata for the current Eureka bootstrap lane.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/sources\">List sources</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Registry State</h2>",
        "        <dl>",
        f"          <dt>Status</dt><dd>{escape(status)}</dd>",
        f"          <dt>Source count</dt><dd>{source_count}</dd>",
        "        </dl>",
        "      </section>",
        "      <section>",
        "        <h2>Filter Sources</h2>",
        "        <form method=\"get\" action=\"/sources\">",
        "          <label for=\"status\">Status</label>",
        f"          <input id=\"status\" name=\"status\" type=\"text\" value=\"{escape(_filter_value(applied_filters, 'status'), quote=True)}\">",
        "          <label for=\"family\">Family</label>",
        f"          <input id=\"family\" name=\"family\" type=\"text\" value=\"{escape(_filter_value(applied_filters, 'family'), quote=True)}\">",
        "          <label for=\"role\">Role</label>",
        f"          <input id=\"role\" name=\"role\" type=\"text\" value=\"{escape(_filter_value(applied_filters, 'role'), quote=True)}\">",
        "          <label for=\"surface\">Surface</label>",
        f"          <input id=\"surface\" name=\"surface\" type=\"text\" value=\"{escape(_filter_value(applied_filters, 'surface'), quote=True)}\">",
        "          <button type=\"submit\">Filter</button>",
        "        </form>",
        "      </section>",
    ]

    if applied_filters:
        parts.extend(
            [
                "      <section>",
                "        <h2>Applied Filters</h2>",
                "        <ul>",
            ]
        )
        for key, value in applied_filters.items():
            parts.append(f"          <li>{escape(str(key))}: {escape(str(value))}</li>")
        parts.extend(["        </ul>", "      </section>"])

    if sources:
        parts.extend(
            [
                "      <section>",
                "        <h2>Sources</h2>",
                "        <ul>",
            ]
        )
        for source in sources:
            link = "/source?id=" + quote(source["source_id"], safe="")
            parts.append(
                "          <li>"
                f"<a href=\"{escape(link, quote=True)}\">{escape(source['name'])}</a> "
                f"<span>[{escape(source['status'])}]</span> "
                f"<span>{escape(source['source_family'])}</span> "
                f"<span>{escape(source['status_summary'])}</span> "
                f"<span>trust: {escape(source['trust_lane'])}</span> "
                f"<span>connector: {escape(_connector_text(source['connector']))}</span> "
                f"<span>roles: {escape(', '.join(source['roles']))}</span> "
                f"<span>surfaces: {escape(', '.join(source['surfaces']))}</span>"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])
    elif not notices:
        parts.extend(
            [
                "      <section>",
                "        <h2>Sources</h2>",
                "        <p>No source records matched the current filters.</p>",
                "      </section>",
            ]
        )

    selected_source = _selected_source(sources, selected_source_id)
    if selected_source is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Selected Source</h2>",
                "        <dl>",
                f"          <dt>Name</dt><dd>{escape(selected_source['name'])}</dd>",
                f"          <dt>Source ID</dt><dd>{escape(selected_source['source_id'])}</dd>",
                f"          <dt>Family</dt><dd>{escape(selected_source['source_family'])}</dd>",
                f"          <dt>Status</dt><dd>{escape(selected_source['status'])}</dd>",
                f"          <dt>Status summary</dt><dd>{escape(selected_source['status_summary'])}</dd>",
                f"          <dt>Trust lane</dt><dd>{escape(selected_source['trust_lane'])}</dd>",
                f"          <dt>Authority class</dt><dd>{escape(selected_source['authority_class'])}</dd>",
                f"          <dt>Connector</dt><dd>{escape(_connector_text(selected_source['connector']))}</dd>",
                f"          <dt>Roles</dt><dd>{escape(', '.join(selected_source['roles']))}</dd>",
                f"          <dt>Surfaces</dt><dd>{escape(', '.join(selected_source['surfaces']))}</dd>",
                f"          <dt>Object types</dt><dd>{escape(', '.join(selected_source['object_types']))}</dd>",
                f"          <dt>Artifact types</dt><dd>{escape(', '.join(selected_source['artifact_types']))}</dd>",
                f"          <dt>Identifier types</dt><dd>{escape(', '.join(selected_source['identifier_types_emitted']))}</dd>",
                f"          <dt>Live access</dt><dd>{escape(selected_source['live_access_mode'])}</dd>",
                f"          <dt>Extraction</dt><dd>{escape(selected_source['extraction_mode'])}</dd>",
                f"          <dt>Legal posture</dt><dd>{escape(selected_source['legal_posture'])}</dd>",
                f"          <dt>Freshness model</dt><dd>{escape(selected_source['freshness_model'])}</dd>",
                f"          <dt>Rights notes</dt><dd>{escape(selected_source['rights_notes'])}</dd>",
                f"          <dt>Notes</dt><dd>{escape(selected_source['notes'])}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )

    if notices:
        parts.extend(
            [
                "      <section>",
                "        <h2>Notices</h2>",
                "        <ul>",
            ]
        )
        for notice in notices:
            message = notice.get("message", "")
            parts.append(
                "          <li>"
                f"{escape(notice['severity'])} {escape(notice['code'])}: {escape(message)}"
                "</li>"
            )
        parts.extend(["        </ul>", "      </section>"])

    parts.extend(
        [
            "    </main>",
            "  </body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _filter_value(filters: Mapping[str, Any] | None, key: str) -> str:
    if not isinstance(filters, Mapping):
        return ""
    value = filters.get(key)
    return value if isinstance(value, str) else ""


def _selected_source(
    sources: list[dict[str, Any]],
    selected_source_id: str | None,
) -> dict[str, Any] | None:
    if selected_source_id is None:
        return None
    for source in sources:
        if source["source_id"] == selected_source_id:
            return source
    return None


def _source_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("source_registry.sources must be a list.")
    sources: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"source_registry.sources[{index}] must be an object.")
        sources.append(_source_entry(item, f"source_registry.sources[{index}]"))
    return sources


def _source_entry(value: Mapping[str, Any], field_name: str) -> dict[str, Any]:
    return {
        "source_id": _require_string(value.get("source_id"), f"{field_name}.source_id"),
        "name": _require_string(value.get("name"), f"{field_name}.name"),
        "source_family": _require_string(value.get("source_family"), f"{field_name}.source_family"),
        "status": _require_string(value.get("status"), f"{field_name}.status"),
        "status_summary": _require_string(value.get("status_summary"), f"{field_name}.status_summary"),
        "roles": _string_list(value.get("roles"), f"{field_name}.roles"),
        "surfaces": _string_list(value.get("surfaces"), f"{field_name}.surfaces"),
        "trust_lane": _require_string(value.get("trust_lane"), f"{field_name}.trust_lane"),
        "authority_class": _require_string(value.get("authority_class"), f"{field_name}.authority_class"),
        "object_types": _string_list(value.get("object_types"), f"{field_name}.object_types"),
        "artifact_types": _string_list(value.get("artifact_types"), f"{field_name}.artifact_types"),
        "identifier_types_emitted": _string_list(
            value.get("identifier_types_emitted"),
            f"{field_name}.identifier_types_emitted",
        ),
        "connector": _require_mapping(value.get("connector"), f"{field_name}.connector"),
        "live_access_mode": _require_string(value.get("live_access_mode"), f"{field_name}.live_access_mode"),
        "extraction_mode": _require_string(value.get("extraction_mode"), f"{field_name}.extraction_mode"),
        "legal_posture": _require_string(value.get("legal_posture"), f"{field_name}.legal_posture"),
        "freshness_model": _require_string(value.get("freshness_model"), f"{field_name}.freshness_model"),
        "rights_notes": _require_string(value.get("rights_notes"), f"{field_name}.rights_notes"),
        "notes": _require_string(value.get("notes"), f"{field_name}.notes"),
    }


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    return _require_mapping(value, field_name)


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


def _optional_notice_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    notices: list[dict[str, str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        notices.append(
            {
                "code": _require_string(item.get("code"), f"{field_name}[{index}].code"),
                "severity": _require_string(item.get("severity"), f"{field_name}[{index}].severity"),
                "message": _optional_string(item.get("message"), f"{field_name}[{index}].message") or "",
            }
        )
    return notices


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    values: list[str] = []
    for index, item in enumerate(value):
        values.append(_require_string(item, f"{field_name}[{index}]"))
    return values


def _connector_text(value: Mapping[str, Any]) -> str:
    label = _require_string(value.get("label"), "connector.label")
    status = _require_string(value.get("status"), "connector.status")
    return f"{label} [{status}]"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value
