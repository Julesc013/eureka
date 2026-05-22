"""Relay profiles, policies, boundaries, and path guards."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Iterable, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_ROOT = REPO_ROOT / "control" / "inventory" / "relay"
RELAY_PROFILE_SCHEMA_VERSION = "relay_profile.v0"
OLD_BROWSER_PROFILE_SCHEMA_VERSION = "old_browser_profile.v0"
TERMINAL_PROFILE_SCHEMA_VERSION = "terminal_profile.v0"
NATIVE_FIXTURE_ENDPOINT_SCHEMA_VERSION = "native_fixture_endpoint.v0"
ALLOWED_RELAY_MODES = {
    "fixture_only",
    "localhost_readonly",
    "old_browser_preview",
    "terminal_preview",
    "native_fixture_preview",
    "policy_blocked",
}
ALLOWED_METHODS = {"GET"}
FORBIDDEN_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
ALLOWED_RENDER_PROFILES = {
    "text",
    "lite_html",
    "file_tree",
    "json_manifest",
    "terminal",
    "native_fixture_json",
}
ALLOWED_ROUTES = [
    "/status",
    "/snapshot",
    "/search",
    "/object/{id}",
    "/source/{id}",
    "/need/{id}",
    "/action/{id}",
    "/manifest",
    "/files",
    "/text/search",
    "/text/object/{id}",
    "/terminal",
]
FORBIDDEN_TRUE_FIELDS = {
    "bind_public_interfaces_allowed",
    "write_allowed",
    "upload_allowed",
    "download_allowed",
    "action_execution_allowed",
    "live_source_access_allowed",
    "account_auth_allowed",
    "telemetry_allowed",
    "relay_response_is_public_truth",
    "relay_accepts_evidence",
    "relay_accepts_candidate",
    "relay_mutates_public_index",
    "relay_mutates_master_index",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "public_bind_allowed",
    "public_relay_enabled",
    "hosted_relay_enabled",
    "write_enabled",
    "upload_enabled",
    "download_enabled",
    "action_execution_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "accounts_enabled",
    "telemetry_enabled",
    "source_sync_enabled",
    "live_access_enabled",
    "outbound_network_allowed",
    "changed_public_search_behavior",
    "enabled_hosting",
    "enabled_public_relay",
    "enabled_live_access",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "mutated_site_dist",
    "mutated_public_index",
    "mutated_master_index",
}


def load_relay_policy(root: Path = REPO_ROOT) -> dict[str, Any]:
    names = [
        "relay_profile_policy",
        "relay_route_policy",
        "relay_security_policy",
        "relay_loopback_policy",
        "relay_read_only_policy",
        "relay_render_policy",
        "relay_old_browser_policy",
        "relay_terminal_policy",
        "relay_native_fixture_policy",
        "relay_path_policy",
        "relay_truth_policy",
        "relay_no_live_access_policy",
    ]
    policy_root = root / "control" / "inventory" / "relay"
    bundle = {name: load_json(policy_root / f"{name}.json") for name in names}
    render = bundle["relay_render_policy"]
    route = bundle["relay_route_policy"]
    loopback = bundle["relay_loopback_policy"]
    paths = bundle["relay_path_policy"]
    return {
        "schema_version": "relay_policy_bundle.v0",
        **bundle,
        "allowed_bind_hosts": loopback.get("allowed_bind_hosts", ["127.0.0.1", "localhost"]),
        "forbidden_bind_hosts": loopback.get("forbidden_bind_hosts", ["0.0.0.0", "::", "*", ""]),
        "allowed_routes": route.get("allowed_routes", list(ALLOWED_ROUTES)),
        "blocked_routes": route.get("blocked_routes", []),
        "allowed_methods": route.get("allowed_methods", ["GET"]),
        "forbidden_methods": route.get("forbidden_methods", sorted(FORBIDDEN_METHODS)),
        "allowed_render_profiles": render.get("allowed_render_profiles", sorted(ALLOWED_RENDER_PROFILES)),
        "required_semantic_fields": render.get(
            "required_semantic_fields",
            [
                "identity",
                "source posture",
                "evidence posture",
                "rights posture",
                "risk posture",
                "action posture",
                "limitations/no-claims",
            ],
        ),
        "allowed_output_roots": paths.get("allowed_output_roots", []),
        "forbidden_output_roots": paths.get("forbidden_output_roots", []),
    }


def load_relay_profile(path: str | Path) -> dict[str, Any]:
    return load_json(ensure_allowed_relay_input_path(path))


def validate_relay_profile(profile: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "relay_profile_id",
        "relay_profile_status",
        "relay_mode",
        "bind_policy",
        "host",
        "port_policy",
        "allowed_routes",
        "allowed_methods",
        "allowed_render_profiles",
        "snapshot_input_policy",
        "authentication_policy",
        "write_policy",
        "upload_policy",
        "download_policy",
        "action_execution_policy",
        "live_access_policy",
        "security_policy_ref",
        "limitations",
        "truth_boundary",
        "product_boundary",
        "no_goals",
        "notes",
    }
    for field in sorted(required):
        if field not in profile:
            errors.append(f"missing relay profile field: {field}")
    if profile.get("schema_version") != RELAY_PROFILE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {RELAY_PROFILE_SCHEMA_VERSION}")
    if profile.get("relay_mode") not in ALLOWED_RELAY_MODES:
        errors.append(f"relay_mode is not allowed: {profile.get('relay_mode')}")
    allowed_methods = {str(item).upper() for item in profile.get("allowed_methods", []) if isinstance(item, str)}
    if not allowed_methods.issubset(ALLOWED_METHODS):
        errors.append("allowed_methods must be GET-only for D-BUNDLE-02")
    allowed_routes = set((policy or {}).get("allowed_routes", ALLOWED_ROUTES))
    for route in profile.get("allowed_routes", []):
        if route not in allowed_routes:
            errors.append(f"relay route is not allowed: {route}")
    if profile.get("host") not in (policy or {}).get("allowed_bind_hosts", ["127.0.0.1", "localhost"]):
        errors.append(f"relay host is not loopback-only: {profile.get('host')}")
    errors.extend(detect_relay_boundary_violations(profile))
    return sorted(dict.fromkeys(errors))


def validate_old_browser_profile(profile: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if profile.get("schema_version") != OLD_BROWSER_PROFILE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {OLD_BROWSER_PROFILE_SCHEMA_VERSION}")
    if profile.get("javascript_required") is not False:
        errors.append("old browser profile must not require JavaScript")
    if profile.get("modern_browser_features_required") is not False:
        errors.append("old browser profile must not require modern browser features")
    if profile.get("css_dependency") not in {"none", "basic", "none_or_basic"}:
        errors.append("old browser profile css_dependency must be none, basic, or none_or_basic")
    return sorted(dict.fromkeys(errors))


def validate_terminal_profile(profile: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if profile.get("schema_version") != TERMINAL_PROFILE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {TERMINAL_PROFILE_SCHEMA_VERSION}")
    if int(profile.get("line_width", 0) or 0) <= 0:
        errors.append("terminal line_width must be positive")
    if profile.get("no_terminal_escape_required_by_default") is not True:
        errors.append("terminal profile must not require terminal escape sequences")
    return sorted(dict.fromkeys(errors))


def validate_native_fixture_endpoint(endpoint: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if endpoint.get("schema_version") != NATIVE_FIXTURE_ENDPOINT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {NATIVE_FIXTURE_ENDPOINT_SCHEMA_VERSION}")
    if endpoint.get("method") != "GET":
        errors.append("native fixture endpoints are GET-only")
    if endpoint.get("write_allowed") is not False:
        errors.append("native fixture endpoints must be read-only")
    if any(token in str(endpoint.get("endpoint_path", "")).casefold() for token in ("admin", "upload", "download", "execute", "install")):
        errors.append("native fixture endpoint exposes a forbidden route family")
    errors.extend(detect_relay_boundary_violations(endpoint))
    return sorted(dict.fromkeys(errors))


def relay_truth_boundary() -> dict[str, bool]:
    return {
        "relay_response_is_public_truth": False,
        "relay_accepts_evidence": False,
        "relay_accepts_candidate": False,
        "relay_mutates_public_index": False,
        "relay_mutates_master_index": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
        "relay_downloads_files": False,
        "relay_executes_actions": False,
        "live_source_access_enabled": False,
        "public_bind_allowed": False,
    }


def relay_product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_public_relay": False,
        "enabled_live_access": False,
        "enabled_downloads": False,
        "enabled_installers": False,
        "enabled_execution": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_site_dist": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }


def relay_no_claims() -> list[str]:
    return [
        "no public relay",
        "no public bind",
        "no hosting",
        "no live source access",
        "no downloads or uploads",
        "no action execution",
        "no accounts or telemetry",
        "no public or master index mutation",
        "no evidence, candidate, or public truth acceptance",
        "no rights clearance, malware safety, or verified installability",
    ]


def detect_relay_boundary_violations(value: Any) -> list[str]:
    violations: list[str] = []
    for path, key, child in iter_key_values(value):
        if key in FORBIDDEN_TRUE_FIELDS and child is True:
            violations.append(f"{path} must be false for D relay artifacts")
    return sorted(dict.fromkeys(violations))


def ensure_allowed_relay_output_path(path: str | Path, policy: Mapping[str, Any] | None = None, root: Path = REPO_ROOT) -> Path:
    resolved = resolve_path(path, root)
    if is_under_temp(resolved):
        return resolved
    rel = repo_relative_or_none(resolved, root)
    if rel is None:
        raise ValueError(f"refusing output outside repository approved roots or temp directory: {resolved}")
    rel_lower = rel.casefold().rstrip("/")
    forbidden = (policy or {}).get("forbidden_output_roots") or [
        "site/dist/",
        "site/dist/data/public_index/",
        "runtime/",
        "contracts/",
        "control/inventory/publication/",
        "master_index/",
        "data/master_index/",
        ".aide.local/",
        ".local/eureka/",
        ".cache/eureka/",
    ]
    for root_text in forbidden:
        candidate = str(root_text).casefold().rstrip("/")
        if rel_lower == candidate or rel_lower.startswith(candidate + "/"):
            raise ValueError(f"refusing forbidden output root: {root_text}")
    allowed = (policy or {}).get("allowed_output_roots") or [
        "control/audits/**/generated/",
        "examples/relay/",
        "explicit temp test directory",
    ]
    for root_text in allowed:
        candidate = str(root_text).casefold().rstrip("/")
        if "temp" in candidate:
            continue
        if candidate.endswith("/**/generated"):
            prefix = candidate[: -len("/**/generated")]
            if rel_lower.startswith(prefix + "/") and "/generated/" in rel_lower:
                return resolved
            continue
        if rel_lower == candidate or rel_lower.startswith(candidate + "/"):
            return resolved
    raise ValueError(f"refusing output outside approved relay roots: {rel}")


def ensure_allowed_relay_input_path(path: str | Path, root: Path = REPO_ROOT) -> Path:
    resolved = resolve_path(path, root)
    if not resolved.exists():
        raise ValueError(f"input path does not exist: {resolved}")
    if is_under_temp(resolved):
        return resolved
    rel = repo_relative_or_none(resolved, root)
    if rel and (
        rel == "examples/relay"
        or rel.startswith("examples/relay/")
        or rel == "examples/snapshots"
        or rel.startswith("examples/snapshots/")
        or rel == "examples/actions"
        or rel.startswith("examples/actions/")
        or rel == "control/audits"
        or rel.startswith("control/audits/")
    ):
        return resolved
    raise ValueError(f"refusing input outside approved relay/snapshot/example roots: {rel or resolved}")


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return payload


def stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}:{stable_hash(value)[:16]}"


def stable_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def resolve_path(path: str | Path, root: Path = REPO_ROOT) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def repo_relative_or_none(path: Path, root: Path = REPO_ROOT) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def is_under_temp(path: Path) -> bool:
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        path.resolve().relative_to(temp_root)
        return True
    except ValueError:
        return False


def iter_key_values(value: Any, prefix: str = "$") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            yield path, str(key), child
            yield from iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_key_values(child, f"{prefix}[{index}]")

