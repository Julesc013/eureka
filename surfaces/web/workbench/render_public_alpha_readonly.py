from __future__ import annotations

from html import escape
from typing import Any, Mapping


def render_public_alpha_readonly_html(payload: Mapping[str, Any]) -> str:
    title = "Eureka Public Alpha"
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        f"    <title>{title}</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        f"      <h1>{title}</h1>",
        "      <p>Reviewed snapshot search. Read-only local alpha.</p>",
        "      <nav>",
        "        <a href=\"/alpha\">Alpha search</a>",
        "        <a href=\"/api/v1/alpha/status\">Status JSON</a>",
        "        <a href=\"/api/v1/alpha/needs\">Known needs JSON</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
    ]
    if payload.get("ok") is False:
        parts.extend(_render_error(payload))
    else:
        parts.extend(_render_status(payload))
        if "results" in payload:
            parts.extend(_render_search(payload))
        elif "record" in payload:
            parts.extend(_render_object(payload))
        elif "source_summary" in payload:
            parts.extend(_render_summary("Source Summary", payload["source_summary"]))
        elif "evidence_summary" in payload:
            parts.extend(_render_summary("Evidence Summary", payload["evidence_summary"]))
        elif "absence_summary" in payload:
            parts.extend(_render_summary("Absence Summary", payload["absence_summary"]))
        elif "known_needs" in payload:
            parts.extend(_render_known_needs(payload))
    parts.extend(
        [
            "      <section>",
            "        <h2>Non-Claims</h2>",
            "        <ul>",
            "          <li>Not production.</li>",
            "          <li>No public launch readiness claim.</li>",
            "          <li>No live source fanout, downloads, extraction, uploads, installs, accounts, or model calls.</li>",
            "          <li>Absence means not present in the current reviewed snapshot.</li>",
            "        </ul>",
            "      </section>",
            "    </main>",
            "  </body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def _render_status(payload: Mapping[str, Any]) -> list[str]:
    snapshot = _mapping(payload.get("snapshot"))
    relay = _mapping(payload.get("relay"))
    return [
        "      <section>",
        "        <h2>Status</h2>",
        "        <dl>",
        f"          <dt>Mode</dt><dd>{escape(str(payload.get('mode') or 'reviewed_snapshot_read_only'))}</dd>",
        f"          <dt>Snapshot</dt><dd>{escape(str(snapshot.get('snapshot_id') or 'unknown'))}</dd>",
        f"          <dt>Records</dt><dd>{escape(str(snapshot.get('record_count') or 0))}</dd>",
        f"          <dt>Relay</dt><dd>{escape(str(relay.get('relay_id') or 'unknown'))}</dd>",
        "          <dt>Read-only</dt><dd>true</dd>",
        "        </dl>",
        "        <form method=\"get\" action=\"/alpha\">",
        "          <label for=\"q\">Search reviewed snapshot</label>",
        "          <input id=\"q\" name=\"q\" type=\"search\" maxlength=\"160\">",
        "          <button type=\"submit\">Search</button>",
        "        </form>",
        "      </section>",
    ]


def _render_search(payload: Mapping[str, Any]) -> list[str]:
    query = _mapping(payload.get("query"))
    results = _mapping_list(payload.get("results"))
    parts = [
        "      <section>",
        "        <h2>Search Results</h2>",
        f"        <p>Query: {escape(str(query.get('normalized') or ''))}</p>",
    ]
    if results:
        parts.append("        <ol>")
        for record in results:
            object_id = str(record.get("object_id") or record.get("record_id") or "")
            href = "/alpha/object?id=" + escape(object_id, quote=True)
            parts.extend(
                [
                    "          <li>",
                    f"            <a href=\"{href}\">{escape(str(record.get('title') or object_id))}</a>",
                    f"            <p>{escape(str(record.get('reviewed_status') or 'reviewed'))}</p>",
                    "          </li>",
                ]
            )
        parts.append("        </ol>")
    else:
        parts.append("        <p>No reviewed snapshot record matched this query.</p>")
        parts.extend(_render_known_needs(payload))
    parts.append("      </section>")
    return parts


def _render_object(payload: Mapping[str, Any]) -> list[str]:
    record = _mapping(payload.get("record"))
    parts = [
        "      <section>",
        f"        <h2>{escape(str(record.get('title') or record.get('object_id') or 'Object'))}</h2>",
        "        <dl>",
        f"          <dt>Object ID</dt><dd>{escape(str(record.get('object_id') or 'unknown'))}</dd>",
        f"          <dt>Record ID</dt><dd>{escape(str(record.get('record_id') or 'unknown'))}</dd>",
        f"          <dt>Domain</dt><dd>{escape(str(record.get('domain_id') or 'unknown'))}</dd>",
        f"          <dt>Status</dt><dd>{escape(str(record.get('reviewed_status') or 'unknown'))}</dd>",
        "        </dl>",
        "      </section>",
    ]
    for heading, key in (("Source Summaries", "source_summaries"), ("Evidence Summaries", "evidence_summaries")):
        summaries = _mapping_list(payload.get(key))
        if summaries:
            parts.append("      <section>")
            parts.append(f"        <h2>{heading}</h2>")
            parts.append("        <ul>")
            for summary in summaries:
                parts.append(f"          <li>{escape(str(summary.get('title') or summary.get('summary_id')))}</li>")
            parts.append("        </ul>")
            parts.append("      </section>")
    return parts


def _render_known_needs(payload: Mapping[str, Any]) -> list[str]:
    needs = _mapping_list(payload.get("known_needs"))
    absence = _mapping_list(payload.get("absence_summaries"))
    if not needs and not absence:
        return []
    parts = ["      <section>", "        <h2>Known Needs</h2>", "        <ul>"]
    for item in absence + needs:
        parts.append(f"          <li>{escape(str(item.get('title') or item.get('summary_id') or item.get('need_id')))}</li>")
    parts.extend(["        </ul>", "      </section>"])
    return parts


def _render_summary(heading: str, value: Any) -> list[str]:
    summary = _mapping(value)
    return [
        "      <section>",
        f"        <h2>{escape(heading)}</h2>",
        "        <dl>",
        f"          <dt>ID</dt><dd>{escape(str(summary.get('summary_id') or 'unknown'))}</dd>",
        f"          <dt>Title</dt><dd>{escape(str(summary.get('title') or 'Untitled'))}</dd>",
        "        </dl>",
        "      </section>",
    ]


def _render_error(payload: Mapping[str, Any]) -> list[str]:
    error = _mapping(payload.get("error"))
    return [
        "      <section>",
        "        <h2>Request Blocked</h2>",
        f"        <p>{escape(str(error.get('code') or 'error'))}: {escape(str(error.get('message') or 'The request was rejected.'))}</p>",
        "      </section>",
    ]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]
