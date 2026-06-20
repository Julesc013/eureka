"""DNS and IP target guards for safe web fetching."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import socket
from typing import Callable
from urllib.parse import urlparse


Resolver = Callable[[str], tuple[str, ...]]


@dataclass(frozen=True)
class DNSGuardResult:
    status: str
    host: str
    addresses: tuple[str, ...]
    error: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status, "host": self.host, "addresses": list(self.addresses), "error": self.error}


def default_resolver(host: str) -> tuple[str, ...]:
    infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    addresses = sorted({str(item[4][0]) for item in infos})
    return tuple(addresses)


class DNSGuard:
    def __init__(self, resolver: Resolver = default_resolver) -> None:
        self._resolver = resolver

    def validate_url(self, url: str) -> DNSGuardResult:
        parsed = urlparse(str(url or ""))
        host = str(parsed.hostname or "").strip()
        if not host:
            return DNSGuardResult("blocked", host, (), "missing_host")
        literal = _ip_literal(host)
        if literal is not None:
            return _validate_addresses(host, (str(literal),))
        try:
            addresses = tuple(str(item) for item in self._resolver(host))
        except Exception as exc:
            return DNSGuardResult("blocked", host, (), f"dns_resolution_failed:{exc}")
        return _validate_addresses(host, addresses)


def _validate_addresses(host: str, addresses: tuple[str, ...]) -> DNSGuardResult:
    if not addresses:
        return DNSGuardResult("blocked", host, (), "dns_resolution_empty")
    for address in addresses:
        ip = _ip_literal(address)
        if ip is None:
            return DNSGuardResult("blocked", host, addresses, f"invalid_ip:{address}")
        if not ip.is_global:
            return DNSGuardResult("blocked", host, addresses, f"non_public_ip:{address}")
    return DNSGuardResult("pass", host, addresses)


def _ip_literal(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(str(value).strip("[]"))
    except ValueError:
        return None
