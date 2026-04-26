from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_local_index_html(
    local_index: Mapping[str, Any],
    *,
    requested_index_path: str = "",
    requested_query: str = "",
    message: str | None = None,
) -> str:
    status = _require_string(local_index.get("status"), "local_index.status")
    index_metadata = _require_mapping(local_index.get("index"), "local_index.index")
    notices = _notice_list(local_index.get("notices"), "local_index.notices")
    results = _results(local_index.get("results"), "local_index.results")
    query = _optional_string(local_index.get("query"), "local_index.query") or requested_query
    result_count = local_index.get("result_count")
    if result_count is not None and (not isinstance(result_count, int) or result_count < 0):
        raise ValueError("local_index.result_count must be a non-negative integer when provided.")

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Local Index</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Local Index</h1>",
        "      <p>Compatibility-first, bootstrap local SQLite search over the current bounded corpus.</p>",
        "      <nav>",
        "        <a href=\"/\">Open exact resolution workbench</a>",
        "        <a href=\"/search\">Search the bounded corpus</a>",
        "        <a href=\"/query-plan\">Compile a bounded query plan</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
    ]
    if message:
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
            "        <h2>Build or Inspect</h2>",
            "        <form method=\"get\" action=\"/index/build\">",
            "          <label for=\"index-path-build\">Index path</label>",
            f"          <input id=\"index-path-build\" name=\"index_path\" type=\"text\" value=\"{escape(requested_index_path, quote=True)}\">",
            "          <button type=\"submit\">Build index</button>",
            "        </form>",
            "        <form method=\"get\" action=\"/index/status\">",
            "          <label for=\"index-path-status\">Index path</label>",
            f"          <input id=\"index-path-status\" name=\"index_path\" type=\"text\" value=\"{escape(requested_index_path, quote=True)}\">",
            "          <button type=\"submit\">Index status</button>",
            "        </form>",
            "      </section>",
            "      <section>",
            "        <h2>Search</h2>",
            "        <form method=\"get\" action=\"/index/search\">",
            "          <label for=\"index-path-search\">Index path</label>",
            f"          <input id=\"index-path-search\" name=\"index_path\" type=\"text\" value=\"{escape(requested_index_path, quote=True)}\">",
            "          <label for=\"query\">Query</label>",
            f"          <input id=\"query\" name=\"q\" type=\"text\" value=\"{escape(query, quote=True)}\">",
            "          <button type=\"submit\">Search index</button>",
            "        </form>",
            "      </section>",
            "      <section>",
            "        <h2>Index</h2>",
            "        <dl>",
            f"          <dt>Status</dt><dd>{escape(status)}</dd>",
            f"          <dt>Path kind</dt><dd>{escape(_require_string(index_metadata.get('index_path_kind'), 'local_index.index.index_path_kind'))}</dd>",
            f"          <dt>Path</dt><dd>{escape(_optional_string(index_metadata.get('index_path'), 'local_index.index.index_path') or '(not reported)')}</dd>",
            f"          <dt>FTS mode</dt><dd>{escape(_require_string(index_metadata.get('fts_mode'), 'local_index.index.fts_mode'))}</dd>",
            f"          <dt>Record count</dt><dd>{_require_int(index_metadata.get('record_count'), 'local_index.index.record_count')}</dd>",
            f"          <dt>Record kinds</dt><dd>{escape(_record_kind_counts_text(index_metadata.get('record_kind_counts')))}</dd>",
            "        </dl>",
            "      </section>",
        ]
    )

    if result_count is not None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Query Summary</h2>",
                "        <dl>",
                f"          <dt>Query</dt><dd>{escape(query)}</dd>",
                f"          <dt>Result count</dt><dd>{result_count}</dd>",
                "        </dl>",
                "      </section>",
            ]
        )

    if results:
        parts.extend(
            [
                "      <section>",
                "        <h2>Results</h2>",
                "        <ul>",
            ]
        )
        for result in results:
            parts.append(
                "          <li>"
                f"<strong>{escape(result['label'])}</strong> "
                f"<span>[{escape(result['record_kind'])}]</span> "
                f"<span>source: {escape(result.get('source_id', '(none)'))}</span> "
                f"<span>family: {escape(result.get('source_family', '(none)'))}</span>"
                "</li>"
            )
            parts.append("          <ul>")
            for field_name in (
                "summary",
                "target_ref",
                "resolved_resource_id",
                "representation_id",
                "member_path",
                "parent_target_ref",
                "parent_representation_id",
                "member_kind",
                "media_type",
                "content_hash",
                "version_or_state",
            ):
                value = result.get(field_name)
                if isinstance(value, str) and value:
                    parts.append(f"            <li>{escape(field_name)}: {escape(value)}</li>")
            size_bytes = result.get("size_bytes")
            if isinstance(size_bytes, int):
                parts.append(f"            <li>size_bytes: {size_bytes}</li>")
            action_hints = result.get("action_hints")
            if isinstance(action_hints, list) and action_hints:
                parts.append(f"            <li>action_hints: {escape(', '.join(str(item) for item in action_hints))}</li>")
            for field_name in (
                "primary_lane",
                "user_cost_score",
                "usefulness_summary",
            ):
                value = result.get(field_name)
                if isinstance(value, str) and value:
                    parts.append(f"            <li>{escape(field_name)}: {escape(value)}</li>")
                elif isinstance(value, int):
                    parts.append(f"            <li>{escape(field_name)}: {value}</li>")
            for field_name in ("result_lanes", "user_cost_reasons"):
                values = result.get(field_name)
                if isinstance(values, list) and values:
                    parts.append(f"            <li>{escape(field_name)}: {escape(', '.join(str(item) for item in values))}</li>")
            if result["route_hints"]:
                parts.append(
                    f"            <li>route_hints: {escape(_mapping_text(result['route_hints']))}</li>"
                )
            if result["evidence"]:
                parts.append(
                    f"            <li>evidence: {escape(', '.join(result['evidence']))}</li>"
                )
            parts.append("          </ul>")
        parts.extend(["        </ul>", "      </section>"])

    if notices:
        parts.extend(
            [
                "      <section>",
                "        <h2>Notices</h2>",
                "        <ul>",
            ]
        )
        for notice in notices:
            parts.append(
                "          <li>"
                f"{escape(notice['severity'])} {escape(notice['code'])}: {escape(notice.get('message', ''))}"
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


def _results(value: Any, field_name: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    results: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{field_name}[{index}] must be an object.")
        results.append(
            {
                "index_record_id": _require_string(item.get("index_record_id"), f"{field_name}[{index}].index_record_id"),
                "record_kind": _require_string(item.get("record_kind"), f"{field_name}[{index}].record_kind"),
                "label": _require_string(item.get("label"), f"{field_name}[{index}].label"),
                "summary": _optional_string(item.get("summary"), f"{field_name}[{index}].summary"),
                "target_ref": _optional_string(item.get("target_ref"), f"{field_name}[{index}].target_ref"),
                "resolved_resource_id": _optional_string(
                    item.get("resolved_resource_id"),
                    f"{field_name}[{index}].resolved_resource_id",
                ),
                "source_id": _optional_string(item.get("source_id"), f"{field_name}[{index}].source_id") or "(none)",
                "source_family": _optional_string(item.get("source_family"), f"{field_name}[{index}].source_family") or "(none)",
                "representation_id": _optional_string(
                    item.get("representation_id"),
                    f"{field_name}[{index}].representation_id",
                ),
                "member_path": _optional_string(item.get("member_path"), f"{field_name}[{index}].member_path"),
                "parent_target_ref": _optional_string(
                    item.get("parent_target_ref"),
                    f"{field_name}[{index}].parent_target_ref",
                ),
                "parent_representation_id": _optional_string(
                    item.get("parent_representation_id"),
                    f"{field_name}[{index}].parent_representation_id",
                ),
                "member_kind": _optional_string(item.get("member_kind"), f"{field_name}[{index}].member_kind"),
                "media_type": _optional_string(item.get("media_type"), f"{field_name}[{index}].media_type"),
                "content_hash": _optional_string(item.get("content_hash"), f"{field_name}[{index}].content_hash"),
                "size_bytes": _optional_int(item.get("size_bytes"), f"{field_name}[{index}].size_bytes"),
                "action_hints": _optional_string_list(item.get("action_hints"), f"{field_name}[{index}].action_hints"),
                "result_lanes": _optional_string_list(item.get("result_lanes"), f"{field_name}[{index}].result_lanes"),
                "primary_lane": _optional_string(item.get("primary_lane"), f"{field_name}[{index}].primary_lane"),
                "user_cost_score": _optional_int(item.get("user_cost_score"), f"{field_name}[{index}].user_cost_score"),
                "user_cost_reasons": _optional_string_list(
                    item.get("user_cost_reasons"),
                    f"{field_name}[{index}].user_cost_reasons",
                ),
                "usefulness_summary": _optional_string(
                    item.get("usefulness_summary"),
                    f"{field_name}[{index}].usefulness_summary",
                ),
                "version_or_state": _optional_string(
                    item.get("version_or_state"),
                    f"{field_name}[{index}].version_or_state",
                ),
                "evidence": _string_list(item.get("evidence"), f"{field_name}[{index}].evidence"),
                "route_hints": _require_mapping(item.get("route_hints"), f"{field_name}[{index}].route_hints"),
            }
        )
    return results


def _notice_list(value: Any, field_name: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
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


def _record_kind_counts_text(value: Any) -> str:
    counts = _require_mapping(value, "local_index.index.record_kind_counts")
    if not counts:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in counts.items())


def _mapping_text(value: Mapping[str, Any]) -> str:
    if not value:
        return "(none)"
    return ", ".join(f"{key}={item}" for key, item in value.items())


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return [_require_string(item, f"{field_name}[{index}]") for index, item in enumerate(value)]


def _optional_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    return _string_list(value, field_name)


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object.")
    return value


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


def _optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    return _require_int(value, field_name)
