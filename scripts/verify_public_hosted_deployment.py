#!/usr/bin/env python3
"""Verify configured public hosted deployment evidence for Eureka.

The verifier is intentionally narrow. It reads explicitly configured Eureka
static/backend URLs from CLI arguments, environment variables, or repo
publication inventory, then checks only those bases. It does not crawl links,
does not follow redirects, does not call external source APIs, and writes no
files.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import socket
import ssl
import sys
from typing import Any, Mapping, Sequence, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ID = "public_hosted_deployment_evidence_v0"
DEFAULT_TIMEOUT_MS = 5000
STATUS_VALUES = {
    "not_configured",
    "configured_unverified",
    "verified_passed",
    "verified_failed",
    "unreachable",
    "unsafe_failed",
    "operator_gated",
    "auth_unavailable",
    "evidence_unavailable",
    "blocked",
}
STATIC_ENV_NAMES = (
    "EUREKA_PUBLIC_STATIC_URL",
    "EUREKA_STATIC_SITE_URL",
    "EUREKA_DEPLOYMENT_EVIDENCE_URL",
)
BACKEND_ENV_NAMES = (
    "EUREKA_PUBLIC_BACKEND_URL",
    "EUREKA_HOSTED_BACKEND_URL",
)
SECRET_QUERY_KEYS = {
    "api_key",
    "auth_token",
    "authorization",
    "credential",
    "credentials",
    "key",
    "password",
    "secret",
    "source_credentials",
    "token",
}
EUREKA_REPO_HOSTS = {
    "julesc013.github.io",
    "julesc013.github.io.",
}
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
SAFE_QUERY_CASES = (
    "windows 7 apps",
    "driver.inf",
    "pc magazine ray tracing",
    "no-such-local-index-hit",
)
BACKEND_ROUTE_CASES: tuple[tuple[str, str, Mapping[str, str], str], ...] = (
    ("healthz", "/healthz", {}, "json"),
    ("status", "/status", {}, "json"),
    ("api_status", "/api/v1/status", {}, "json"),
    ("sources", "/api/v1/sources", {}, "json"),
    ("api_search_windows_7_apps", "/api/v1/search", {"q": "windows 7 apps"}, "json"),
    ("query_plan_windows_7_apps", "/api/v1/query-plan", {"q": "windows 7 apps"}, "json"),
    ("html_search_windows_7_apps", "/search", {"q": "windows 7 apps"}, "html"),
)
BLOCKED_REQUEST_CASES: tuple[tuple[str, Mapping[str, str], str], ...] = (
    ("q_too_long", {"q": "x" * 161}, "query_too_long"),
    ("limit_too_large", {"q": "windows", "limit": "9999"}, "limit_too_large"),
    ("mode_live_probe", {"q": "windows", "mode": "live_probe"}, "live_probes_disabled"),
    ("mode_live_federated", {"q": "windows", "mode": "live_federated"}, "live_probes_disabled"),
    ("include_raw_source_payload", {"q": "windows", "include": "raw_source_payload"}, "unsupported_include"),
    ("index_path", {"q": "windows", "index_path": "/tmp/x"}, "local_paths_forbidden"),
    ("store_root", {"q": "windows", "store_root": "/tmp/x"}, "local_paths_forbidden"),
    ("local_path", {"q": "windows", "local_path": "/tmp/x"}, "local_paths_forbidden"),
    ("path", {"q": "windows", "path": "/tmp/x"}, "local_paths_forbidden"),
    ("file_path", {"q": "windows", "file_path": "/tmp/x"}, "local_paths_forbidden"),
    ("directory", {"q": "windows", "directory": "/tmp/x"}, "local_paths_forbidden"),
    ("root", {"q": "windows", "root": "/tmp/x"}, "local_paths_forbidden"),
    ("url", {"q": "windows", "url": "https://example.invalid"}, "forbidden_parameter"),
    ("fetch_url", {"q": "windows", "fetch_url": "https://example.invalid"}, "forbidden_parameter"),
    ("crawl_url", {"q": "windows", "crawl_url": "https://example.invalid"}, "forbidden_parameter"),
    ("source_url", {"q": "windows", "source_url": "https://example.invalid"}, "forbidden_parameter"),
    ("download", {"q": "windows", "download": "true"}, "downloads_disabled"),
    ("install", {"q": "windows", "install": "true"}, "installs_disabled"),
    ("execute", {"q": "windows", "execute": "true"}, "installs_disabled"),
    ("upload", {"q": "windows", "upload": "true"}, "uploads_disabled"),
    ("source_credentials", {"q": "windows", "source_credentials": "secret-value"}, "forbidden_parameter"),
    ("auth_token", {"q": "windows", "auth_token": "secret-value"}, "forbidden_parameter"),
    ("api_key", {"q": "windows", "api_key": "secret-value"}, "forbidden_parameter"),
    ("live_probe", {"q": "windows", "live_probe": "true"}, "live_probes_disabled"),
    ("live_source", {"q": "windows", "live_source": "internet_archive"}, "live_probes_disabled"),
    ("network", {"q": "windows", "network": "true"}, "forbidden_parameter"),
    ("arbitrary_source", {"q": "windows", "arbitrary_source": "true"}, "forbidden_parameter"),
)
FALSE_STATUS_FLAGS = (
    "live_probes_enabled",
    "source_connectors_enabled",
    "external_source_calls_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "external_calls_performed",
)


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


@dataclass(frozen=True)
class ConfiguredUrl:
    url: str
    source: str
    explicit: bool


@dataclass(frozen=True)
class HttpResult:
    url: str
    status_code: int | None
    headers: dict[str, str]
    content_type: str | None
    body: str
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status_code is not None and 200 <= self.status_code < 300

    def json_body(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.body)
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}


def verify_public_hosted_deployment(
    *,
    static_url: str | None = None,
    backend_url: str | None = None,
    from_env: bool = False,
    from_repo_config: bool = False,
    timeout_ms: int = DEFAULT_TIMEOUT_MS,
    strict: bool = False,
) -> dict[str, Any]:
    warnings: list[str] = []
    limitations: list[str] = []
    notes: list[str] = [
        "Only explicitly configured static/backend URLs are eligible for HTTP checks.",
        "Redirects are recorded but not followed.",
        "No deployment, provider API, external source API, model API, source connector, telemetry, account, upload, download, install, arbitrary URL fetch, or index/cache/ledger mutation is performed.",
    ]

    static_candidates: list[ConfiguredUrl] = []
    backend_candidates: list[ConfiguredUrl] = []
    if static_url:
        static_candidates.append(ConfiguredUrl(static_url, "cli", True))
    if backend_url:
        backend_candidates.append(ConfiguredUrl(backend_url, "cli", True))
    if from_env:
        static_candidates.extend(_urls_from_env(STATIC_ENV_NAMES))
        backend_candidates.extend(_urls_from_env(BACKEND_ENV_NAMES))
    if from_repo_config:
        repo_static, repo_backend = _urls_from_repo_config()
        static_candidates.extend(repo_static)
        backend_candidates.extend(repo_backend)

    static_config = _choose_valid_url(static_candidates, role="static", warnings=warnings)
    backend_config = _choose_valid_url(backend_candidates, role="backend", warnings=warnings)

    static_result = _verify_static_site(static_config, backend_config, timeout_ms)
    backend_result = _verify_backend(backend_config, timeout_ms)
    public_index_results = static_result["public_index_results"]
    static_handoff_results = static_result["static_handoff_results"]

    static_status = static_result["status"]
    backend_status = backend_result["status"]
    route_status = _aggregate_route_status(backend_result["route_results"], backend_config is not None)
    safety_status = _aggregate_safety_status(backend_result["safe_query_results"], backend_result["blocked_request_results"], backend_config is not None)
    tls_results = _tls_results(static_config, backend_config, static_result, backend_result)
    cors_results = _header_results("cors", static_result, backend_result)
    cache_header_results = _header_results("cache", static_result, backend_result)
    rate_limit_results = _rate_limit_results(static_result, backend_result, backend_config is not None)
    privacy_logging_telemetry_results = _privacy_logging_telemetry_results(backend_result)
    status_flags = backend_result["status_flags"] or static_result["status_flags"]

    static_verified = static_status == "verified_passed"
    backend_verified = backend_status == "verified_passed"
    deployment_verified = static_verified and backend_verified
    hard_booleans = _hard_booleans(
        static_verified=static_verified,
        backend_verified=backend_verified,
        deployment_verified=deployment_verified,
        status_flags=status_flags,
    )
    ok = _calculate_ok(
        strict=strict,
        static_config=static_config,
        backend_config=backend_config,
        static_status=static_status,
        backend_status=backend_status,
        safety_status=safety_status,
    )
    if backend_config is None:
        limitations.append("No hosted backend URL is configured; backend route, safe-query, blocked-request, CORS, telemetry, and rate-limit evidence are operator-gated.")
    if static_config is None:
        limitations.append("No public static URL is configured; static deployment evidence is operator-gated.")
    if rate_limit_results.get("status") != "verified_passed":
        limitations.append("Rate-limit or edge evidence is unavailable unless response headers or operator evidence are recorded.")

    return {
        "ok": ok,
        "evidence_id": EVIDENCE_ID,
        "static_url": static_config.url if static_config else None,
        "static_url_source": static_config.source if static_config else "unavailable",
        "backend_url": backend_config.url if backend_config else None,
        "backend_url_source": backend_config.source if backend_config else "unavailable",
        "static_site_status": static_status,
        "hosted_backend_status": backend_status,
        "search_handoff_status": static_result["search_handoff_status"],
        "route_verification_status": route_status,
        "safety_verification_status": safety_status,
        "tls_status": tls_results["status"],
        "cors_status": cors_results["status"],
        "cache_header_status": cache_header_results["status"],
        "rate_limit_status": rate_limit_results["status"],
        "logging_telemetry_status": privacy_logging_telemetry_results["status"],
        "route_results": backend_result["route_results"],
        "static_route_results": static_result.get("static_route_results", []),
        "safe_query_results": backend_result["safe_query_results"],
        "blocked_request_results": backend_result["blocked_request_results"],
        "status_flags": status_flags,
        "static_handoff_results": static_handoff_results,
        "public_index_results": public_index_results,
        "tls_results": tls_results,
        "cors_results": cors_results,
        "cache_header_results": cache_header_results,
        "rate_limit_results": rate_limit_results,
        "privacy_logging_telemetry_results": privacy_logging_telemetry_results,
        "hard_booleans": hard_booleans,
        "warnings": warnings + static_result["warnings"] + backend_result["warnings"],
        "limitations": limitations + static_result["limitations"] + backend_result["limitations"],
        "notes": notes,
    }


def _urls_from_env(names: Sequence[str]) -> list[ConfiguredUrl]:
    urls: list[ConfiguredUrl] = []
    for name in names:
        value = os.environ.get(name)
        if value:
            urls.append(ConfiguredUrl(value, f"env:{name}", True))
    return urls


def _urls_from_repo_config() -> tuple[list[ConfiguredUrl], list[ConfiguredUrl]]:
    static_urls: list[ConfiguredUrl] = []
    backend_urls: list[ConfiguredUrl] = []
    deployment_targets = _load_json(REPO_ROOT / "control" / "inventory" / "publication" / "deployment_targets.json")
    for target in deployment_targets.get("targets", []) if isinstance(deployment_targets.get("targets"), list) else []:
        if not isinstance(target, Mapping):
            continue
        kind = target.get("kind")
        if kind == "static":
            url = target.get("canonical_base_url")
            if isinstance(url, str) and url.strip():
                static_urls.append(ConfiguredUrl(url, "repo:control/inventory/publication/deployment_targets.json", False))
        if target.get("id") == "public_search_backend":
            for key in ("base_url", "hosted_url"):
                url = target.get(key)
                if isinstance(url, str) and url.strip():
                    backend_urls.append(ConfiguredUrl(url, "repo:control/inventory/publication/deployment_targets.json", False))

    search_config = _load_json(REPO_ROOT / "site" / "dist" / "data" / "search_config.json")
    hosted_url = search_config.get("hosted_backend_url")
    if isinstance(hosted_url, str) and hosted_url.strip():
        backend_urls.append(ConfiguredUrl(hosted_url, "repo:site/dist/data/search_config.json", False))

    live_handoff = _load_json(REPO_ROOT / "control" / "inventory" / "publication" / "live_backend_handoff.json")
    for key in ("hosted_backend_url", "backend_url", "public_backend_url"):
        url = live_handoff.get(key)
        if isinstance(url, str) and url.strip():
            backend_urls.append(ConfiguredUrl(url, "repo:control/inventory/publication/live_backend_handoff.json", False))
    return static_urls, backend_urls


def _choose_valid_url(candidates: Sequence[ConfiguredUrl], *, role: str, warnings: list[str]) -> ConfiguredUrl | None:
    seen: set[str] = set()
    for candidate in candidates:
        raw = candidate.url.strip()
        if not raw or raw in seen:
            continue
        seen.add(raw)
        parsed = urlparse(raw)
        if parsed.scheme not in {"http", "https"}:
            warnings.append(f"{role} URL from {candidate.source} rejected: scheme is not http/https.")
            continue
        if parsed.username or parsed.password:
            warnings.append(f"{role} URL from {candidate.source} rejected: credentials in URL are forbidden.")
            continue
        if not parsed.hostname:
            warnings.append(f"{role} URL from {candidate.source} rejected: hostname missing.")
            continue
        if not candidate.explicit and not _looks_like_repo_eureka_url(parsed):
            warnings.append(f"{role} URL from {candidate.source} rejected: repo-config URL is not a recognized Eureka public URL.")
            continue
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", parsed.query, ""))
        return ConfiguredUrl(clean_url, candidate.source, candidate.explicit)
    return None


def _looks_like_repo_eureka_url(parsed: Any) -> bool:
    host = (parsed.hostname or "").casefold()
    if host in EUREKA_REPO_HOSTS and (parsed.path or "/").startswith("/eureka"):
        return True
    return host in LOCAL_HOSTS


def _verify_static_site(
    static_config: ConfiguredUrl | None,
    backend_config: ConfiguredUrl | None,
    timeout_ms: int,
) -> dict[str, Any]:
    if static_config is None:
        return {
            "status": "not_configured",
            "search_handoff_status": "not_configured",
            "responses": {},
            "static_handoff_results": _missing_static_handoff_results(),
            "public_index_results": [{"status": "not_configured", "checked": False, "notes": ["No static URL configured."]}],
            "status_flags": _default_static_status_flags(),
            "warnings": [],
            "limitations": ["Static URL unavailable; static hosting must be verified by an operator."],
        }

    root_url = _with_trailing_slash(static_config.url)
    checks = {
        "root": root_url,
        "search_page": urljoin(root_url, "search.html"),
        "search_config": urljoin(root_url, "data/search_config.json"),
        "public_index_summary": urljoin(root_url, "data/public_index_summary.json"),
    }
    responses = {name: _fetch(url, timeout_ms=timeout_ms) for name, url in checks.items()}
    warnings: list[str] = []
    limitations: list[str] = []
    notes: list[str] = []

    response_statuses = [response.status_code for response in responses.values()]
    if any(status is None for status in response_statuses):
        status = "unreachable"
    elif any((status or 0) >= 400 for status in response_statuses):
        status = "verified_failed"
    elif any(300 <= (status or 0) < 400 for status in response_statuses):
        status = "configured_unverified"
    else:
        status = "verified_passed"

    config_payload = responses["search_config"].json_body()
    index_summary_payload = responses["public_index_summary"].json_body()
    handoff_result = _review_static_search_config(config_payload, backend_config)
    public_index_result = _review_public_index_summary(index_summary_payload)
    if not handoff_result["passed"]:
        status = "verified_failed" if status == "verified_passed" else status
        warnings.extend(handoff_result["notes"])
    if not public_index_result["passed"]:
        status = "verified_failed" if status == "verified_passed" else status
        warnings.extend(public_index_result["notes"])
    if status == "verified_passed":
        notes.append("Static root, search page, search_config, and public_index_summary returned successful responses.")
    elif status == "configured_unverified":
        limitations.append("One or more static checks returned a redirect; redirects are not followed by this verifier.")

    route_rows = [
        {
            "check": name,
            "url": _redact_url(response.url),
            "status_code": response.status_code,
            "content_type": response.content_type,
            "status": _status_for_response(response),
            "headers": _selected_headers(response.headers),
            "error": _redact_text(response.error),
        }
        for name, response in responses.items()
    ]
    return {
        "status": status,
        "search_handoff_status": "verified_passed" if handoff_result["passed"] and status in {"verified_passed", "configured_unverified"} else "operator_gated",
        "responses": responses,
        "static_route_results": route_rows,
        "static_handoff_results": [handoff_result],
        "public_index_results": [public_index_result],
        "status_flags": _status_flags_from_static_config(config_payload),
        "warnings": warnings,
        "limitations": limitations,
        "notes": notes,
    }


def _verify_backend(backend_config: ConfiguredUrl | None, timeout_ms: int) -> dict[str, Any]:
    if backend_config is None:
        return {
            "status": "not_configured",
            "route_results": _missing_route_results(),
            "safe_query_results": _missing_safe_query_results(),
            "blocked_request_results": _missing_blocked_request_results(),
            "responses": {},
            "status_flags": {},
            "warnings": [],
            "limitations": ["Hosted backend URL unavailable; hosted route and safety checks are operator-gated."],
        }

    base_url = _with_trailing_slash(backend_config.url)
    responses: dict[str, HttpResult] = {}
    route_results = []
    warnings: list[str] = []
    for check_id, path, query, response_kind in BACKEND_ROUTE_CASES:
        url = _url_with_query(urljoin(base_url, path.lstrip("/")), query)
        response = _fetch(url, timeout_ms=timeout_ms)
        responses[check_id] = response
        result = _review_backend_route(check_id, path, query, response_kind, response)
        route_results.append(result)
        if not result["passed"]:
            warnings.extend(result["notes"])

    safe_query_results = []
    for query_text in SAFE_QUERY_CASES:
        response = _fetch(_url_with_query(urljoin(base_url, "api/v1/search"), {"q": query_text}), timeout_ms=timeout_ms)
        responses[f"safe_query:{query_text}"] = response
        result = _review_safe_query(query_text, response)
        safe_query_results.append(result)
        if not result["passed"]:
            warnings.extend(result["notes"])

    blocked_request_results = []
    for case_id, query, expected_error in BLOCKED_REQUEST_CASES:
        response = _fetch(_url_with_query(urljoin(base_url, "api/v1/search"), query), timeout_ms=timeout_ms)
        responses[f"blocked:{case_id}"] = response
        result = _review_blocked_request(case_id, query, expected_error, response)
        blocked_request_results.append(result)
        if not result["passed"]:
            warnings.extend(result["notes"])

    all_responses = list(responses.values())
    if any(response.status_code is None for response in all_responses):
        status = "unreachable"
    elif any(not row.get("passed") for row in route_results + safe_query_results + blocked_request_results):
        status = "unsafe_failed" if any(not row.get("passed") for row in blocked_request_results) else "verified_failed"
    else:
        status = "verified_passed"
    status_flags = _collect_backend_status_flags(responses)
    return {
        "status": status,
        "route_results": route_results,
        "safe_query_results": safe_query_results,
        "blocked_request_results": blocked_request_results,
        "responses": responses,
        "status_flags": status_flags,
        "warnings": warnings,
        "limitations": [],
    }


def _review_backend_route(
    check_id: str,
    path: str,
    query: Mapping[str, str],
    response_kind: str,
    response: HttpResult,
) -> dict[str, Any]:
    notes: list[str] = []
    passed = response.status_code is not None and 200 <= response.status_code < 300
    payload = response.json_body() if response_kind == "json" else {}
    if response_kind == "json":
        if not payload:
            passed = False
            notes.append("json_response_missing")
        if payload.get("mode") not in {None, "local_index_only"}:
            passed = False
            notes.append("mode_not_local_index_only")
        for key in FALSE_STATUS_FLAGS:
            if payload.get(key) is True:
                passed = False
                notes.append(f"{key}_true")
    else:
        if "live_probe" in response.body.casefold() and "disabled" not in response.body.casefold():
            passed = False
            notes.append("html_live_probe_claim_ambiguous")
    if _contains_private_or_secret_marker(response.body):
        passed = False
        notes.append("private_or_secret_marker_detected")
    return {
        "route": path,
        "check_id": check_id,
        "expected_status": "2xx",
        "actual_status": response.status_code,
        "content_type": response.content_type,
        "query_keys": sorted(query),
        "contract_alignment": "aligned" if passed else "failed",
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _review_safe_query(query_text: str, response: HttpResult) -> dict[str, Any]:
    payload = response.json_body()
    results = payload.get("results") if isinstance(payload.get("results"), list) else []
    notes: list[str] = []
    passed = response.status_code is not None and 200 <= response.status_code < 300
    if payload.get("ok") not in {None, True}:
        passed = False
        notes.append("ok_not_true")
    if payload.get("mode") not in {None, "local_index_only"}:
        passed = False
        notes.append("mode_not_local_index_only")
    if not isinstance(results, list):
        passed = False
        notes.append("results_not_list")
    if _contains_private_or_secret_marker(response.body):
        passed = False
        notes.append("private_or_secret_marker_detected")
    return {
        "query": query_text,
        "route": "/api/v1/search",
        "expected": "2xx local_index_only response",
        "actual_status": response.status_code,
        "local_index_only": payload.get("mode") == "local_index_only" or payload.get("mode") is None,
        "result_count": len(results),
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _review_blocked_request(case_id: str, query: Mapping[str, str], expected_error: str, response: HttpResult) -> dict[str, Any]:
    payload = response.json_body()
    error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
    actual_error = error.get("code")
    notes: list[str] = []
    passed = response.status_code is not None and 400 <= response.status_code < 500
    if payload.get("ok") not in {None, False}:
        passed = False
        notes.append("ok_not_false")
    if actual_error not in {None, expected_error}:
        passed = False
        notes.append(f"unexpected_error:{actual_error}")
    if _contains_private_or_secret_marker(response.body):
        passed = False
        notes.append("secret_or_path_leaked")
    return {
        "forbidden_parameter": case_id,
        "route": "/api/v1/search",
        "query_keys": sorted(query),
        "expected_rejection": expected_error,
        "actual_status": response.status_code,
        "actual_error": actual_error,
        "leaked_secret_or_path": _contains_private_or_secret_marker(response.body),
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _review_static_search_config(payload: Mapping[str, Any], backend_config: ConfiguredUrl | None) -> dict[str, Any]:
    notes: list[str] = []
    passed = bool(payload)
    if not payload:
        notes.append("search_config_json_missing_or_invalid")
    hosted_url = payload.get("hosted_backend_url")
    if payload.get("mode") not in {None, "local_index_only"}:
        passed = False
        notes.append("mode_not_local_index_only")
    for key in (
        "live_probes_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "installs_enabled",
        "local_paths_enabled",
        "arbitrary_url_fetch_enabled",
        "telemetry_enabled",
        "accounts_enabled",
    ):
        if payload.get(key) is True:
            passed = False
            notes.append(f"{key}_true")
    if hosted_url and backend_config and _normalize_compare_url(str(hosted_url)) != _normalize_compare_url(backend_config.url):
        passed = False
        notes.append("hosted_backend_url_mismatch")
    if hosted_url and not backend_config:
        passed = False
        notes.append("hosted_backend_url_present_without_verified_backend_argument")
    if payload.get("hosted_backend_verified") is True and not backend_config:
        passed = False
        notes.append("hosted_backend_verified_without_backend_evidence")
    if payload.get("search_form_enabled") is True and not backend_config:
        passed = False
        notes.append("search_form_enabled_without_backend_evidence")
    return {
        "search_config_checked": bool(payload),
        "backend_url_in_search_config": _redact_url(str(hosted_url)) if hosted_url else None,
        "backend_url_verified": backend_config is not None,
        "search_form_enabled": payload.get("search_form_enabled"),
        "hosted_backend_verified": payload.get("hosted_backend_verified"),
        "contract_alignment": "aligned" if passed else "failed",
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _review_public_index_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    notes: list[str] = []
    passed = bool(payload)
    if not payload:
        notes.append("public_index_summary_json_missing_or_invalid")
    for key in ("contains_live_data", "contains_private_data", "contains_executables"):
        if payload.get(key) is not False:
            passed = False
            notes.append(f"{key}_not_false")
    if payload.get("local_index_only") is not True:
        passed = False
        notes.append("local_index_only_not_true")
    return {
        "status": "verified_passed" if passed else "verified_failed",
        "checked": bool(payload),
        "document_count": payload.get("document_count"),
        "source_count": payload.get("source_count"),
        "contains_live_data": payload.get("contains_live_data"),
        "contains_private_data": payload.get("contains_private_data"),
        "contains_executables": payload.get("contains_executables"),
        "local_index_only": payload.get("local_index_only"),
        "passed": passed,
        "notes": notes or ["ok"],
    }


def _missing_static_handoff_results() -> list[dict[str, Any]]:
    return [
        {
            "search_config_checked": False,
            "backend_url_in_search_config": None,
            "backend_url_verified": False,
            "search_form_enabled": None,
            "hosted_backend_verified": None,
            "contract_alignment": "not_checked",
            "passed": False,
            "notes": ["No static URL configured."],
        }
    ]


def _missing_route_results() -> list[dict[str, Any]]:
    return [
        {
            "route": path,
            "check_id": check_id,
            "expected_status": "2xx",
            "actual_status": None,
            "content_type": None,
            "query_keys": sorted(query),
            "contract_alignment": "not_checked",
            "passed": False,
            "notes": ["Hosted backend URL not configured."],
        }
        for check_id, path, query, _kind in BACKEND_ROUTE_CASES
    ]


def _missing_safe_query_results() -> list[dict[str, Any]]:
    return [
        {
            "query": query,
            "route": "/api/v1/search",
            "expected": "2xx local_index_only response",
            "actual_status": None,
            "local_index_only": None,
            "result_count": None,
            "passed": False,
            "notes": ["Hosted backend URL not configured."],
        }
        for query in SAFE_QUERY_CASES
    ]


def _missing_blocked_request_results() -> list[dict[str, Any]]:
    return [
        {
            "forbidden_parameter": case_id,
            "route": "/api/v1/search",
            "query_keys": sorted(query),
            "expected_rejection": expected_error,
            "actual_status": None,
            "actual_error": None,
            "leaked_secret_or_path": False,
            "passed": False,
            "notes": ["Hosted backend URL not configured."],
        }
        for case_id, query, expected_error in BLOCKED_REQUEST_CASES
    ]


def _aggregate_route_status(route_results: Sequence[Mapping[str, Any]], configured: bool) -> str:
    if not configured:
        return "not_configured"
    if all(row.get("passed") is True for row in route_results):
        return "verified_passed"
    if any(row.get("actual_status") is None for row in route_results):
        return "unreachable"
    return "verified_failed"


def _aggregate_safety_status(
    safe_query_results: Sequence[Mapping[str, Any]],
    blocked_request_results: Sequence[Mapping[str, Any]],
    configured: bool,
) -> str:
    if not configured:
        return "operator_gated"
    if all(row.get("passed") is True for row in list(safe_query_results) + list(blocked_request_results)):
        return "verified_passed"
    if any(row.get("passed") is not True for row in blocked_request_results):
        return "unsafe_failed"
    return "verified_failed"


def _tls_results(
    static_config: ConfiguredUrl | None,
    backend_config: ConfiguredUrl | None,
    static_result: Mapping[str, Any],
    backend_result: Mapping[str, Any],
) -> dict[str, Any]:
    entries = []
    for role, config, result in (
        ("static", static_config, static_result),
        ("backend", backend_config, backend_result),
    ):
        if config is None:
            entries.append({"role": role, "status": "not_configured", "https": None, "notes": ["URL not configured."]})
            continue
        parsed = urlparse(config.url)
        local_dev = (parsed.hostname or "").casefold() in LOCAL_HOSTS
        if parsed.scheme == "https":
            status = "verified_passed" if result.get("status") in {"verified_passed", "configured_unverified"} else "configured_unverified"
            notes = ["urllib completed TLS certificate validation for successful HTTPS responses."] if status == "verified_passed" else ["HTTPS configured but route evidence is incomplete."]
        elif local_dev:
            status = "operator_gated"
            notes = ["Local/dev URL is not public TLS evidence."]
        else:
            status = "verified_failed"
            notes = ["Public URL is not HTTPS."]
        entries.append({"role": role, "status": status, "https": parsed.scheme == "https", "local_dev": local_dev, "notes": notes})
    aggregate = "verified_passed" if any(row["role"] == "static" and row["status"] == "verified_passed" for row in entries) else "operator_gated"
    if backend_config and not any(row["role"] == "backend" and row["status"] == "verified_passed" for row in entries):
        aggregate = "verified_failed"
    return {"status": aggregate, "entries": entries}


def _header_results(kind: str, static_result: Mapping[str, Any], backend_result: Mapping[str, Any]) -> dict[str, Any]:
    header_names = {
        "cors": ("access-control-allow-origin", "access-control-allow-methods", "access-control-allow-headers"),
        "cache": ("cache-control", "etag", "expires", "last-modified"),
    }[kind]
    entries = []
    responses: list[tuple[str, HttpResult]] = []
    responses.extend((f"static:{name}", response) for name, response in static_result.get("responses", {}).items())
    responses.extend((f"backend:{name}", response) for name, response in backend_result.get("responses", {}).items())
    for label, response in responses:
        headers = _casefold_headers(response.headers)
        selected = {name: headers.get(name) for name in header_names if headers.get(name)}
        entries.append({"target": label, "url": _redact_url(response.url), "headers": selected})
    any_present = any(entry["headers"] for entry in entries)
    if not entries:
        status = "not_configured"
    elif any_present:
        status = "verified_passed"
    else:
        status = "evidence_unavailable"
    return {"status": status, "entries": entries, "notes": ["Missing CORS/cache headers are recorded as evidence gaps unless a future contract requires them."]}


def _rate_limit_results(static_result: Mapping[str, Any], backend_result: Mapping[str, Any], backend_configured: bool) -> dict[str, Any]:
    header_names = ("ratelimit-limit", "ratelimit-remaining", "ratelimit-reset", "x-ratelimit-limit", "x-ratelimit-remaining")
    entries = []
    responses: list[tuple[str, HttpResult]] = []
    responses.extend((f"static:{name}", response) for name, response in static_result.get("responses", {}).items())
    responses.extend((f"backend:{name}", response) for name, response in backend_result.get("responses", {}).items())
    for label, response in responses:
        headers = _casefold_headers(response.headers)
        selected = {name: headers.get(name) for name in header_names if headers.get(name)}
        if selected:
            entries.append({"target": label, "url": _redact_url(response.url), "headers": selected})
    if entries:
        status = "verified_passed"
    elif backend_configured:
        status = "evidence_unavailable"
    else:
        status = "operator_gated"
    return {
        "status": status,
        "entries": entries,
        "edge_provider_evidence": None,
        "host_platform_evidence": None,
        "notes": ["No edge/rate-limit claim is made without response headers or operator evidence."],
    }


def _privacy_logging_telemetry_results(backend_result: Mapping[str, Any]) -> dict[str, Any]:
    flags = backend_result.get("status_flags") if isinstance(backend_result.get("status_flags"), Mapping) else {}
    if not flags:
        return {
            "status": "operator_gated",
            "telemetry_enabled": None,
            "logging_policy_verified": False,
            "notes": ["No hosted backend status endpoint was verified; logging/telemetry evidence remains operator-gated."],
        }
    telemetry_enabled = flags.get("telemetry_enabled")
    return {
        "status": "verified_passed" if telemetry_enabled is False else "unsafe_failed",
        "telemetry_enabled": telemetry_enabled,
        "logging_policy_verified": False,
        "notes": ["Status flags were checked; log retention remains operator/future unless separately evidenced."],
    }


def _hard_booleans(
    *,
    static_verified: bool,
    backend_verified: bool,
    deployment_verified: bool,
    status_flags: Mapping[str, Any],
) -> dict[str, bool]:
    return {
        "deployment_verified": deployment_verified,
        "production_ready_claimed": False,
        "static_deployment_verified": static_verified,
        "backend_deployment_verified": backend_verified,
        "hosted_public_search_live": backend_verified,
        "public_search_mode_local_index_only": status_flags.get("mode") in {None, "local_index_only"},
        "live_probes_enabled": bool(status_flags.get("live_probes_enabled") is True),
        "source_connectors_enabled": bool(status_flags.get("source_connectors_enabled") is True),
        "external_source_calls_enabled": bool(status_flags.get("external_source_calls_enabled") is True),
        "downloads_enabled": bool(status_flags.get("downloads_enabled") is True),
        "uploads_enabled": bool(status_flags.get("uploads_enabled") is True),
        "installs_enabled": bool(status_flags.get("installs_enabled") is True),
        "local_paths_enabled": bool(status_flags.get("local_paths_enabled") is True),
        "arbitrary_url_fetch_enabled": bool(status_flags.get("arbitrary_url_fetch_enabled") is True),
        "telemetry_enabled": bool(status_flags.get("telemetry_enabled") is True),
        "accounts_enabled": bool(status_flags.get("accounts_enabled") is True),
        "master_index_mutation_enabled": False,
        "source_cache_runtime_enabled": False,
        "evidence_ledger_runtime_enabled": False,
        "candidate_index_runtime_enabled": False,
    }


def _calculate_ok(
    *,
    strict: bool,
    static_config: ConfiguredUrl | None,
    backend_config: ConfiguredUrl | None,
    static_status: str,
    backend_status: str,
    safety_status: str,
) -> bool:
    if strict:
        return (
            static_config is not None
            and backend_config is not None
            and static_status == "verified_passed"
            and backend_status == "verified_passed"
            and safety_status == "verified_passed"
        )
    return True


def _fetch(url: str, *, timeout_ms: int) -> HttpResult:
    request = Request(
        url,
        method="GET",
        headers={"User-Agent": "eureka-public-hosted-deployment-verifier/0"},
    )
    opener = build_opener(NoRedirectHandler)
    try:
        with opener.open(request, timeout=timeout_ms / 1000) as response:  # nosec - URL is explicitly configured.
            body = response.read(512 * 1024).decode("utf-8", errors="replace")
            headers = dict(response.headers.items())
            return HttpResult(
                url=url,
                status_code=int(response.status),
                headers=headers,
                content_type=response.headers.get("Content-Type"),
                body=body,
            )
    except HTTPError as exc:
        body = exc.read(128 * 1024).decode("utf-8", errors="replace")
        return HttpResult(
            url=url,
            status_code=int(exc.code),
            headers=dict(exc.headers.items()),
            content_type=exc.headers.get("Content-Type") if exc.headers else None,
            body=body,
            error=f"HTTP {exc.code}",
        )
    except (TimeoutError, socket.timeout, ssl.SSLError, OSError, URLError) as exc:
        return HttpResult(url=url, status_code=None, headers={}, content_type=None, body="", error=_redact_text(str(exc)))


def _collect_backend_status_flags(responses: Mapping[str, HttpResult]) -> dict[str, Any]:
    flags: dict[str, Any] = {}
    for key in ("status", "api_status", "healthz"):
        response = responses.get(key)
        if not response:
            continue
        payload = response.json_body()
        for flag in (
            "mode",
            "live_probes_enabled",
            "source_connectors_enabled",
            "external_source_calls_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
            "telemetry_enabled",
            "accounts_enabled",
            "external_calls_performed",
        ):
            if flag in payload and flag not in flags:
                flags[flag] = payload.get(flag)
    return flags


def _status_flags_from_static_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    flags = _default_static_status_flags()
    if payload:
        for key in list(flags):
            if key in payload:
                flags[key] = payload.get(key)
        flags["mode"] = payload.get("mode", flags["mode"])
    return flags


def _default_static_status_flags() -> dict[str, Any]:
    return {
        "mode": "local_index_only",
        "live_probes_enabled": False,
        "source_connectors_enabled": False,
        "external_source_calls_enabled": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "installs_enabled": False,
        "local_paths_enabled": False,
        "arbitrary_url_fetch_enabled": False,
        "telemetry_enabled": False,
        "accounts_enabled": False,
        "external_calls_performed": False,
    }


def _status_for_response(response: HttpResult) -> str:
    if response.status_code is None:
        return "unreachable"
    if 200 <= response.status_code < 300:
        return "verified_passed"
    if 300 <= response.status_code < 400:
        return "configured_unverified"
    return "verified_failed"


def _selected_headers(headers: Mapping[str, str]) -> dict[str, str]:
    folded = _casefold_headers(headers)
    selected_names = (
        "content-type",
        "cache-control",
        "etag",
        "last-modified",
        "expires",
        "access-control-allow-origin",
        "strict-transport-security",
        "x-content-type-options",
        "x-frame-options",
        "ratelimit-limit",
        "ratelimit-remaining",
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
    )
    return {name: folded[name] for name in selected_names if name in folded}


def _casefold_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {str(key).casefold(): str(value) for key, value in headers.items()}


def _url_with_query(base_url: str, query: Mapping[str, str]) -> str:
    if not query:
        return base_url
    return base_url + "?" + urlencode(query)


def _with_trailing_slash(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if not path.endswith("/"):
        path += "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", parsed.query, ""))


def _normalize_compare_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path.endswith("/") and path != "/":
        path = path[:-1]
    return urlunparse((parsed.scheme, parsed.netloc.casefold(), path, "", "", ""))


def _redact_url(url: str | None) -> str | None:
    if not url:
        return url
    parsed = urlparse(url)
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc += f":{parsed.port}"
    pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.casefold() in SECRET_QUERY_KEYS:
            pairs.append((key, "<redacted>"))
        else:
            pairs.append((key, value))
    return urlunparse((parsed.scheme, netloc, parsed.path, "", urlencode(pairs), ""))


def _redact_text(text: str | None) -> str | None:
    if text is None:
        return None
    redacted = text.replace(str(REPO_ROOT), "<repo>")
    redacted = redacted.replace("\\", "/")
    redacted = redacted.replace("secret-value", "<redacted>")
    return redacted[:600]


def _contains_private_or_secret_marker(text: str) -> bool:
    folded = text.casefold().replace("\\\\", "\\")
    markers = ("secret-value", "traceback", "c:\\", "d:\\", "/users/", "/home/")
    return any(marker in folded for marker in markers)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Hosted Deployment Evidence",
        f"ok: {report.get('ok')}",
        f"static_url: {report.get('static_url')}",
        f"static_site_status: {report.get('static_site_status')}",
        f"backend_url: {report.get('backend_url')}",
        f"hosted_backend_status: {report.get('hosted_backend_status')}",
        f"route_verification_status: {report.get('route_verification_status')}",
        f"safety_verification_status: {report.get('safety_verification_status')}",
        f"rate_limit_status: {report.get('rate_limit_status')}",
    ]
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {item}" for item in report["warnings"])
    if report.get("limitations"):
        lines.append("limitations:")
        lines.extend(f"- {item}" for item in report["limitations"])
    return "\n".join(lines) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-url", help="Explicit static site URL to verify.")
    parser.add_argument("--backend-url", help="Explicit hosted backend URL to verify.")
    parser.add_argument("--from-env", action="store_true", help="Read configured URLs from Eureka environment variables.")
    parser.add_argument("--from-repo-config", action="store_true", help="Read configured URLs from repo publication inventory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON evidence.")
    parser.add_argument("--strict", action="store_true", help="Require both static and hosted backend verification to pass.")
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS, help="HTTP timeout in milliseconds.")
    return parser


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = verify_public_hosted_deployment(
        static_url=args.static_url,
        backend_url=args.backend_url,
        from_env=args.from_env,
        from_repo_config=args.from_repo_config,
        timeout_ms=args.timeout_ms,
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
