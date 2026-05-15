"""Validation helpers for LAN safety gates."""

from .errors import LocalNetworkPolicyError
from .hosts import validate_service_host
from .policy import is_mutation_allowed_for_scope, is_route_allowed_for_scope


def validate_bind_lan_flag_required(host: str, bind_lan: bool) -> str:
    return validate_service_host(host, bind_lan=bind_lan)


def validate_no_lan_mutation(method: str, path: str, client_scope: object) -> None:
    scope = str(getattr(client_scope, "value", client_scope) or "").lower()
    if scope in {"lan", "unknown"} and str(method or "").upper() != "GET":
        raise LocalNetworkPolicyError("LAN clients may not use mutation routes")
    if scope in {"lan", "unknown"} and is_mutation_allowed_for_scope(method, path, scope):
        raise LocalNetworkPolicyError("LAN mutation route is blocked")


def validate_lan_read_only_route(method: str, path: str) -> str:
    if not is_route_allowed_for_scope(method, path, "lan"):
        raise LocalNetworkPolicyError("route is not allowed for read-only LAN scope")
    return path
