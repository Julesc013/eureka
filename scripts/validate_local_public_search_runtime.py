from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SEARCH_MODULE = REPO_ROOT / "runtime" / "gateway" / "public_api" / "public_search.py"
WEB_SERVER = REPO_ROOT / "surfaces" / "web" / "server" / "workbench_server.py"
API_ROUTES = REPO_ROOT / "surfaces" / "web" / "server" / "api_routes.py"
HTML_RENDERER = REPO_ROOT / "surfaces" / "web" / "workbench" / "render_public_search.py"
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "public_search_smoke.py"
ROUTES = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_routes.json"
SAFETY = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_safety.json"
PUBLIC_ALPHA_ROUTES = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
API_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_API_CONTRACT.md"
MODE_DOC = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md"
SAFETY_DOC = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md"
READINESS_DOC = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md"

REQUIRED_ROUTES = {
    "/search",
    "/api/v1/status",
    "/api/v1/search",
    "/api/v1/query-plan",
    "/api/v1/sources",
    "/api/v1/source/{source_id}",
}
PROHIBITED_RUNTIME_TOKENS = {
    "requests.",
    "urllib.request.urlopen",
    "InternetArchive",
    "google",
    "download_url",
    "install_url",
}
REQUIRED_DOC_PHRASES = {
    API_DOC: (
        "Local Public Search Runtime v0",
        "local/prototype backend runtime only",
        "does not make public search hosted",
    ),
    MODE_DOC: (
        "Local Public Search Runtime v0",
        "local_index_only",
        "no live probes",
        "no downloads",
    ),
    SAFETY_DOC: (
        "Local Public Search Runtime v0",
        "does not add rate-limit middleware",
        "does not enable live probes",
    ),
    READINESS_DOC: (
        "Local Public Search Runtime v0",
        "hosted_public_runtime_approved: false",
        "static_search_handoff_approved: false",
    ),
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Local Public Search Runtime v0 without external network calls."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_local_public_search_runtime()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_local_public_search_runtime() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    routes = _load_json(ROUTES, errors)
    safety = _load_json(SAFETY, errors)
    public_alpha = _load_json(PUBLIC_ALPHA_ROUTES, errors)

    _validate_files(errors)
    _validate_public_search_module(errors)
    _validate_route_inventory(routes, errors)
    _validate_safety_inventory(safety, errors)
    _validate_public_alpha_inventory(public_alpha, errors)
    _validate_docs(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "local_public_search_runtime_validator_v0",
        "runtime_scope": "local_prototype_backend",
        "mode": "local_index_only",
        "routes": sorted(REQUIRED_ROUTES),
        "hosted_public_deployment": False,
        "static_search_handoff": False,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_files(errors: list[str]) -> None:
    for path in (
        PUBLIC_SEARCH_MODULE,
        WEB_SERVER,
        API_ROUTES,
        HTML_RENDERER,
        SMOKE_SCRIPT,
        REPO_ROOT / "contracts" / "api" / "search_request.v0.json",
        REPO_ROOT / "contracts" / "api" / "search_response.v0.json",
        REPO_ROOT / "contracts" / "api" / "error_response.v0.json",
        REPO_ROOT / "contracts" / "api" / "search_result_card.v0.json",
    ):
        if not path.is_file():
            errors.append(f"{_rel(path)}: missing required local public-search runtime file.")


def _validate_public_search_module(errors: list[str]) -> None:
    if not PUBLIC_SEARCH_MODULE.is_file():
        return
    text = PUBLIC_SEARCH_MODULE.read_text(encoding="utf-8")
    for token in (
        "class PublicSearchPublicApi",
        "def validate_public_search_query",
        "public_search_error_response",
        "public_result_card_from_index_record",
        "local_index_only",
        "live_probes_disabled",
        "downloads_disabled",
        "local_paths_forbidden",
    ):
        if token not in text:
            errors.append(f"{_rel(PUBLIC_SEARCH_MODULE)}: missing token {token!r}.")
    for token in PROHIBITED_RUNTIME_TOKENS:
        if token in text:
            errors.append(f"{_rel(PUBLIC_SEARCH_MODULE)}: prohibited runtime token {token!r}.")
    if "index_path" in text and "FORBIDDEN_PARAMETERS" not in text:
        errors.append(f"{_rel(PUBLIC_SEARCH_MODULE)}: index_path must appear only as a forbidden parameter.")


def _validate_route_inventory(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_search_routes.json: must be a JSON object.")
        return
    expected = {
        "status": "local_runtime_implemented",
        "implemented_now": True,
        "runtime_routes_implemented": True,
        "first_allowed_mode": "local_index_only",
        "implementation_scope": "local_prototype_backend",
        "hosted_public_runtime_implemented": False,
        "static_handoff_implemented": False,
    }
    _expect_values("public_search_routes.json", payload, expected, errors)
    if payload.get("runtime_modes_implemented") != ["local_index_only"]:
        errors.append("public_search_routes.json: runtime_modes_implemented must be [local_index_only].")
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("public_search_routes.json: routes must be a list.")
        return
    by_path = {
        route.get("path_template"): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("path_template"), str)
    }
    missing = sorted(REQUIRED_ROUTES - set(by_path))
    if missing:
        errors.append(f"public_search_routes.json: missing runtime routes {missing}.")
    for path in REQUIRED_ROUTES & set(by_path):
        route = _mapping(by_path[path])
        expected_route = {
            "status": "local_runtime_implemented",
            "implemented_now": True,
            "implementation_scope": "local_prototype_backend",
            "hosted_public_deployment": False,
            "live_probe_allowed": False,
            "downloads_allowed": False,
            "local_paths_allowed": False,
            "uploads_allowed": False,
            "auth_required": False,
            "rate_limit_required_before_public": True,
        }
        _expect_values(f"public_search_routes.json route {path}", route, expected_route, errors)
        if route.get("allowed_modes") != ["local_index_only"]:
            errors.append(f"public_search_routes.json route {path}: allowed_modes must be local_index_only only.")


def _validate_safety_inventory(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_search_safety.json: must be a JSON object.")
        return
    expected = {
        "status": "local_runtime_guard_active",
        "no_runtime_implemented": False,
        "local_public_search_runtime_implemented": True,
        "hosted_public_search_runtime_implemented": False,
        "no_hosted_public_search_live": True,
        "first_allowed_mode": "local_index_only",
    }
    _expect_values("public_search_safety.json", payload, expected, errors)
    if payload.get("allowed_modes") != ["local_index_only"]:
        errors.append("public_search_safety.json: allowed_modes must be local_index_only only.")
    for mode in ("live_probe", "live_federated", "arbitrary_url_fetch", "local_path_search", "upload_search", "download_or_install"):
        if mode not in _string_list(payload.get("disabled_modes")):
            errors.append(f"public_search_safety.json: disabled_modes missing {mode}.")
    required_forbidden = {
        "index_path",
        "store_root",
        "local_path",
        "path",
        "url",
        "fetch_url",
        "download",
        "install",
        "execute",
        "upload",
        "source_credentials",
        "auth_token",
        "api_key",
        "live_probe",
    }
    missing = sorted(required_forbidden - set(_string_list(payload.get("forbidden_parameters"))))
    if missing:
        errors.append(f"public_search_safety.json: forbidden_parameters missing {missing}.")
    if _mapping(payload.get("rate_limit_policy")).get("runtime_middleware_implemented") is not False:
        errors.append("public_search_safety.json: runtime rate-limit middleware must remain unimplemented.")
    if _mapping(payload.get("logging_privacy_policy")).get("telemetry_implemented") is not False:
        errors.append("public_search_safety.json: telemetry runtime must remain unimplemented.")


def _validate_public_alpha_inventory(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_alpha_routes.json: must be a JSON object.")
        return
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("public_alpha_routes.json: routes must be a list.")
        return
    by_path = {
        route.get("route_pattern"): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("route_pattern"), str)
    }
    for path in REQUIRED_ROUTES:
        route = _mapping(by_path.get(path))
        if not route:
            errors.append(f"public_alpha_routes.json: missing {path}.")
            continue
        if route.get("classification") != "safe_public_alpha":
            errors.append(f"public_alpha_routes.json: {path} must be safe_public_alpha.")
        if route.get("local_path_parameters") != []:
            errors.append(f"public_alpha_routes.json: {path} must list no local path parameters.")
        behavior = _mapping(route.get("mode_behavior"))
        if behavior.get("public_alpha") != "allowed":
            errors.append(f"public_alpha_routes.json: {path} must be allowed in public_alpha.")


def _validate_docs(errors: list[str]) -> None:
    for path, phrases in REQUIRED_DOC_PHRASES.items():
        if not path.is_file():
            errors.append(f"{_rel(path)}: missing.")
            continue
        text = path.read_text(encoding="utf-8")
        folded = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in folded:
                errors.append(f"{_rel(path)}: missing phrase {phrase!r}.")
        for prohibited in (
            "public search is hosted",
            "production api stability is guaranteed",
            "live probes are enabled",
            "downloads are enabled",
            "uploads are enabled",
        ):
            if prohibited in folded:
                errors.append(f"{_rel(path)}: contains prohibited claim {prohibited!r}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
    return None


def _expect_values(
    label: str,
    payload: Mapping[str, Any],
    expected: Mapping[str, Any],
    errors: list[str],
) -> None:
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            errors.append(f"{label}: {key} must be {expected_value!r}.")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Local Public Search Runtime validation",
        f"status: {report['status']}",
        f"runtime_scope: {report['runtime_scope']}",
        f"mode: {report['mode']}",
        f"routes: {len(report['routes'])}",
        f"hosted_public_deployment: {report['hosted_public_deployment']}",
        f"static_search_handoff: {report['static_search_handoff']}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
