"""Relay route table and path matching."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.relay.profiles import ALLOWED_ROUTES, relay_product_boundary, relay_truth_boundary, stable_id
from runtime.relay.security import validate_method_allowed, validate_no_write_route


ROUTE_DEFINITIONS = [
    ("/status", "status", "json_manifest"),
    ("/snapshot", "snapshot", "lite_html"),
    ("/search", "search", "lite_html"),
    ("/object/{id}", "object", "lite_html"),
    ("/source/{id}", "source", "lite_html"),
    ("/need/{id}", "need", "lite_html"),
    ("/action/{id}", "action", "lite_html"),
    ("/manifest", "manifest", "json_manifest"),
    ("/files", "files", "file_tree"),
    ("/text/search", "search", "text"),
    ("/text/object/{id}", "object", "text"),
    ("/terminal", "terminal", "terminal"),
]


def build_relay_route_table(profile: Mapping[str, Any] | None = None, policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    allowed = set((profile or {}).get("allowed_routes") or (policy or {}).get("allowed_routes", ALLOWED_ROUTES))
    routes = []
    for route_path, route_kind, output_profile in ROUTE_DEFINITIONS:
        if route_path not in allowed:
            continue
        routes.append(
            {
                "schema_version": "relay_route.v0",
                "route_id": stable_id("relay_route", route_path),
                "route_path": route_path,
                "route_status": "fixture_only",
                "route_kind": route_kind,
                "allowed_methods": ["GET"],
                "input_source": "verified_fixture_snapshot",
                "output_profile": output_profile,
                "required_snapshot_fields": [
                    "identity",
                    "source posture",
                    "evidence posture",
                    "rights posture",
                    "risk posture",
                    "action posture",
                    "limitations/no-claims",
                ],
                "blocked_actions": ["POST", "PUT", "PATCH", "DELETE", "upload", "download", "execute", "live_source_access"],
                "limitations": ["Read-only fixture route; no public hosting or live source access."],
                "truth_boundary": relay_truth_boundary(),
                "product_boundary": relay_product_boundary(),
            }
        )
    return routes


def match_relay_route(path: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    path = "/" + path.lstrip("/")
    path_no_query = path.split("?", 1)[0]
    for route in build_relay_route_table(None, policy):
        route_path = str(route["route_path"])
        if route_path == path_no_query:
            return {**route, "path_params": {}}
        params = _match_dynamic(route_path, path_no_query)
        if params is not None:
            return {**route, "path_params": params}
    return {
        "schema_version": "relay_route.v0",
        "route_id": stable_id("relay_route", {"unknown": path_no_query}),
        "route_path": path_no_query,
        "route_status": "blocked_by_policy",
        "route_kind": "unknown",
        "allowed_methods": [],
        "input_source": "none",
        "output_profile": "text",
        "required_snapshot_fields": [],
        "blocked_actions": ["unknown_route"],
        "limitations": ["Route is not allowed by D-BUNDLE-02 relay policy."],
        "truth_boundary": relay_truth_boundary(),
        "product_boundary": relay_product_boundary(),
        "path_params": {},
    }


def validate_relay_route(route: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "route_id",
        "route_path",
        "route_status",
        "route_kind",
        "allowed_methods",
        "input_source",
        "output_profile",
        "required_snapshot_fields",
        "blocked_actions",
        "limitations",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in route:
            errors.append(f"missing relay route field: {field}")
    if route.get("schema_version") != "relay_route.v0":
        errors.append("schema_version must be relay_route.v0")
    for method in route.get("allowed_methods", []):
        errors.extend(validate_method_allowed(str(method), policy))
    errors.extend(validate_no_write_route(route, policy))
    if route.get("route_status") != "blocked_by_policy" and route.get("route_path") not in (policy or {}).get("allowed_routes", ALLOWED_ROUTES):
        errors.append(f"route_path is not allowed: {route.get('route_path')}")
    return sorted(dict.fromkeys(errors))


def _match_dynamic(route_pattern: str, path: str) -> dict[str, str] | None:
    if "{id}" not in route_pattern:
        return None
    prefix = route_pattern.split("{id}", 1)[0]
    if not path.startswith(prefix):
        return None
    value = path[len(prefix) :]
    if not value or "/" in value:
        return None
    return {"id": value}

