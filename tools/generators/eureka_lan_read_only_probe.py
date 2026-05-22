#!/usr/bin/env python3
"""Probe read-only LAN-safe Eureka routes without starting a server."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_network import classify_client_scope


READ_ONLY_ROUTES: tuple[tuple[str, str, dict[str, str]], ...] = (
    ("GET", "/", {}),
    ("GET", "/status", {}),
    ("GET", "/health", {}),
    ("GET", "/search", {"q": "sampleproject"}),
    ("GET", "/absence", {"q": "definitely-not-present-local-12"}),
    ("GET", "/api/v1/status", {}),
    ("GET", "/api/v1/health", {}),
    ("GET", "/api/v1/search", {"q": "sampleproject"}),
    ("GET", "/api/v1/absence", {"q": "definitely-not-present-local-12"}),
)
MUTATION_ROUTES: tuple[tuple[str, str, dict[str, str]], ...] = (
    ("POST", "/rebuild", {"operator_label": "lan_smoke"}),
    (
        "POST",
        "/review/nonexistent-local-12/decision",
        {"decision": "reject", "reason": "lan smoke mutation block check"},
    ),
    ("POST", "/workers/run", {}),
    ("POST", "/api/v1/source-probe", {}),
)
REJECTED_STATUSES = {400, 401, 403, 404, 405}
FORBIDDEN_HTML_MARKERS = (
    "<script",
    "javascript:",
    "src=\"http://",
    "src=\"https://",
    "href=\"http://",
    "href=\"https://",
    "method=\"post\"",
    "formmethod=\"post\"",
)
FORBIDDEN_CLAIMS = (
    "production ready",
    "public launch ready",
    "globally complete",
    "exhaustive coverage",
    "rights cleared",
    "malware safe",
    "installability certified",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        result = run_probe(validate_base_url(args.base_url))
    except ValueError as exc:
        result = fail_result("base_url_rejected", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("lan_probe_failed", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1

    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") in {"pass", "pass_with_warnings"} else 1


def run_probe(base_url: str) -> dict[str, Any]:
    read_only = {
        route_key(method, path): check_read_only_route(base_url, method, path, params)
        for method, path, params in READ_ONLY_ROUTES
    }
    mutations = {
        route_key(method, path): check_mutation_route(base_url, method, path, params)
        for method, path, params in MUTATION_ROUTES
    }
    read_only_ok = all(item.get("ok") for item in read_only.values())
    mutation_ok = all(item.get("blocked") for item in mutations.values())
    operator_localhost_only = mutations["POST /rebuild"].get("status_code") in {401, 403}
    status = "pass" if read_only_ok and mutation_ok and operator_localhost_only else "fail"
    return {
        "schema_version": "local_lan_read_only_probe_result.v0",
        "status": status,
        "base_url": base_url,
        "base_url_scope": classify_base_url_scope(base_url),
        "read_only_routes": read_only,
        "mutation_routes": mutations,
        "read_only_routes_passed": read_only_ok,
        "mutation_routes_blocked": mutation_ok,
        "operator_mutations_localhost_only": bool(operator_localhost_only),
        "source_probe_routes_blocked": bool(mutations["POST /api/v1/source-probe"].get("blocked")),
        "workunit_execution_from_lan": False,
        "review_mutation_from_lan": False,
        "rebuild_mutation_from_lan": False,
        "external_internet_used": False,
        "source_probe_executed": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": ["HTTP client scope depends on the caller network path; LAN scope is separately validated by the LOCAL route gate."],
    }


def check_read_only_route(base_url: str, method: str, path: str, params: dict[str, str]) -> dict[str, Any]:
    response = fetch(base_url, method, path, params)
    body = str(response.get("body", ""))
    content_type = str(response.get("content_type", ""))
    lowered = body.lower()
    is_html = "text/html" in content_type
    external_assets = is_html and any(marker in lowered for marker in FORBIDDEN_HTML_MARKERS[:6])
    mutation_controls = is_html and any(marker in lowered for marker in FORBIDDEN_HTML_MARKERS[6:])
    forbidden_claims = any(marker in lowered for marker in FORBIDDEN_CLAIMS)
    boundary_visible = _boundary_visible(body, response.get("payload"))
    response.update(
        {
            "ok": 200 <= int(response.get("status_code", 0)) < 400
            and boundary_visible
            and not external_assets
            and not mutation_controls
            and not forbidden_claims,
            "boundary_visible": boundary_visible,
            "external_assets_found": external_assets,
            "mutation_controls_found": mutation_controls,
            "forbidden_claims_found": forbidden_claims,
        }
    )
    response.pop("body", None)
    return response


def check_mutation_route(base_url: str, method: str, path: str, params: dict[str, str]) -> dict[str, Any]:
    response = fetch(base_url, method, path, params)
    status_code = int(response.get("status_code", 0))
    response.update(
        {
            "blocked": status_code in REJECTED_STATUSES,
            "accepted_statuses": sorted(REJECTED_STATUSES),
            "mutation_performed": False,
        }
    )
    response.pop("body", None)
    return response


def fetch(base_url: str, method: str, path: str, params: dict[str, str]) -> dict[str, Any]:
    url = build_url(base_url, path, params if method == "GET" else None)
    body = urlencode(params).encode("utf-8") if method != "GET" and params else None
    request = Request(url, method=method, data=body, headers={"Accept": "application/json,text/html,text/plain"})
    if body is not None:
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urlopen(request, timeout=5) as response:
            raw = response.read().decode("utf-8")
            status_code = int(response.getcode())
            content_type = str(response.headers.get("Content-Type", ""))
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        status_code = int(exc.code)
        content_type = str(exc.headers.get("Content-Type", ""))
    except URLError as exc:
        return {"url": url, "status_code": 0, "content_type": "", "error": str(exc), "payload": None}
    return {
        "url": url,
        "status_code": status_code,
        "content_type": content_type,
        "body": raw,
        "payload": parse_json(raw) if "application/json" in content_type else None,
    }


def validate_base_url(base_url: str) -> str:
    split = urlsplit(str(base_url or ""))
    if split.scheme != "http":
        raise ValueError("base-url must use http")
    host = (split.hostname or "").lower()
    if not split.port:
        raise ValueError("base-url must include an explicit port")
    if host in {"", "*", "0.0.0.0", "::"}:
        raise ValueError("base-url must target a concrete localhost or private LAN address")
    scope = classify_client_scope(host).value
    if host != "localhost" and scope not in {"loopback", "lan"}:
        raise ValueError("base-url must be localhost, loopback, or private LAN; public internet hosts are refused")
    return urlunsplit((split.scheme, split.netloc, split.path.rstrip("/"), "", ""))


def classify_base_url_scope(base_url: str) -> str:
    return classify_client_scope(urlsplit(base_url).hostname or "").value


def build_url(base_url: str, path: str, params: dict[str, str] | None = None) -> str:
    return urlunsplit(("http", urlsplit(base_url).netloc, path, urlencode(params or {}), ""))


def parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def route_key(method: str, path: str) -> str:
    return f"{method} {path}"


def _boundary_visible(body: str, payload: Any) -> bool:
    text = json.dumps(payload, sort_keys=True).lower() if isinstance(payload, dict) else body.lower()
    markers = ("read_only", "read-only", "read only", "local", "reviewed_public_index_only", "reviewed local")
    return any(marker in text for marker in markers)


def fail_result(code: str, message: str, base_url: str) -> dict[str, Any]:
    return {
        "schema_version": "local_lan_read_only_probe_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "base_url": base_url,
        "read_only_routes_passed": False,
        "mutation_routes_blocked": False,
        "operator_mutations_localhost_only": False,
        "external_internet_used": False,
        "source_probe_executed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    print(f"read_only_routes_passed: {result.get('read_only_routes_passed')}", file=stdout)
    print(f"mutation_routes_blocked: {result.get('mutation_routes_blocked')}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
