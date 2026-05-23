"""Host validation for localhost and explicit LAN bind mode."""

from .errors import LocalNetworkHostError


LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
DEFAULT_BIND_HOSTS = {"127.0.0.1", "localhost"}
LAN_BIND_HOSTS = {"0.0.0.0", "::"}


def is_loopback_host(host: str) -> bool:
    return _normalize_host(host) in LOOPBACK_HOSTS


def is_lan_bind_host(host: str) -> bool:
    return _normalize_host(host) in LAN_BIND_HOSTS


def validate_service_host(host: str, bind_lan: bool = False) -> str:
    value = _normalize_host(host)
    if value in DEFAULT_BIND_HOSTS:
        return value
    if value in LAN_BIND_HOSTS:
        if bind_lan:
            return value
        raise LocalNetworkHostError(f"LAN bind host requires explicit --bind-lan: {host!r}")
    if not value:
        raise LocalNetworkHostError("service host is required")
    raise LocalNetworkHostError(f"host is outside the local service policy: {host!r}")


def classify_client_host(client_host: str) -> str:
    value = _normalize_host(client_host)
    if value in LOOPBACK_HOSTS or value.startswith("127."):
        return "loopback"
    if _is_private_ipv4(value) or _is_local_ipv6(value):
        return "lan"
    return "unknown"


def _normalize_host(host: str) -> str:
    value = str(host or "").strip().lower()
    if value.startswith("[") and value.endswith("]"):
        return value[1:-1]
    return value


def _is_private_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    try:
        numbers = [int(part) for part in parts]
    except ValueError:
        return False
    if any(number < 0 or number > 255 for number in numbers):
        return False
    if numbers[0] == 10:
        return True
    if numbers[0] == 192 and numbers[1] == 168:
        return True
    return numbers[0] == 172 and 16 <= numbers[1] <= 31


def _is_local_ipv6(value: str) -> bool:
    return value == "::1" or value.startswith("fe80:") or value.startswith("fd") or value.startswith("fc")
