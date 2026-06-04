"""Basic HTML renderer for SurfaceKernel view models."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping

from runtime.surface.renderers.common import (
    action_ids,
    fallback_items,
    fallback_reason_codes,
    fallback_status,
    policy_notes,
    renderer_envelope,
    status_of,
    summary_of,
    text_value,
    title_of,
)


PROFILE_ID = "html_basic_v0"
RENDERER_ID = "surface_html_basic_v0"


def render_html_basic_v0(view_model: Mapping[str, Any]) -> dict[str, Any]:
    body = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{_e(title_of(view_model))}</title>",
        "</head>",
        "<body>",
        "<main>",
        f"<h1>{_e(title_of(view_model))}</h1>",
        f'<p data-status="{_e(status_of(view_model))}">Status: {_e(status_of(view_model))}</p>',
        f"<p>{_e(summary_of(view_model))}</p>",
    ]
    fallback = fallback_status(view_model)
    if fallback:
        body.append(f"<p>Fallback status: {_e(fallback)}</p>")
    reasons = fallback_reason_codes(view_model)
    if reasons:
        body.append("<section><h2>Reasons</h2><ul>")
        body.extend(f"<li>{_e(reason)}</li>" for reason in reasons)
        body.append("</ul></section>")
    _append_items(body, "Candidates", fallback_items(view_model, "candidates"), "candidate_id")
    _append_items(body, "Needs", fallback_items(view_model, "needs"), "need_id")
    actions = action_ids(view_model)
    body.append("<section><h2>Actions</h2><ul>")
    if actions:
        body.extend(f"<li>{_e(action)}</li>" for action in actions)
    else:
        body.append("<li>none</li>")
    body.append("</ul></section>")
    notes = policy_notes(view_model)
    if notes:
        body.append("<section><h2>Notes</h2><ul>")
        body.extend(f"<li>{_e(note)}</li>" for note in notes)
        body.append("</ul></section>")
    body.extend(["</main>", "</body>", "</html>"])
    return renderer_envelope(
        profile=PROFILE_ID,
        media_type="text/html; charset=utf-8",
        content="\n".join(body),
        content_format="html",
    )


def _append_items(body: list[str], heading: str, items: list[Mapping[str, Any]], id_key: str) -> None:
    if not items:
        return
    body.append(f"<section><h2>{_e(heading)}</h2><ul>")
    for item in items:
        title = text_value(item.get("title") or item.get(id_key) or item.get("item_id"), "untitled")
        status = text_value(item.get("canonical_status") or item.get("status"), "unknown")
        body.append(f"<li>{_e(title)} <span>[{_e(status)}]</span></li>")
    body.append("</ul></section>")


def _e(value: str) -> str:
    return escape(value, quote=True)
