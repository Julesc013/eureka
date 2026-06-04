"""JSON renderer for SurfaceKernel view models."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.surface.renderers.common import copy_view, renderer_envelope, status_of


PROFILE_ID = "json_v0"
RENDERER_ID = "surface_json_v0"


def render_json_v0(view_model: Mapping[str, Any]) -> dict[str, Any]:
    content = copy_view(view_model)
    return renderer_envelope(
        profile=PROFILE_ID,
        media_type="application/json",
        content={
            "schema_version": "surface_json_v0",
            "status": status_of(content),
            "view_model": content,
        },
        content_format="structured",
    )
