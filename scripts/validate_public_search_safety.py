from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SAFETY = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_safety.json"
REQUEST_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_request.v0.json"
ERROR_SCHEMA = REPO_ROOT / "contracts" / "api" / "error_response.v0.json"
ROUTES = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_routes.json"
LIVE_PROBE_GATEWAY = (
    REPO_ROOT / "control" / "inventory" / "publication" / "live_probe_gateway.json"
)
PUBLIC_ALPHA_SAFE_MODE = REPO_ROOT / "docs" / "operations" / "PUBLIC_ALPHA_SAFE_MODE.md"
SAFETY_DOC = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md"
READINESS_DOC = (
    REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md"
)
API_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_API_CONTRACT.md"
CARD_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md"

REQUIRED_ALLOWED_MODES = {"local_index_only"}
REQUIRED_DISABLED_MODES = {
    "live_probe",
    "live_federated",
    "arbitrary_url_fetch",
    "local_path_search",
    "upload_search",
    "download_or_install",
}
REQUIRED_FORBIDDEN_PARAMETERS = {
    "index_path",
    "store_root",
    "run_store_root",
    "task_store_root",
    "memory_store_root",
    "local_path",
    "path",
    "file_path",
    "directory",
    "root",
    "url",
    "fetch_url",
    "crawl_url",
    "source_url",
    "download",
    "install",
    "execute",
    "upload",
    "user_file",
    "source_credentials",
    "auth_token",
    "api_key",
    "live_probe",
    "live_source",
    "network",
    "arbitrary_source",
}
REQUIRED_FORBIDDEN_BEHAVIORS = {
    "arbitrary_url_fetching",
    "live_external_source_fanout",
    "google_scraping",
    "internet_archive_live_calls",
    "wayback_live_calls",
    "github_live_calls",
    "package_registry_live_calls",
    "local_filesystem_search",
    "caller_provided_index_path",
    "caller_provided_store_root",
    "downloads",
    "installs",
    "executable_launch",
    "uploads",
    "account_or_session_requirement",
    "telemetry_by_default",
    "private_path_leakage",
    "credential_submission",
    "raw_source_payload_return",
    "unbounded_query_or_result_behavior",
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
}
REQUIRED_OPERATOR_FLAGS = {
    "EUREKA_PUBLIC_SEARCH_MODE",
    "EUREKA_ALLOW_LIVE_PROBES",
    "EUREKA_ALLOW_DOWNLOADS",
    "EUREKA_ALLOW_INSTALLS",
    "EUREKA_ALLOW_LOCAL_PATHS",
    "EUREKA_ALLOW_USER_UPLOADS",
    "EUREKA_ALLOW_TELEMETRY",
    "EUREKA_MAX_QUERY_LEN",
    "EUREKA_MAX_RESULTS",
    "EUREKA_SEARCH_TIMEOUT_MS",
    "EUREKA_PUBLIC_SEARCH_ENABLED",
    "EUREKA_OPERATOR_KILL_SWITCH",
}
FUTURE_ROUTE_STATUSES = {"future_contract", "reserved", "planned", "deferred", "local_runtime_implemented"}
REQUIRED_DOC_PHRASES = {
    SAFETY_DOC: (
        "Local Public Search Runtime v0",
        "local_index_only",
        "maximum query length: 160",
        "maximum result limit: 25",
        "maximum runtime target: 3000 ms",
        "forbidden parameters",
        "forbidden behaviors",
        "telemetry is not implemented and defaults off",
        "EUREKA_OPERATOR_KILL_SWITCH=1",
        "Public Alpha Safe Mode remains non-production",
        "GitHub Pages remains static-only",
        "does not add rate-limit middleware",
        "does not enable live probes",
    ),
    READINESS_DOC: (
        "Local Public Search Runtime v0",
        "hosted_public_runtime_approved: false",
        "Static handoff is implemented by Public Search Static Handoff v0",
        "production_claim_allowed: false",
    ),
    API_DOC: (
        "Public Search Safety / Abuse Guard v0",
        "runtime readiness checklist",
    ),
    CARD_DOC: (
        "Public Search Safety / Abuse Guard v0",
        "runtime readiness checklist",
    ),
}
PROHIBITED_DOC_CLAIMS = (
    "public search is live",
    "/api/v1/search is live",
    "public search safety is production-complete",
    "production api stability is guaranteed",
    "production-ready public search",
    "live probes are enabled",
    "downloads are enabled",
    "installs are enabled",
    "uploads are enabled",
    "telemetry is enabled",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Public Search Safety / Abuse Guard v0 without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_search_safety()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_search_safety() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    safety = _load_json(SAFETY, errors)
    request = _load_json(REQUEST_SCHEMA, errors)
    error_schema = _load_json(ERROR_SCHEMA, errors)
    routes = _load_json(ROUTES, errors)
    live_probe_gateway = _load_json(LIVE_PROBE_GATEWAY, errors)

    _validate_safety_inventory(safety, errors)
    _validate_request_alignment(request, safety, errors)
    _validate_error_schema(error_schema, safety, errors)
    _validate_routes(routes, errors)
    _validate_live_probe_gateway(live_probe_gateway, errors)
    _validate_docs(errors)

    safety_map = _mapping(safety)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_safety_validator_v0",
        "safety_policy_id": safety_map.get("safety_policy_id"),
        "first_allowed_mode": safety_map.get("first_allowed_mode"),
        "allowed_modes": _string_list(safety_map.get("allowed_modes")),
        "disabled_modes": sorted(_string_list(safety_map.get("disabled_modes"))),
        "max_query_length": _mapping(safety_map.get("request_limits")).get("max_query_length"),
        "max_result_limit": _mapping(safety_map.get("result_limits")).get("max_result_limit"),
        "max_runtime_ms_contract": _mapping(safety_map.get("timeout_policy")).get(
            "max_runtime_ms_contract"
        ),
        "telemetry_default": _mapping(safety_map.get("logging_privacy_policy")).get(
            "telemetry_default"
        ),
        "runtime_readiness_checklist": safety_map.get("runtime_readiness_checklist"),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_safety_inventory(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_search_safety.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "safety_policy_id": "eureka-public-search-safety-abuse-guard-v0",
        "status": "local_runtime_guard_active",
        "stability": "experimental",
        "no_runtime_implemented": False,
        "local_public_search_runtime_implemented": True,
        "hosted_public_search_runtime_implemented": False,
        "no_public_search_live": True,
        "no_hosted_public_search_live": True,
        "first_allowed_mode": "local_index_only",
        "created_by_slice": "public_search_safety_abuse_guard_v0",
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            errors.append(f"public_search_safety.json: {key} must be {expected_value!r}.")
    if set(_string_list(payload.get("allowed_modes"))) != REQUIRED_ALLOWED_MODES:
        errors.append("public_search_safety.json: allowed_modes must contain only local_index_only.")
    disabled_modes = set(_string_list(payload.get("disabled_modes")))
    if not REQUIRED_DISABLED_MODES.issubset(disabled_modes):
        errors.append(
            "public_search_safety.json: disabled_modes missing "
            f"{sorted(REQUIRED_DISABLED_MODES - disabled_modes)}."
        )
    _validate_limits(payload, errors)
    _require_subset(
        "public_search_safety.json: forbidden_parameters",
        REQUIRED_FORBIDDEN_PARAMETERS,
        set(_string_list(payload.get("forbidden_parameters"))),
        errors,
    )
    _require_subset(
        "public_search_safety.json: forbidden_behaviors",
        REQUIRED_FORBIDDEN_BEHAVIORS,
        set(_string_list(payload.get("forbidden_behaviors"))),
        errors,
    )
    _require_subset(
        "public_search_safety.json: required_error_codes",
        REQUIRED_ERROR_CODES,
        set(_string_list(payload.get("required_error_codes"))),
        errors,
    )
    _validate_error_mapping(_mapping(payload.get("error_mapping")), errors)
    _validate_privacy_and_operator_controls(payload, errors)
    _validate_dependencies(payload, errors)


def _validate_limits(payload: Mapping[str, Any], errors: list[str]) -> None:
    request_limits = _mapping(payload.get("request_limits"))
    expected_request = {
        "max_query_length": 160,
        "min_query_length_after_trim": 1,
        "max_include_items": 8,
        "max_request_body_bytes": 8192,
        "request_method_v0": "GET",
        "post_json_status": "future",
        "caller_provided_index_roots_allowed": False,
        "caller_provided_store_roots_allowed": False,
        "caller_provided_urls_allowed": False,
        "caller_provided_uploads_allowed": False,
    }
    _expect_mapping_values("public_search_safety.json: request_limits", request_limits, expected_request, errors)
    result_limits = _mapping(payload.get("result_limits"))
    expected_result = {
        "default_result_limit": 10,
        "max_result_limit": 25,
        "max_checked_sources_v0": "controlled_local_index_only",
        "max_live_sources_v0": 0,
        "raw_source_payloads_allowed": False,
        "download_urls_allowed": False,
        "install_urls_allowed": False,
    }
    _expect_mapping_values("public_search_safety.json: result_limits", result_limits, expected_result, errors)
    timeout = _mapping(payload.get("timeout_policy"))
    if timeout.get("max_runtime_ms_contract") not in {3000, 5000}:
        errors.append("public_search_safety.json: max_runtime_ms_contract must be 3000 or 5000.")
    if timeout.get("timeout_error_code") != "timeout":
        errors.append("public_search_safety.json: timeout_error_code must be timeout.")


def _validate_error_mapping(mapping: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "empty_query_after_trim": "query_required",
        "query_over_160_characters": "query_too_long",
        "limit_above_25": "limit_too_large",
        "unsupported_mode": "unsupported_mode",
        "unsupported_profile": "unsupported_profile",
        "unsupported_include": "unsupported_include",
        "forbidden_parameter_default": "forbidden_parameter",
        "local_path_or_root_parameter": "local_paths_forbidden",
        "download_parameter_or_action": "downloads_disabled",
        "install_or_execute_parameter_or_action": "installs_disabled",
        "upload_or_user_file_parameter": "uploads_disabled",
        "live_probe_or_live_source_parameter": "live_probes_disabled",
        "backend_required_but_unavailable": "live_backend_unavailable",
        "future_rate_limit_exceeded": "rate_limited",
        "runtime_timeout": "timeout",
        "malformed_request": "bad_request",
    }
    _expect_mapping_values("public_search_safety.json: error_mapping", mapping, expected, errors)


def _validate_privacy_and_operator_controls(payload: Mapping[str, Any], errors: list[str]) -> None:
    logging_policy = _mapping(payload.get("logging_privacy_policy"))
    expected_logging = {
        "telemetry_implemented": False,
        "telemetry_default": "off",
        "raw_query_logging_default": "disabled",
        "private_path_logging": "forbidden",
        "credential_logging": "forbidden",
        "external_query_log_uploads_by_default": False,
    }
    _expect_mapping_values("public_search_safety.json: logging_privacy_policy", logging_policy, expected_logging, errors)
    telemetry = _mapping(payload.get("telemetry_policy"))
    expected_telemetry = {
        "implemented": False,
        "default_enabled": False,
        "analytics_enabled": False,
        "crash_report_uploads_enabled": False,
        "query_log_uploads_enabled": False,
        "future_opt_in_required": True,
    }
    _expect_mapping_values("public_search_safety.json: telemetry_policy", telemetry, expected_telemetry, errors)
    rate = _mapping(payload.get("rate_limit_policy"))
    if rate.get("runtime_middleware_implemented") is not False:
        errors.append("public_search_safety.json: rate-limit middleware must not be implemented.")
    if rate.get("required_before_public_exposure") is not True:
        errors.append("public_search_safety.json: rate limit policy must be required before exposure.")
    controls = _mapping(_mapping(payload.get("operator_controls")).get("required_future_flags"))
    missing_flags = sorted(REQUIRED_OPERATOR_FLAGS - set(controls))
    if missing_flags:
        errors.append(f"public_search_safety.json: operator controls missing {missing_flags}.")
    expected_flags = {
        "EUREKA_PUBLIC_SEARCH_MODE": "local_index_only",
        "EUREKA_ALLOW_LIVE_PROBES": "0",
        "EUREKA_ALLOW_DOWNLOADS": "0",
        "EUREKA_ALLOW_INSTALLS": "0",
        "EUREKA_ALLOW_LOCAL_PATHS": "0",
        "EUREKA_ALLOW_USER_UPLOADS": "0",
        "EUREKA_ALLOW_TELEMETRY": "0",
        "EUREKA_MAX_QUERY_LEN": "160",
        "EUREKA_MAX_RESULTS": "25",
        "EUREKA_SEARCH_TIMEOUT_MS": "3000",
        "EUREKA_PUBLIC_SEARCH_ENABLED": "0",
        "EUREKA_OPERATOR_KILL_SWITCH": "1",
    }
    _expect_mapping_values("public_search_safety.json: operator controls", controls, expected_flags, errors)


def _validate_dependencies(payload: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("public_alpha_defaults", "static_site_defaults"):
        defaults = _mapping(payload.get(key))
        for flag in (
            "public_search_live",
            "local_paths_allowed",
            "live_probes_allowed",
            "downloads_allowed",
            "installs_allowed",
            "uploads_allowed",
            "telemetry_allowed",
        ):
            if flag in defaults and defaults.get(flag) is not False:
                errors.append(f"public_search_safety.json: {key}.{flag} must be false.")
    static_defaults = _mapping(payload.get("static_site_defaults"))
    if static_defaults.get("github_pages_static_only") is not True:
        errors.append("public_search_safety.json: GitHub Pages must remain static-only.")
    if static_defaults.get("search_form_added") is not True:
        errors.append("public_search_safety.json: static search handoff form must be recorded as added.")
    if static_defaults.get("static_search_handoff_added") is not True:
        errors.append("public_search_safety.json: static_search_handoff_added must be true.")
    if static_defaults.get("hosted_form_enabled") is not False:
        errors.append("public_search_safety.json: hosted_form_enabled must remain false.")
    for key in ("live_backend_dependency", "live_probe_dependency", "action_policy_dependency", "local_cache_privacy_dependency"):
        dependency = _mapping(payload.get(key))
        if not dependency:
            errors.append(f"public_search_safety.json: missing {key}.")
    prerequisites = set(_string_list(payload.get("prerequisites_for_runtime")))
    for prerequisite in (
        "python scripts/validate_public_search_contract.py",
        "python scripts/validate_public_search_result_card_contract.py",
        "python scripts/validate_public_search_safety.py",
        "no local path parameters accepted",
        "no live probes accepted",
        "no downloads, installs, execution, or uploads exposed",
        "operator flags wired and default-disabled",
        "kill switch wired and tested",
        "logging/privacy posture accepted",
    ):
        if prerequisite not in prerequisites:
            errors.append(f"public_search_safety.json: prerequisites_for_runtime missing {prerequisite!r}.")


def _validate_request_alignment(request: Any, safety: Any, errors: list[str]) -> None:
    if not isinstance(request, Mapping):
        errors.append("search_request.v0.json: must be a JSON object.")
        return
    properties = _mapping(request.get("properties"))
    mode_enum = set(_string_list(_mapping(properties.get("mode")).get("enum")))
    if mode_enum != REQUIRED_ALLOWED_MODES:
        errors.append("search_request.v0.json: mode enum must contain only local_index_only.")
    q = _mapping(properties.get("q"))
    if q.get("maxLength") != 160:
        errors.append("search_request.v0.json: q maxLength must be 160.")
    limit = _mapping(properties.get("limit"))
    if limit.get("default") != 10 or limit.get("maximum") != 25:
        errors.append("search_request.v0.json: limit must default to 10 and max at 25.")
    forbidden = set(_string_list(request.get("x-forbidden_parameters")))
    safety_forbidden = set(_string_list(_mapping(safety).get("forbidden_parameters")))
    _require_subset("search_request.v0.json: x-forbidden_parameters", REQUIRED_FORBIDDEN_PARAMETERS, forbidden, errors)
    missing_safety = sorted(safety_forbidden - forbidden)
    if missing_safety:
        errors.append(f"search_request.v0.json: missing safety forbidden parameters {missing_safety}.")
    behaviors = set(_string_list(request.get("x-forbidden_behaviors")))
    for behavior in ("live_probe", "live_federated", "arbitrary_url_fetch", "local_path_search", "download", "install", "execute", "upload"):
        if behavior not in behaviors:
            errors.append(f"search_request.v0.json: x-forbidden_behaviors missing {behavior}.")


def _validate_error_schema(payload: Any, safety: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("error_response.v0.json: must be a JSON object.")
        return
    code_enum = set(
        _string_list(
            _mapping(
                _mapping(_mapping(_mapping(payload.get("properties")).get("error")).get("properties")).get("code")
            ).get("enum")
        )
    )
    _require_subset("error_response.v0.json: error code enum", REQUIRED_ERROR_CODES, code_enum, errors)
    safety_codes = set(_string_list(_mapping(safety).get("required_error_codes")))
    _require_subset("error_response.v0.json: safety required error codes", safety_codes, code_enum, errors)


def _validate_routes(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_search_routes.json: must be a JSON object.")
        return
    if payload.get("implemented_now") is not True or payload.get("runtime_routes_implemented") is not True:
        errors.append("public_search_routes.json: local public search runtime routes must be implemented.")
    if payload.get("hosted_public_runtime_implemented") is not False:
        errors.append("public_search_routes.json: hosted public runtime must remain unimplemented.")
    if payload.get("static_handoff_implemented") is not True:
        errors.append("public_search_routes.json: static search handoff must be implemented by P30.")
    if set(_string_list(payload.get("contract_modes"))) != REQUIRED_ALLOWED_MODES:
        errors.append("public_search_routes.json: contract_modes must contain only local_index_only.")
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("public_search_routes.json: routes must be a list.")
        return
    for index, route in enumerate(routes):
        if not isinstance(route, Mapping):
            errors.append(f"public_search_routes.json: routes[{index}] must be an object.")
            continue
        label = route.get("path_template", index)
        if route.get("status") not in FUTURE_ROUTE_STATUSES:
            errors.append(f"public_search_routes.json: route {label} has unsupported status.")
        if route.get("status") == "local_runtime_implemented":
            if route.get("implemented_now") is not True:
                errors.append(f"public_search_routes.json: route {label} must be implemented locally.")
            if route.get("implementation_scope") != "local_prototype_backend":
                errors.append(f"public_search_routes.json: route {label} must be local_prototype_backend.")
            if route.get("hosted_public_deployment") is not False:
                errors.append(f"public_search_routes.json: route {label} must not be hosted public deployment.")
        elif route.get("implemented_now") is not False:
            errors.append(f"public_search_routes.json: route {label} must not be implemented unless marked local_runtime_implemented.")
        for flag in ("live_probe_allowed", "downloads_allowed", "local_paths_allowed", "uploads_allowed"):
            if route.get(flag) is not False:
                errors.append(f"public_search_routes.json: route {label} must keep {flag}=false.")
        if route.get("allowed_modes") != ["local_index_only"]:
            errors.append(f"public_search_routes.json: route {label} must allow only local_index_only.")
        if route.get("rate_limit_required_before_public") is not True:
            errors.append(f"public_search_routes.json: route {label} must require rate limits before public exposure.")


def _validate_live_probe_gateway(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_probe_gateway.json: must be a JSON object.")
        return
    expected = {
        "no_live_probes_implemented": True,
        "no_network_calls_performed": True,
        "enabled_by_default": False,
        "public_alpha_default_enabled": False,
        "public_search_contract_default_mode": "local_index_only",
        "public_search_live_probe_mode_implemented": False,
    }
    _expect_mapping_values("live_probe_gateway.json", payload, expected, errors)
    limits = _mapping(payload.get("global_limits"))
    for key in ("allow_arbitrary_url_fetch", "allow_downloads", "allow_write_actions", "allow_auth_user_credentials"):
        if limits.get(key) is not False:
            errors.append(f"live_probe_gateway.json: global_limits.{key} must be false.")


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
        for claim in PROHIBITED_DOC_CLAIMS:
            if claim in folded and not _is_negated_claim(folded, claim):
                errors.append(f"{_rel(path)}: contains prohibited claim {claim!r}.")
    if PUBLIC_ALPHA_SAFE_MODE.is_file():
        text = PUBLIC_ALPHA_SAFE_MODE.read_text(encoding="utf-8").casefold()
        for phrase in ("public search safety / abuse guard v0", "public search is not live", "telemetry defaults off"):
            if phrase not in text:
                errors.append(f"{_rel(PUBLIC_ALPHA_SAFE_MODE)}: missing phrase {phrase!r}.")


def _is_negated_claim(text: str, claim: str) -> bool:
    allowed = (
        f"not {claim}",
        f"does not {claim}",
        f"must not {claim}",
        f"no {claim}",
        f"no documentation claims {claim}",
        f"{claim} is not",
        f"{claim} are not",
    )
    return any(item in text for item in allowed)


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_rel(path)}: missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
        return None


def _expect_mapping_values(label: str, payload: Mapping[str, Any], expected: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            errors.append(f"{label}: {key} must be {expected_value!r}.")


def _require_subset(label: str, expected: set[str], actual: set[str], errors: list[str]) -> None:
    missing = sorted(expected - actual)
    if missing:
        errors.append(f"{label} missing {missing}.")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    return [item for item in value] if isinstance(value, list) and all(isinstance(item, str) for item in value) else []


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Search Safety / Abuse Guard validation",
        f"status: {report['status']}",
        f"safety_policy_id: {report['safety_policy_id']}",
        f"first_allowed_mode: {report['first_allowed_mode']}",
        f"max_query_length: {report['max_query_length']}",
        f"max_result_limit: {report['max_result_limit']}",
        f"max_runtime_ms_contract: {report['max_runtime_ms_contract']}",
        f"telemetry_default: {report['telemetry_default']}",
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
