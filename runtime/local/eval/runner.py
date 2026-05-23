"""Runner for deterministic local route suites."""

from __future__ import annotations

import json
from typing import Any, Mapping
import urllib.parse
import urllib.request

from .assertions import (
    assert_absence_non_global,
    assert_html_contains,
    assert_html_not_contains,
    assert_json_shape,
    assert_no_mutation_controls,
    assert_route_rejected,
    assert_status_ok,
)
from .latency import now_counter, record_elapsed_ms
from .reports import build_json_report
from .suites import LocalEvalCase, LocalEvalSuite, get_default_local_eval_suites
from .validation import validate_localhost_base_url


class LocalEvalRunner:
    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = int(timeout_seconds)

    def run_suite(self, suite: LocalEvalSuite, base_url: str) -> dict[str, Any]:
        checked_url = validate_localhost_base_url(base_url)
        cases = [self._run_case(case, checked_url, suite.name) for case in suite.cases]
        failed = [case for case in cases if not case.get("passed")]
        return {
            "schema_version": "local_eval_suite_result.v0",
            "suite": suite.name,
            "status": "pass" if not failed else "fail",
            "purpose": suite.purpose,
            "case_count": len(cases),
            "passed_case_count": len(cases) - len(failed),
            "failed_case_count": len(failed),
            "cases": cases,
            "warnings": [],
            "limitations": ["deterministic localhost suite"],
        }

    def run_all(self, base_url: str) -> dict[str, Any]:
        checked_url = validate_localhost_base_url(base_url)
        suites = [self.run_suite(suite, checked_url) for suite in get_default_local_eval_suites()]
        return build_json_report(checked_url, suites)

    def _run_case(self, case: LocalEvalCase, base_url: str, suite_name: str) -> dict[str, Any]:
        started = now_counter()
        if case.method == "INPROC":
            response = self._run_inproc_case(case)
        else:
            response = self._fetch(base_url, case)
        elapsed = record_elapsed_ms(started)
        errors: list[str] = []
        try:
            self._assert_case(case, response)
        except Exception as exc:
            errors.append(str(exc))
        return {
            "schema_version": "local_eval_case_result.v0",
            "suite": suite_name,
            "case_id": case.case_id,
            "method": case.method,
            "path": case.path,
            "status_code": response.get("status_code", 0),
            "content_type": response.get("content_type", ""),
            "passed": not errors,
            "elapsed_ms": elapsed,
            "errors": errors,
            "warnings": list(response.get("warnings", [])),
            "limitations": list(case.notes) + list(response.get("limitations", [])),
        }

    def _fetch(self, base_url: str, case: LocalEvalCase) -> dict[str, Any]:
        url = _build_url(base_url, case.path, case.params)
        body = urllib.parse.urlencode(case.body or {}).encode("utf-8") if case.body else None
        request = urllib.request.Request(
            url,
            data=body if case.method != "GET" else None,
            method=case.method,
            headers={"Accept": "application/json,text/html,text/plain"},
        )
        if body is not None:
            request.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                return {
                    "status_code": int(response.getcode()),
                    "content_type": str(response.headers.get("Content-Type", "")),
                    "body": raw,
                    "payload": _parse_json(raw),
                    "warnings": [],
                    "limitations": [],
                }
        except Exception as exc:
            code = int(getattr(exc, "code", 0) or 0)
            if code:
                read = getattr(exc, "read", None)
                raw = read().decode("utf-8") if callable(read) else ""
                headers = getattr(exc, "headers", {}) or {}
                return {
                    "status_code": code,
                    "content_type": str(headers.get("Content-Type", "")) if hasattr(headers, "get") else "",
                    "body": raw,
                    "payload": _parse_json(raw),
                    "warnings": [],
                    "limitations": [],
                }
            return {
                "status_code": 0,
                "content_type": "",
                "body": "",
                "payload": None,
                "warnings": [str(exc)],
                "limitations": ["route fetch failed"],
            }

    def _run_inproc_case(self, case: LocalEvalCase) -> dict[str, Any]:
        if case.path == "worker_registry":
            from runtime.local.worker import get_default_worker_registry

            registry = get_default_worker_registry()
            blocked = set(registry.blocked_kinds())
            expected = {"source_probe_worker", "extraction_worker", "ai_model_worker"}
            ok = expected.issubset(blocked)
            return {
                "status_code": 200 if ok else 500,
                "content_type": "application/json",
                "body": "",
                "payload": {
                    "enabled_worker_kinds": list(registry.enabled_kinds()),
                    "blocked_worker_kinds": list(registry.blocked_kinds()),
                    "source_probe_worker_blocked": "source_probe_worker" in blocked,
                    "extraction_worker_blocked": "extraction_worker" in blocked,
                    "ai_model_worker_blocked": "ai_model_worker" in blocked,
                },
                "warnings": [],
                "limitations": ["worker registry was inspected without worker execution"],
            }
        return {"status_code": 500, "content_type": "application/json", "payload": {}, "warnings": ["unknown in-process case"], "limitations": []}

    def _assert_case(self, case: LocalEvalCase, response: Mapping[str, Any]) -> None:
        if case.method in {"POST", "PUT", "PATCH", "DELETE"} or case.expect_statuses != (200,):
            if all(status >= 400 for status in case.expect_statuses):
                assert_route_rejected(response, case.expect_statuses)
            else:
                assert_status_ok(response, case.expect_statuses)
        else:
            assert_status_ok(response, case.expect_statuses)
        body = str(response.get("body", ""))
        payload = response.get("payload")
        if case.expect_content == "json":
            assert_json_shape(payload, ())
        if case.expect_content == "html":
            if "text/html" not in str(response.get("content_type", "")):
                raise AssertionError("HTML content type is required")
            assert_no_mutation_controls(body)
            for marker in ("<script", "javascript:", "src=\"http://", "href=\"http://", "src=\"https://", "href=\"https://"):
                assert_html_not_contains(body, marker)
        if case.path.endswith("/absence") or case.path == "/api/v1/absence":
            assert_absence_non_global(payload if case.expect_content == "json" else body)
        text = json.dumps(payload, sort_keys=True) if payload is not None else body
        for marker in case.markers:
            if marker not in text:
                if case.case_id == "overlong" and response.get("status_code") in {400, 405}:
                    continue
                assert_html_contains(text, marker)
        for marker in case.absent_markers:
            assert_html_not_contains(text, marker)


def _build_url(base_url: str, path: str, params: Mapping[str, str] | None = None) -> str:
    split = urllib.parse.urlsplit(base_url)
    return urllib.parse.urlunsplit((split.scheme, split.netloc, path, urllib.parse.urlencode(params or {}), ""))


def _parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None
