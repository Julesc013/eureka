#!/usr/bin/env python3
"""Run a local hosted-mode rehearsal for Eureka public search.

This script starts the P54 hosted wrapper on localhost, exercises the public
routes over HTTP, and shuts the wrapper down. It is intentionally local-only:
non-local base URLs are rejected, no external source APIs are called, and no
deployment evidence is claimed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.gateway.public_api.public_search import (  # noqa: E402
    MAX_QUERY_LENGTH,
    MAX_RESULT_LIMIT,
    MODE,
)
from scripts.run_hosted_public_search import (  # noqa: E402
    load_hosted_public_search_config,
    validate_hosted_public_search_config,
)


REHEARSAL_ID = "hosted_public_search_rehearsal_v0"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
DEFAULT_TIMEOUT_MS = 5000
SAFE_ENV = {
    "EUREKA_PUBLIC_MODE": "1",
    "EUREKA_SEARCH_MODE": "local_index_only",
    "EUREKA_ALLOW_LIVE_PROBES": "0",
    "EUREKA_ALLOW_DOWNLOADS": "0",
    "EUREKA_ALLOW_UPLOADS": "0",
    "EUREKA_ALLOW_LOCAL_PATHS": "0",
    "EUREKA_ALLOW_ARBITRARY_URL_FETCH": "0",
    "EUREKA_ALLOW_INSTALL_ACTIONS": "0",
    "EUREKA_ALLOW_TELEMETRY": "0",
    "EUREKA_MAX_QUERY_LEN": "160",
    "EUREKA_MAX_RESULTS": "20",
    "EUREKA_GLOBAL_TIMEOUT_MS": "5000",
    "EUREKA_OPERATOR_KILL_SWITCH": "0",
    "PYTHONUNBUFFERED": "1",
}
SAFE_ROUTE_CASES: tuple[tuple[str, str, Mapping[str, str], str], ...] = (
    ("healthz", "/healthz", {}, "json"),
    ("status", "/status", {}, "json"),
    ("api_status", "/api/v1/status", {}, "json"),
    ("sources", "/api/v1/sources", {}, "json"),
    ("api_search_windows_7_apps", "/api/v1/search", {"q": "windows 7 apps"}, "json"),
    ("api_search_driver_inf", "/api/v1/search", {"q": "driver.inf"}, "json"),
    ("api_search_pc_magazine_ray_tracing", "/api/v1/search", {"q": "pc magazine ray tracing"}, "json"),
    ("query_plan_windows_7_apps", "/api/v1/query-plan", {"q": "windows 7 apps"}, "json"),
    ("html_search_windows_7_apps", "/search", {"q": "windows 7 apps"}, "html"),
)
SAFE_QUERY_CASES = (
    "windows 7 apps",
    "driver.inf",
    "pc magazine ray tracing",
    "firefox xp",
    "no-such-local-index-hit",
)
BLOCKED_REQUEST_CASES: tuple[tuple[str, Mapping[str, str], str, str], ...] = (
    ("missing_q", {}, "query_required", "required_query"),
    ("query_too_long", {"q": "x" * (MAX_QUERY_LENGTH + 1)}, "query_too_long", "query_limit"),
    ("limit_too_large", {"q": "windows", "limit": str(MAX_RESULT_LIMIT + 1)}, "limit_too_large", "result_limit"),
    ("limit_negative", {"q": "windows", "limit": "-1"}, "bad_request", "result_limit"),
    ("limit_non_integer", {"q": "windows", "limit": "abc"}, "bad_request", "result_limit"),
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
    "hosted_deployment_performed",
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
    "traceback",
)


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: dict[str, str]
    body: str

    def json_body(self) -> dict[str, Any]:
        payload = json.loads(self.body)
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


def run_hosted_public_search_rehearsal(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    timeout_ms: int = DEFAULT_TIMEOUT_MS,
    skip_startup: bool = False,
    base_url: str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    del strict
    if skip_startup:
        if not base_url:
            return _failed_preflight("skip_startup_requires_base_url")
        if not _is_local_base_url(base_url):
            return _failed_preflight("non_local_base_url_rejected", base_url=base_url)
        chosen_base_url = base_url.rstrip("/")
        process: subprocess.Popen[str] | None = None
        server_started = False
        startup_results = [{"check_id": "skip_startup", "passed": True, "notes": ["using_existing_local_base_url"]}]
    else:
        if host not in LOCAL_HOSTS:
            return _failed_preflight("non_local_host_rejected", host=host)
        chosen_port = _choose_port(host) if port == 0 else port
        chosen_base_url = f"http://{host}:{chosen_port}"
        env = _safe_env(chosen_port)
        config = load_hosted_public_search_config(host=host, port=chosen_port, environ=env)
        config_report = validate_hosted_public_search_config(config)
        startup_results = [
            {
                "check_id": "hosted_wrapper_check_config",
                "passed": config_report.get("status") == "valid",
                "status": config_report.get("status"),
                "errors": list(config_report.get("errors", [])),
                "warnings": list(config_report.get("warnings", [])),
            }
        ]
        if config_report.get("status") != "valid":
            return _assemble_report(
                base_url=chosen_base_url,
                server_started=False,
                startup_results=startup_results,
                route_results=[],
                safe_query_results=[],
                blocked_request_results=[],
                static_handoff_results=[],
                public_index_results=[],
                deployment_template_results=[],
                process_output={},
            )
        process = _start_wrapper(host, chosen_port, env)
        server_started = True
        health = _wait_for_health(chosen_base_url, timeout_ms)
        startup_results.append(health)

    try:
        route_results = [_run_route(chosen_base_url, *case) for case in SAFE_ROUTE_CASES]
        safe_query_results = [_run_safe_query(chosen_base_url, query) for query in SAFE_QUERY_CASES]
        blocked_request_results = [_run_blocked_request(chosen_base_url, *case) for case in BLOCKED_REQUEST_CASES]
        static_handoff_results = _check_static_handoff()
        public_index_results = _check_public_index()
        deployment_template_results = _check_deployment_templates()
    finally:
        process_output = _stop_process(process) if process is not None else {}

    return _assemble_report(
        base_url=chosen_base_url,
        server_started=server_started,
        startup_results=startup_results,
        route_results=route_results,
        safe_query_results=safe_query_results,
        blocked_request_results=blocked_request_results,
        static_handoff_results=static_handoff_results,
        public_index_results=public_index_results,
        deployment_template_results=deployment_template_results,
        process_output=process_output,
    )


def _failed_preflight(reason: str, **extra: Any) -> dict[str, Any]:
    report = {
        "ok": False,
        "rehearsal_id": REHEARSAL_ID,
        "mode": "hosted_local_rehearsal",
        "server_started": False,
        "base_url": extra.get("base_url"),
        "startup_results": [{"check_id": reason, "passed": False, "notes": [reason]}],
        "route_results": [],
        "safe_query_results": [],
        "blocked_request_results": [],
        "static_handoff_results": [],
        "public_index_results": [],
        "deployment_template_results": [],
        "hard_booleans": _hard_booleans(),
        "summary": {"status": "failed", "failed_checks": 1, "passed_checks": 0, "total_checks": 1},
        "notes": ["Non-local hosted rehearsal targets are rejected by design."],
    }
    report.update(extra)
    return report


def _assemble_report(
    *,
    base_url: str,
    server_started: bool,
    startup_results: list[dict[str, Any]],
    route_results: list[dict[str, Any]],
    safe_query_results: list[dict[str, Any]],
    blocked_request_results: list[dict[str, Any]],
    static_handoff_results: list[dict[str, Any]],
    public_index_results: list[dict[str, Any]],
    deployment_template_results: list[dict[str, Any]],
    process_output: Mapping[str, Any],
) -> dict[str, Any]:
    checks = (
        startup_results
        + route_results
        + safe_query_results
        + blocked_request_results
        + static_handoff_results
        + public_index_results
        + deployment_template_results
    )
    failed = [item for item in checks if item.get("passed") is not True]
    hard_booleans = _hard_booleans()
    return {
        "ok": not failed,
        "rehearsal_id": REHEARSAL_ID,
        "created_by": "hosted_public_search_rehearsal_runner_v0",
        "mode": "hosted_local_rehearsal",
        "public_search_mode": MODE,
        "server_started": server_started,
        "base_url": base_url,
        "env": dict(SAFE_ENV),
        "startup_results": startup_results,
        "route_results": route_results,
        "safe_query_results": safe_query_results,
        "blocked_request_results": blocked_request_results,
        "static_handoff_results": static_handoff_results,
        "public_index_results": public_index_results,
        "deployment_template_results": deployment_template_results,
        "process_output": process_output,
        "hard_booleans": hard_booleans,
        "summary": {
            "status": "passed" if not failed else "failed",
            "total_checks": len(checks),
            "passed_checks": len(checks) - len(failed),
            "failed_checks": len(failed),
            "safe_route_count": len(route_results),
            "safe_query_count": len(safe_query_results),
            "blocked_request_count": len(blocked_request_results),
            "passed_blocked_request_count": sum(1 for item in blocked_request_results if item.get("passed")),
            "public_index_document_count": _public_index_document_count(),
        },
        "notes": [
            "The rehearsal starts the hosted wrapper on localhost only and performs HTTP checks against that local process.",
            "No provider API, deployed service, external source, live probe, model, credential, upload, download, account, telemetry, arbitrary URL fetch, index mutation, pack import, or master-index mutation is used.",
            "This is not hosted deployment evidence and does not prove edge rate limits.",
        ],
    }


def _start_wrapper(host: str, port: int, env: Mapping[str, str]) -> subprocess.Popen[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_hosted_public_search.py"),
        "--host",
        host,
        "--port",
        str(port),
    ]
    return subprocess.Popen(
        command,
        cwd=str(REPO_ROOT),
        env=dict(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def _stop_process(process: subprocess.Popen[str]) -> dict[str, Any]:
    if process.poll() is None:
        process.terminate()
    try:
        stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate(timeout=5)
    return {
        "returncode": process.returncode,
        "stdout_excerpt": _redact_excerpt(stdout),
        "stderr_excerpt": _redact_excerpt(stderr),
    }


def _wait_for_health(base_url: str, timeout_ms: int) -> dict[str, Any]:
    deadline = time.monotonic() + (timeout_ms / 1000)
    attempts = 0
    last_error = ""
    while time.monotonic() < deadline:
        attempts += 1
        response = _http_get(base_url, "/healthz", {})
        if response.status_code == 200:
            payload = _safe_json(response)
            passed = payload.get("mode") == MODE and _payload_false_flags(payload)
            return {
                "check_id": "startup_healthz",
                "path": "/healthz",
                "observed_status": response.status_code,
                "attempts": attempts,
                "passed": passed,
                "notes": ["ok"] if passed else ["healthz_flags_not_safe"],
            }
        last_error = response.body[:160]
        time.sleep(0.05)
    return {
        "check_id": "startup_healthz",
        "path": "/healthz",
        "observed_status": None,
        "attempts": attempts,
        "passed": False,
        "notes": ["startup_timeout", _redact_excerpt(last_error)],
    }


def _run_route(base_url: str, check_id: str, path: str, query: Mapping[str, str], response_kind: str) -> dict[str, Any]:
    response = _http_get(base_url, path, query)
    notes: list[str] = []
    passed = response.status_code == 200
    payload: dict[str, Any] = {}
    if response_kind == "json":
        payload = _safe_json(response)
        if payload.get("mode") not in {None, MODE}:
            passed = False
            notes.append("mode_not_local_index_only")
        if not _payload_false_flags(payload):
            passed = False
            notes.append("safety_flags_not_false")
    else:
        lowered = response.body.casefold()
        for phrase in ("eureka hosted public search", "local_index_only", "live probes"):
            if phrase not in lowered:
                passed = False
                notes.append(f"missing_{phrase.replace(' ', '_')}")
    if not _has_no_private_marker(response.body):
        passed = False
        notes.append("private_or_secret_marker_leaked")
    return {
        "check_id": check_id,
        "path": path,
        "query_keys": sorted(query),
        "response_kind": response_kind,
        "observed_status": response.status_code,
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _run_safe_query(base_url: str, query_text: str) -> dict[str, Any]:
    response = _http_get(base_url, "/api/v1/search", {"q": query_text})
    payload = _safe_json(response)
    results = payload.get("results") if isinstance(payload.get("results"), list) else []
    notes: list[str] = []
    passed = response.status_code == 200
    if payload.get("ok") is not True:
        passed = False
        notes.append("ok_not_true")
    if payload.get("mode") != MODE:
        passed = False
        notes.append("mode_not_local_index_only")
    if not isinstance(results, list):
        passed = False
        notes.append("results_not_list")
    if not (payload.get("warnings") or payload.get("limitations") or payload.get("absence_summary") or results):
        passed = False
        notes.append("warnings_limitations_or_absence_missing")
    if results and not all(_result_card_has_safety_shape(item) for item in results if isinstance(item, Mapping)):
        passed = False
        notes.append("result_card_safety_shape_missing")
    if not _has_no_private_marker(response.body):
        passed = False
        notes.append("private_or_secret_marker_leaked")
    return {
        "query": query_text,
        "observed_status": response.status_code,
        "result_count": len(results),
        "mode": payload.get("mode"),
        "warnings_or_limitations_present": bool(payload.get("warnings") or payload.get("limitations") or payload.get("absence_summary") or results),
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _run_blocked_request(
    base_url: str,
    case_id: str,
    query: Mapping[str, str],
    expected_code: str,
    category: str,
) -> dict[str, Any]:
    response = _http_get(base_url, "/api/v1/search", query)
    payload = _safe_json(response)
    error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
    notes: list[str] = []
    passed = 400 <= response.status_code < 500
    if payload.get("ok") is not False:
        passed = False
        notes.append("ok_not_false")
    if error.get("code") != expected_code:
        passed = False
        notes.append(f"unexpected_error_code:{error.get('code')}")
    if not _has_no_private_marker(response.body):
        passed = False
        notes.append("private_or_secret_marker_leaked")
    return {
        "case_id": case_id,
        "category": category,
        "path": "/api/v1/search",
        "query_keys": sorted(query),
        "expected_error_code": expected_code,
        "actual_error_code": error.get("code"),
        "observed_status": response.status_code,
        "public_safe_error": payload.get("ok") is False and isinstance(error, Mapping),
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _check_static_handoff() -> list[dict[str, Any]]:
    dist = REPO_ROOT / "site" / "dist"
    config_path = dist / "data" / "search_config.json"
    summary_path = dist / "data" / "public_index_summary.json"
    pages = (
        dist / "search.html",
        dist / "lite" / "search.html",
        dist / "text" / "search.txt",
        dist / "files" / "search.README.txt",
        config_path,
        summary_path,
    )
    results: list[dict[str, Any]] = []
    for path in pages:
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
        if parser.q_maxlengths and max(parser.q_maxlengths) > MAX_QUERY_LENGTH:
            passed = False
            notes.append("q_maxlength_too_large")
        if not _has_no_private_marker(text):
            passed = False
            notes.append("private_or_secret_marker_present")
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
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (docs_path, stats_path, coverage_path, summary_path)
        if path.is_file()
    )
    dangerous_actions = []
    live_flags = []
    for doc in docs:
        if not isinstance(doc, Mapping):
            continue
        for action in doc.get("allowed_actions", []) if isinstance(doc.get("allowed_actions"), list) else []:
            if str(action) in {"download", "install", "execute", "upload"}:
                dangerous_actions.append(str(doc.get("doc_id", "unknown")))
        if doc.get("live_supported") is True or doc.get("live_enabled") is True:
            live_flags.append(str(doc.get("doc_id", "unknown")))
    source_count = len(coverage.get("sources", [])) if isinstance(coverage.get("sources"), list) else summary.get("source_count")
    passed = (
        docs_path.is_file()
        and stats_path.is_file()
        and coverage_path.is_file()
        and summary_path.is_file()
        and len(docs) == stats.get("document_count") == summary.get("document_count")
        and summary.get("contains_live_data") is False
        and summary.get("contains_private_data") is False
        and summary.get("contains_executables") is False
        and not dangerous_actions
        and not live_flags
        and _has_no_private_marker(combined)
    )
    return [
        {
            "artifact_root": "data/public_index",
            "document_count": len(docs),
            "stats_document_count": stats.get("document_count"),
            "summary_document_count": summary.get("document_count"),
            "source_count": source_count,
            "contains_live_data": summary.get("contains_live_data"),
            "contains_private_data": summary.get("contains_private_data"),
            "contains_executables": summary.get("contains_executables"),
            "enabled_dangerous_action_count": len(dangerous_actions),
            "live_source_flag_count": len(live_flags),
            "passed": passed,
            "notes": ["ok"] if passed else ["public_index_compatibility_check_failed"],
        }
    ]


def _check_deployment_templates() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    dockerfile = REPO_ROOT / "Dockerfile"
    render_yaml = REPO_ROOT / "deploy" / "render" / "render.yaml"
    for path, template_id in ((dockerfile, "dockerfile"), (render_yaml, "render_template")):
        if not path.exists():
            results.append(
                {
                    "template_id": template_id,
                    "path": _rel(path),
                    "exists": False,
                    "passed": True,
                    "notes": ["template_not_present_optional"],
                }
            )
            continue
        text = path.read_text(encoding="utf-8")
        folded = text.casefold()
        notes: list[str] = []
        passed = True
        for env_name in (
            "EUREKA_ALLOW_LIVE_PROBES",
            "EUREKA_ALLOW_DOWNLOADS",
            "EUREKA_ALLOW_UPLOADS",
            "EUREKA_ALLOW_LOCAL_PATHS",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH",
            "EUREKA_ALLOW_INSTALL_ACTIONS",
            "EUREKA_ALLOW_TELEMETRY",
        ):
            if f"{env_name.casefold()}=1" in folded or f"{env_name.casefold()} true" in folded:
                passed = False
                notes.append(f"{env_name}_enabled")
        if template_id == "dockerfile" and "scripts/run_hosted_public_search.py" not in text:
            passed = False
            notes.append("hosted_wrapper_command_missing")
        if "local_index_only" not in text:
            passed = False
            notes.append("local_index_only_missing")
        if "deployment evidence" in folded and "not deployment evidence" not in folded and "not deployed" not in folded:
            passed = False
            notes.append("deployment_claim_ambiguous")
        results.append(
            {
                "template_id": template_id,
                "path": _rel(path),
                "exists": True,
                "passed": passed,
                "notes": notes or ["ok"],
            }
        )
    return results


def _http_get(base_url: str, path: str, query: Mapping[str, str]) -> HttpResponse:
    url = base_url.rstrip("/") + path
    if query:
        url += "?" + urlencode(query)
    request = Request(url, method="GET", headers={"User-Agent": "eureka-local-hosted-rehearsal/0"})
    try:
        with urlopen(request, timeout=5) as response:  # nosec - local-only URL is validated.
            body = response.read().decode("utf-8", errors="replace")
            return HttpResponse(status_code=int(response.status), headers=dict(response.headers.items()), body=body)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return HttpResponse(status_code=int(exc.code), headers=dict(exc.headers.items()), body=body)
    except (TimeoutError, socket.timeout, OSError) as exc:
        return HttpResponse(status_code=0, headers={}, body=str(exc))
    except URLError as exc:
        return HttpResponse(status_code=0, headers={}, body=str(exc.reason))


def _safe_json(response: HttpResponse) -> dict[str, Any]:
    try:
        return response.json_body()
    except Exception:
        return {}


def _payload_false_flags(payload: Mapping[str, Any]) -> bool:
    for flag in (
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
        if payload.get(flag) not in {None, False}:
            return False
    return True


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
    )


def _choose_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _safe_env(port: int) -> dict[str, str]:
    env = dict(os.environ)
    env.update(SAFE_ENV)
    env["PORT"] = str(port)
    return env


def _is_local_base_url(base_url: str) -> bool:
    parsed = urlparse(base_url)
    return parsed.scheme == "http" and (parsed.hostname or "").casefold() in LOCAL_HOSTS


def _hard_booleans() -> dict[str, bool]:
    return {
        "hosted_deployment_performed": False,
        "hosted_deployment_verified": False,
        "live_probes_enabled": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "installs_enabled": False,
        "local_paths_enabled": False,
        "arbitrary_url_fetch_enabled": False,
        "telemetry_enabled": False,
        "accounts_enabled": False,
        "external_calls_performed": False,
        "ai_runtime_enabled": False,
        "master_index_mutated": False,
    }


def _has_no_private_marker(text: str) -> bool:
    folded = text.casefold().replace("\\\\", "\\")
    return not any(marker in folded for marker in PRIVATE_MARKERS)


def _redact_excerpt(text: str | None, limit: int = 4000) -> str:
    if not text:
        return ""
    cleaned = text.replace(str(REPO_ROOT), "<repo>").replace("\\", "/")
    cleaned = cleaned.replace("secret-value", "<redacted>")
    return cleaned[:limit]


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
    lines = [
        "Hosted Public Search Rehearsal",
        f"status: {summary.get('status')}",
        f"mode: {report.get('mode')}",
        f"base_url: {report.get('base_url')}",
        f"server_started: {report.get('server_started')}",
        f"checks: {summary.get('passed_checks')}/{summary.get('total_checks')}",
        f"safe routes: {summary.get('safe_route_count')}",
        f"safe queries: {summary.get('safe_query_count')}",
        f"blocked requests: {summary.get('passed_blocked_request_count')}/{summary.get('blocked_request_count')}",
        f"public index documents: {summary.get('public_index_document_count')}",
    ]
    return "\n".join(lines) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON rehearsal evidence.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero on any required failure.")
    parser.add_argument("--host", default="127.0.0.1", help="Local bind host. Non-local hosts are rejected.")
    parser.add_argument("--port", type=int, default=0, help="Local bind port. 0 chooses a free local port.")
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS, help="Startup timeout in milliseconds.")
    parser.add_argument("--skip-startup", action="store_true", help="Use an already-running local base URL.")
    parser.add_argument("--base-url", help="Already-running local base URL for --skip-startup.")
    return parser


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = run_hosted_public_search_rehearsal(
        host=args.host,
        port=args.port,
        timeout_ms=args.timeout_ms,
        skip_startup=args.skip_startup,
        base_url=args.base_url,
        strict=args.strict,
    )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
