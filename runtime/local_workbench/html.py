"""Small deterministic HTML helpers for the local workbench."""

from html import escape
from typing import Any, Mapping, Sequence


NON_CLAIM_BANNER = (
    "Local appliance prototype. Localhost only. Not production. "
    "Not public launch. Operator-gated local review only. Reviewed local projection, not global proof."
)


def escape_html(value: Any) -> str:
    return escape("" if value is None else str(value), quote=True)


def render_document(title: str, body: str, *, status_banner: str | None = None) -> str:
    banner = status_banner or NON_CLAIM_BANNER
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{escape_html(title)}</title>",
            "</head>",
            "<body>",
            f'  <header role="banner"><p class="notice prototype">{escape_html(banner)}</p>{render_navigation()}</header>',
            "  <main>",
            body,
            "  </main>",
            "</body>",
            "</html>",
        ]
    )


def render_navigation() -> str:
    links = (
        render_link("/", "Home"),
        render_link("/status", "Status"),
        render_link("/search", "Search"),
        render_link("/absence?q=sampleproject", "Absence example"),
        render_link("/review", "Review"),
        render_link("/rebuild", "Rebuild"),
        render_link("/api/v1/status", "JSON status"),
    )
    return "<nav aria-label=\"Primary\"><ul>" + "".join(f"<li>{item}</li>" for item in links) + "</ul></nav>"


def render_link(href: str, text: str) -> str:
    return f'<a href="{escape_html(href)}">{escape_html(text)}</a>'


def render_table(rows: Sequence[Mapping[str, Any]] | Sequence[Sequence[Any]], headers: Sequence[str] | None = None) -> str:
    if not rows:
        return "<p>No rows.</p>"
    header_values = list(headers or _headers_from_rows(rows))
    head = "<thead><tr>" + "".join(f"<th scope=\"col\">{escape_html(item)}</th>" for item in header_values) + "</tr></thead>"
    body_rows: list[str] = []
    for row in rows:
        if isinstance(row, Mapping):
            values = [row.get(item, "") for item in header_values]
        else:
            values = list(row)
        body_rows.append("<tr>" + "".join(f"<td>{escape_html(item)}</td>" for item in values) + "</tr>")
    return "<table>" + head + "<tbody>" + "".join(body_rows) + "</tbody></table>"


def render_notice(kind: str, text: str) -> str:
    return f'<p class="notice {escape_html(kind)}">{escape_html(text)}</p>'


def render_limitations(limitations: Sequence[Any]) -> str:
    if not limitations:
        return ""
    return "<section aria-labelledby=\"limitations-heading\"><h2 id=\"limitations-heading\">Limitations</h2><ul>" + "".join(
        f"<li>{escape_html(item)}</li>" for item in limitations
    ) + "</ul></section>"


def render_warnings(warnings: Sequence[Any]) -> str:
    if not warnings:
        return ""
    return "<section aria-labelledby=\"warnings-heading\"><h2 id=\"warnings-heading\">Warnings</h2><ul>" + "".join(
        f"<li>{escape_html(item)}</li>" for item in warnings
    ) + "</ul></section>"


def _headers_from_rows(rows: Sequence[Mapping[str, Any]] | Sequence[Sequence[Any]]) -> tuple[str, ...]:
    first = rows[0]
    if isinstance(first, Mapping):
        return tuple(str(item) for item in first.keys())
    return tuple(f"column_{index + 1}" for index, _ in enumerate(first))
