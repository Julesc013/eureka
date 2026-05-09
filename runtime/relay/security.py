"""Read-only and loopback security checks for the relay runtime."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.relay.profiles import (
    ALLOWED_METHODS,
    relay_no_claims,
    relay_product_boundary,
    relay_truth_boundary,
    stable_id,
)


UNSAFE_ROUTE_TOKENS = ("admin", "upload", "download", "execute", "install", "mirror", "write", "delete")


def validate_bind_host(host: str, policy: Mapping[str, Any] | None = None) -> list[str]:
    allowed = set((policy or {}).get("allowed_bind_hosts", ["127.0.0.1", "localhost"]))
    forbidden = set((policy or {}).get("forbidden_bind_hosts", ["0.0.0.0", "::", "*", ""]))
    if host in forbidden:
        return [f"public or wildcard bind host is forbidden: {host!r}"]
    if host not in allowed:
        return [f"bind host is not explicitly loopback-only: {host!r}"]
    return []


def validate_method_allowed(method: str, policy: Mapping[str, Any] | None = None) -> list[str]:
    method = method.upper()
    allowed = {str(item).upper() for item in (policy or {}).get("allowed_methods", sorted(ALLOWED_METHODS))}
    forbidden = {str(item).upper() for item in (policy or {}).get("forbidden_methods", ["POST", "PUT", "PATCH", "DELETE"])}
    if method in forbidden:
        return [f"method is forbidden for read-only relay: {method}"]
    if method not in allowed:
        return [f"method is not allowed for read-only relay: {method}"]
    return []


def validate_no_write_route(route: str | Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    path = str(route.get("route_path", "") if isinstance(route, Mapping) else route)
    lowered = path.casefold()
    for token in UNSAFE_ROUTE_TOKENS:
        if token in lowered:
            return [f"route exposes unsafe token {token!r}: {path}"]
    return []


def validate_no_live_access(policy: Mapping[str, Any] | None = None) -> list[str]:
    payload = policy or {}
    errors: list[str] = []
    for key in ("live_access_enabled", "source_sync_enabled", "downloads_enabled", "uploads_enabled", "accounts_enabled", "telemetry_enabled", "action_execution_enabled"):
        if payload.get(key) is True:
            errors.append(f"{key} must remain false")
    no_live_policy = payload.get("relay_no_live_access_policy", {})
    if isinstance(no_live_policy, Mapping):
        for key in ("no_network_outbound", "no_source_sync", "no_live_probes", "no_external_resource_fetch", "no_download_mirror_install_execute"):
            if no_live_policy.get(key) is not True:
                errors.append(f"relay_no_live_access_policy.{key} must be true")
    return errors


def build_policy_blocked_response(reason: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "relay_response.v0",
        "response_id": stable_id("relay_response", {"status": 403, "reason": reason}),
        "status_code": 403,
        "content_type": "text/plain; charset=utf-8",
        "render_profile": "text",
        "body_summary": reason,
        "body": f"Blocked by relay policy: {reason}\nNo live access, writes, downloads, uploads, or execution are enabled.\n",
        "headers": {"Cache-Control": "no-store", "X-Eureka-Relay": "fixture-only-readonly"},
        "semantic_fields_present": ["limitations/no-claims", "action posture"],
        "blocked_actions": ["write", "upload", "download", "execute", "live_source_access", "public_bind"],
        "no_claims": relay_no_claims(),
        "truth_boundary": relay_truth_boundary(),
        "product_boundary": relay_product_boundary(),
    }

