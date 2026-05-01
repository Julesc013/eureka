from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "site/dist"

HANDOFF_PATH = PUBLICATION_DIR / "live_backend_handoff.json"
ROUTES_PATH = PUBLICATION_DIR / "live_backend_routes.json"
CAPABILITIES_PATH = PUBLICATION_DIR / "surface_capabilities.json"
HANDOFF_DOC = REPO_ROOT / "docs" / "reference" / "LIVE_BACKEND_HANDOFF_CONTRACT.md"
ERROR_DOC = REPO_ROOT / "docs" / "reference" / "LIVE_BACKEND_ERROR_ENVELOPE.md"
ARCH_DOC = REPO_ROOT / "docs" / "architecture" / "LIVE_BACKEND_HANDOFF.md"

REQUIRED_ENDPOINTS = {
    "/healthz",
    "/status",
    "/api/v1/status",
    "/api/v1/search",
    "/api/v1/query-plan",
    "/api/v1/sources",
    "/api/v1/source/{source_id}",
    "/api/v1/evidence/{evidence_id}",
    "/api/v1/object/{object_id}",
    "/api/v1/result/{result_id}",
    "/api/v1/absence",
    "/api/v1/absence/{need_id}",
    "/api/v1/compare",
    "/api/v1/capabilities",
    "/api/v1/live-probe",
}
ALLOWED_TOP_LEVEL_ENDPOINTS = {
    "/healthz",
    "/status",
}
REQUIRED_CAPABILITIES = {
    "static_site",
    "generated_public_data",
    "lite_surface",
    "text_surface",
    "files_surface",
    "demo_snapshots",
    "public_alpha_wrapper",
    "live_backend",
    "live_search",
    "live_probe_gateway",
    "internet_archive_live_probe",
    "external_baseline_observations",
    "native_clients",
    "rust_runtime",
}
DISABLED_LIVE_CAPABILITIES = {
    "live_backend",
    "live_search",
    "live_probe_gateway",
    "internet_archive_live_probe",
}
REQUIRED_ERROR_CODES = {
    "live_backend_unavailable",
    "capability_disabled",
    "live_probes_disabled",
    "route_not_public_alpha_safe",
    "rate_limited",
    "source_disabled",
    "source_timeout",
    "bad_request",
    "not_found",
    "internal_error",
}
FUTURE_ROUTE_STATUSES = {
    "planned",
    "deferred",
    "blocked",
    "unsafe_for_public_alpha",
    "placeholder",
}
COMMON_BACKEND_DEPLOYMENT_CONFIG_PATHS = (
    "Procfile",
    "Dockerfile",
    "docker-compose.yml",
    "render.yaml",
    "fly.toml",
    "vercel.json",
    "netlify.toml",
    "wrangler.toml",
)
PROHIBITED_POSITIVE_PATTERNS = (
    re.compile(r"\blive backend (is )?(available|enabled|running|deployed|exists)\b", re.IGNORECASE),
    re.compile(r"\b/api/v1 (is )?(live|available|enabled|stable)\b", re.IGNORECASE),
    re.compile(r"\bpublic api (is )?(stable|production)\b", re.IGNORECASE),
    re.compile(r"\bproduction api\b", re.IGNORECASE),
    re.compile(r"\blive probes (are )?enabled\b", re.IGNORECASE),
    re.compile(r"\binternet archive live probe (is )?enabled\b", re.IGNORECASE),
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"href", "src", "action"} and value:
                self.references.append((key.lower(), value))


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka's future live backend handoff contract without network access."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_live_backend_handoff(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_live_backend_handoff(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    publication_dir = repo_root / "control" / "inventory" / "publication"
    site_root = repo_root / "site" / "dist"
    errors: list[str] = []
    warnings: list[str] = []

    handoff = _load_json(publication_dir / "live_backend_handoff.json", repo_root, errors)
    routes = _load_json(publication_dir / "live_backend_routes.json", repo_root, errors)
    capabilities = _load_json(publication_dir / "surface_capabilities.json", repo_root, errors)

    _validate_handoff(handoff, errors)
    route_summary = _validate_routes(routes, errors)
    capability_summary = _validate_capabilities(capabilities, errors)
    api_v1_links = _validate_static_pages(site_root, repo_root, errors)
    _validate_docs(repo_root, errors)
    _validate_no_backend_deployment_config(repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "live_backend_handoff_validator_v0",
        "repo_root": str(repo_root),
        "handoff_inventory": _rel(publication_dir / "live_backend_handoff.json", repo_root),
        "route_inventory": _rel(publication_dir / "live_backend_routes.json", repo_root),
        "capability_inventory": _rel(publication_dir / "surface_capabilities.json", repo_root),
        "reserved_endpoints": sorted(REQUIRED_ENDPOINTS),
        "registered_endpoints": route_summary["registered_endpoints"],
        "disabled_live_capabilities": capability_summary["disabled_live_capabilities"],
        "api_v1_static_links": api_v1_links,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_handoff(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_backend_handoff.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "handoff_id": "eureka-live-backend-handoff",
        "status": "planned",
        "stability": "experimental",
        "no_live_backend_implemented": True,
        "no_deployment_performed": True,
        "static_site_current": True,
        "public_alpha_backend_future": True,
        "cors_policy_status": "unresolved",
        "auth_policy_status": "unresolved",
        "rate_limit_policy_status": "unresolved",
        "live_probe_dependency_status": "requires_live_probe_gateway_contract_v0",
        "created_by_slice": "live_backend_handoff_contract_v0",
    }
    _expect_mapping_values("live_backend_handoff.json", payload, expected, errors)
    endpoints = set(_string_list(payload.get("endpoint_prefixes_reserved")))
    missing = sorted(REQUIRED_ENDPOINTS - endpoints)
    if missing:
        errors.append(f"live_backend_handoff.json: missing reserved endpoints {missing}.")
    required_flags = set(_string_list(payload.get("capability_flags_required")))
    for flag in DISABLED_LIVE_CAPABILITIES:
        if flag not in required_flags:
            errors.append(f"live_backend_handoff.json: capability_flags_required missing {flag}.")
    policy = payload.get("static_to_live_link_policy")
    if not isinstance(policy, Mapping):
        errors.append("live_backend_handoff.json: static_to_live_link_policy must be an object.")
    else:
        for flag in (
            "static_pages_must_not_link_as_live",
            "static_pages_must_check_capability_flags_first",
            "static_pages_must_label_api_v1_as_future_reserved",
            "static_demo_routes_are_not_live_api_routes",
        ):
            if policy.get(flag) is not True:
                errors.append(f"live_backend_handoff.json: static_to_live_link_policy.{flag} must be true.")
    envelope = payload.get("error_envelope")
    if not isinstance(envelope, Mapping):
        errors.append("live_backend_handoff.json: error_envelope must be an object.")
    else:
        codes = set(_string_list(envelope.get("required_error_codes")))
        missing_codes = sorted(REQUIRED_ERROR_CODES - codes)
        if missing_codes:
            errors.append(f"live_backend_handoff.json: error_envelope missing codes {missing_codes}.")


def _validate_routes(payload: Any, errors: list[str]) -> dict[str, Any]:
    registered: list[str] = []
    if not isinstance(payload, Mapping):
        errors.append("live_backend_routes.json: must be a JSON object.")
        return {"registered_endpoints": registered}
    expected = {
        "schema_version": "0.1.0",
        "registry_id": "eureka-live-backend-routes",
        "status": "planned",
        "stability": "experimental",
        "route_prefix": "/api/v1",
        "no_live_backend_implemented": True,
        "current_local_api_prefix": "/api",
        "current_local_api_public_contract": False,
    }
    _expect_mapping_values("live_backend_routes.json", payload, expected, errors)
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("live_backend_routes.json: routes must be a list.")
        return {"registered_endpoints": registered}
    by_path: dict[str, Mapping[str, Any]] = {}
    for index, route in enumerate(routes):
        if not isinstance(route, Mapping):
            errors.append(f"live_backend_routes.json: routes[{index}] must be an object.")
            continue
        missing = {
            "path_template",
            "method",
            "status",
            "stability",
            "current_implementation_status",
            "static_handoff_allowed",
            "requires_live_backend",
            "requires_auth",
            "live_probe_related",
            "public_alpha_allowed",
            "expected_response_kind",
            "notes",
        } - set(route)
        if missing:
            errors.append(f"live_backend_routes.json: route {route.get('path_template', index)} missing {sorted(missing)}.")
        path = route.get("path_template")
        if isinstance(path, str):
            registered.append(path)
            by_path[path] = route
            if path not in ALLOWED_TOP_LEVEL_ENDPOINTS and not path.startswith("/api/v1/") and path != "/api/v1":
                errors.append(f"live_backend_routes.json: route {path} must use /api/v1.")
        if route.get("status") not in FUTURE_ROUTE_STATUSES:
            errors.append(f"live_backend_routes.json: route {path} must remain future/deferred/blocked, not {route.get('status')!r}.")
        if route.get("requires_live_backend") is not True:
            errors.append(f"live_backend_routes.json: route {path} must require a live backend.")
        if "hosted" not in str(route.get("current_implementation_status", "")) and "not_implemented" not in str(route.get("current_implementation_status", "")):
            errors.append(f"live_backend_routes.json: route {path} must be marked not currently hosted/implemented.")
    missing = sorted(REQUIRED_ENDPOINTS - set(by_path))
    if missing:
        errors.append(f"live_backend_routes.json: missing required endpoints {missing}.")
    live_probe = by_path.get("/api/v1/live-probe")
    if isinstance(live_probe, Mapping):
        if live_probe.get("status") not in {"blocked", "deferred", "unsafe_for_public_alpha"}:
            errors.append("live_backend_routes.json: /api/v1/live-probe must be blocked/deferred.")
        if live_probe.get("public_alpha_allowed") is not False:
            errors.append("live_backend_routes.json: /api/v1/live-probe must not be public-alpha allowed.")
        if live_probe.get("static_handoff_allowed") is not False:
            errors.append("live_backend_routes.json: /api/v1/live-probe must not allow static handoff.")
        if live_probe.get("live_probe_related") is not True:
            errors.append("live_backend_routes.json: /api/v1/live-probe must be live_probe_related.")
    return {"registered_endpoints": sorted(registered)}


def _validate_capabilities(payload: Any, errors: list[str]) -> dict[str, Any]:
    disabled: list[str] = []
    if not isinstance(payload, Mapping):
        errors.append("surface_capabilities.json: must be a JSON object.")
        return {"disabled_live_capabilities": disabled}
    if payload.get("schema_version") != "0.1.0":
        errors.append("surface_capabilities.json: schema_version must be 0.1.0.")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list):
        errors.append("surface_capabilities.json: capabilities must be a list.")
        return {"disabled_live_capabilities": disabled}
    by_id = {
        item.get("id"): item
        for item in capabilities
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    missing = sorted(REQUIRED_CAPABILITIES - set(by_id))
    if missing:
        errors.append(f"surface_capabilities.json: missing capabilities {missing}.")
    for capability_id in ("static_site", "generated_public_data"):
        item = by_id.get(capability_id)
        if isinstance(item, Mapping):
            if item.get("status") != "implemented":
                errors.append(f"surface_capabilities.json: {capability_id}.status must be implemented.")
            if item.get("enabled_by_default") is not True:
                errors.append(f"surface_capabilities.json: {capability_id}.enabled_by_default must be true.")
            if item.get("requires_backend") is not False:
                errors.append(f"surface_capabilities.json: {capability_id}.requires_backend must be false.")
    for capability_id in DISABLED_LIVE_CAPABILITIES:
        item = by_id.get(capability_id)
        if not isinstance(item, Mapping):
            continue
        if item.get("enabled_by_default") is not False:
            errors.append(f"surface_capabilities.json: {capability_id}.enabled_by_default must be false.")
        if item.get("requires_backend") is not True:
            errors.append(f"surface_capabilities.json: {capability_id}.requires_backend must be true.")
        if item.get("status") in {"implemented", "static_demo", "recorded_fixture"}:
            errors.append(f"surface_capabilities.json: {capability_id}.status must remain future/deferred/blocked.")
        disabled.append(capability_id)
    return {"disabled_live_capabilities": sorted(disabled)}


def _validate_static_pages(site_root: Path, repo_root: Path, errors: list[str]) -> list[str]:
    hits: list[str] = []
    if not site_root.exists():
        errors.append("site/dist: static artifact is missing.")
        return hits
    for path in sorted(site_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".html", ".txt", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".html":
            parser = LinkParser()
            parser.feed(text)
            for attr, value in parser.references:
                if "/api/v1" in value:
                    hit = f"{_rel(path, repo_root)}: {attr}={value!r}"
                    hits.append(hit)
                    errors.append(f"{hit}: static artifact must not link to /api/v1 as live.")
        _validate_no_positive_live_claims(path, text, repo_root, errors)
    return hits


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    docs = {
        "handoff": repo_root / "docs" / "reference" / "LIVE_BACKEND_HANDOFF_CONTRACT.md",
        "error": repo_root / "docs" / "reference" / "LIVE_BACKEND_ERROR_ENVELOPE.md",
        "architecture": repo_root / "docs" / "architecture" / "LIVE_BACKEND_HANDOFF.md",
    }
    for label, path in docs.items():
        if not path.exists():
            errors.append(f"{_rel(path, repo_root)}: required {label} doc is missing.")
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.casefold()
        for phrase in ("not a production api", "/api/v1", "not implemented"):
            if phrase not in lowered:
                errors.append(f"{_rel(path, repo_root)}: missing handoff phrase {phrase!r}.")
    error_text = docs["error"].read_text(encoding="utf-8") if docs["error"].exists() else ""
    for code in sorted(REQUIRED_ERROR_CODES):
        if code not in error_text:
            errors.append(f"docs/reference/LIVE_BACKEND_ERROR_ENVELOPE.md: missing error code {code}.")
    wrapper = repo_root / "docs" / "operations" / "PUBLIC_ALPHA_WRAPPER.md"
    safe_mode = repo_root / "docs" / "operations" / "PUBLIC_ALPHA_SAFE_MODE.md"
    for path in (wrapper, safe_mode):
        if path.exists():
            lowered = path.read_text(encoding="utf-8").casefold()
            if "/api/v1" in lowered and "future" not in lowered:
                errors.append(f"{_rel(path, repo_root)}: /api/v1 reference must be future/reserved.")


def _validate_no_backend_deployment_config(repo_root: Path, errors: list[str]) -> None:
    for relative in COMMON_BACKEND_DEPLOYMENT_CONFIG_PATHS:
        path = repo_root / relative
        if path.exists():
            errors.append(f"{relative}: backend/provider deployment config must not be added by this task.")


def _validate_no_positive_live_claims(path: Path, text: str, repo_root: Path, errors: list[str]) -> None:
    for pattern in PROHIBITED_POSITIVE_PATTERNS:
        for match in pattern.finditer(text):
            before = text[max(0, match.start() - 160) : match.start()].casefold()
            context = text[max(0, match.start() - 32) : match.end() + 32].casefold()
            if "no " in before[-40:] or "not " in before[-40:] or "does not " in before[-96:]:
                continue
            if "future" in before[-80:] or "reserved" in before[-80:]:
                continue
            if "must not" in context or "not a" in context or "not live" in context:
                continue
            errors.append(f"{_rel(path, repo_root)}: prohibited positive live-backend claim: {match.group(0)!r}.")


def _expect_mapping_values(
    label: str, payload: Mapping[str, Any], expected: Mapping[str, Any], errors: list[str]
) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{label}.{key} must be {value!r}.")


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {exc}.")
    return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Live backend handoff validation",
        f"status: {report['status']}",
        f"reserved_endpoints: {len(report['reserved_endpoints'])}",
        f"registered_endpoints: {len(report['registered_endpoints'])}",
        f"disabled_live_capabilities: {len(report['disabled_live_capabilities'])}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
