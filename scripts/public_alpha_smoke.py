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

from runtime.gateway.public_api import (
    build_demo_absence_public_api,
    build_demo_action_plan_public_api,
    build_demo_archive_resolution_evals_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_decomposition_public_api,
    build_demo_query_planner_public_api,
    build_demo_representation_selection_public_api,
    build_demo_representations_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import WebServerConfig, WorkbenchWsgiApp


CREATED_BY_SLICE = "public_alpha_deployment_readiness_review_v0"
PRIVATE_PATH_SENTINEL = "EUREKA_PRIVATE_PATH_SENTINEL_DO_NOT_LEAK"


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


def run_public_alpha_smoke() -> dict[str, object]:
    app = _build_public_alpha_app()
    checks: list[SmokeCheckResult] = []

    checks.append(
        _expect_json(
            app,
            "status",
            "/api/status",
            {},
            _status_payload_is_safe,
            "200 JSON with public_alpha mode, disabled local-path capabilities, and no private path leakage",
        )
    )
    checks.append(
        _expect_json(
            app,
            "source list",
            "/api/sources",
            {},
            lambda payload, text: isinstance(payload.get("source_count"), int),
            "200 JSON source registry listing",
        )
    )
    checks.append(
        _expect_json(
            app,
            "query plan",
            "/api/query-plan",
            {"q": "Windows 7 apps"},
            lambda payload, text: payload.get("status") == "planned",
            "200 JSON deterministic query plan",
        )
    )
    checks.append(
        _expect_json(
            app,
            "search",
            "/api/search",
            {"q": "synthetic"},
            lambda payload, text: payload.get("query") == "synthetic",
            "200 JSON deterministic search results",
        )
    )
    checks.append(
        _expect_json(
            app,
            "archive resolution evals",
            "/api/evals/archive-resolution",
            {},
            lambda payload, text: payload.get("status") == "evaluated",
            "200 JSON archive-resolution eval report",
        )
    )

    checks.extend(
        [
            _expect_blocked(
                app,
                "local index path",
                "/api/index/status",
                {"index_path": "D:/private/eureka-index.sqlite3"},
                "local_path_parameters_blocked",
            ),
            _expect_blocked(
                app,
                "run store root",
                "/api/runs",
                {"run_store_root": "D:/private/eureka-runs"},
                "local_path_parameters_blocked",
            ),
            _expect_blocked(
                app,
                "task store root",
                "/api/tasks",
                {"task_store_root": "D:/private/eureka-tasks"},
                "local_path_parameters_blocked",
            ),
            _expect_blocked(
                app,
                "memory store root",
                "/api/memories",
                {"memory_store_root": "D:/private/eureka-memory"},
                "local_path_parameters_blocked",
            ),
            _expect_blocked(
                app,
                "bundle path inspection",
                "/api/inspect/bundle",
                {"bundle_path": "D:/private/eureka-bundle.zip"},
                "local_path_parameters_blocked",
            ),
            _expect_blocked(
                app,
                "stored export root",
                "/api/stored",
                {
                    "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                    "store_root": "D:/private/eureka-store",
                },
                "local_path_parameters_blocked",
            ),
            _expect_blocked(
                app,
                "arbitrary output path",
                "/api/status",
                {"output": "D:/private/output.json"},
                "local_path_parameters_blocked",
            ),
            _expect_blocked(
                app,
                "fixture byte fetch",
                "/api/fetch",
                {
                    "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                    "representation_id": "rep.synthetic-demo-app.source",
                },
                "route_disabled_in_public_alpha",
            ),
        ]
    )

    passed_count = sum(1 for check in checks if check.passed)
    failed_count = len(checks) - passed_count
    return {
        "status": "passed" if failed_count == 0 else "failed",
        "created_by_slice": CREATED_BY_SLICE,
        "mode": "public_alpha",
        "total_checks": len(checks),
        "passed_checks": passed_count,
        "failed_checks": failed_count,
        "checks": [check.to_dict() for check in checks],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Eureka's local Public Alpha Safe Mode smoke checks.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a stable JSON smoke report instead of a plain-text summary.",
    )
    args = parser.parse_args(argv)

    report = run_public_alpha_smoke()
    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_smoke_report(report))
    return 0 if report["status"] == "passed" else 1


def format_smoke_report(report: Mapping[str, object]) -> str:
    lines = [
        "Public Alpha Smoke",
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


def _build_public_alpha_app() -> WorkbenchWsgiApp:
    config = WebServerConfig.public_alpha(
        index_root=PRIVATE_PATH_SENTINEL + "/index",
        run_store_root=PRIVATE_PATH_SENTINEL + "/runs",
        task_store_root=PRIVATE_PATH_SENTINEL + "/tasks",
        memory_store_root=PRIVATE_PATH_SENTINEL + "/memory",
        export_store_root=PRIVATE_PATH_SENTINEL + "/exports",
    )
    return WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        absence_public_api=build_demo_absence_public_api(),
        action_plan_public_api=build_demo_action_plan_public_api(),
        archive_resolution_evals_public_api=build_demo_archive_resolution_evals_public_api(),
        comparison_public_api=build_demo_comparison_public_api(),
        compatibility_public_api=build_demo_compatibility_public_api(),
        decomposition_public_api=build_demo_decomposition_public_api(),
        handoff_public_api=build_demo_representation_selection_public_api(),
        query_planner_public_api=build_demo_query_planner_public_api(),
        representations_public_api=build_demo_representations_public_api(),
        search_public_api=build_demo_search_public_api(),
        source_registry_public_api=build_demo_source_registry_public_api(),
        subject_states_public_api=build_demo_subject_states_public_api(),
        default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        server_config=config,
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
            name=name,
            route=route,
            expected=expected,
            observed_status=response.status_code,
            passed=False,
            code="unexpected_status",
            message=f"Expected HTTP 200, observed {response.status_line}.",
        )
    try:
        payload = response.json_body()
    except json.JSONDecodeError as error:
        return SmokeCheckResult(
            name=name,
            route=route,
            expected=expected,
            observed_status=response.status_code,
            passed=False,
            code="invalid_json",
            message=str(error),
        )
    passed = predicate(payload, response.text)
    return SmokeCheckResult(
        name=name,
        route=route,
        expected=expected,
        observed_status=response.status_code,
        passed=passed,
        code="ok" if passed else "payload_mismatch",
        message="Check passed." if passed else "JSON payload did not satisfy the smoke expectation.",
    )


def _expect_blocked(
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
    actual_code = str(payload.get("code") or "")
    passed = (
        response.status_code == 403
        and payload.get("status") == "blocked"
        and actual_code == expected_code
    )
    return SmokeCheckResult(
        name=name,
        route=route,
        expected=f"403 JSON blocked response with code {expected_code}",
        observed_status=response.status_code,
        passed=passed,
        code=actual_code or "missing_block_code",
        message="Check passed." if passed else f"Observed {response.status_line} with payload {payload!r}.",
    )


def _status_payload_is_safe(payload: dict[str, object], text: str) -> bool:
    disabled = payload.get("disabled_capabilities")
    return (
        payload.get("mode") == "public_alpha"
        and payload.get("safe_mode_enabled") is True
        and isinstance(disabled, list)
        and "caller_local_index_paths" in disabled
        and "caller_run_store_roots" in disabled
        and "caller_task_store_roots" in disabled
        and "caller_memory_store_roots" in disabled
        and "caller_export_store_roots" in disabled
        and payload.get("live_probes_enabled") is False
        and payload.get("live_internet_archive_enabled") is False
        and payload.get("downloads_enabled") is False
        and payload.get("local_paths_enabled") is False
        and payload.get("user_storage_enabled") is False
        and payload.get("deployment_approved") is False
        and payload.get("production_ready") is False
        and PRIVATE_PATH_SENTINEL not in text
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
    status_line = str(captured["status"])
    return SmokeHttpResponse(
        status_code=int(status_line.split(" ", 1)[0]),
        status_line=status_line,
        headers={key.lower(): value for key, value in captured["headers"]},
        body=body,
    )


def _route(path: str, query: Mapping[str, str]) -> str:
    if not query:
        return path
    return f"{path}?{urlencode(query)}"


if __name__ == "__main__":
    raise SystemExit(main())
