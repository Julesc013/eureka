from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HostProfile:
    host_profile_id: str
    os_family: str
    architecture: str
    runtime_family: str | None = None
    features: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "host_profile_id": self.host_profile_id,
            "os_family": self.os_family,
            "architecture": self.architecture,
            "features": list(self.features),
        }
        if self.runtime_family is not None:
            payload["runtime_family"] = self.runtime_family
        return payload


_BOOTSTRAP_HOST_PROFILES: dict[str, HostProfile] = {
    "windows-x86_64": HostProfile(
        host_profile_id="windows-x86_64",
        os_family="windows",
        architecture="x86_64",
    ),
    "linux-x86_64": HostProfile(
        host_profile_id="linux-x86_64",
        os_family="linux",
        architecture="x86_64",
    ),
    "macos-arm64": HostProfile(
        host_profile_id="macos-arm64",
        os_family="macos",
        architecture="arm64",
    ),
}


def bootstrap_host_profiles() -> tuple[HostProfile, ...]:
    return tuple(_BOOTSTRAP_HOST_PROFILES.values())


def bootstrap_host_profile_ids() -> tuple[str, ...]:
    return tuple(_BOOTSTRAP_HOST_PROFILES.keys())


def resolve_bootstrap_host_profile(host_profile_id: str) -> HostProfile:
    normalized_host_profile_id = host_profile_id.strip()
    if not normalized_host_profile_id:
        raise ValueError("host_profile_id must be a non-empty string.")
    try:
        return _BOOTSTRAP_HOST_PROFILES[normalized_host_profile_id]
    except KeyError as error:
        allowed = ", ".join(bootstrap_host_profile_ids())
        raise ValueError(
            f"host_profile_id must be one of: {allowed}."
        ) from error
