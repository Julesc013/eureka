"""Relay request and response model builders."""

from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse

from runtime.relay.profiles import relay_no_claims, relay_product_boundary, relay_truth_boundary, stable_id
from runtime.relay.routes import match_relay_route
from runtime.relay.security import build_policy_blocked_response, validate_method_allowed
from runtime.relay.snapshot_store import get_snapshot_record, query_snapshot_records
from runtime.relay.terminal import build_terminal_menu


def build_relay_request(method: str, path: str, query: Mapping[str, Any] | str | None, profile: Mapping[str, Any] | None, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    parsed = urlparse(path)
    route_path = parsed.path or "/"
    query_params = _query_params(query if query is not None else parsed.query)
    route = match_relay_route(route_path, policy)
    errors = validate_method_allowed(method, policy)
    if route.get("route_status") == "blocked_by_policy":
        errors.append("route is not allowed by relay policy")
    allowed = not errors
    render_profile = str(query_params.get("format", [route.get("output_profile", "lite_html")])[0])
    return {
        "schema_version": "relay_request.v0",
        "request_id": stable_id("relay_request", {"method": method.upper(), "path": route_path, "query": query_params}),
        "method": method.upper(),
        "path": route_path,
        "query_params": query_params,
        "render_profile": render_profile,
        "client_profile": profile.get("relay_mode", "localhost_readonly") if isinstance(profile, Mapping) else "localhost_readonly",
        "snapshot_ref": "",
        "allowed": allowed,
        "blocked_reason": "; ".join(errors),
        "limitations": ["Read-only fixture request; no writes, uploads, downloads, execution, or live access."],
        "route": route,
    }


def build_relay_response(request: Mapping[str, Any], snapshot_store: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not request.get("allowed", False):
        return build_policy_blocked_response(str(request.get("blocked_reason", "request blocked")), policy)
    route = request.get("route", {})
    route_kind = str(route.get("route_kind", "unknown"))
    path_params = route.get("path_params", {}) if isinstance(route.get("path_params"), Mapping) else {}
    body: Any
    status_code = 200
    summary = "Read-only relay fixture response."
    render_profile = str(request.get("render_profile") or route.get("output_profile", "lite_html"))
    if route_kind == "status":
        body = build_relay_status(snapshot_store)
        summary = "Relay status: localhost-only, read-only, no live access."
    elif route_kind == "manifest":
        body = build_relay_manifest(snapshot_store, policy)
        render_profile = "json_manifest"
        summary = "Relay manifest for fixture routes and snapshot refs."
    elif route_kind == "snapshot":
        body = {"records": snapshot_store.get("records", []), "manifest": snapshot_store.get("manifest", {})}
        summary = "Snapshot records exposed as read-only fixture data."
    elif route_kind == "search":
        body = {"records": query_snapshot_records(snapshot_store, _first_query(request), policy)}
        summary = "Fixture search projection; no public ranking or live fanout."
    elif route_kind == "object":
        record = get_snapshot_record(snapshot_store, "object_record", path_params.get("id"), policy)
        body = {"record": record} if record else {"record": None, "message": "object not found in fixture snapshot"}
        status_code = 200 if record else 404
        summary = "Fixture object projection."
    elif route_kind == "source":
        record = get_snapshot_record(snapshot_store, "source_record", path_params.get("id"), policy)
        body = {"record": record} if record else {"record": None, "message": "source not found in fixture snapshot"}
        status_code = 200 if record else 404
        summary = "Fixture source projection."
    elif route_kind == "need":
        record = get_snapshot_record(snapshot_store, "need_record", path_params.get("id"), policy)
        body = {"record": record} if record else {"record": None, "message": "need not found in fixture snapshot"}
        status_code = 200 if record else 404
        summary = "Fixture need projection."
    elif route_kind == "action":
        record = get_snapshot_record(snapshot_store, "action_manifest", path_params.get("id"), policy)
        body = {"record": record} if record else {"record": None, "message": "action not found in fixture snapshot"}
        status_code = 200 if record else 404
        summary = "Read-only action manifest projection; no action execution."
    elif route_kind == "files":
        body = {"records": snapshot_store.get("records", []), "manifest": snapshot_store.get("manifest", {})}
        render_profile = "file_tree"
        summary = "File-tree style index projection."
    elif route_kind == "terminal":
        body = {"terminal_menu": build_terminal_menu(snapshot_store, policy), "records": snapshot_store.get("records", [])}
        render_profile = "terminal"
        summary = "Terminal text menu projection."
    else:
        return build_policy_blocked_response("route is not allowed by relay policy", policy)
    return {
        "schema_version": "relay_response.v0",
        "response_id": stable_id("relay_response", {"request": request.get("request_id", ""), "status": status_code, "summary": summary}),
        "status_code": status_code,
        "content_type": _content_type(render_profile),
        "render_profile": render_profile,
        "body_summary": summary,
        "body": body,
        "headers": {"Cache-Control": "no-store", "X-Eureka-Relay": "fixture-only-readonly"},
        "semantic_fields_present": ["identity", "source posture", "evidence posture", "rights posture", "risk posture", "action posture", "limitations/no-claims"],
        "blocked_actions": ["write", "upload", "download", "execute", "live_source_access", "public_bind"],
        "no_claims": relay_no_claims(),
        "truth_boundary": relay_truth_boundary(),
        "product_boundary": relay_product_boundary(),
    }


def validate_relay_response(response: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "response_id",
        "status_code",
        "content_type",
        "render_profile",
        "body_summary",
        "headers",
        "semantic_fields_present",
        "blocked_actions",
        "no_claims",
        "truth_boundary",
        "product_boundary",
    }
    for field in sorted(required):
        if field not in response:
            errors.append(f"missing relay response field: {field}")
    if response.get("schema_version") != "relay_response.v0":
        errors.append("schema_version must be relay_response.v0")
    for boundary_name in ("truth_boundary", "product_boundary"):
        boundary = response.get(boundary_name, {})
        if isinstance(boundary, Mapping):
            for key, value in boundary.items():
                if value is True:
                    errors.append(f"{boundary_name}.{key} must be false")
    return sorted(dict.fromkeys(errors))


def build_relay_status(snapshot_store: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "relay_status.v0",
        "relay_status_id": stable_id("relay_status", snapshot_store.get("snapshot_ref", "")),
        "relay_mode": "localhost_readonly",
        "localhost_only": True,
        "read_only": True,
        "live_access_enabled": False,
        "source_sync_enabled": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "accounts_enabled": False,
        "telemetry_enabled": False,
        "action_execution_enabled": False,
        "snapshot_loaded": bool(snapshot_store.get("records")),
        "snapshot_ref": snapshot_store.get("snapshot_ref", ""),
        "limitations": ["Fixture-only relay status. No server is public or hosted by default."],
        "truth_boundary": relay_truth_boundary(),
        "product_boundary": relay_product_boundary(),
    }


def build_relay_manifest(snapshot_store: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "relay_manifest.v0",
        "relay_manifest_id": stable_id("relay_manifest", snapshot_store.get("snapshot_ref", "")),
        "relay_mode": "localhost_readonly",
        "routes": (policy or {}).get("allowed_routes", []),
        "profiles": (policy or {}).get("allowed_render_profiles", []),
        "snapshot_refs": [snapshot_store.get("snapshot_ref", "")],
        "no_goals": ["no public relay", "no live source access", "no writes", "no downloads", "no execution"],
        "blocked_actions": ["POST", "PUT", "PATCH", "DELETE", "upload", "download", "execute", "public_bind"],
        "limitations": ["Read-only fixture manifest; not a hosted/public route activation."],
        "truth_boundary": relay_truth_boundary(),
        "product_boundary": relay_product_boundary(),
    }


def _query_params(query: Mapping[str, Any] | str | None) -> dict[str, list[str]]:
    if isinstance(query, Mapping):
        result: dict[str, list[str]] = {}
        for key, value in query.items():
            if isinstance(value, list):
                result[str(key)] = [str(item) for item in value]
            else:
                result[str(key)] = [str(value)]
        return result
    if isinstance(query, str) and query:
        return {key: [str(item) for item in value] for key, value in parse_qs(query, keep_blank_values=True).items()}
    return {}


def _first_query(request: Mapping[str, Any]) -> str:
    query_params = request.get("query_params", {})
    if isinstance(query_params, Mapping):
        for key in ("q", "query", "term"):
            value = query_params.get(key)
            if isinstance(value, list) and value:
                return str(value[0])
            if value:
                return str(value)
    return ""


def _content_type(render_profile: str) -> str:
    if render_profile == "lite_html":
        return "text/html; charset=utf-8"
    if render_profile in {"json_manifest", "native_fixture_json"}:
        return "application/json; charset=utf-8"
    return "text/plain; charset=utf-8"

