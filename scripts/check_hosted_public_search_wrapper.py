#!/usr/bin/env python3
"""Run in-process smoke checks for the hosted public search wrapper."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from io import BytesIO
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_hosted_public_search import (  # noqa: E402
    HostedPublicSearchWsgiApp,
    load_hosted_public_search_config,
    validate_hosted_public_search_config,
)


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    path: str
    passed: bool
    status_code: int | None
    expected: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "path": self.path,
            "passed": self.passed,
            "status_code": self.status_code,
            "expected": self.expected,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class WsgiResponse:
    status_code: int
    headers: dict[str, str]
    body_bytes: bytes

    @property
    def body_text(self) -> str:
        return self.body_bytes.decode("utf-8")

    def json(self) -> dict[str, Any]:
        payload = json.loads(self.body_text)
        if not isinstance(payload, dict):
            raise AssertionError("JSON response must be an object.")
        return payload


def run_hosted_public_search_wrapper_checks() -> dict[str, Any]:
    config = load_hosted_public_search_config()
    config_report = validate_hosted_public_search_config(config)
    app = HostedPublicSearchWsgiApp(config=config)
    checks: list[CheckResult] = []

    if config_report["status"] != "valid":
        checks.append(
            CheckResult(
                check_id="check_config",
                path="--check-config",
                passed=False,
                status_code=None,
                expected="valid safe hosted wrapper config",
                notes="; ".join(str(error) for error in config_report["errors"]),
            )
        )
    else:
        checks.append(
            CheckResult(
                check_id="check_config",
                path="--check-config",
                passed=True,
                status_code=None,
                expected="valid safe hosted wrapper config",
                notes="Safe defaults accepted.",
            )
        )

    _expect_json(app, checks, "healthz", "/healthz", expected_status=200, required_false_flags=True)
    _expect_json(app, checks, "status_top_level", "/status", expected_status=200, required_false_flags=True)
    _expect_json(app, checks, "status_api", "/api/v1/status", expected_status=200, required_false_flags=True)
    _expect_json(
        app,
        checks,
        "api_search",
        "/api/v1/search?" + urlencode({"q": "windows 7 apps"}),
        expected_status=200,
        required_false_flags=True,
        required_body_keys=("results", "result_count"),
    )
    _expect_json(
        app,
        checks,
        "query_plan",
        "/api/v1/query-plan?" + urlencode({"q": "windows 7 apps"}),
        expected_status=200,
        required_false_flags=True,
        required_body_keys=("query_plan",),
    )
    _expect_json(app, checks, "sources", "/api/v1/sources", expected_status=200, required_false_flags=True)
    _expect_html(
        app,
        checks,
        "html_search",
        "/search?" + urlencode({"q": "windows 7 apps"}),
        expected_status=200,
    )

    for parameter in ("index_path", "url", "live_probe", "download", "upload"):
        _expect_blocked(
            app,
            checks,
            check_id=f"blocked_{parameter}",
            path="/api/v1/search?" + urlencode({"q": "windows 7 apps", parameter: "1"}),
            parameter=parameter,
        )
    _expect_blocked(
        app,
        checks,
        check_id="blocked_too_long_query",
        path="/api/v1/search?" + urlencode({"q": "x" * 161}),
        parameter="q",
        expected_code="query_too_long",
    )

    failed = [check for check in checks if not check.passed]
    return {
        "status": "passed" if not failed else "failed",
        "created_by": "hosted_public_search_wrapper_check_v0",
        "mode": "local_index_only",
        "total_checks": len(checks),
        "passed_checks": len(checks) - len(failed),
        "failed_checks": len(failed),
        "checks": [check.to_dict() for check in checks],
        "hard_booleans": {
            "hosted_backend_deployed": False,
            "hosted_deployment_verified": False,
            "dynamic_backend_deployed": False,
            "live_probes_enabled": False,
            "downloads_enabled": False,
            "uploads_enabled": False,
            "local_paths_enabled": False,
            "arbitrary_url_fetch_enabled": False,
            "telemetry_enabled": False,
            "accounts_enabled": False,
            "external_calls_enabled": False,
            "ai_runtime_enabled": False,
        },
        "errors": [check.notes for check in failed],
    }


def _expect_json(
    app: HostedPublicSearchWsgiApp,
    checks: list[CheckResult],
    check_id: str,
    path: str,
    *,
    expected_status: int,
    required_false_flags: bool,
    required_body_keys: Sequence[str] = (),
) -> None:
    response = _call_wsgi_app(app, path)
    passed = response.status_code == expected_status
    notes: list[str] = []
    try:
        payload = response.json()
    except Exception as exc:  # pragma: no cover - defensive check payload
        passed = False
        payload = {}
        notes.append(f"invalid JSON: {exc}")
    for key in required_body_keys:
        if key not in payload:
            passed = False
            notes.append(f"missing key {key}")
    if required_false_flags:
        for key in (
            "hosted_backend_deployed",
            "hosted_deployment_verified",
            "dynamic_backend_deployed",
            "live_probes_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
            "telemetry_enabled",
            "accounts_enabled",
            "external_calls_enabled",
            "ai_runtime_enabled",
        ):
            if payload.get(key) is not False:
                passed = False
                notes.append(f"{key} was not false")
    if payload.get("mode") not in {None, "local_index_only"}:
        passed = False
        notes.append("mode was not local_index_only")
    if check_id in {"status_top_level", "status_api", "api_search"}:
        if payload.get("public_index_present") is not True:
            passed = False
            notes.append("public_index_present was not true")
        if payload.get("index_status") not in {None, "generated_public_search_index"}:
            passed = False
            notes.append("index_status was not generated_public_search_index")
        if "index_document_count" in payload and not (
            isinstance(payload.get("index_document_count"), int)
            and int(payload["index_document_count"]) > 0
        ):
            passed = False
            notes.append("index_document_count was not positive")
    checks.append(
        CheckResult(
            check_id=check_id,
            path=path,
            passed=passed,
            status_code=response.status_code,
            expected=f"HTTP {expected_status} JSON with hosted-safe false flags",
            notes="; ".join(notes) if notes else "OK",
        )
    )


def _expect_html(
    app: HostedPublicSearchWsgiApp,
    checks: list[CheckResult],
    check_id: str,
    path: str,
    *,
    expected_status: int,
) -> None:
    response = _call_wsgi_app(app, path)
    text = response.body_text.casefold()
    passed = response.status_code == expected_status
    notes: list[str] = []
    for phrase in ("eureka hosted public search", "local_index_only", "live probes"):
        if phrase not in text:
            passed = False
            notes.append(f"missing phrase {phrase!r}")
    checks.append(
        CheckResult(
            check_id=check_id,
            path=path,
            passed=passed,
            status_code=response.status_code,
            expected=f"HTTP {expected_status} no-JS HTML search page",
            notes="; ".join(notes) if notes else "OK",
        )
    )


def _expect_blocked(
    app: HostedPublicSearchWsgiApp,
    checks: list[CheckResult],
    *,
    check_id: str,
    path: str,
    parameter: str,
    expected_code: str | None = None,
) -> None:
    response = _call_wsgi_app(app, path)
    passed = 400 <= response.status_code < 500
    notes: list[str] = []
    try:
        payload = response.json()
    except Exception as exc:  # pragma: no cover - defensive check payload
        passed = False
        payload = {}
        notes.append(f"invalid JSON: {exc}")
    error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
    if error.get("parameter") != parameter:
        passed = False
        notes.append(f"error parameter was {error.get('parameter')!r}")
    if expected_code and error.get("code") != expected_code:
        passed = False
        notes.append(f"error code was {error.get('code')!r}")
    checks.append(
        CheckResult(
            check_id=check_id,
            path=path,
            passed=passed,
            status_code=response.status_code,
            expected=f"blocked public-safe error for {parameter}",
            notes="; ".join(notes) if notes else "OK",
        )
    )


def _call_wsgi_app(app: HostedPublicSearchWsgiApp, path_with_query: str) -> WsgiResponse:
    if "?" in path_with_query:
        path, query = path_with_query.split("?", 1)
    else:
        path, query = path_with_query, ""
    captured: dict[str, Any] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": "GET",
        "SCRIPT_NAME": "",
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "SERVER_NAME": "127.0.0.1",
        "SERVER_PORT": "8080",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": BytesIO(b""),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    body = b"".join(app(environ, start_response))
    status_text = str(captured.get("status", "500 Internal Server Error"))
    return WsgiResponse(
        status_code=int(status_text.split(" ", 1)[0]),
        headers={str(key): str(value) for key, value in captured.get("headers", {}).items()},
        body_bytes=body,
    )


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Hosted public search wrapper check",
        f"status: {report['status']}",
        f"mode: {report['mode']}",
        f"checks: {report['passed_checks']}/{report['total_checks']}",
    ]
    for check in report["checks"]:
        mark = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- {mark} {check['check_id']}: {check['notes']}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = run_hosted_public_search_wrapper_checks()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
