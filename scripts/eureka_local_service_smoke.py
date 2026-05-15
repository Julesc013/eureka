#!/usr/bin/env python3
"""Smoke test the read-only Eureka local HTTP service."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
FORBIDDEN_HOSTS = {"0.0.0.0", "::", "", "*"}
SMOKE_ROUTES = (
    "/",
    "/status",
    "/api/v1/status",
    "/api/v1/search",
    "/api/v1/absence",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Loopback service URL, for example http://127.0.0.1:8765.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON result output path.")
    args = parser.parse_args(argv)

    try:
        base_url = validate_base_url(args.base_url)
        result = run_smoke(base_url)
    except ValueError as exc:
        result = fail_result("base_url_rejected", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("smoke_failed", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1

    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def run_smoke(base_url: str) -> dict[str, Any]:
    routes: dict[str, dict[str, Any]] = {}
    routes["/"] = fetch_route(base_url, "/")
    routes["/status"] = fetch_route(base_url, "/status")
    routes["/api/v1/status"] = fetch_route(base_url, "/api/v1/status")
    routes["/api/v1/search"] = fetch_route(base_url, "/api/v1/search", {"q": "sampleproject"})
    routes["/api/v1/absence"] = fetch_route(base_url, "/api/v1/absence", {"q": "definitely-not-present-local-04"})

    search_payload = routes["/api/v1/search"].get("payload", {})
    search_results = search_payload.get("results", []) if isinstance(search_payload, dict) else []
    if search_results:
        first = search_results[0]
        if isinstance(first, dict):
            record_id = str(first.get("record_id", ""))
            source_id = str(first.get("source_id", ""))
            if record_id:
                routes["/api/v1/object/<record_id>"] = fetch_route(base_url, f"/api/v1/object/{record_id}")
            if source_id:
                routes["/api/v1/source/<source_id>"] = fetch_route(base_url, f"/api/v1/source/{source_id}")

    required = [routes[item]["ok"] for item in SMOKE_ROUTES]
    status_payload = routes["/api/v1/status"].get("payload", {})
    result = {
        "schema_version": "local_http_service_smoke_result.v0",
        "status": "pass" if all(required) else "fail",
        "base_url": base_url,
        "routes": routes,
        "status_route_passed": bool(routes["/status"]["ok"] and routes["/api/v1/status"]["ok"]),
        "search_route_passed": bool(routes["/api/v1/search"]["ok"]),
        "absence_route_passed": bool(routes["/api/v1/absence"]["ok"]),
        "read_only": True,
        "localhost_only": True,
        "lan_enabled": False,
        "deployment_performed": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": list(status_payload.get("warnings", [])) if isinstance(status_payload, dict) else [],
        "limitations": ["local service smoke checks loopback routes only"],
    }
    return result


def fetch_route(base_url: str, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    url = build_url(base_url, path, params)
    request = Request(url, method="GET", headers={"Accept": "application/json,text/plain"})
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")
            status_code = int(response.getcode())
            content_type = str(response.headers.get("Content-Type", ""))
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        status_code = int(exc.code)
        content_type = str(exc.headers.get("Content-Type", ""))
    except URLError as exc:
        return {"ok": False, "url": url, "status_code": 0, "error": str(exc)}

    payload = parse_json(body) if "application/json" in content_type else None
    return {
        "ok": 200 <= status_code < 400,
        "url": url,
        "status_code": status_code,
        "content_type": content_type,
        "payload": payload,
    }


def validate_base_url(base_url: str) -> str:
    split = urlsplit(base_url)
    if split.scheme != "http":
        raise ValueError("only http loopback URLs are supported")
    host = (split.hostname or "").lower()
    if host in FORBIDDEN_HOSTS or host not in ALLOWED_HOSTS:
        raise ValueError("base-url must use 127.0.0.1 or localhost")
    if not split.port:
        raise ValueError("base-url must include an explicit port")
    return urlunsplit((split.scheme, split.netloc, split.path.rstrip("/"), "", ""))


def build_url(base_url: str, path: str, params: dict[str, str] | None = None) -> str:
    query = urlencode(params or {})
    return urlunsplit(("http", urlsplit(base_url).netloc, path, query, ""))


def parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def fail_result(code: str, message: str, base_url: str) -> dict[str, Any]:
    return {
        "schema_version": "local_http_service_smoke_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "base_url": base_url,
        "lan_enabled": False,
        "deployment_performed": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": ["smoke script refuses non-loopback URLs"],
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("base_url"):
        print(f"base_url: {result['base_url']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
