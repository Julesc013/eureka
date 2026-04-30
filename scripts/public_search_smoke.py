from __future__ import annotations

import argparse
from dataclasses import dataclass
from io import BytesIO
import json
from pathlib import Path
import sys
from typing import Callable, Mapping
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


CREATED_BY_SLICE = "local_public_search_runtime_v0"


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
    checks = [
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
                and isinstance(payload.get("results"), list)
                and len(payload["results"]) > 0
            ),
            "200 governed public-search envelope with results",
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
        _expect_html(
            app,
            "html search",
            "/search",
            {"q": "windows 7 apps"},
            lambda text: "Eureka Public Search" in text and "local-index-only" in text and "Blocked actions" in text,
            "200 server-rendered public-search HTML",
        ),
        _expect_public_search_error(
            app,
            "forbidden index_path",
            "/api/v1/search",
            {"q": "archive", "index_path": "D:/private/eureka-index.sqlite3"},
            "local_paths_forbidden",
        ),
        _expect_public_search_error(
            app,
            "forbidden url",
            "/api/v1/search",
            {"q": "archive", "url": "https://example.invalid/"},
            "forbidden_parameter",
        ),
        _expect_public_search_error(
            app,
            "forbidden live probe",
            "/api/v1/search",
            {"q": "archive", "live_probe": "1"},
            "live_probes_disabled",
        ),
        _expect_public_search_error(
            app,
            "query too long",
            "/api/v1/search",
            {"q": "x" * 161},
            "query_too_long",
        ),
    ]
    passed_count = sum(1 for check in checks if check.passed)
    failed_count = len(checks) - passed_count
    return {
        "status": "passed" if failed_count == 0 else "failed",
        "created_by_slice": CREATED_BY_SLICE,
        "mode": "local_index_only",
        "total_checks": len(checks),
        "passed_checks": passed_count,
        "failed_checks": failed_count,
        "checks": [check.to_dict() for check in checks],
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
        and "D:/" not in text
        and "C:/" not in text
    )


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
