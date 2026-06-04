"""Built-in renderer registry for SurfaceKernel dispatch."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from runtime.surface.profiles import HTML_BASIC_V0, JSON_V0, SNAPSHOT_V0, TEXT_V0
from runtime.surface.renderers.html_basic_v0 import RENDERER_ID as HTML_RENDERER_ID, render_html_basic_v0
from runtime.surface.renderers.json_v0 import RENDERER_ID as JSON_RENDERER_ID, render_json_v0
from runtime.surface.renderers.snapshot_v0 import RENDERER_ID as SNAPSHOT_RENDERER_ID, render_snapshot_v0
from runtime.surface.renderers.text_v0 import RENDERER_ID as TEXT_RENDERER_ID, render_text_v0


Renderer = Callable[[Mapping[str, Any]], dict[str, Any]]

_RENDERERS: dict[str, tuple[str, Renderer]] = {
    JSON_V0: (JSON_RENDERER_ID, render_json_v0),
    TEXT_V0: (TEXT_RENDERER_ID, render_text_v0),
    HTML_BASIC_V0: (HTML_RENDERER_ID, render_html_basic_v0),
    SNAPSHOT_V0: (SNAPSHOT_RENDERER_ID, render_snapshot_v0),
}


def builtin_renderer(profile: str) -> Renderer:
    return _RENDERERS.get(profile, _RENDERERS[HTML_BASIC_V0])[1]


def builtin_renderer_id(profile: str) -> str:
    return _RENDERERS.get(profile, _RENDERERS[HTML_BASIC_V0])[0]
