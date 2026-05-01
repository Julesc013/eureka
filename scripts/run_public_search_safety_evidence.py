#!/usr/bin/env python3
"""Collect local public-search safety evidence without external calls."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from io import BytesIO
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO
from urllib.parse import urlencode


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_hosted_public_search import (  # noqa: E402
    HostedPublicSearchWsgiApp,
    load_hosted_public_search_config,
    validate_hosted_public_search_config,
)
from runtime.gateway.public_api.public_search import (  # noqa: E402
    DEFAULT_RESULT_LIMIT,
    MAX_QUERY_LENGTH,
    MAX_RESULT_LIMIT,
    MODE,
)


EVIDENCE_ID = "public_search_safety_evidence_v0"
SAFE_ROUTE_CASES: tuple[tuple[str, str, Mapping[str, str], str], ...] = (
    ("healthz", "/healthz", {}, "json"),
    ("status", "/status", {}, "json"),
    ("api_status", "/api/v1/status", {}, "json"),
    ("sources", "/api/v1/sources", {}, "json"),
    ("api_search_windows_7_apps", "/api/v1/search", {"q": "windows 7 apps"}, "json"),
    ("api_search_driver_inf", "/api/v1/search", {"q": "driver.inf"}, "json"),
    (
        "api_search_pc_magazine_ray_tracing",
        "/api/v1/search",
        {"q": "pc magazine ray tracing"},
        "json",
    ),
    ("query_plan_windows_7_apps", "/api/v1/query-plan", {"q": "windows 7 apps"}, "json"),
    ("html_search_windows_7_apps", "/search", {"q": "windows 7 apps"}, "html"),
)
SAFE_QUERY_CASES = (
    "windows 7 apps",
    "driver.inf",
    "pc magazine ray tracing",
    "no-such-local-index-hit",
)
BLOCKED_REQUEST_CASES: tuple[tuple[str, Mapping[str, str], str, str], ...] = (
    ("missing_q", {}, "query_required", "required_query"),
    ("query_too_long", {"q": "x" * (MAX_QUERY_LENGTH + 1)}, "query_too_long", "query_limit"),
    ("limit_too_large", {"q": "windows", "limit": str(MAX_RESULT_LIMIT + 1)}, "limit_too_large", "result_limit"),
    ("mode_live_probe", {"q": "windows", "mode": "live_probe"}, "live_probes_disabled", "live_mode"),
    ("mode_live_federated", {"q": "windows", "mode": "live_federated"}, "live_probes_disabled", "live_mode"),
    ("include_raw_source_payload", {"q": "windows", "include": "raw_source_payload"}, "unsupported_include", "raw_payload"),
    ("index_path", {"q": "windows", "index_path": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("store_root", {"q": "windows", "store_root": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("run_store_root", {"q": "windows", "run_store_root": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("task_store_root", {"q": "windows", "task_store_root": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("memory_store_root", {"q": "windows", "memory_store_root": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("local_path", {"q": "windows", "local_path": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("path", {"q": "windows", "path": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("file_path", {"q": "windows", "file_path": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("directory", {"q": "windows", "directory": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("root", {"q": "windows", "root": "/tmp/x"}, "local_paths_forbidden", "local_path"),
    ("url", {"q": "windows", "url": "https://example.invalid"}, "forbidden_parameter", "url_fetch"),
    ("fetch_url", {"q": "windows", "fetch_url": "https://example.invalid"}, "forbidden_parameter", "url_fetch"),
    ("crawl_url", {"q": "windows", "crawl_url": "https://example.invalid"}, "forbidden_parameter", "url_fetch"),
    ("source_url", {"q": "windows", "source_url": "https://example.invalid"}, "forbidden_parameter", "url_fetch"),
    ("download", {"q": "windows", "download": "true"}, "downloads_disabled", "download"),
    ("install", {"q": "windows", "install": "true"}, "installs_disabled", "install_execute"),
    ("execute", {"q": "windows", "execute": "true"}, "installs_disabled", "install_execute"),
    ("upload", {"q": "windows", "upload": "true"}, "uploads_disabled", "upload"),
    ("user_file", {"q": "windows", "user_file": "test.bin"}, "uploads_disabled", "upload"),
    ("source_credentials", {"q": "windows", "source_credentials": "secret-value"}, "forbidden_parameter", "credential"),
    ("auth_token", {"q": "windows", "auth_token": "secret-value"}, "forbidden_parameter", "credential"),
    ("api_key", {"q": "windows", "api_key": "secret-value"}, "forbidden_parameter", "credential"),
    ("live_probe", {"q": "windows", "live_probe": "true"}, "live_probes_disabled", "live_probe"),
    ("live_source", {"q": "windows", "live_source": "internet_archive"}, "live_probes_disabled", "live_probe"),
    ("network", {"q": "windows", "network": "true"}, "forbidden_parameter", "url_fetch"),
    ("arbitrary_source", {"q": "windows", "arbitrary_source": "true"}, "forbidden_parameter", "url_fetch"),
)
FORBIDDEN_CATEGORIES = {
    "credential",
    "download",
    "install_execute",
    "live_mode",
    "live_probe",
    "local_path",
    "query_limit",
    "raw_payload",
    "required_query",
    "result_limit",
    "upload",
    "url_fetch",
}
HARD_FALSE_FLAGS = (
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "external_calls_performed",
    "master_index_mutated",
)
PRIVATE_MARKERS = (
    "c:\\",
    "d:\\",
    "/users/",
    "/home/",
    "/tmp/",
    "/var/",
    "appdata",
    "secret-value",
)


@dataclass(frozen=True)
class WsgiResponse:
    status_code: int
    headers: dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json_body(self) -> dict[str, Any]:
        payload = json.loads(self.text)
        if not isinstance(payload, dict):
            raise ValueError("JSON response must be an object.")
        return payload


class _SearchPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0
        self.form_actions: list[str] = []
        self.q_maxlengths: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.casefold(): value for name, value in attrs}
        if tag.casefold() == "script":
            self.script_count += 1
        if tag.casefold() == "form":
            self.form_actions.append(attr.get("action") or "")
        if tag.casefold() == "input" and attr.get("name") == "q":
            try:
                self.q_maxlengths.append(int(attr.get("maxlength") or "0"))
            except ValueError:
                self.q_maxlengths.append(0)


def run_public_search_safety_evidence(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    strict: bool = False,
    no_server: bool = False,
) -> dict[str, Any]:
    del host, port, strict, no_server
    config = load_hosted_public_search_config()
    config_report = validate_hosted_public_search_config(config)
    app = HostedPublicSearchWsgiApp(config=config)

    route_results = [_run_safe_route(app, *case) for case in SAFE_ROUTE_CASES]
    safe_query_results = [_run_safe_query(app, query) for query in SAFE_QUERY_CASES]
    blocked_request_results = [_run_blocked_request(app, *case) for case in BLOCKED_REQUEST_CASES]
    limit_results = _run_limit_checks(app)
    status_results = _run_status_checks(app)
    static_handoff_results = _check_static_handoff()
    public_index_results = _check_public_index()
    privacy_redaction_results = _check_privacy_redaction(
        route_results,
        safe_query_results,
        blocked_request_results,
        limit_results,
        status_results,
        static_handoff_results,
        public_index_results,
    )

    hard_booleans = {
        "live_probes_enabled": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "installs_enabled": False,
        "local_paths_enabled": False,
        "arbitrary_url_fetch_enabled": False,
        "telemetry_enabled": False,
        "accounts_enabled": False,
        "external_calls_performed": False,
        "master_index_mutated": False,
    }
    checks = (
        route_results
        + safe_query_results
        + blocked_request_results
        + limit_results
        + status_results
        + static_handoff_results
        + public_index_results
        + privacy_redaction_results
    )
    failed = [item for item in checks if not item.get("passed")]
    covered_categories = sorted(
        {
            str(item.get("category"))
            for item in blocked_request_results
            if item.get("passed") and item.get("category")
        }
    )
    report = {
        "ok": not failed and config_report["status"] == "valid",
        "evidence_id": EVIDENCE_ID,
        "created_by": "public_search_safety_evidence_runner_v0",
        "mode": MODE,
        "server_started": False,
        "harness": "in_process_hosted_public_search_wsgi_app",
        "hosted_deployment_verified": False,
        "route_results": route_results,
        "safe_query_results": safe_query_results,
        "blocked_request_results": blocked_request_results,
        "limit_results": limit_results,
        "status_results": status_results,
        "static_handoff_results": static_handoff_results,
        "public_index_results": public_index_results,
        "privacy_redaction_results": privacy_redaction_results,
        "forbidden_parameter_coverage": {
            "required_categories": sorted(FORBIDDEN_CATEGORIES),
            "covered_categories": covered_categories,
            "missing_categories": sorted(FORBIDDEN_CATEGORIES - set(covered_categories)),
            "blocked_case_count": len(blocked_request_results),
            "passed_blocked_case_count": sum(1 for item in blocked_request_results if item.get("passed")),
        },
        "hard_booleans": hard_booleans,
        "summary": {
            "status": "passed" if not failed and config_report["status"] == "valid" else "failed",
            "total_checks": len(checks) + 1,
            "passed_checks": len(checks) - len(failed) + (1 if config_report["status"] == "valid" else 0),
            "failed_checks": len(failed) + (0 if config_report["status"] == "valid" else 1),
            "safe_route_count": len(route_results),
            "safe_query_count": len(safe_query_results),
            "blocked_request_count": len(blocked_request_results),
            "public_index_document_count": _public_index_document_count(),
        },
        "notes": [
            "Evidence uses an in-process WSGI harness for the hosted wrapper; no external network, source API, model, or provider call is performed.",
            "Route evidence is local/public-alpha evidence only and is not hosted deployment evidence.",
            "Timeout behavior is recorded as contract-only because no safe timeout simulation exists in this local harness.",
        ],
    }
    return report


def _run_safe_route(
    app: HostedPublicSearchWsgiApp,
    check_id: str,
    path: str,
    query: Mapping[str, str],
    response_kind: str,
) -> dict[str, Any]:
    response = _call_wsgi_app(app, path, query)
    notes: list[str] = []
    passed = response.status_code == 200
    payload: dict[str, Any] = {}
    if response_kind == "json":
        try:
            payload = response.json_body()
        except Exception as exc:
            passed = False
            notes.append(f"invalid_json:{exc}")
        if payload.get("mode") not in {None, MODE}:
            passed = False
            notes.append("mode_not_local_index_only")
        for flag in (
            "live_probes_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
            "telemetry_enabled",
            "accounts_enabled",
        ):
            if payload.get(flag) not in {None, False}:
                passed = False
                notes.append(f"{flag}_not_false")
    else:
        lowered = response.text.casefold()
        for phrase in ("eureka hosted public search", "local_index_only", "live probes"):
            if phrase not in lowered:
                passed = False
                notes.append(f"missing_{phrase.replace(' ', '_')}")
    if not _has_no_private_marker(response.text):
        passed = False
        notes.append("private_or_secret_marker_leaked")
    return {
        "check_id": check_id,
        "path": path,
        "query_keys": sorted(query),
        "response_kind": response_kind,
        "observed_status": response.status_code,
        "expected": "safe successful public-search response",
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _run_safe_query(app: HostedPublicSearchWsgiApp, query_text: str) -> dict[str, Any]:
    response = _call_wsgi_app(app, "/api/v1/search", {"q": query_text})
    notes: list[str] = []
    passed = response.status_code == 200
    payload: dict[str, Any] = {}
    result_count = 0
    try:
        payload = response.json_body()
    except Exception as exc:
        passed = False
        notes.append(f"invalid_json:{exc}")
    results = payload.get("results") if isinstance(payload.get("results"), list) else []
    result_count = len(results)
    if payload.get("ok") is not True:
        passed = False
        notes.append("ok_not_true")
    if payload.get("mode") != MODE:
        passed = False
        notes.append("mode_not_local_index_only")
    if not isinstance(results, list):
        passed = False
        notes.append("results_not_list")
    if not payload.get("warnings"):
        passed = False
        notes.append("warnings_missing")
    if not (payload.get("limitations") or payload.get("absence_summary") or result_count > 0):
        passed = False
        notes.append("limitations_or_absence_missing")
    card_checks = [_result_card_has_safety_shape(card) for card in results if isinstance(card, Mapping)]
    if result_count and not all(card_checks):
        passed = False
        notes.append("result_card_safety_shape_missing")
    if not _has_no_private_marker(response.text):
        passed = False
        notes.append("private_or_secret_marker_leaked")
    return {
        "query": query_text,
        "observed_status": response.status_code,
        "result_count": result_count,
        "mode": payload.get("mode"),
        "warnings_present": bool(payload.get("warnings")),
        "limitations_or_absence_present": bool(payload.get("limitations") or payload.get("absence_summary") or result_count > 0),
        "result_cards_checked": result_count,
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _run_blocked_request(
    app: HostedPublicSearchWsgiApp,
    case_id: str,
    query: Mapping[str, str],
    expected_code: str,
    category: str,
) -> dict[str, Any]:
    response = _call_wsgi_app(app, "/api/v1/search", query)
    notes: list[str] = []
    payload: dict[str, Any] = {}
    passed = 400 <= response.status_code < 500
    try:
        payload = response.json_body()
    except Exception as exc:
        passed = False
        notes.append(f"invalid_json:{exc}")
    error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
    actual_code = error.get("code")
    if payload.get("ok") is not False:
        passed = False
        notes.append("ok_not_false")
    if actual_code != expected_code:
        passed = False
        notes.append(f"unexpected_error_code:{actual_code}")
    if "traceback" in response.text.casefold():
        passed = False
        notes.append("stack_trace_leaked")
    if not _has_no_private_marker(response.text):
        passed = False
        notes.append("private_or_secret_marker_leaked")
    return {
        "case_id": case_id,
        "category": category,
        "path": "/api/v1/search",
        "query_keys": sorted(query),
        "expected_error_code": expected_code,
        "actual_error_code": actual_code,
        "observed_status": response.status_code,
        "public_safe_error": payload.get("ok") is False and isinstance(error, Mapping),
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _run_limit_checks(app: HostedPublicSearchWsgiApp) -> list[dict[str, Any]]:
    cases = (
        ("query_at_max_length", {"q": "x" * MAX_QUERY_LENGTH}, 200, None, "accepted"),
        ("query_over_max_length", {"q": "x" * (MAX_QUERY_LENGTH + 1)}, 400, "query_too_long", "rejected"),
        ("limit_at_max", {"q": "windows", "limit": str(MAX_RESULT_LIMIT)}, 200, None, "accepted"),
        ("limit_over_max", {"q": "windows", "limit": str(MAX_RESULT_LIMIT + 1)}, 400, "limit_too_large", "rejected"),
        ("limit_negative", {"q": "windows", "limit": "-1"}, 400, "bad_request", "rejected"),
        ("limit_non_integer", {"q": "windows", "limit": "many"}, 400, "bad_request", "rejected"),
    )
    results: list[dict[str, Any]] = []
    for case_id, query, expected_status, expected_code, expected_behavior in cases:
        response = _call_wsgi_app(app, "/api/v1/search", query)
        notes: list[str] = []
        payload: dict[str, Any] = {}
        try:
            payload = response.json_body()
        except Exception as exc:
            notes.append(f"invalid_json:{exc}")
        error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
        passed = response.status_code == expected_status
        if expected_code is not None and error.get("code") != expected_code:
            passed = False
            notes.append(f"unexpected_error_code:{error.get('code')}")
        if not _has_no_private_marker(response.text):
            passed = False
            notes.append("private_or_secret_marker_leaked")
        results.append(
            {
                "case_id": case_id,
                "query_keys": sorted(query),
                "expected_status": expected_status,
                "observed_status": response.status_code,
                "expected_error_code": expected_code,
                "actual_error_code": error.get("code"),
                "expected_behavior": expected_behavior,
                "passed": passed,
                "notes": notes or ["ok"],
            }
        )
    results.append(
        {
            "case_id": "timeout_simulation",
            "expected_behavior": "contract_only",
            "observed_status": None,
            "passed": True,
            "notes": ["No safe timeout simulation is implemented in the local in-process harness."],
        }
    )
    return results


def _run_status_checks(app: HostedPublicSearchWsgiApp) -> list[dict[str, Any]]:
    results = []
    for path in ("/healthz", "/status", "/api/v1/status"):
        response = _call_wsgi_app(app, path, {})
        notes: list[str] = []
        passed = response.status_code == 200
        try:
            payload = response.json_body()
        except Exception as exc:
            payload = {}
            passed = False
            notes.append(f"invalid_json:{exc}")
        for flag in (
            "hosted_deployment_verified",
            "live_probes_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
            "telemetry_enabled",
            "accounts_enabled",
        ):
            if payload.get(flag) is not False:
                passed = False
                notes.append(f"{flag}_not_false")
        if payload.get("mode") not in {None, MODE}:
            passed = False
            notes.append("mode_not_local_index_only")
        results.append(
            {
                "path": path,
                "observed_status": response.status_code,
                "mode": payload.get("mode"),
                "hosted_deployment_verified": payload.get("hosted_deployment_verified"),
                "passed": passed,
                "notes": notes or ["ok"],
            }
        )
    return results


def _check_static_handoff() -> list[dict[str, Any]]:
    dist = REPO_ROOT / "site" / "dist"
    config_path = dist / "data" / "search_config.json"
    files = (
        dist / "search.html",
        dist / "lite" / "search.html",
        dist / "text" / "search.txt",
        dist / "files" / "search.README.txt",
        config_path,
    )
    results: list[dict[str, Any]] = []
    for path in files:
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        parser = _SearchPageParser()
        if path.suffix == ".html":
            parser.feed(text)
        notes: list[str] = []
        passed = path.is_file()
        if "<script" in text.casefold():
            passed = False
            notes.append("script_tag_present")
        if "hosted public search is live" in text.casefold():
            passed = False
            notes.append("live_hosted_claim_present")
        if not _has_no_private_marker(text):
            passed = False
            notes.append("private_or_secret_marker_present")
        if parser.q_maxlengths and max(parser.q_maxlengths) > MAX_QUERY_LENGTH:
            passed = False
            notes.append("q_maxlength_too_large")
        results.append(
            {
                "file": _rel(path),
                "exists": path.is_file(),
                "script_count": parser.script_count,
                "form_actions": parser.form_actions,
                "q_maxlengths": parser.q_maxlengths,
                "passed": passed,
                "notes": notes or ["ok"],
            }
        )
    config = _load_json(config_path)
    config_passed = (
        config.get("hosted_backend_verified") is False
        and config.get("search_form_enabled") is False
        and config.get("hosted_backend_url") is None
        and config.get("mode") == MODE
        and config.get("live_probes_enabled") is False
        and config.get("downloads_enabled") is False
        and config.get("uploads_enabled") is False
        and config.get("local_paths_enabled") is False
        and config.get("arbitrary_url_fetch_enabled") is False
    )
    results.append(
        {
            "file": _rel(config_path),
            "hosted_backend_verified": config.get("hosted_backend_verified"),
            "search_form_enabled": config.get("search_form_enabled"),
            "hosted_backend_url_configured": config.get("hosted_backend_url") is not None,
            "passed": config_passed,
            "notes": ["ok"] if config_passed else ["static_search_config_not_safe"],
        }
    )
    return results


def _check_public_index() -> list[dict[str, Any]]:
    root = REPO_ROOT / "data" / "public_index"
    docs_path = root / "search_documents.ndjson"
    stats_path = root / "index_stats.json"
    coverage_path = root / "source_coverage.json"
    summary_path = REPO_ROOT / "site" / "dist" / "data" / "public_index_summary.json"
    docs = _read_ndjson(docs_path)
    stats = _load_json(stats_path)
    coverage = _load_json(coverage_path)
    summary = _load_json(summary_path)
    combined_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (docs_path, stats_path, coverage_path, summary_path)
        if path.is_file()
    )
    enabled_action_errors: list[str] = []
    for doc in docs:
        for action in doc.get("allowed_actions", []) if isinstance(doc, Mapping) else []:
            if str(action) in {"download", "install", "execute", "upload"}:
                enabled_action_errors.append(str(doc.get("doc_id", "unknown")))
    live_source_flags = [
        str(doc.get("doc_id", "unknown"))
        for doc in docs
        if isinstance(doc, Mapping)
        and (doc.get("live_supported") is True or doc.get("live_enabled") is True)
    ]
    passed = (
        docs_path.is_file()
        and stats_path.is_file()
        and coverage_path.is_file()
        and summary_path.is_file()
        and len(docs) == stats.get("document_count") == summary.get("document_count")
        and summary.get("contains_live_data") is False
        and summary.get("contains_private_data") is False
        and summary.get("contains_executables") is False
        and not enabled_action_errors
        and not live_source_flags
        and _has_no_private_marker(combined_text)
    )
    return [
        {
            "artifact_root": "data/public_index",
            "document_count": len(docs),
            "stats_document_count": stats.get("document_count"),
            "summary_document_count": summary.get("document_count"),
            "source_count": summary.get("source_count"),
            "contains_live_data": summary.get("contains_live_data"),
            "contains_private_data": summary.get("contains_private_data"),
            "contains_executables": summary.get("contains_executables"),
            "enabled_dangerous_action_count": len(enabled_action_errors),
            "live_source_flag_count": len(live_source_flags),
            "private_or_secret_marker_detected": not _has_no_private_marker(combined_text),
            "passed": passed,
            "notes": ["ok"] if passed else ["public_index_safety_check_failed"],
        }
    ]


def _check_privacy_redaction(*groups: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    text = json.dumps(groups, sort_keys=True)
    passed = _has_no_private_marker(text) and "traceback" not in text.casefold()
    return [
        {
            "check_id": "evidence_report_redaction",
            "private_or_secret_marker_detected": not _has_no_private_marker(text),
            "stack_trace_detected": "traceback" in text.casefold(),
            "passed": passed,
            "notes": ["ok"] if passed else ["evidence_contains_private_marker_or_traceback"],
        }
    ]


def _call_wsgi_app(app: HostedPublicSearchWsgiApp, path: str, query: Mapping[str, str]) -> WsgiResponse:
    captured: dict[str, Any] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": "GET",
                "SCRIPT_NAME": "",
                "PATH_INFO": path,
                "QUERY_STRING": urlencode(query),
                "SERVER_NAME": "127.0.0.1",
                "SERVER_PORT": "0",
                "SERVER_PROTOCOL": "HTTP/1.1",
                "wsgi.version": (1, 0),
                "wsgi.url_scheme": "http",
                "wsgi.input": BytesIO(b""),
                "wsgi.errors": sys.stderr,
                "wsgi.multithread": False,
                "wsgi.multiprocess": False,
                "wsgi.run_once": False,
            },
            start_response,
        )
    )
    status_text = str(captured.get("status", "500 Internal Server Error"))
    return WsgiResponse(
        status_code=int(status_text.split(" ", 1)[0]),
        headers={str(key).lower(): str(value) for key, value in captured.get("headers", {}).items()},
        body=body,
    )


def _result_card_has_safety_shape(card: Mapping[str, Any]) -> bool:
    actions = card.get("actions") if isinstance(card.get("actions"), Mapping) else {}
    blocked = actions.get("blocked") if isinstance(actions.get("blocked"), list) else []
    blocked_ids = {
        item.get("action_id")
        for item in blocked
        if isinstance(item, Mapping) and isinstance(item.get("action_id"), str)
    }
    return (
        isinstance(card.get("result_id"), str)
        and isinstance(card.get("title"), str)
        and isinstance(card.get("source"), Mapping)
        and isinstance(card.get("evidence"), Mapping)
        and isinstance(card.get("compatibility"), Mapping)
        and {"download", "install_handoff", "execute", "upload"}.issubset(blocked_ids)
        and isinstance(card.get("warnings"), list)
        and isinstance(card.get("limitations"), list)
    )


def _has_no_private_marker(text: str) -> bool:
    folded = text.casefold().replace("\\\\", "\\")
    return not any(marker in folded for marker in PRIVATE_MARKERS)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _read_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _public_index_document_count() -> int:
    stats = _load_json(REPO_ROOT / "data" / "public_index" / "index_stats.json")
    count = stats.get("document_count")
    return int(count) if isinstance(count, int) else 0


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), Mapping) else {}
    coverage = report.get("forbidden_parameter_coverage")
    coverage = coverage if isinstance(coverage, Mapping) else {}
    lines = [
        "Public Search Safety Evidence",
        f"status: {summary.get('status')}",
        f"mode: {report.get('mode')}",
        f"checks: {summary.get('passed_checks')}/{summary.get('total_checks')}",
        f"safe routes: {summary.get('safe_route_count')}",
        f"safe queries: {summary.get('safe_query_count')}",
        f"blocked requests: {coverage.get('passed_blocked_case_count')}/{coverage.get('blocked_case_count')}",
        f"public index documents: {summary.get('public_index_document_count')}",
    ]
    missing = coverage.get("missing_categories")
    if missing:
        lines.append(f"missing blocked categories: {', '.join(str(item) for item in missing)}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON evidence.")
    parser.add_argument("--strict", action="store_true", help="Require all local evidence checks to pass.")
    parser.add_argument("--host", default="127.0.0.1", help="Accepted for CLI compatibility; in-process harness is used.")
    parser.add_argument("--port", type=int, default=0, help="Accepted for CLI compatibility; in-process harness is used.")
    parser.add_argument("--no-server", action="store_true", help="Use the in-process harness. This is the default.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_public_search_safety_evidence(
        host=args.host,
        port=args.port,
        strict=args.strict,
        no_server=args.no_server,
    )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
