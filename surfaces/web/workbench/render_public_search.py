from __future__ import annotations

from html import escape
from typing import Any, Mapping
from urllib.parse import quote


def render_public_search_html(envelope: Mapping[str, Any] | None) -> str:
    query = ""
    if envelope is not None:
        query_block = envelope.get("query")
        if isinstance(query_block, Mapping):
            query = str(query_block.get("raw") or query_block.get("normalized") or "")
        elif envelope.get("error"):
            error = envelope.get("error")
            if isinstance(error, Mapping) and error.get("parameter") == "q":
                query = ""

    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "  <head>",
        "    <meta charset=\"utf-8\">",
        "    <title>Eureka Public Search</title>",
        "  </head>",
        "  <body>",
        "    <header>",
        "      <h1>Eureka Public Search</h1>",
        "      <p>Local-index-only prototype search over controlled Eureka records.</p>",
        "      <nav>",
        "        <a href=\"/api/v1/status\">Status JSON</a>",
        "        <a href=\"/api/v1/sources\">Sources JSON</a>",
        "        <a href=\"/\">Compatibility workbench</a>",
        "      </nav>",
        "    </header>",
        "    <main>",
        "      <section>",
        "        <h2>Search</h2>",
        "        <form method=\"get\" action=\"/search\">",
        "          <label for=\"q\">Query</label>",
        f"          <input id=\"q\" name=\"q\" type=\"search\" maxlength=\"160\" value=\"{escape(query, quote=True)}\">",
        "          <button type=\"submit\">Search</button>",
        "        </form>",
        "      </section>",
        "      <section>",
        "        <h2>Safety Posture</h2>",
        "        <ul>",
        "          <li>Mode: local-index-only.</li>",
        "          <li>No live probes, arbitrary URL fetches, downloads, installs, uploads, local path search, accounts, or telemetry.</li>",
        "          <li>Local/prototype backend runtime only. This is not hosted public deployment and not a production claim.</li>",
        "        </ul>",
        "      </section>",
    ]

    if envelope is None:
        parts.extend(
            [
                "      <section>",
                "        <h2>Ready</h2>",
                "        <p>Enter a bounded query such as windows 7 apps, firefox xp, driver.inf, or pc magazine.</p>",
                "      </section>",
            ]
        )
    elif envelope.get("ok") is False:
        parts.extend(_render_error(envelope))
    else:
        parts.extend(_render_success(envelope))

    parts.extend(["    </main>", "  </body>", "</html>", ""])
    return "\n".join(parts)


def _render_error(envelope: Mapping[str, Any]) -> list[str]:
    error = _mapping(envelope.get("error"))
    code = str(error.get("code") or "bad_request")
    message = str(error.get("message") or "The public search request was rejected.")
    parameter = error.get("parameter")
    lines = [
        "      <section>",
        "        <h2>Request Blocked</h2>",
        f"        <p><strong>{escape(code)}</strong>: {escape(message)}</p>",
    ]
    if parameter:
        lines.append(f"        <p>Parameter: {escape(str(parameter))}</p>")
    lines.extend(_render_warnings(envelope.get("warnings")))
    lines.extend(["      </section>"])
    return lines


def _render_success(envelope: Mapping[str, Any]) -> list[str]:
    query = _mapping(envelope.get("query"))
    results = _mapping_list(envelope.get("results"))
    lines = [
        "      <section>",
        "        <h2>Search State</h2>",
        "        <dl>",
        f"          <dt>Mode</dt><dd>{escape(str(envelope.get('mode') or 'local_index_only'))}</dd>",
        f"          <dt>Query</dt><dd>{escape(str(query.get('normalized') or ''))}</dd>",
        f"          <dt>Results</dt><dd>{len(results)}</dd>",
        "        </dl>",
        "      </section>",
    ]
    if results:
        lines.extend(["      <section>", "        <h2>Results</h2>", "        <ol>"])
        for card in results:
            lines.extend(_render_card(card))
        lines.extend(["        </ol>", "      </section>"])
    else:
        absence = _mapping(envelope.get("absence_summary"))
        message = str(absence.get("message") or "No controlled local-index records matched this query.")
        lines.extend(
            [
                "      <section>",
                "        <h2>No Results</h2>",
                f"        <p>{escape(message)}</p>",
                "      </section>",
            ]
        )
    gaps = _mapping_list(envelope.get("gaps"))
    if gaps:
        lines.extend(["      <section>", "        <h2>Gaps</h2>", "        <ul>"])
        for gap in gaps:
            lines.append(f"          <li>{escape(str(gap.get('message') or gap.get('gap_type') or 'gap'))}</li>")
        lines.extend(["        </ul>", "      </section>"])
    lines.extend(_render_warnings(envelope.get("warnings")))
    return lines


def _render_card(card: Mapping[str, Any]) -> list[str]:
    title = str(card.get("title") or card.get("result_id") or "Untitled result")
    subtitle = str(card.get("subtitle") or "")
    source = _mapping(card.get("source"))
    compatibility = _mapping(card.get("compatibility"))
    user_cost = _mapping(card.get("user_cost"))
    evidence = _mapping(card.get("evidence"))
    links = _mapping(card.get("links"))
    inspect_link = links.get("inspect")
    source_link = links.get("source")
    lines = [
        "          <li>",
        f"            <h3>{escape(title)}</h3>",
    ]
    if subtitle:
        lines.append(f"            <p>{escape(subtitle)}</p>")
    lines.extend(
        [
            "            <dl>",
            f"              <dt>Lane</dt><dd>{escape(str(card.get('result_lane') or 'other'))}</dd>",
            f"              <dt>User cost</dt><dd>{escape(str(user_cost.get('score') or 'unknown'))} ({escape(str(user_cost.get('label') or 'unknown'))})</dd>",
            f"              <dt>Source</dt><dd>{escape(str(source.get('source_label') or source.get('source_id') or 'unknown'))}</dd>",
            f"              <dt>Compatibility</dt><dd>{escape(str(compatibility.get('status') or 'unknown'))}</dd>",
            f"              <dt>Evidence summaries</dt><dd>{escape(str(evidence.get('evidence_count') or 0))}</dd>",
            "            </dl>",
        ]
    )
    lines.extend(_render_actions(card.get("actions")))
    warnings = _mapping_list(card.get("warnings"))
    if warnings:
        lines.append("            <p>Warnings: " + escape(", ".join(str(item.get("warning_type") or "warning") for item in warnings)) + "</p>")
    limitations = card.get("limitations")
    if isinstance(limitations, list) and limitations:
        lines.append("            <p>Limitations: " + escape(", ".join(str(item) for item in limitations[:8])) + "</p>")
    safe_links = []
    if isinstance(inspect_link, str) and inspect_link.startswith("/"):
        safe_links.append(f"<a href=\"{escape(inspect_link, quote=True)}\">inspect</a>")
    if isinstance(source_link, str) and source_link.startswith("/"):
        safe_links.append(f"<a href=\"{escape(source_link, quote=True)}\">source</a>")
    if safe_links:
        lines.append("            <p>" + " ".join(safe_links) + "</p>")
    lines.append("          </li>")
    return lines


def _render_actions(value: Any) -> list[str]:
    actions = _mapping(value)
    blocked = _mapping_list(actions.get("blocked"))
    allowed = _mapping_list(actions.get("allowed"))
    future = _mapping_list(actions.get("future_gated"))
    lines = ["            <p>Allowed actions: " + escape(", ".join(_action_ids(allowed)) or "none") + "</p>"]
    lines.append("            <p>Blocked actions: " + escape(", ".join(_action_ids(blocked)) or "none") + "</p>")
    if future:
        lines.append("            <p>Future-gated actions: " + escape(", ".join(_action_ids(future))) + "</p>")
    return lines


def _render_warnings(value: Any) -> list[str]:
    warnings = _mapping_list(value)
    if not warnings:
        return []
    lines = ["      <section>", "        <h2>Warnings</h2>", "        <ul>"]
    for warning in warnings:
        lines.append(f"          <li>{escape(str(warning.get('message') or warning.get('warning_type') or 'warning'))}</li>")
    lines.extend(["        </ul>", "      </section>"])
    return lines


def _action_ids(actions: list[Mapping[str, Any]]) -> list[str]:
    return [str(item.get("action_id") or "unknown") for item in actions]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]
