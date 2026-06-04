"""Baseline renderer entry points for SurfaceKernel."""

from runtime.surface.renderers.html_basic_v0 import render_html_basic_v0
from runtime.surface.renderers.json_v0 import render_json_v0
from runtime.surface.renderers.registry import builtin_renderer, builtin_renderer_id
from runtime.surface.renderers.snapshot_v0 import render_snapshot_v0
from runtime.surface.renderers.text_v0 import render_text_v0

__all__ = [
    "builtin_renderer",
    "builtin_renderer_id",
    "render_html_basic_v0",
    "render_json_v0",
    "render_snapshot_v0",
    "render_text_v0",
]
