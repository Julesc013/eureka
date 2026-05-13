"""Classify request clients for local network routing."""

from enum import Enum

from .hosts import classify_client_host


class ClientScope(str, Enum):
    LOOPBACK = "loopback"
    LAN = "lan"
    UNKNOWN = "unknown"


def classify_client_scope(client_host: str) -> ClientScope:
    value = classify_client_host(client_host)
    if value == ClientScope.LOOPBACK.value:
        return ClientScope.LOOPBACK
    if value == ClientScope.LAN.value:
        return ClientScope.LAN
    return ClientScope.UNKNOWN
