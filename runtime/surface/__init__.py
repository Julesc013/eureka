"""Surface projection boundary for Eureka runtime payloads."""

from runtime.surface.cache_key import build_surface_cache_key
from runtime.surface.capabilities import negotiate_surface_profile
from runtime.surface.dispatch import dispatch_surface_renderer, effective_surface_renderer_id
from runtime.surface.kernel import SurfaceKernel, SurfaceRequest
from runtime.surface.output_policy import apply_surface_output_policy
from runtime.surface.profiles import REPRESENTATION_PROFILES, resolve_profile
from runtime.surface.renderers import (
    builtin_renderer,
    builtin_renderer_id,
    render_html_basic_v0,
    render_json_v0,
    render_snapshot_v0,
    render_text_v0,
)
from runtime.surface.routes import SURFACE_ROUTES, resolve_surface_route
from runtime.surface.view_models import adapt_surface_view_model

__all__ = [
    "REPRESENTATION_PROFILES",
    "SURFACE_ROUTES",
    "SurfaceKernel",
    "SurfaceRequest",
    "adapt_surface_view_model",
    "apply_surface_output_policy",
    "builtin_renderer",
    "builtin_renderer_id",
    "build_surface_cache_key",
    "dispatch_surface_renderer",
    "effective_surface_renderer_id",
    "negotiate_surface_profile",
    "render_html_basic_v0",
    "render_json_v0",
    "render_snapshot_v0",
    "render_text_v0",
    "resolve_profile",
    "resolve_surface_route",
]
