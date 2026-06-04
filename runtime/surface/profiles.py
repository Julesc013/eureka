"""Representation profile vocabulary for SurfaceKernel."""

from __future__ import annotations

from dataclasses import dataclass


JSON_V0 = "json_v0"
TEXT_V0 = "text_v0"
HTML_BASIC_V0 = "html_basic_v0"
SNAPSHOT_V0 = "snapshot_v0"
DEFAULT_PUBLIC_PROFILE = HTML_BASIC_V0


@dataclass(frozen=True)
class RepresentationProfile:
    profile_id: str
    output_family: str
    renderer_ready: bool = True
    public_safe: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "output_family": self.output_family,
            "renderer_ready": self.renderer_ready,
            "public_safe": self.public_safe,
        }


REPRESENTATION_PROFILES: dict[str, RepresentationProfile] = {
    JSON_V0: RepresentationProfile(JSON_V0, "json"),
    TEXT_V0: RepresentationProfile(TEXT_V0, "text"),
    HTML_BASIC_V0: RepresentationProfile(HTML_BASIC_V0, "html"),
    SNAPSHOT_V0: RepresentationProfile(SNAPSHOT_V0, "snapshot"),
}

PROFILE_ALIASES = {
    "api_client": JSON_V0,
    "json": JSON_V0,
    "json_v0": JSON_V0,
    "text": TEXT_V0,
    "text_v0": TEXT_V0,
    "standard_web": HTML_BASIC_V0,
    "lite_html": HTML_BASIC_V0,
    "html": HTML_BASIC_V0,
    "html_basic_v0": HTML_BASIC_V0,
    "snapshot": SNAPSHOT_V0,
    "snapshot_v0": SNAPSHOT_V0,
    "native_client": JSON_V0,
}


def resolve_profile(value: str | None, *, default: str = DEFAULT_PUBLIC_PROFILE) -> tuple[str, bool]:
    """Return a supported profile id and whether a fallback mapping was needed."""
    if value is None or not str(value).strip():
        return default, False
    normalized = str(value).strip()
    profile = PROFILE_ALIASES.get(normalized, "")
    if profile in REPRESENTATION_PROFILES:
        return profile, False
    return default, True
