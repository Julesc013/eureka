"""String template helpers for the local workbench."""

from .html import escape_html, render_link


def search_form(query: str = "") -> str:
    return (
        '<form action="/search" method="get">'
        '<label for="q">Search reviewed index</label> '
        f'<input id="q" name="q" type="search" value="{escape_html(query)}"> '
        '<button type="submit">Search</button>'
        "</form>"
    )


def record_links(record_id: str, source_id: str) -> str:
    links = [render_link(f"/object/{record_id}", "Object")]
    if source_id:
        links.append(render_link(f"/source/{source_id}", "Source"))
    return "<p>" + " | ".join(links) + "</p>"
