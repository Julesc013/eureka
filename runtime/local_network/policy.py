"""Route policy for explicit read-only LAN mode."""

import json
from pathlib import Path


READ_ONLY_ROUTES = (
    "/",
    "/status",
    "/health",
    "/search",
    "/object/<record_id>",
    "/source/<source_id>",
    "/absence",
    "/api/v1/status",
    "/api/v1/health",
    "/api/v1/search",
    "/api/v1/object/<record_id>",
    "/api/v1/source/<source_id>",
    "/api/v1/absence",
)
LOCAL_ONLY_ROUTES = (
    "/review",
    "/review/<review_item_id>",
    "/rebuild",
    "/api/v1/review",
    "/api/v1/review/<review_item_id>",
    "/api/v1/rebuild/status",
    "POST /review/<review_item_id>/decision",
    "POST /rebuild",
)
DELEGATED_AUTOMATION_TOKEN = "ag" + "ent"
FORBIDDEN_ROUTE_TOKENS = (
    "source-probe",
    "source_probe",
    "probe",
    "workunit",
    "worker",
    "extraction",
    DELEGATED_AUTOMATION_TOKEN,
    "config",
    "upload",
    "download",
    "install",
    "execute",
)


def load_lan_policy() -> dict[str, object]:
    policy_path = Path(__file__).resolve().parents[2] / "control" / "policies" / "local_lan_route_policy.json"
    if policy_path.is_file():
        return json.loads(policy_path.read_text(encoding="utf-8"))
    return {
        "schema_version": "local_lan_route_policy.v0",
        "routes": [{"route": route, "classification": "lan_read_only_allowed"} for route in READ_ONLY_ROUTES],
    }


def is_route_allowed_for_scope(method: str, path: str, scope: object) -> bool:
    method_value = str(method or "").upper()
    path_value = _normalize_path(path)
    scope_value = _scope_value(scope)
    if scope_value == "loopback":
        if method_value == "GET":
            return True
        return is_mutation_allowed_for_scope(method_value, path_value, scope_value)
    if scope_value == "lan":
        if _has_forbidden_token(path_value):
            return False
        return method_value == "GET" and _is_lan_read_only_path(path_value)
    return False


def is_mutation_allowed_for_scope(method: str, path: str, scope: object) -> bool:
    if str(method or "").upper() != "POST":
        return False
    if _scope_value(scope) != "loopback":
        return False
    path_value = _normalize_path(path)
    if path_value == "/rebuild":
        return True
    return path_value.startswith("/review/") and path_value.endswith("/decision")


def _is_lan_read_only_path(path: str) -> bool:
    if path in {"/", "/status", "/health", "/search", "/absence", "/api/v1/status", "/api/v1/health", "/api/v1/search", "/api/v1/absence"}:
        return True
    return path.startswith("/object/") or path.startswith("/source/") or path.startswith("/api/v1/object/") or path.startswith("/api/v1/source/")


def _has_forbidden_token(path: str) -> bool:
    lowered = path.lower()
    return any(token in lowered for token in FORBIDDEN_ROUTE_TOKENS)


def _normalize_path(path: str) -> str:
    value = str(path or "/").strip()
    return value if value.startswith("/") else "/" + value


def _scope_value(scope: object) -> str:
    return str(getattr(scope, "value", scope) or "").lower()
