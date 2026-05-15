"""Safety warnings and checks for explicit read-only LAN mode."""

from typing import Mapping

from .errors import LocalNetworkSafetyError


def build_lan_warning() -> str:
    return "LAN mode is explicit and read-only; it is local network inspection, not hosting."


def build_firewall_warning() -> str:
    return "Check the operating system firewall before binding to all interfaces, and stop the service when finished."


def validate_lan_mode_safe(config: Mapping[str, object]) -> Mapping[str, object]:
    if bool(config.get("bind_lan")) and not bool(config.get("read_only", True)):
        raise LocalNetworkSafetyError("LAN mode must stay read-only")
    if bool(config.get("deployment_performed")):
        raise LocalNetworkSafetyError("LAN mode must not be deployment")
    if bool(config.get("site_dist_writes_enabled")):
        raise LocalNetworkSafetyError("LAN mode must not write site artifacts")
    return config
