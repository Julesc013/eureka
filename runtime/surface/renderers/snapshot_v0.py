"""Deterministic snapshot renderer for SurfaceKernel view models."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from runtime.surface.renderers.common import (
    action_ids,
    fallback_status,
    policy_notes,
    renderer_envelope,
    stable_json,
    status_of,
    summary_of,
    title_of,
)


PROFILE_ID = "snapshot_v0"
RENDERER_ID = "surface_snapshot_v0"


def render_snapshot_v0(view_model: Mapping[str, Any]) -> dict[str, Any]:
    canonical = {
        "schema_version": "surface_snapshot_v0",
        "view_model_version": str(view_model.get("view_model_version") or "surface_view_model.v0"),
        "route_id": str(view_model.get("route_id") or "unknown"),
        "view_family": str(view_model.get("view_family") or "unknown"),
        "entity_id": str(view_model.get("entity_id") or "unknown"),
        "canonical_status": status_of(view_model),
        "title": title_of(view_model),
        "summary": summary_of(view_model),
        "fallback_status": fallback_status(view_model) or None,
        "actions": sorted(action_ids(view_model)),
        "policy_notes": sorted(policy_notes(view_model)),
    }
    canonical["content_digest"] = hashlib.sha256(stable_json(view_model).encode("utf-8")).hexdigest()[:24]
    return renderer_envelope(
        profile=PROFILE_ID,
        media_type="application/vnd.eureka.surface.snapshot+json",
        content=canonical,
        content_format="snapshot",
    )
