"""Shared helpers for SurfaceKernel baseline renderers."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Mapping


def renderer_envelope(
    *,
    profile: str,
    media_type: str,
    content: Any,
    content_format: str,
) -> dict[str, Any]:
    return {
        "schema_version": "surface_renderer_output.v0",
        "representation_profile": profile,
        "media_type": media_type,
        "content_format": content_format,
        "content": content,
    }


def copy_view(view_model: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(view_model))


def text_value(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value)
    return text if text else default


def status_of(view_model: Mapping[str, Any]) -> str:
    return text_value(view_model.get("canonical_status"), "unknown")


def title_of(view_model: Mapping[str, Any]) -> str:
    return text_value(view_model.get("title"), text_value(view_model.get("entity_id"), "Untitled"))


def summary_of(view_model: Mapping[str, Any]) -> str:
    return text_value(view_model.get("summary"), "Summary unavailable")


def action_ids(view_model: Mapping[str, Any]) -> list[str]:
    actions: list[str] = []
    for action in view_model.get("actions") or []:
        if isinstance(action, Mapping):
            action_id = text_value(action.get("action_id"))
        else:
            action_id = text_value(action)
        if action_id:
            actions.append(action_id)
    return actions


def policy_notes(view_model: Mapping[str, Any]) -> list[str]:
    return [text_value(note) for note in view_model.get("policy_notes") or [] if text_value(note)]


def fallback_summary(view_model: Mapping[str, Any]) -> Mapping[str, Any] | None:
    payload = view_model.get("payload")
    if not isinstance(payload, Mapping):
        return None
    fallback = payload.get("fallback_summary")
    return fallback if isinstance(fallback, Mapping) else None


def fallback_status(view_model: Mapping[str, Any]) -> str:
    fallback = fallback_summary(view_model)
    if fallback is None:
        return ""
    return text_value(fallback.get("canonical_status") or fallback.get("status"), "")


def fallback_reason_codes(view_model: Mapping[str, Any]) -> list[str]:
    fallback = fallback_summary(view_model)
    if fallback is None:
        return []
    return [text_value(item) for item in fallback.get("reason_codes") or [] if text_value(item)]


def fallback_items(view_model: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    fallback = fallback_summary(view_model)
    if fallback is None:
        return []
    return [item for item in fallback.get(key) or [] if isinstance(item, Mapping)]


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
