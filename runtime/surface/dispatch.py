"""Renderer dispatch boundary for SurfaceKernel."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Callable, Mapping

from runtime.surface.renderers.registry import builtin_renderer, builtin_renderer_id


RendererCallable = Callable[[Mapping[str, Any]], Mapping[str, Any]]


CUSTOM_RENDERER_ID = "custom_surface_renderer_v0"


def dispatch_surface_renderer(
    view_model: Mapping[str, Any],
    *,
    representation_profile: str,
    renderer_id: str | None = None,
    renderer: RendererCallable | None = None,
) -> dict[str, Any]:
    """Dispatch a renderer-ready view model copy without passing runtime context."""
    renderer_input = deepcopy(dict(view_model))
    before = _stable_json(renderer_input)
    if renderer is None:
        selected_renderer = builtin_renderer(representation_profile)
        selected_renderer_id = renderer_id or builtin_renderer_id(representation_profile)
    else:
        selected_renderer = renderer
        selected_renderer_id = renderer_id or CUSTOM_RENDERER_ID
    output = dict(selected_renderer(deepcopy(renderer_input)))
    after = _stable_json(renderer_input)
    return {
        "schema_version": "surface_renderer_dispatch_result.v0",
        "renderer_id": selected_renderer_id,
        "representation_profile": representation_profile,
        "renderer_input": renderer_input,
        "renderer_output": output,
        "renderer_input_mutated": before != after,
        "renderer_called_source_provider": False,
        "renderer_created_verified_state": False,
        "renderer_mutated_reviewed_index": False,
        "renderer_mutated_public_index": False,
        "renderer_mutated_master_index": False,
    }


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def effective_surface_renderer_id(
    representation_profile: str,
    *,
    renderer_id: str | None = None,
    renderer: RendererCallable | None = None,
) -> str:
    if renderer_id:
        return renderer_id
    if renderer is not None:
        return CUSTOM_RENDERER_ID
    return builtin_renderer_id(representation_profile)
