from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-search-rehearsal-v0"
REPORT = AUDIT_DIR / "public_search_rehearsal_report.json"
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "public_search_smoke.py"
PUBLIC_ALPHA_ROUTES = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
HANDOFF = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_handoff.json"
ROUTES = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_routes.json"
SAFETY = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_safety.json"

REQUIRED_AUDIT_FILES = (
    "README.md",
    "REHEARSAL_SCOPE.md",
    "ROUTE_MATRIX.md",
    "SAFE_QUERY_RESULTS.md",
    "BLOCKED_REQUEST_RESULTS.md",
    "STATIC_HANDOFF_REVIEW.md",
    "PUBLIC_ALPHA_REVIEW.md",
    "CONTRACT_ALIGNMENT_REVIEW.md",
    "LIMITATIONS_AND_BLOCKERS.md",
    "NEXT_STEPS.md",
    "public_search_rehearsal_report.json",
)
REQUIRED_ROUTES = {
    "GET /search",
    "GET /api/v1/search",
    "GET /api/v1/query-plan",
    "GET /api/v1/status",
    "GET /api/v1/sources",
    "GET /api/v1/source/{source_id}",
}
REQUIRED_SAFE_QUERIES = {
    "windows 7 apps",
    "latest firefox before xp support ended",
    "driver.inf",
    "thinkpad t42 wifi windows 2000",
    "registry repair",
    "blue ftp",
    "pc magazine ray tracing",
    "archive",
    "no-such-local-index-hit",
}
REQUIRED_BLOCKED_CODES = {
    "missing q": "query_required",
    "query too long": "query_too_long",
    "limit too large": "limit_too_large",
    "unsupported mode live_probe": "live_probes_disabled",
    "index_path parameter": "local_paths_forbidden",
    "store_root parameter": "local_paths_forbidden",
    "url parameter": "forbidden_parameter",
    "fetch_url parameter": "forbidden_parameter",
    "download=true": "downloads_disabled",
    "install=true": "installs_disabled",
    "upload=true": "uploads_disabled",
    "source_credentials parameter": "forbidden_parameter",
    "api_key parameter": "forbidden_parameter",
    "live_source parameter": "live_probes_disabled",
}
UNSAFE_FLAG_FIELDS = (
    "live_probes_enabled",
    "downloads_enabled",
    "installs_enabled",
    "uploads_enabled",
    "local_paths_enabled",
    "telemetry_enabled",
)
PROHIBITED_CLAIMS = (
    "hosted public search is live",
    "public search is hosted",
    "hosted public search deployed",
    "production-ready public search",
    "production api stability is guaranteed",
    "live probes are enabled",
    "downloads are enabled",
    "installs are enabled",
    "uploads are enabled",
    "telemetry is enabled",
)
PRIVATE_PATH_MARKERS = (
    "c:/",
    "d:/",
    "\\users\\",
    "/users/",
    "/home/",
    "/tmp/",
    "appdata/",
    "appdata\\",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Public Search Rehearsal v0 without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_search_rehearsal()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_search_rehearsal() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    payload = _load_json(REPORT, errors)
    public_alpha = _load_json(PUBLIC_ALPHA_ROUTES, errors)
    handoff = _load_json(HANDOFF, errors)
    routes = _load_json(ROUTES, errors)
    safety = _load_json(SAFETY, errors)

    _validate_audit_files(errors)
    _validate_report(payload, errors)
    _validate_route_inventory(routes, errors)
    _validate_public_alpha_inventory(public_alpha, errors)
    _validate_handoff_and_safety(handoff, safety, errors)
    _validate_smoke_script(errors)
    _validate_claims_and_paths(errors)

    report_map = _mapping(payload)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_rehearsal_validator_v0",
        "report_id": report_map.get("report_id"),
        "mode": report_map.get("mode"),
        "decision": report_map.get("decision"),
        "hosted_backend_status": report_map.get("hosted_backend_status"),
        "route_count": len(_list(report_map.get("route_results"))),
        "safe_query_count": len(_list(report_map.get("safe_query_results"))),
        "blocked_request_count": len(_list(report_map.get("blocked_request_results"))),
        "pass_count": report_map.get("pass_count"),
        "fail_count": report_map.get("fail_count"),
        "next_recommended_milestone": report_map.get("next_recommended_milestone"),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_audit_files(errors: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/public-search-rehearsal-v0: audit directory is missing.")
        return
    for name in REQUIRED_AUDIT_FILES:
        path = AUDIT_DIR / name
        if not path.is_file():
            errors.append(f"control/audits/public-search-rehearsal-v0/{name}: missing required file.")


def _validate_report(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_search_rehearsal_report.json: must be a JSON object.")
        return
    expected = {
        "report_id": "public_search_rehearsal_v0",
        "created_by_slice": "public_search_rehearsal_v0",
        "mode": "local_index_only",
        "decision": "local_rehearsal_passed",
        "hosted_backend_status": "unavailable",
        "public_search_runtime_available": True,
        "static_handoff_available": True,
        "fail_count": 0,
        "unavailable_count": 0,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            errors.append(
                f"public_search_rehearsal_report.json: {key} must be {expected_value!r}."
            )
    for key in UNSAFE_FLAG_FIELDS:
        if payload.get(key) is not False:
            errors.append(f"public_search_rehearsal_report.json: {key} must be false.")
    if not payload.get("next_recommended_milestone"):
        errors.append("public_search_rehearsal_report.json: next milestone is required.")

    _validate_route_results(_list(payload.get("route_results")), errors)
    _validate_safe_query_results(_list(payload.get("safe_query_results")), errors)
    _validate_blocked_request_results(_list(payload.get("blocked_request_results")), errors)
    _validate_named_review(
        payload,
        "static_handoff_review",
        {"status": "passed", "fake_hosted_backend_claim": False},
        errors,
    )
    _validate_named_review(
        payload,
        "public_alpha_review",
        {"status": "passed", "public_search_routes_safe_public_alpha": True},
        errors,
    )
    _validate_named_review(
        payload,
        "contract_alignment",
        {"status": "passed", "live_backend_future": True, "live_probe_future": True},
        errors,
    )
    blockers = payload.get("blockers")
    if blockers not in ([], None):
        errors.append("public_search_rehearsal_report.json: local rehearsal blockers must be empty.")


def _validate_route_results(results: list[Any], errors: list[str]) -> None:
    by_route = {
        result.get("route"): result
        for result in results
        if isinstance(result, Mapping) and isinstance(result.get("route"), str)
    }
    missing = sorted(REQUIRED_ROUTES - set(by_route))
    if missing:
        errors.append(f"public_search_rehearsal_report.json: route_results missing {missing}.")
    for route in REQUIRED_ROUTES & set(by_route):
        item = _mapping(by_route[route])
        expected = {
            "implemented_locally": True,
            "public_alpha_safe": True,
            "static_host_route": False,
            "requires_backend": True,
            "mode": "local_index_only",
            "status": "passed",
        }
        for key, expected_value in expected.items():
            if item.get(key) != expected_value:
                errors.append(
                    f"public_search_rehearsal_report.json: route {route} {key} "
                    f"must be {expected_value!r}."
                )


def _validate_safe_query_results(results: list[Any], errors: list[str]) -> None:
    by_query = {
        result.get("query"): result
        for result in results
        if isinstance(result, Mapping) and isinstance(result.get("query"), str)
    }
    missing = sorted(REQUIRED_SAFE_QUERIES - set(by_query))
    if missing:
        errors.append(f"public_search_rehearsal_report.json: safe queries missing {missing}.")
    for query in REQUIRED_SAFE_QUERIES & set(by_query):
        item = _mapping(by_query[query])
        for key in (
            "envelope_ok",
            "result_cards_contract_ok",
            "warnings_present",
            "limitations_or_absence_present",
            "no_private_path_leakage",
        ):
            if item.get(key) is not True:
                errors.append(
                    f"public_search_rehearsal_report.json: safe query {query!r} "
                    f"{key} must be true."
                )
        if item.get("status") != "passed":
            errors.append(
                f"public_search_rehearsal_report.json: safe query {query!r} must pass."
            )
        if not isinstance(item.get("result_count"), int) or item.get("result_count") < 0:
            errors.append(
                f"public_search_rehearsal_report.json: safe query {query!r} result_count "
                "must be a non-negative integer."
            )


def _validate_blocked_request_results(results: list[Any], errors: list[str]) -> None:
    by_case = {
        result.get("case"): result
        for result in results
        if isinstance(result, Mapping) and isinstance(result.get("case"), str)
    }
    missing = sorted(set(REQUIRED_BLOCKED_CODES) - set(by_case))
    if missing:
        errors.append(f"public_search_rehearsal_report.json: blocked cases missing {missing}.")
    for case, expected_code in REQUIRED_BLOCKED_CODES.items():
        if case not in by_case:
            continue
        item = _mapping(by_case[case])
        if item.get("expected_error_code") != expected_code:
            errors.append(
                f"public_search_rehearsal_report.json: blocked case {case!r} "
                f"expected_error_code must be {expected_code!r}."
            )
        if item.get("actual_error_code") != expected_code:
            errors.append(
                f"public_search_rehearsal_report.json: blocked case {case!r} "
                f"actual_error_code must be {expected_code!r}."
            )
        for key in ("no_stack_trace", "no_private_path_leakage"):
            if item.get(key) is not True:
                errors.append(
                    f"public_search_rehearsal_report.json: blocked case {case!r} "
                    f"{key} must be true."
                )
        if item.get("status") != "passed":
            errors.append(
                f"public_search_rehearsal_report.json: blocked case {case!r} must pass."
            )


def _validate_named_review(
    payload: Mapping[str, Any],
    key: str,
    expected: Mapping[str, Any],
    errors: list[str],
) -> None:
    review = _mapping(payload.get(key))
    if not review:
        errors.append(f"public_search_rehearsal_report.json: {key} review is required.")
        return
    for field, expected_value in expected.items():
        if review.get(field) != expected_value:
            errors.append(
                f"public_search_rehearsal_report.json: {key}.{field} "
                f"must be {expected_value!r}."
            )


def _validate_route_inventory(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_search_routes.json: must be a JSON object.")
        return
    if payload.get("status") != "local_runtime_implemented":
        errors.append("public_search_routes.json: status must remain local_runtime_implemented.")
    if payload.get("hosted_public_runtime_implemented") is not False:
        errors.append("public_search_routes.json: hosted public runtime must remain false.")
    if payload.get("static_handoff_implemented") is not True:
        errors.append("public_search_routes.json: static handoff must remain true.")
    if payload.get("local_rehearsal_status") != "completed":
        errors.append("public_search_routes.json: local_rehearsal_status must be completed.")
    if payload.get("local_rehearsal") != "control/audits/public-search-rehearsal-v0/public_search_rehearsal_report.json":
        errors.append("public_search_routes.json: local_rehearsal must point at the P31 report.")


def _validate_public_alpha_inventory(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_alpha_routes.json: must be a JSON object.")
        return
    if payload.get("public_search_rehearsal_status") != "completed":
        errors.append("public_alpha_routes.json: public_search_rehearsal_status must be completed.")
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("public_alpha_routes.json: routes must be a list.")
        return
    required_patterns = {
        "/search",
        "/api/v1/status",
        "/api/v1/search",
        "/api/v1/query-plan",
        "/api/v1/sources",
        "/api/v1/source/{source_id}",
    }
    by_pattern = {
        route.get("route_pattern"): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("route_pattern"), str)
    }
    missing = sorted(required_patterns - set(by_pattern))
    if missing:
        errors.append(f"public_alpha_routes.json: missing public search route patterns {missing}.")
    for pattern in required_patterns & set(by_pattern):
        route = _mapping(by_pattern[pattern])
        if route.get("classification") != "safe_public_alpha":
            errors.append(f"public_alpha_routes.json: {pattern} must be safe_public_alpha.")


def _validate_handoff_and_safety(handoff: Any, safety: Any, errors: list[str]) -> None:
    if not isinstance(handoff, Mapping):
        errors.append("public_search_handoff.json: must be a JSON object.")
    else:
        if handoff.get("local_rehearsal_status") != "completed":
            errors.append("public_search_handoff.json: local_rehearsal_status must be completed.")
        if handoff.get("hosted_backend_status") != "unavailable":
            errors.append("public_search_handoff.json: hosted backend must remain unavailable.")
    if not isinstance(safety, Mapping):
        errors.append("public_search_safety.json: must be a JSON object.")
    else:
        if safety.get("local_rehearsal_status") != "completed":
            errors.append("public_search_safety.json: local_rehearsal_status must be completed.")
        if safety.get("hosted_public_search_runtime_implemented") is not False:
            errors.append("public_search_safety.json: hosted public search runtime must remain false.")
        for key in ("downloads_allowed", "installs_allowed", "uploads_allowed", "live_probes_allowed"):
            public_alpha_defaults = _mapping(safety.get("public_alpha_defaults"))
            if public_alpha_defaults.get(key) is not False:
                errors.append(f"public_search_safety.json: public_alpha_defaults.{key} must be false.")


def _validate_smoke_script(errors: list[str]) -> None:
    if not SMOKE_SCRIPT.is_file():
        errors.append("scripts/public_search_smoke.py: missing rehearsal smoke script.")
        return
    text = SMOKE_SCRIPT.read_text(encoding="utf-8")
    for token in (
        "CREATED_BY_SLICE = \"public_search_rehearsal_v0\"",
        "SAFE_QUERY_CASES",
        "BLOCKED_REQUEST_CASES",
        "run_public_search_smoke",
        "_run_safe_query",
        "_run_blocked_request",
    ):
        if token not in text:
            errors.append(f"scripts/public_search_smoke.py: missing token {token!r}.")
    for token in ("urllib.request.urlopen", "requests.", "internetarchive", "google"):
        if token in text.casefold():
            errors.append(f"scripts/public_search_smoke.py: prohibited external-call token {token!r}.")


def _validate_claims_and_paths(errors: list[str]) -> None:
    audit_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(AUDIT_DIR.glob("*"))
        if path.is_file()
    ).casefold()
    for phrase in PROHIBITED_CLAIMS:
        if phrase in audit_text:
            errors.append(f"public-search-rehearsal-v0: prohibited claim {phrase!r}.")
    for marker in PRIVATE_PATH_MARKERS:
        if marker in audit_text:
            errors.append(f"public-search-rehearsal-v0: private path marker {marker!r} found.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: missing JSON file.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Search Rehearsal Validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"mode: {report.get('mode')}",
        f"decision: {report.get('decision')}",
        f"routes: {report.get('route_count')}",
        f"safe queries: {report.get('safe_query_count')}",
        f"blocked requests: {report.get('blocked_request_count')}",
        "",
    ]
    for error in report.get("errors", []):
        lines.append(f"ERROR: {error}")
    for warning in report.get("warnings", []):
        lines.append(f"WARNING: {warning}")
    if not report.get("errors"):
        lines.append("All Public Search Rehearsal v0 checks passed.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
