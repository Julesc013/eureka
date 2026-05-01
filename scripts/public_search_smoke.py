from __future__ import annotations

import argparse
from dataclasses import dataclass
from io import BytesIO
import json
from pathlib import Path
import sys
from typing import Any, Callable, Mapping
from urllib.parse import urlencode


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.gateway.public_api import (  # noqa: E402
    build_demo_absence_public_api,
    build_demo_action_plan_public_api,
    build_demo_archive_resolution_evals_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_decomposition_public_api,
    build_demo_public_search_public_api,
    build_demo_query_planner_public_api,
    build_demo_representation_selection_public_api,
    build_demo_representations_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import WebServerConfig, WorkbenchWsgiApp  # noqa: E402


CREATED_BY_SLICE = "public_search_rehearsal_v0"
BASE_RUNTIME_SLICE = "local_public_search_runtime_v0"
MODE = "local_index_only"
MAX_QUERY_LENGTH = 160
SAFE_QUERY_CASES = (
    "windows 7 apps",
    "latest firefox before xp support ended",
    "driver.inf",
    "thinkpad t42 wifi windows 2000",
    "registry repair",
    "blue ftp",
    "pc magazine ray tracing",
    "archive",
    "no-such-local-index-hit",
)
BLOCKED_REQUEST_CASES = (
    ("missing q", {}, "query_required"),
    ("query too long", {"q": "x" * (MAX_QUERY_LENGTH + 1)}, "query_too_long"),
    ("limit too large", {"q": "windows", "limit": "26"}, "limit_too_large"),
    ("unsupported mode live_probe", {"q": "windows", "mode": "live_probe"}, "live_probes_disabled"),
    ("forbidden index_path", {"q": "windows", "index_path": "blocked-local-index"}, "local_paths_forbidden"),
    ("forbidden store_root", {"q": "windows", "store_root": "blocked-store-root"}, "local_paths_forbidden"),
    ("forbidden url", {"q": "windows", "url": "https://example.invalid/"}, "forbidden_parameter"),
    ("forbidden fetch_url", {"q": "windows", "fetch_url": "https://example.invalid/"}, "forbidden_parameter"),
    ("download disabled", {"q": "windows", "download": "true"}, "downloads_disabled"),
    ("install disabled", {"q": "windows", "install": "true"}, "installs_disabled"),
    ("upload disabled", {"q": "windows", "upload": "true"}, "uploads_disabled"),
    (
        "source credentials forbidden",
        {"q": "windows", "source_credentials": "redacted"},
        "forbidden_parameter",
    ),
    ("api key forbidden", {"q": "windows", "api_key": "redacted"}, "forbidden_parameter"),
    ("live source disabled", {"q": "windows", "live_source": "internet_archive"}, "live_probes_disabled"),
)


@dataclass(frozen=True)
class SmokeHttpResponse:
    status_code: int
    status_line: str
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json_body(self) -> dict[str, object]:
        return json.loads(self.text)


@dataclass(frozen=True)
class SmokeCheckResult:
    name: str
    route: str
    expected: str
    observed_status: int
    passed: bool
    code: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "route": self.route,
            "expected": self.expected,
            "observed_status": self.observed_status,
            "passed": self.passed,
            "code": self.code,
            "message": self.message,
        }


def run_public_search_smoke() -> dict[str, object]:
    app = _build_app()
    route_results = [
        _expect_json(
            app,
            "status",
            "/api/v1/status",
            {},
            _public_search_status_is_safe,
            "200 public-search status with local_index_only and disabled unsafe capabilities",
        ),
        _expect_json(
            app,
            "search",
            "/api/v1/search",
            {"q": "windows 7 apps"},
            lambda payload, text: (
                payload.get("ok") is True
                and payload.get("mode") == "local_index_only"
                and payload.get("index_status") == "generated_public_search_index"
                and isinstance(payload.get("index_document_count"), int)
                and int(payload["index_document_count"]) > 0
                and isinstance(payload.get("results"), list)
                and len(payload["results"]) > 0
            ),
            "200 governed public-search envelope with generated-index results",
        ),
        _expect_json(
            app,
            "driver search",
            "/api/v1/search",
            {"q": "driver.inf"},
            lambda payload, text: (
                payload.get("ok") is True
                and payload.get("mode") == "local_index_only"
                and isinstance(payload.get("results"), list)
            ),
            "200 governed public-search envelope for second representative query",
        ),
        _expect_json(
            app,
            "query plan",
            "/api/v1/query-plan",
            {"q": "windows 7 apps"},
            lambda payload, text: payload.get("ok") is True and payload.get("no_live_probe") is True,
            "200 governed query-plan envelope",
        ),
        _expect_json(
            app,
            "sources",
            "/api/v1/sources",
            {},
            lambda payload, text: payload.get("ok") is True and isinstance(payload.get("sources"), list),
            "200 governed source summaries",
        ),
        _expect_json(
            app,
            "source detail",
            "/api/v1/source/synthetic-fixtures",
            {},
            lambda payload, text: (
                payload.get("ok") is True
                and payload.get("selected_source_id") == "synthetic-fixtures"
                and isinstance(payload.get("sources"), list)
                and _has_no_private_path(text)
            ),
            "200 governed source detail without private path leakage",
        ),
        _expect_html(
            app,
            "html search",
            "/search",
            {"q": "windows 7 apps"},
            lambda text: "Eureka Public Search" in text and "local-index-only" in text and "Blocked actions" in text,
            "200 server-rendered public-search HTML",
        ),
    ]
    safe_query_results = [_run_safe_query(app, query) for query in SAFE_QUERY_CASES]
    blocked_request_results = [
        _run_blocked_request(app, name, query, expected_code)
        for name, query, expected_code in BLOCKED_REQUEST_CASES
    ]
    checks = (
        [check.to_dict() for check in route_results]
        + [_check_from_safe_query(result) for result in safe_query_results]
        + [_check_from_blocked_request(result) for result in blocked_request_results]
    )
    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    return {
        "status": "passed" if failed_count == 0 else "failed",
        "created_by_slice": CREATED_BY_SLICE,
        "base_runtime_slice": BASE_RUNTIME_SLICE,
        "mode": MODE,
        "implementation_scope": "local_prototype_backend",
        "hosted_public_deployment": False,
        "live_probes_enabled": False,
        "downloads_enabled": False,
        "installs_enabled": False,
        "uploads_enabled": False,
        "local_paths_enabled": False,
        "telemetry_enabled": False,
        "total_checks": len(checks),
        "passed_checks": passed_count,
        "failed_checks": failed_count,
        "route_results": [check.to_dict() for check in route_results],
        "safe_query_results": safe_query_results,
        "blocked_request_results": blocked_request_results,
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run local public-search runtime smoke checks without external network calls.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON smoke report instead of a plain-text summary.",
    )
    args = parser.parse_args(argv)
    report = run_public_search_smoke()
    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(format_smoke_report(report))
    return 0 if report["status"] == "passed" else 1


def format_smoke_report(report: Mapping[str, object]) -> str:
    lines = [
        "Public Search Smoke",
        f"status: {report['status']}",
        f"mode: {report['mode']}",
        f"checks: {report['passed_checks']}/{report['total_checks']} passed",
        f"safe queries: {len(report.get('safe_query_results', []))}",
        f"blocked requests: {len(report.get('blocked_request_results', []))}",
        "",
    ]
    for item in report["checks"]:
        if not isinstance(item, Mapping):
            continue
        marker = "PASS" if item.get("passed") else "FAIL"
        lines.append(
            f"[{marker}] {item.get('name')}: {item.get('route')} "
            f"({item.get('code')})"
        )
        if not item.get("passed"):
            lines.append(f"  {item.get('message')}")
    lines.append("")
    return "\n".join(lines)


def _build_app() -> WorkbenchWsgiApp:
    return WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        absence_public_api=build_demo_absence_public_api(),
        action_plan_public_api=build_demo_action_plan_public_api(),
        actions_public_api=build_demo_resolution_actions_public_api(),
        archive_resolution_evals_public_api=build_demo_archive_resolution_evals_public_api(),
        comparison_public_api=build_demo_comparison_public_api(),
        compatibility_public_api=build_demo_compatibility_public_api(),
        decomposition_public_api=build_demo_decomposition_public_api(),
        handoff_public_api=build_demo_representation_selection_public_api(),
        query_planner_public_api=build_demo_query_planner_public_api(),
        representations_public_api=build_demo_representations_public_api(),
        search_public_api=build_demo_search_public_api(),
        public_search_public_api=build_demo_public_search_public_api(),
        source_registry_public_api=build_demo_source_registry_public_api(),
        subject_states_public_api=build_demo_subject_states_public_api(),
        default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        server_config=WebServerConfig.local_dev(),
    )


def _expect_json(
    app: WorkbenchWsgiApp,
    name: str,
    path: str,
    query: Mapping[str, str],
    predicate: Callable[[dict[str, object], str], bool],
    expected: str,
) -> SmokeCheckResult:
    response = _request(app, path, query)
    route = _route(path, query)
    if response.status_code != 200:
        return SmokeCheckResult(
            name,
            route,
            expected,
            response.status_code,
            False,
            "unexpected_status",
            f"Expected HTTP 200, observed {response.status_line}.",
        )
    try:
        payload = response.json_body()
    except json.JSONDecodeError as error:
        return SmokeCheckResult(name, route, expected, response.status_code, False, "invalid_json", str(error))
    passed = predicate(payload, response.text)
    return SmokeCheckResult(
        name,
        route,
        expected,
        response.status_code,
        passed,
        "ok" if passed else "payload_mismatch",
        "Check passed." if passed else "JSON payload did not satisfy the smoke expectation.",
    )


def _expect_html(
    app: WorkbenchWsgiApp,
    name: str,
    path: str,
    query: Mapping[str, str],
    predicate: Callable[[str], bool],
    expected: str,
) -> SmokeCheckResult:
    response = _request(app, path, query)
    route = _route(path, query)
    content_type = response.headers.get("content-type", "")
    passed = response.status_code == 200 and content_type.startswith("text/html") and predicate(response.text)
    return SmokeCheckResult(
        name,
        route,
        expected,
        response.status_code,
        passed,
        "ok" if passed else "html_mismatch",
        "Check passed." if passed else f"Observed {response.status_line} with content-type {content_type}.",
    )


def _expect_public_search_error(
    app: WorkbenchWsgiApp,
    name: str,
    path: str,
    query: Mapping[str, str],
    expected_code: str,
) -> SmokeCheckResult:
    response = _request(app, path, query)
    route = _route(path, query)
    try:
        payload = response.json_body()
    except json.JSONDecodeError:
        payload = {}
    error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
    actual_code = str(error.get("code") or "")
    passed = response.status_code == 400 and payload.get("ok") is False and actual_code == expected_code
    return SmokeCheckResult(
        name,
        route,
        f"400 governed public-search error code {expected_code}",
        response.status_code,
        passed,
        actual_code or "missing_error_code",
        "Check passed." if passed else f"Observed {response.status_line} with payload {payload!r}.",
    )


def _run_safe_query(app: WorkbenchWsgiApp, query: str) -> dict[str, object]:
    response = _request(app, "/api/v1/search", {"q": query})
    route = _route("/api/v1/search", {"q": query})
    payload: dict[str, Any] = {}
    parse_error: str | None = None
    try:
        payload = response.json_body()
    except json.JSONDecodeError as error:
        parse_error = str(error)
    results = payload.get("results") if isinstance(payload, Mapping) else None
    result_list = results if isinstance(results, list) else []
    result_cards_contract_ok = all(
        _result_card_is_contract_aligned(card) for card in result_list if isinstance(card, Mapping)
    ) and len(result_list) == sum(1 for card in result_list if isinstance(card, Mapping))
    envelope_ok = (
        response.status_code == 200
        and payload.get("ok") is True
        and payload.get("mode") == MODE
        and isinstance(payload.get("query"), Mapping)
        and isinstance(results, list)
    )
    warnings_present = bool(payload.get("warnings"))
    limitations_or_absence_present = bool(payload.get("absence_summary")) or any(
        isinstance(card, Mapping) and bool(card.get("limitations")) for card in result_list
    )
    no_private_path_leakage = _has_no_private_path(response.text)
    passed = (
        envelope_ok
        and result_cards_contract_ok
        and warnings_present
        and limitations_or_absence_present
        and no_private_path_leakage
    )
    return {
        "query": query,
        "route": route,
        "observed_status": response.status_code,
        "ok": payload.get("ok"),
        "result_count": len(result_list),
        "envelope_ok": envelope_ok,
        "result_cards_contract_ok": result_cards_contract_ok,
        "warnings_present": warnings_present,
        "limitations_or_absence_present": limitations_or_absence_present,
        "no_private_path_leakage": no_private_path_leakage,
        "passed": passed,
        "message": "Check passed." if passed else parse_error or "Safe query response did not satisfy rehearsal expectations.",
    }


def _run_blocked_request(
    app: WorkbenchWsgiApp,
    name: str,
    query: Mapping[str, str],
    expected_code: str,
) -> dict[str, object]:
    response = _request(app, "/api/v1/search", query)
    route = _route("/api/v1/search", query)
    payload: dict[str, Any] = {}
    parse_error: str | None = None
    try:
        payload = response.json_body()
    except json.JSONDecodeError as error:
        parse_error = str(error)
    error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
    actual_code = str(error.get("code") or "")
    no_private_path_leakage = _has_no_private_path(response.text)
    no_stack_trace = "traceback" not in response.text.casefold()
    passed = (
        response.status_code == 400
        and payload.get("ok") is False
        and actual_code == expected_code
        and no_private_path_leakage
        and no_stack_trace
    )
    return {
        "name": name,
        "route": route,
        "expected_error_code": expected_code,
        "actual_error_code": actual_code,
        "observed_status": response.status_code,
        "ok": payload.get("ok"),
        "no_private_path_leakage": no_private_path_leakage,
        "no_stack_trace": no_stack_trace,
        "passed": passed,
        "message": "Check passed." if passed else parse_error or f"Observed {response.status_line} with code {actual_code!r}.",
    }


def _check_from_safe_query(result: Mapping[str, object]) -> dict[str, object]:
    return {
        "name": f"safe query: {result.get('query')}",
        "route": result.get("route"),
        "expected": "200 governed search envelope with contract-aligned cards or absence summary",
        "observed_status": result.get("observed_status"),
        "passed": result.get("passed"),
        "code": "ok" if result.get("passed") else "safe_query_mismatch",
        "message": result.get("message"),
    }


def _check_from_blocked_request(result: Mapping[str, object]) -> dict[str, object]:
    return {
        "name": f"blocked request: {result.get('name')}",
        "route": result.get("route"),
        "expected": f"400 governed error code {result.get('expected_error_code')}",
        "observed_status": result.get("observed_status"),
        "passed": result.get("passed"),
        "code": result.get("actual_error_code") or "missing_error_code",
        "message": result.get("message"),
    }


def _result_card_is_contract_aligned(card: Mapping[str, Any]) -> bool:
    source = card.get("source")
    user_cost = card.get("user_cost")
    evidence = card.get("evidence")
    actions = card.get("actions")
    compatibility = card.get("compatibility")
    blocked_actions = []
    if isinstance(actions, Mapping) and isinstance(actions.get("blocked"), list):
        blocked_actions = [
            item.get("action_id")
            for item in actions["blocked"]
            if isinstance(item, Mapping)
        ]
    return (
        isinstance(card.get("result_id"), str)
        and isinstance(card.get("title"), str)
        and isinstance(card.get("record_kind"), str)
        and isinstance(card.get("result_lane"), str)
        and isinstance(source, Mapping)
        and isinstance(source.get("source_id"), str)
        and isinstance(source.get("source_family"), str)
        and isinstance(user_cost, Mapping)
        and isinstance(user_cost.get("score"), int)
        and isinstance(evidence, Mapping)
        and isinstance(evidence.get("evidence_count"), int)
        and isinstance(compatibility, Mapping)
        and isinstance(actions, Mapping)
        and isinstance(actions.get("allowed"), list)
        and isinstance(actions.get("blocked"), list)
        and {"download", "install_handoff", "execute", "upload"}.issubset(set(blocked_actions))
        and isinstance(card.get("warnings"), list)
        and isinstance(card.get("limitations"), list)
    )


def _public_search_status_is_safe(payload: dict[str, object], text: str) -> bool:
    public_search = payload.get("public_search")
    return (
        payload.get("ok") is True
        and isinstance(public_search, dict)
        and public_search.get("implemented") is True
        and public_search.get("implementation_scope") == "local_prototype_backend"
        and public_search.get("hosted_public_deployment") is False
        and public_search.get("mode") == "local_index_only"
        and public_search.get("live_probes_enabled") is False
        and public_search.get("downloads_enabled") is False
        and public_search.get("installs_enabled") is False
        and public_search.get("uploads_enabled") is False
        and public_search.get("local_paths_enabled") is False
        and public_search.get("telemetry_enabled") is False
        and public_search.get("production_ready") is False
        and payload.get("index_status") == "generated_public_search_index"
        and isinstance(payload.get("index_document_count"), int)
        and int(payload["index_document_count"]) > 0
        and _has_no_private_path(text)
    )


def _has_no_private_path(text: str) -> bool:
    folded = text.replace("\\", "/").casefold()
    private_markers = (
        "c:/",
        "d:/",
        "/users/",
        "/home/",
        "/tmp/",
        "appdata/",
    )
    return not any(marker in folded for marker in private_markers)


def _request(
    app: WorkbenchWsgiApp,
    path: str,
    query: Mapping[str, str],
) -> SmokeHttpResponse:
    captured: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = headers

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": "GET",
                "PATH_INFO": path,
                "QUERY_STRING": urlencode(query),
                "wsgi.input": BytesIO(b""),
            },
            start_response,
        )
    )
    status = str(captured["status"])
    return SmokeHttpResponse(
        status_code=int(status.split(" ", 1)[0]),
        status_line=status,
        headers={key.lower(): value for key, value in captured["headers"]},
        body=body,
    )


def _route(path: str, query: Mapping[str, str]) -> str:
    if not query:
        return path
    return f"{path}?{urlencode(query)}"


if __name__ == "__main__":
    raise SystemExit(main())
