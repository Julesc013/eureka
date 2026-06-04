"""Plain text renderer for SurfaceKernel view models."""

from __future__ import annotations

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


PROFILE_ID = "text_v0"
RENDERER_ID = "surface_text_v0"


def render_text_v0(view_model: Mapping[str, Any]) -> dict[str, Any]:
    lines = [
        title_of(view_model),
        f"Status: {status_of(view_model)}",
        f"Summary: {summary_of(view_model)}",
    ]
    fallback = fallback_status(view_model)
    if fallback:
        lines.append(f"Fallback status: {fallback}")
    reasons = fallback_reason_codes(view_model)
    if reasons:
        lines.append("Reasons: " + ", ".join(reasons))
    candidate_titles = [_item_label(item, "candidate_id") for item in fallback_items(view_model, "candidates")]
    if candidate_titles:
        lines.append("Candidates: " + "; ".join(candidate_titles))
    need_titles = [_item_label(item, "need_id") for item in fallback_items(view_model, "needs")]
    if need_titles:
        lines.append("Needs: " + "; ".join(need_titles))
    actions = action_ids(view_model)
    lines.append("Actions: " + (", ".join(actions) if actions else "none"))
    notes = policy_notes(view_model)
    if notes:
        lines.append("Notes: " + "; ".join(notes))
    return renderer_envelope(
        profile=PROFILE_ID,
        media_type="text/plain; charset=utf-8",
        content="\n".join(lines),
        content_format="text",
    )


def _item_label(item: Mapping[str, Any], id_key: str) -> str:
    title = text_value(item.get("title"))
    item_id = text_value(item.get(id_key) or item.get("item_id"))
    status = text_value(item.get("canonical_status") or item.get("status"), "unknown")
    label = title or item_id or "untitled"
    return f"{label} [{status}]"
