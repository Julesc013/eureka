"""Deterministic cache key model for SurfaceKernel."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def build_surface_cache_key(
    *,
    route: str,
    entity_id: str,
    view_model_version: str,
    representation_profile: str,
    renderer_id: str | None = None,
    skin_id: str | None = None,
    language: str | None = None,
    visibility_posture: str,
    policy_posture: str,
    data_version: str | None = None,
) -> dict[str, Any]:
    parts = {
        "route": route or "unknown",
        "entity_id": entity_id or "unknown",
        "view_model_version": view_model_version or "surface_view_model.v0",
        "representation_profile": representation_profile or "html_basic_v0",
        "renderer_id": renderer_id or "renderer_unselected",
        "skin_id": skin_id or "default",
        "language": language or "und",
        "visibility_posture": visibility_posture or "public",
        "policy_posture": policy_posture or "public_read_only",
        "data_version": data_version or "unknown",
    }
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()[:24]
    return {
        "schema_version": "surface_cache_key.v0",
        "cache_key": f"surface:{digest}",
        "parts": parts,
    }
