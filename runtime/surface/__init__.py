"""Surface projection boundary for Eureka runtime payloads."""

from runtime.surface.cache_key import build_surface_cache_key
from runtime.surface.capabilities import negotiate_surface_profile
from runtime.surface.dispatch import dispatch_surface_renderer
from runtime.surface.kernel import SurfaceKernel, SurfaceRequest
from runtime.surface.output_policy import apply_surface_output_policy
from runtime.surface.profiles import REPRESENTATION_PROFILES, resolve_profile
from runtime.surface.routes import SURFACE_ROUTES, resolve_surface_route
from runtime.surface.view_models import adapt_surface_view_model

__all__ = [
    "REPRESENTATION_PROFILES",
    "SURFACE_ROUTES",
    "SurfaceKernel",
    "SurfaceRequest",
    "adapt_surface_view_model",
    "apply_surface_output_policy",
    "build_surface_cache_key",
    "dispatch_surface_renderer",
    "negotiate_surface_profile",
    "resolve_profile",
    "resolve_surface_route",
]
