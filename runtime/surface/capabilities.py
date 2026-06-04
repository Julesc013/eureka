"""Small capability negotiation helper for SurfaceKernel."""

from __future__ import annotations

from dataclasses import dataclass

from runtime.surface.profiles import DEFAULT_PUBLIC_PROFILE, REPRESENTATION_PROFILES, resolve_profile


@dataclass(frozen=True)
class CapabilityDecision:
    representation_profile: str
    supported_profiles: tuple[str, ...]
    requested_profile: str | None = None
    fallback_used: bool = False
    reason: str = "explicit_or_default_profile"

    def to_dict(self) -> dict[str, object]:
        return {
            "representation_profile": self.representation_profile,
            "supported_profiles": list(self.supported_profiles),
            "requested_profile": self.requested_profile,
            "fallback_used": self.fallback_used,
            "reason": self.reason,
        }


def negotiate_surface_profile(
    *,
    requested_profile: str | None = None,
    accept_header: str | None = None,
    surface_default: str | None = None,
) -> CapabilityDecision:
    """Negotiate a renderer-ready profile with conservative fallback behavior."""
    default_profile, _ = resolve_profile(surface_default, default=DEFAULT_PUBLIC_PROFILE)
    requested = requested_profile or _profile_from_accept_header(accept_header)
    profile, fallback_used = resolve_profile(requested, default=default_profile)
    reason = "explicit_profile" if requested_profile else ("accept_header" if accept_header else "surface_default")
    if fallback_used:
        reason = "unsupported_profile_fallback"
    return CapabilityDecision(
        representation_profile=profile,
        supported_profiles=tuple(REPRESENTATION_PROFILES),
        requested_profile=requested,
        fallback_used=fallback_used,
        reason=reason,
    )


def _profile_from_accept_header(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.casefold()
    if "application/json" in normalized:
        return "json_v0"
    if "text/plain" in normalized:
        return "text_v0"
    if "text/html" in normalized:
        return "html_basic_v0"
    return None
