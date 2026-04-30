from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUEST_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_request.v0.json"
RESPONSE_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_response.v0.json"
ERROR_SCHEMA = REPO_ROOT / "contracts" / "api" / "error_response.v0.json"
ROUTES_PATH = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_routes.json"
LIVE_BACKEND_ROUTES = (
    REPO_ROOT / "control" / "inventory" / "publication" / "live_backend_routes.json"
)
LIVE_PROBE_GATEWAY = (
    REPO_ROOT / "control" / "inventory" / "publication" / "live_probe_gateway.json"
)
SURFACE_CAPABILITIES = (
    REPO_ROOT / "control" / "inventory" / "publication" / "surface_capabilities.json"
)
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_API_CONTRACT.md"
MODE_DOC = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md"
STATIC_SITE = REPO_ROOT / "site" / "dist"

REQUIRED_FORBIDDEN_PARAMETERS = {
    "index_path",
    "store_root",
    "run_store_root",
    "task_store_root",
    "memory_store_root",
    "local_path",
    "path",
    "url",
    "fetch_url",
    "download",
    "install",
    "upload",
    "user_file",
    "live_probe",
    "source_credentials",
}
REQUIRED_ERROR_CODES = {
    "bad_request",
    "query_required",
    "query_too_long",
    "limit_too_large",
    "unsupported_mode",
    "unsupported_profile",
    "unsupported_include",
    "forbidden_parameter",
    "local_paths_forbidden",
    "downloads_disabled",
    "installs_disabled",
    "uploads_disabled",
    "live_probes_disabled",
    "live_backend_unavailable",
    "rate_limited",
    "timeout",
    "not_found",
    "internal_error",
}
REQUIRED_ROUTES = {
    ("GET", "/search"),
    ("GET", "/api/v1/search"),
    ("GET", "/api/v1/query-plan"),
    ("GET", "/api/v1/status"),
    ("GET", "/api/v1/sources"),
    ("GET", "/api/v1/source/{source_id}"),
}
FUTURE_ROUTE_STATUSES = {"future_contract", "reserved", "planned", "deferred"}
LOCAL_RUNTIME_ROUTE_STATUSES = FUTURE_ROUTE_STATUSES | {"local_runtime_implemented"}
REQUIRED_DOC_PHRASES = {
    "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md": (
        "contract-first",
        "local_index_only",
        "Local Public Search Runtime v0",
        "local/prototype backend runtime only",
        "does not make public search hosted",
        "does not claim production API stability",
        "must not fan out to live Internet Archive, Google",
        "downloads_disabled",
        "installs_disabled",
        "uploads_disabled",
        "local_paths_forbidden",
        "live_probes_disabled",
        "Public Search Result Card Contract v0",
        "Public Search Safety / Abuse Guard v0",
    ),
    "docs/operations/PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md": (
        "local/prototype backend runtime only",
        "local_index_only",
        "live external calls",
        "local path search or private file ingestion",
        "downloads, executable mirrors, installer handoff",
        "Public Search Safety / Abuse Guard v0",
    ),
}
PROHIBITED_DOC_CLAIMS = (
    "public search api is live",
    "/api/v1/search is live",
    "users can search the hosted backend",
    "production api stability is guaranteed",
    "production-ready public search",
    "live probes are enabled",
    "downloads are enabled",
    "installs are enabled",
    "uploads are enabled",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Public Search API Contract v0 without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_search_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_search_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    request = _load_json(REQUEST_SCHEMA, errors)
    response = _load_json(RESPONSE_SCHEMA, errors)
    error = _load_json(ERROR_SCHEMA, errors)
    routes = _load_json(ROUTES_PATH, errors)
    live_backend_routes = _load_json(LIVE_BACKEND_ROUTES, errors)
    live_probe_gateway = _load_json(LIVE_PROBE_GATEWAY, errors)
    surface_capabilities = _load_json(SURFACE_CAPABILITIES, errors)

    _validate_request_schema(request, errors)
    _validate_response_schema(response, errors)
    _validate_error_schema(error, errors)
    route_summary = _validate_route_inventory(routes, errors)
    _validate_live_backend_alignment(live_backend_routes, errors)
    _validate_live_probe_disabled(live_probe_gateway, surface_capabilities, errors)
    _validate_docs(errors)
    _validate_static_site_claims(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_contract_validator_v0",
        "contract_id": "public_search_api_contract_v0",
        "request_schema": _rel(REQUEST_SCHEMA),
        "response_schema": _rel(RESPONSE_SCHEMA),
        "error_schema": _rel(ERROR_SCHEMA),
        "route_inventory": _rel(ROUTES_PATH),
        "first_allowed_mode": _first_mode(request),
        "runtime_routes_implemented": _mapping(routes).get("runtime_routes_implemented"),
        "registered_routes": route_summary["registered_routes"],
        "forbidden_parameters": sorted(_forbidden_parameters(request)),
        "required_error_codes": sorted(REQUIRED_ERROR_CODES),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_request_schema(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("contracts/api/search_request.v0.json: must be a JSON object.")
        return
    if payload.get("x-contract_id") != "eureka_public_search_request_v0":
        errors.append("search_request.v0.json: x-contract_id is unexpected.")
    if payload.get("x-status") != "contract_only":
        errors.append("search_request.v0.json: x-status must be contract_only.")
    required = payload.get("required")
    if required != ["q"]:
        errors.append("search_request.v0.json: q must be the only required field.")
    properties = _mapping(payload.get("properties"))
    q = _mapping(properties.get("q"))
    if q.get("type") != "string" or q.get("maxLength") != 160:
        errors.append("search_request.v0.json: q must be a string with maxLength 160.")
    limit = _mapping(properties.get("limit"))
    if limit.get("default") != 10 or limit.get("minimum") != 1 or limit.get("maximum") != 25:
        errors.append("search_request.v0.json: limit must default to 10 and be bounded 1..25.")
    profile_enum = _string_list(_mapping(properties.get("profile")).get("enum"))
    for profile in ("standard_web", "lite_html", "text", "api_client"):
        if profile not in profile_enum:
            errors.append(f"search_request.v0.json: profile enum missing {profile}.")
    mode_enum = _string_list(_mapping(properties.get("mode")).get("enum"))
    if mode_enum != ["local_index_only"]:
        errors.append("search_request.v0.json: mode enum must contain only local_index_only.")
    source_policy_enum = _string_list(_mapping(properties.get("source_policy")).get("enum"))
    if source_policy_enum != ["local_index_only"]:
        errors.append(
            "search_request.v0.json: source_policy enum must contain only local_index_only."
        )
    include_enum = _string_list(
        _mapping(_mapping(properties.get("include")).get("items")).get("enum")
    )
    for include in (
        "query_plan",
        "source_summaries",
        "evidence_summaries",
        "compatibility_summaries",
        "absence_summary",
    ):
        if include not in include_enum:
            errors.append(f"search_request.v0.json: include enum missing {include}.")
    forbidden = _forbidden_parameters(payload)
    missing = sorted(REQUIRED_FORBIDDEN_PARAMETERS - forbidden)
    if missing:
        errors.append(f"search_request.v0.json: forbidden parameter list missing {missing}.")
    for value in ("live_probe", "url", "download", "install", "upload"):
        if value in mode_enum or value in source_policy_enum:
            errors.append(f"search_request.v0.json: unsafe value {value!r} must not be a mode.")
    transport = _mapping(payload.get("x-transport"))
    if transport.get("get_query_parameters") is not True:
        errors.append("search_request.v0.json: GET query transport must be supported.")
    if transport.get("post_body_implemented_now") is not False:
        errors.append("search_request.v0.json: POST body must not be implemented now.")


def _validate_response_schema(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("contracts/api/search_response.v0.json: must be a JSON object.")
        return
    if payload.get("x-contract_id") != "eureka_public_search_response_v0":
        errors.append("search_response.v0.json: x-contract_id is unexpected.")
    required = set(_string_list(payload.get("required")))
    for field in (
        "ok",
        "schema_version",
        "contract_id",
        "mode",
        "query",
        "limits",
        "results",
        "checked_sources",
        "gaps",
        "warnings",
        "generated_by",
        "stability",
    ):
        if field not in required:
            errors.append(f"search_response.v0.json: required top-level field missing {field}.")
    properties = _mapping(payload.get("properties"))
    if _mapping(properties.get("mode")).get("const") != "local_index_only":
        errors.append("search_response.v0.json: mode must be const local_index_only.")
    defs = _mapping(payload.get("$defs"))
    result = _mapping(defs.get("result"))
    result_required = set(_string_list(result.get("required")))
    for field in (
        "result_id",
        "title",
        "record_kind",
        "source_id",
        "source_family",
        "public_target_ref",
        "result_lane",
        "user_cost",
        "compatibility",
        "evidence",
        "actions",
        "links",
        "limitations",
    ):
        if field not in result_required:
            errors.append(f"search_response.v0.json: result required field missing {field}.")
    lane_enum = _string_list(
        _mapping(_mapping(_mapping(result.get("properties")).get("result_lane"))).get("enum")
    )
    for lane in ("best_direct_answer", "absence_or_next_steps", "still_searching"):
        if lane not in lane_enum:
            errors.append(f"search_response.v0.json: result_lane enum missing {lane}.")
    checked_as = _string_list(
        _mapping(
            _mapping(_mapping(defs.get("checked_source")).get("properties")).get("checked_as")
        ).get("enum")
    )
    for value in ("local_index", "recorded_fixture", "static_summary", "not_checked"):
        if value not in checked_as:
            errors.append(f"search_response.v0.json: checked_as enum missing {value}.")
    prohibited = set(_string_list(payload.get("x-prohibited_result_fields")))
    for field in ("download_url", "install_url", "private_local_path", "raw_source_payload"):
        if field not in prohibited:
            errors.append(f"search_response.v0.json: prohibited result fields missing {field}.")
    stability = _mapping(payload.get("x-field_stability"))
    for key in ("stable_draft", "experimental", "volatile", "future"):
        if key not in stability:
            errors.append(f"search_response.v0.json: x-field_stability missing {key}.")


def _validate_error_schema(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("contracts/api/error_response.v0.json: must be a JSON object.")
        return
    if payload.get("x-contract_id") != "eureka_public_search_error_response_v0":
        errors.append("error_response.v0.json: x-contract_id is unexpected.")
    properties = _mapping(payload.get("properties"))
    error_properties = _mapping(_mapping(properties.get("error")).get("properties"))
    code_enum = set(_string_list(_mapping(error_properties.get("code")).get("enum")))
    missing = sorted(REQUIRED_ERROR_CODES - code_enum)
    if missing:
        errors.append(f"error_response.v0.json: missing required error codes {missing}.")
    extension_codes = set(_string_list(payload.get("x-required_error_codes")))
    missing_extension = sorted(REQUIRED_ERROR_CODES - extension_codes)
    if missing_extension:
        errors.append(
            f"error_response.v0.json: x-required_error_codes missing {missing_extension}."
        )
    required = set(_string_list(_mapping(properties.get("error")).get("required")))
    for field in ("code", "message", "status", "retryable"):
        if field not in required:
            errors.append(f"error_response.v0.json: error object missing required {field}.")


def _validate_route_inventory(payload: Any, errors: list[str]) -> dict[str, Any]:
    registered: list[str] = []
    if not isinstance(payload, Mapping):
        errors.append("public_search_routes.json: must be a JSON object.")
        return {"registered_routes": registered}
    expected = {
        "schema_version": "0.1.0",
        "registry_id": "eureka-public-search-routes",
        "contract_id": "public_search_api_contract_v0",
        "status": "local_runtime_implemented",
        "implemented_now": True,
        "runtime_routes_implemented": True,
        "first_allowed_mode": "local_index_only",
        "implementation_scope": "local_prototype_backend",
        "hosted_public_runtime_implemented": False,
        "static_handoff_implemented": False,
    }
    _expect_mapping_values("public_search_routes.json", payload, expected, errors)
    if _string_list(payload.get("contract_modes")) != ["local_index_only"]:
        errors.append("public_search_routes.json: contract_modes must contain only local_index_only.")
    if payload.get("runtime_modes_implemented") != ["local_index_only"]:
        errors.append("public_search_routes.json: runtime_modes_implemented must be [local_index_only].")
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("public_search_routes.json: routes must be a list.")
        return {"registered_routes": registered}
    by_key: dict[tuple[str, str], Mapping[str, Any]] = {}
    for index, route in enumerate(routes):
        if not isinstance(route, Mapping):
            errors.append(f"public_search_routes.json: routes[{index}] must be an object.")
            continue
        method = route.get("method")
        path = route.get("path_template")
        if isinstance(method, str) and isinstance(path, str):
            registered.append(f"{method} {path}")
            by_key[(method, path)] = route
        required_fields = {
            "method",
            "path_template",
            "status",
            "stability",
            "implemented_now",
            "requires_backend",
            "static_site_route",
            "allowed_modes",
            "live_probe_allowed",
            "downloads_allowed",
            "local_paths_allowed",
            "uploads_allowed",
            "auth_required",
            "rate_limit_required_before_public",
            "notes",
        }
        missing = sorted(required_fields - set(route))
        if missing:
            errors.append(f"public_search_routes.json: route {path or index} missing {missing}.")
        if route.get("status") not in LOCAL_RUNTIME_ROUTE_STATUSES:
            errors.append(f"public_search_routes.json: route {path} has unsupported status.")
        if route.get("status") == "local_runtime_implemented":
            if route.get("implemented_now") is not True:
                errors.append(f"public_search_routes.json: route {path}.implemented_now must be true.")
            if route.get("implementation_scope") != "local_prototype_backend":
                errors.append(f"public_search_routes.json: route {path}.implementation_scope must be local_prototype_backend.")
            if route.get("hosted_public_deployment") is not False:
                errors.append(f"public_search_routes.json: route {path}.hosted_public_deployment must be false.")
        elif route.get("implemented_now") is not False:
            errors.append(f"public_search_routes.json: route {path}.implemented_now must be false unless local runtime implemented.")
        for flag in ("static_site_route", "live_probe_allowed", "downloads_allowed", "local_paths_allowed", "uploads_allowed"):
            if route.get(flag) is not False:
                errors.append(f"public_search_routes.json: route {path}.{flag} must be false.")
        if route.get("requires_backend") is not True:
            errors.append(f"public_search_routes.json: route {path}.requires_backend must be true.")
        if route.get("auth_required") is not False:
            errors.append(f"public_search_routes.json: route {path}.auth_required must be false for v0.")
        if route.get("rate_limit_required_before_public") is not True:
            errors.append(
                f"public_search_routes.json: route {path}.rate_limit_required_before_public must be true."
            )
        if _string_list(route.get("allowed_modes")) != ["local_index_only"]:
            errors.append(f"public_search_routes.json: route {path} must allow only local_index_only.")
    missing_routes = sorted(
        f"{method} {path}" for method, path in REQUIRED_ROUTES - set(by_key)
    )
    if missing_routes:
        errors.append(f"public_search_routes.json: missing required routes {missing_routes}.")
    return {"registered_routes": sorted(registered)}


def _validate_live_backend_alignment(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_backend_routes.json: must be a JSON object.")
        return
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("live_backend_routes.json: routes must be a list.")
        return
    by_path = {
        route.get("path_template"): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("path_template"), str)
    }
    for path in ("/api/v1/search", "/api/v1/query-plan", "/api/v1/status", "/api/v1/sources"):
        route = by_path.get(path)
        if not isinstance(route, Mapping):
            errors.append(f"live_backend_routes.json: missing {path}.")
            continue
        if route.get("status") not in {"planned", "deferred", "blocked", "unsafe_for_public_alpha"}:
            errors.append(f"live_backend_routes.json: {path} must remain future/planned.")
        if route.get("requires_live_backend") is not True:
            errors.append(f"live_backend_routes.json: {path} must require a live backend.")
        if route.get("live_probe_related") is not False:
            errors.append(f"live_backend_routes.json: {path} must not be live_probe_related.")


def _validate_live_probe_disabled(gateway: Any, capabilities: Any, errors: list[str]) -> None:
    if not isinstance(gateway, Mapping):
        errors.append("live_probe_gateway.json: must be a JSON object.")
    else:
        expected = {
            "no_live_probes_implemented": True,
            "no_network_calls_performed": True,
            "enabled_by_default": False,
            "public_alpha_default_enabled": False,
        }
        _expect_mapping_values("live_probe_gateway.json", gateway, expected, errors)
        limits = _mapping(gateway.get("global_limits"))
        if limits.get("allow_arbitrary_url_fetch") is not False:
            errors.append("live_probe_gateway.json: arbitrary URL fetch must remain disabled.")
        if limits.get("allow_downloads") is not False:
            errors.append("live_probe_gateway.json: downloads must remain disabled.")
    if not isinstance(capabilities, Mapping):
        errors.append("surface_capabilities.json: must be a JSON object.")
        return
    by_id = {
        item.get("id"): item
        for item in capabilities.get("capabilities", [])
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    for capability_id in ("live_probe_gateway", "internet_archive_live_probe", "live_search"):
        item = by_id.get(capability_id)
        if not isinstance(item, Mapping):
            errors.append(f"surface_capabilities.json: missing {capability_id}.")
            continue
        if item.get("enabled_by_default") is not False:
            errors.append(f"surface_capabilities.json: {capability_id} must be disabled by default.")
        if item.get("status") in {"implemented", "static_demo", "recorded_fixture"}:
            errors.append(f"surface_capabilities.json: {capability_id} must not be implemented.")


def _validate_docs(errors: list[str]) -> None:
    docs = {
        "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md": REFERENCE_DOC,
        "docs/operations/PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md": MODE_DOC,
    }
    for relative, path in docs.items():
        if not path.is_file():
            errors.append(f"{relative}: required public search contract doc is missing.")
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.casefold()
        for phrase in REQUIRED_DOC_PHRASES.get(relative, ()):
            if phrase.casefold() not in lowered:
                errors.append(f"{relative}: missing phrase {phrase!r}.")
        for claim in PROHIBITED_DOC_CLAIMS:
            if claim in lowered:
                errors.append(f"{relative}: prohibited live/production claim {claim!r}.")


def _validate_static_site_claims(errors: list[str]) -> None:
    if not STATIC_SITE.exists():
        errors.append("site/dist: static site artifact is missing.")
        return
    for path in sorted(STATIC_SITE.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".html", ".txt", ".json"}:
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for claim in PROHIBITED_DOC_CLAIMS:
            if claim in text:
                errors.append(f"{_rel(path)}: prohibited public search live/production claim {claim!r}.")


def _first_mode(payload: Any) -> str | None:
    if not isinstance(payload, Mapping):
        return None
    enum = _string_list(
        _mapping(_mapping(payload.get("properties")).get("mode")).get("enum")
    )
    return enum[0] if enum else None


def _forbidden_parameters(payload: Any) -> set[str]:
    if not isinstance(payload, Mapping):
        return set()
    return set(_string_list(payload.get("x-forbidden_parameters")))


def _expect_mapping_values(
    label: str, payload: Mapping[str, Any], expected: Mapping[str, Any], errors: list[str]
) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{label}: {key} must be {value!r}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: JSON file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public search contract validation",
        f"status: {report['status']}",
        f"contract_id: {report.get('contract_id')}",
        f"first_allowed_mode: {report.get('first_allowed_mode')}",
        f"runtime_routes_implemented: {report.get('runtime_routes_implemented')}",
        f"registered_routes: {len(report.get('registered_routes', []))}",
        f"forbidden_parameters: {len(report.get('forbidden_parameters', []))}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
