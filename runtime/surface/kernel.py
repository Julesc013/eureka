"""SurfaceKernel orchestration over canonical view-model projections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from runtime.surface.cache_key import build_surface_cache_key
from runtime.surface.capabilities import negotiate_surface_profile
from runtime.surface.dispatch import RendererCallable, dispatch_surface_renderer
from runtime.surface.fallback import safe_degraded_view
from runtime.surface.output_policy import OPERATOR_POSTURE, apply_surface_output_policy
from runtime.surface.routes import resolve_surface_route
from runtime.surface.view_models import adapt_surface_view_model


@dataclass(frozen=True)
class SurfaceRequest:
    route_id: str
    entity_id: str = ""
    payload: Any = None
    requested_profile: str | None = None
    accept_header: str | None = None
    visibility_posture: str = "public"
    policy_posture: str | None = None
    renderer_id: str | None = None
    skin_id: str | None = None
    language: str | None = None
    data_version: str | None = None
    renderer: RendererCallable | None = None


class SurfaceKernel:
    """Coordinate route, profile, policy, cache, and renderer-ready projection."""

    def __init__(self, view_loader: Callable[[SurfaceRequest], Mapping[str, Any]] | None = None) -> None:
        self._view_loader = view_loader

    def project(self, request: SurfaceRequest) -> dict[str, Any]:
        route = resolve_surface_route(request.route_id)
        capability = negotiate_surface_profile(
            requested_profile=request.requested_profile,
            accept_header=request.accept_header,
        )
        if request.visibility_posture == OPERATOR_POSTURE:
            route_allowed = route.operator_allowed
        else:
            route_allowed = route.public_allowed
        if not route_allowed:
            canonical_view = safe_degraded_view(
                route.route_id,
                request.entity_id,
                f"{route.route_id} is unavailable for {request.visibility_posture}",
            )
        else:
            source_payload = self._view_loader(request) if self._view_loader is not None else request.payload
            canonical_view = adapt_surface_view_model(route.route_id, source_payload)
        policy_view = apply_surface_output_policy(
            canonical_view,
            visibility_posture=request.visibility_posture,
            policy_posture=request.policy_posture,
        )
        entity_id = request.entity_id or str(policy_view.get("entity_id") or route.route_id)
        cache = build_surface_cache_key(
            route=route.route_id,
            entity_id=entity_id,
            view_model_version=str(policy_view.get("view_model_version") or "surface_view_model.v0"),
            representation_profile=capability.representation_profile,
            renderer_id=request.renderer_id,
            skin_id=request.skin_id,
            language=request.language,
            visibility_posture=request.visibility_posture,
            policy_posture=str(policy_view.get("policy_posture") or ""),
            data_version=request.data_version,
        )
        renderer_result = dispatch_surface_renderer(
            policy_view,
            representation_profile=capability.representation_profile,
            renderer_id=request.renderer_id,
            renderer=request.renderer,
        )
        return {
            "schema_version": "surface_projection.v0",
            "route": route.to_dict(),
            "capability": capability.to_dict(),
            "view_model": policy_view,
            "cache": cache,
            "renderer_result": renderer_result,
            "surface_kernel_mutated_reviewed_index": False,
            "surface_kernel_mutated_public_index": False,
            "surface_kernel_mutated_master_index": False,
            "surface_kernel_called_source_provider": False,
        }
