#!/usr/bin/env python3
"""Validate P53 Public Search Production Contract v0 without network access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "public-search-production-contract-v0"
REPORT_PATH = AUDIT_ROOT / "public_search_production_contract_report.json"
API_ROOT = ROOT / "contracts" / "api"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "ROUTE_CONTRACT.md",
    "REQUEST_CONTRACT.md",
    "RESPONSE_CONTRACT.md",
    "ERROR_CONTRACT.md",
    "RESULT_CARD_ALIGNMENT.md",
    "SOURCE_STATUS_CONTRACT.md",
    "EVIDENCE_SUMMARY_CONTRACT.md",
    "ABSENCE_AND_GAP_CONTRACT.md",
    "SAFETY_AND_LIMITS_CONTRACT.md",
    "VERSIONING_AND_COMPATIBILITY.md",
    "STATIC_TO_DYNAMIC_HANDOFF_REQUIREMENTS.md",
    "HOSTED_WRAPPER_REQUIREMENTS.md",
    "RUNTIME_NON_GOALS.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "public_search_production_contract_report.json",
}

REQUIRED_SCHEMAS = {
    "search_request.v0.json",
    "search_response.v0.json",
    "error_response.v0.json",
    "search_result_card.v0.json",
    "source_status.v0.json",
    "evidence_summary.v0.json",
    "absence_report.v0.json",
    "public_search_status.v0.json",
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

REQUIRED_ERROR_CODES = {
    "query_required",
    "query_too_long",
    "limit_too_large",
    "unsupported_mode",
    "unsupported_profile",
    "unsupported_include",
    "forbidden_parameter",
    "local_paths_forbidden",
    "arbitrary_url_fetch_forbidden",
    "downloads_disabled",
    "installs_disabled",
    "uploads_disabled",
    "live_probes_disabled",
    "live_backend_unavailable",
    "rate_limited",
    "timeout",
    "bad_request",
    "internal_error_public_safe",
}

REQUIRED_ROUTES = {
    "/healthz",
    "/status",
    "/search",
    "/api/v1/status",
    "/api/v1/search",
    "/api/v1/query-plan",
    "/api/v1/sources",
    "/api/v1/source/{source_id}",
}

ALLOWED_ROUTE_CLASSIFICATIONS = {
    "implemented_local_prototype",
    "hosted_future",
    "static_handoff",
    "contract_only",
    "deferred",
}

FORBIDDEN_CLAIMS = (
    "hosted public search is live",
    "hosted search is live",
    "deployment success is verified",
    "live probes are enabled",
    "downloads are enabled",
    "uploads are enabled",
    "installs are enabled",
    "production-ready",
    "production ready",
)


def validate_public_search_production_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _validate_audit_pack(errors)
    report = _load_json(REPORT_PATH, errors)
    schemas = {name: _load_json(API_ROOT / name, errors) for name in REQUIRED_SCHEMAS}

    _validate_report(report, errors)
    _validate_request_schema(schemas.get("search_request.v0.json"), errors)
    _validate_response_schema(schemas.get("search_response.v0.json"), errors)
    _validate_error_schema(schemas.get("error_response.v0.json"), errors)
    _validate_result_card_schema(schemas.get("search_result_card.v0.json"), errors)
    _validate_source_status_schema(schemas.get("source_status.v0.json"), errors)
    _validate_evidence_summary_schema(schemas.get("evidence_summary.v0.json"), errors)
    _validate_absence_schema(schemas.get("absence_report.v0.json"), errors)
    _validate_public_status_schema(schemas.get("public_search_status.v0.json"), errors)
    _validate_docs_and_claims(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_production_contract_validator_v0",
        "report_id": _mapping(report).get("report_id"),
        "active_mode": _mapping(report).get("active_mode"),
        "hosted_search_implemented": _mapping(report).get("hosted_search_implemented"),
        "live_probes_enabled": _mapping(report).get("live_probes_enabled"),
        "required_schemas": sorted(REQUIRED_SCHEMAS),
        "required_routes": sorted(REQUIRED_ROUTES),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_audit_pack(errors: list[str]) -> None:
    if not AUDIT_ROOT.is_dir():
        errors.append("P53 audit pack is missing.")
        return
    present = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - present)
    if missing:
        errors.append(f"P53 audit pack missing required files: {missing}.")


def _validate_report(report: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        errors.append("public_search_production_contract_report.json must be an object.")
        return
    required = {
        "report_id",
        "created_by_slice",
        "repo_head",
        "branch",
        "worktree_status",
        "contract_status",
        "routes",
        "active_mode",
        "future_modes",
        "request_limits",
        "forbidden_parameters",
        "response_contracts",
        "error_codes",
        "result_card_alignment",
        "source_status_contract",
        "evidence_summary_contract",
        "absence_contract",
        "safety_flags",
        "hosted_search_implemented",
        "dynamic_backend_deployed",
        "live_probes_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "installs_enabled",
        "local_paths_enabled",
        "arbitrary_url_fetch_enabled",
        "telemetry_enabled",
        "static_handoff_requirements",
        "hosted_wrapper_requirements",
        "command_results",
        "remaining_gaps",
        "next_recommended_branch",
        "notes",
    }
    missing = sorted(required - set(report))
    if missing:
        errors.append(f"report missing required keys: {missing}.")
    if report.get("report_id") != "public_search_production_contract_v0":
        errors.append("report_id must be public_search_production_contract_v0.")
    if report.get("active_mode") != "local_index_only":
        errors.append("active_mode must be local_index_only.")
    for key in (
        "hosted_search_implemented",
        "dynamic_backend_deployed",
        "live_probes_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "installs_enabled",
        "local_paths_enabled",
        "arbitrary_url_fetch_enabled",
        "telemetry_enabled",
    ):
        if report.get(key) is not False:
            errors.append(f"{key} must be false.")

    route_paths = set()
    for route in _list_of_mappings(report.get("routes")):
        path = route.get("path")
        classification = route.get("classification")
        if isinstance(path, str):
            route_paths.add(path)
        if classification not in ALLOWED_ROUTE_CLASSIFICATIONS:
            errors.append(f"route {path!r} has invalid classification {classification!r}.")
    missing_routes = sorted(REQUIRED_ROUTES - route_paths)
    if missing_routes:
        errors.append(f"report routes missing {missing_routes}.")

    missing_params = sorted(REQUIRED_FORBIDDEN_PARAMETERS - set(_string_list(report.get("forbidden_parameters"))))
    if missing_params:
        errors.append(f"report forbidden_parameters missing {missing_params}.")
    missing_codes = sorted(REQUIRED_ERROR_CODES - set(_string_list(report.get("error_codes"))))
    if missing_codes:
        errors.append(f"report error_codes missing {missing_codes}.")
    if not isinstance(report.get("command_results"), list) or not report["command_results"]:
        errors.append("report command_results must be non-empty.")
    if not report.get("hosted_wrapper_requirements"):
        errors.append("hosted_wrapper_requirements must be present.")


def _validate_request_schema(payload: Any, errors: list[str]) -> None:
    props = _mapping(_mapping(payload).get("properties"))
    q = _mapping(props.get("q"))
    if q.get("maxLength") != 160:
        errors.append("search_request q maxLength must be 160.")
    limit = _mapping(props.get("limit"))
    if limit.get("default") != 10 or limit.get("maximum") != 25:
        errors.append("search_request limit must default to 10 and max at 25.")
    mode_enum = _string_list(_mapping(props.get("mode")).get("enum"))
    if mode_enum != ["local_index_only"]:
        errors.append("search_request active mode enum must be local_index_only only.")
    for profile in ("standard_web", "lite_html", "text", "api_client", "snapshot", "native_client"):
        if profile not in _string_list(_mapping(props.get("profile")).get("enum")):
            errors.append(f"search_request profile enum missing {profile}.")
    include_enum = _string_list(_mapping(_mapping(props.get("include")).get("items")).get("enum"))
    for include in ("evidence", "compatibility", "source_summary", "limitations", "gaps", "actions"):
        if include not in include_enum:
            errors.append(f"search_request include enum missing {include}.")
    missing = sorted(REQUIRED_FORBIDDEN_PARAMETERS - set(_string_list(_mapping(payload).get("x-forbidden_parameters"))))
    if missing:
        errors.append(f"search_request forbidden parameters missing {missing}.")


def _validate_response_schema(payload: Any, errors: list[str]) -> None:
    props = _mapping(_mapping(payload).get("properties"))
    for field in (
        "result_count",
        "checked",
        "limitations",
        "absence",
        "source_status",
        "timing",
        "request_limits",
        "next_actions",
        "live_probes_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "installs_enabled",
        "local_paths_enabled",
        "arbitrary_url_fetch_enabled",
    ):
        if field not in props:
            errors.append(f"search_response properties missing {field}.")
    if _mapping(payload).get("x-result_card_schema") != "contracts/api/search_result_card.v0.json":
        errors.append("search_response must reference search_result_card.v0.json.")
    for key, expected in (
        ("x-source_status_schema", "contracts/api/source_status.v0.json"),
        ("x-evidence_summary_schema", "contracts/api/evidence_summary.v0.json"),
        ("x-absence_report_schema", "contracts/api/absence_report.v0.json"),
        ("x-public_search_status_schema", "contracts/api/public_search_status.v0.json"),
    ):
        if _mapping(payload).get(key) != expected:
            errors.append(f"search_response {key} must be {expected}.")


def _validate_error_schema(payload: Any, errors: list[str]) -> None:
    props = _mapping(_mapping(payload).get("properties"))
    err = _mapping(props.get("error"))
    err_props = _mapping(err.get("properties"))
    codes = set(_string_list(_mapping(err_props.get("code")).get("enum")))
    missing = sorted(REQUIRED_ERROR_CODES - codes)
    if missing:
        errors.append(f"error_response code enum missing {missing}.")
    for field in ("code", "message", "status", "retryable", "severity"):
        if field not in _string_list(err.get("required")):
            errors.append(f"error_response error object required missing {field}.")
    for field in ("mode", "limitations", "request_limits"):
        if field not in props:
            errors.append(f"error_response properties missing {field}.")
    rules = set(_string_list(_mapping(payload).get("x-public_safe_error_rules")))
    for rule in ("no_stack_traces", "no_private_local_paths", "no_secret_values"):
        if rule not in rules:
            errors.append(f"error_response public-safe rules missing {rule}.")


def _validate_result_card_schema(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("search_result_card schema must be an object.")
        return
    blocked = set(_string_list(payload.get("x-blocked_or_future_gated_actions")))
    for action in (
        "download",
        "install_handoff",
        "execute",
        "upload",
        "live_probe",
        "mirror",
        "package_manager_handoff",
        "emulator_handoff",
    ):
        if action not in blocked:
            errors.append(f"result card blocked/future-gated actions missing {action}.")


def _validate_source_status_schema(payload: Any, errors: list[str]) -> None:
    props = _mapping(_mapping(payload).get("properties"))
    for field in ("source_id", "source_family", "label", "status", "coverage_depth", "live_supported", "live_enabled", "network_required", "limitations", "next_coverage_step", "public_safe"):
        if field not in props:
            errors.append(f"source_status properties missing {field}.")
    status_enum = set(_string_list(_mapping(props.get("status")).get("enum")))
    for status in ("active_fixture", "active_recorded_fixture", "placeholder", "local_private_future", "live_disabled", "live_enabled_future"):
        if status not in status_enum:
            errors.append(f"source_status enum missing {status}.")


def _validate_evidence_summary_schema(payload: Any, errors: list[str]) -> None:
    props = _mapping(_mapping(payload).get("properties"))
    for field in ("evidence_id", "evidence_kind", "claim_type", "source_id", "source_family", "subject_ref", "locator", "confidence", "limitations", "provenance_notes", "privacy_classification", "rights_classification", "public_safe"):
        if field not in props:
            errors.append(f"evidence_summary properties missing {field}.")
    forbidden = set(_string_list(_mapping(payload).get("x-forbidden_content")))
    for item in ("long_copyrighted_text", "private_paths", "credentials", "raw_source_payload"):
        if item not in forbidden:
            errors.append(f"evidence_summary forbidden content missing {item}.")


def _validate_absence_schema(payload: Any, errors: list[str]) -> None:
    props = _mapping(_mapping(payload).get("properties"))
    enum = set(_string_list(_mapping(props.get("absence_status")).get("enum")))
    for status in ("no_verified_result", "known_unresolved_need", "source_gap", "capability_gap", "policy_gap", "unknown"):
        if status not in enum:
            errors.append(f"absence_report status enum missing {status}.")
    if _mapping(payload).get("x-query_intelligence_runtime_implemented") is not False:
        errors.append("absence_report must record query intelligence runtime as false.")


def _validate_public_status_schema(payload: Any, errors: list[str]) -> None:
    props = _mapping(_mapping(payload).get("properties"))
    for field in ("public_search_implemented", "hosted_search_implemented", "local_runtime_available", "mode", "live_probes_enabled", "downloads_enabled", "uploads_enabled", "installs_enabled", "local_paths_enabled", "arbitrary_url_fetch_enabled", "telemetry_enabled", "account_required", "max_query_length", "default_limit", "max_limit", "index_status", "source_status_summary", "limitations"):
        if field not in props:
            errors.append(f"public_search_status properties missing {field}.")
    if _mapping(props.get("hosted_search_implemented")).get("const") is not False:
        errors.append("public_search_status hosted_search_implemented must const false.")
    if _mapping(props.get("live_probes_enabled")).get("const") is not False:
        errors.append("public_search_status live_probes_enabled must const false.")


def _validate_docs_and_claims(errors: list[str]) -> None:
    required_docs = [
        ROOT / "docs" / "reference" / "PUBLIC_SEARCH_PRODUCTION_CONTRACT.md",
        ROOT / "docs" / "reference" / "PUBLIC_ERROR_CONTRACT.md",
        ROOT / "docs" / "reference" / "PUBLIC_SOURCE_STATUS_CONTRACT.md",
        ROOT / "docs" / "reference" / "PUBLIC_EVIDENCE_SUMMARY_CONTRACT.md",
        ROOT / "docs" / "operations" / "PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md",
        ROOT / "docs" / "operations" / "PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md",
        ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md",
    ]
    for path in required_docs:
        if not path.is_file():
            errors.append(f"{_rel(path)} is missing.")

    safety_doc = ROOT / "docs" / "operations" / "PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md"
    if safety_doc.is_file():
        text = safety_doc.read_text(encoding="utf-8").casefold()
        for phrase in ("no downloads", "no uploads", "no live probes", "telemetry", "operator kill switch"):
            if phrase not in text:
                errors.append(f"{_rel(safety_doc)} missing safety phrase {phrase!r}.")

    wrapper = AUDIT_ROOT / "HOSTED_WRAPPER_REQUIREMENTS.md"
    if wrapper.is_file():
        text = wrapper.read_text(encoding="utf-8")
        for env_var in (
            "EUREKA_PUBLIC_MODE",
            "EUREKA_SEARCH_MODE",
            "EUREKA_ALLOW_LIVE_PROBES",
            "EUREKA_ALLOW_DOWNLOADS",
            "EUREKA_ALLOW_UPLOADS",
            "EUREKA_ALLOW_LOCAL_PATHS",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH",
            "EUREKA_MAX_QUERY_LEN",
            "EUREKA_MAX_RESULTS",
            "EUREKA_GLOBAL_TIMEOUT_MS",
        ):
            if env_var not in text:
                errors.append(f"HOSTED_WRAPPER_REQUIREMENTS.md missing {env_var}.")

    combined_parts: list[str] = []
    for root in (AUDIT_ROOT, ROOT / "docs" / "reference", ROOT / "docs" / "operations"):
        if not root.exists():
            continue
        for path in root.glob("*.md"):
            if path.name == "README.md" or "PUBLIC_SEARCH" in path.name or path.parent == AUDIT_ROOT:
                combined_parts.append(path.read_text(encoding="utf-8"))
    combined = "\n".join(combined_parts).casefold()
    for claim in FORBIDDEN_CLAIMS:
        if claim in combined:
            errors.append(f"forbidden product/deployment claim found: {claim}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)} is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)} is invalid JSON: {exc}.")
    return None


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public search production contract validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"active_mode: {report.get('active_mode')}",
        f"hosted_search_implemented: {report.get('hosted_search_implemented')}",
        f"live_probes_enabled: {report.get('live_probes_enabled')}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_search_production_contract()
    output = stdout or __import__("sys").stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
