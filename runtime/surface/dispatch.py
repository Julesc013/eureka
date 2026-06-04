"""Renderer dispatch boundary for SurfaceKernel."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Callable, Mapping


RendererCallable = Callable[[Mapping[str, Any]], Mapping[str, Any]]


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
        output = {
            "schema_version": "surface_renderer_ready_payload.v0",
            "content": renderer_input,
        }
    else:
        output = dict(renderer(deepcopy(renderer_input)))
    after = _stable_json(renderer_input)
    return {
        "schema_version": "surface_renderer_dispatch_result.v0",
        "renderer_id": renderer_id or "renderer_ready_payload_v0",
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
