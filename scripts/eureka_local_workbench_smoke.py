#!/usr/bin/env python3
"""Smoke test the server-rendered local HTML workbench."""

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
HTML_CHECKS = {
    "/": ("Eureka Local Appliance", "Local appliance prototype", "<form", "Unavailable capabilities"),
    "/status": ("Status", "Store status", "Runtime and non-claim flags", "JSON health"),
    "/search": ("Search", "Submitted query", "Reviewed result count", "Reviewed results are from the local reviewed public index only"),
    "/object/not-present": ("Object not found", "local reviewed index"),
    "/source/not-present": ("Source", "Source coverage shown here is local", "No local reviewed index records"),
    "/absence": ("Absence", "local current-index absence only", "Checked local layers", "Unchecked and deferred layers"),
}
FORBIDDEN_HTML = ("<script", "javascript:", "method=\"post\"", "formmethod=\"post\"", "https://", "http://example")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
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
        result = fail_result("workbench_smoke_failed", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def run_smoke(base_url: str) -> dict[str, Any]:
    routes = {
        "/": fetch_html(base_url, "/"),
        "/status": fetch_html(base_url, "/status"),
        "/search": fetch_html(base_url, "/search", {"q": "sampleproject"}),
        "/object/not-present": fetch_html(base_url, "/object/not-present", expected_statuses=(200, 404)),
        "/source/not-present": fetch_html(base_url, "/source/not-present"),
        "/absence": fetch_html(base_url, "/absence", {"q": "definitely-not-present-local-05"}),
    }
    api_status = fetch_json(base_url, "/api/v1/status")
    api_search = fetch_json(base_url, "/api/v1/search", {"q": "sampleproject"})
    results = []
    if isinstance(api_search.get("payload"), dict):
        results = api_search["payload"].get("results", []) or []
    if results and isinstance(results[0], dict):
        record_id = str(results[0].get("record_id", ""))
        source_id = str(results[0].get("source_id", ""))
        if record_id:
            routes["/object/<record_id>"] = fetch_html(base_url, f"/object/{record_id}")
        if source_id:
            routes["/source/<source_id>"] = fetch_html(base_url, f"/source/{source_id}")

    ok = all(item.get("ok") for item in routes.values()) and api_status.get("ok") and api_search.get("ok")
    return {
        "schema_version": "local_html_smoke_result.v0",
        "status": "pass" if ok else "fail",
        "base_url": base_url,
        "routes": routes,
        "home_page_passed": bool(routes["/"].get("ok")),
        "status_page_passed": bool(routes["/status"].get("ok")),
        "search_page_passed": bool(routes["/search"].get("ok")),
        "object_not_found_passed": bool(routes["/object/not-present"].get("ok")),
        "source_empty_passed": bool(routes["/source/not-present"].get("ok")),
        "absence_page_passed": bool(routes["/absence"].get("ok")),
        "json_api_still_passed": bool(api_status.get("ok") and api_search.get("ok")),
        "mutation_controls_found": any(item.get("mutation_controls_found") for item in routes.values()),
        "external_assets_found": any(item.get("external_assets_found") for item in routes.values()),
        "forbidden_claims_found": any(item.get("forbidden_claims_found") for item in routes.values()),
        "lan_enabled": False,
        "deployment_performed": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": ["local workbench smoke checks loopback HTML routes only"],
    }


def fetch_html(
    base_url: str,
    path: str,
    params: dict[str, str] | None = None,
    expected_statuses: tuple[int, ...] = (200,),
) -> dict[str, Any]:
    result = fetch(base_url, path, params, accept="text/html")
    body = str(result.get("body", ""))
    expected = HTML_CHECKS.get(path, ())
    marker_ok = all(marker in body for marker in expected)
    lowered = body.lower()
    mutation = any(item in lowered for item in ("method=\"post\"", "formmethod=\"post\"", "review mutation", "rebuild index", "enable lan"))
    external = any(item in lowered for item in ("src=\"http://", "src=\"https://", "href=\"http://", "href=\"https://"))
    forbidden_claim = any(
        item in lowered
        for item in (
            "production ready",
            "public launch ready",
            "globally complete",
            "exhaustive coverage",
            "legal approval",
            "rights cleared",
            "malware safe",
            "installability certified",
        )
    )
    result.update(
        {
            "ok": int(result.get("status_code", 0)) in expected_statuses
            and "text/html" in str(result.get("content_type", ""))
            and marker_ok
            and not mutation
            and not external
            and not forbidden_claim,
            "marker_ok": marker_ok,
            "mutation_controls_found": mutation,
            "external_assets_found": external,
            "forbidden_claims_found": forbidden_claim,
        }
    )
    result.pop("body", None)
    return result


def fetch_json(base_url: str, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    result = fetch(base_url, path, params, accept="application/json")
    result["payload"] = parse_json(str(result.get("body", "")))
    result["ok"] = bool(result.get("ok")) and "application/json" in str(result.get("content_type", "")) and isinstance(result["payload"], dict)
    result.pop("body", None)
    return result


def fetch(base_url: str, path: str, params: dict[str, str] | None, accept: str) -> dict[str, Any]:
    url = build_url(base_url, path, params)
    request = Request(url, method="GET", headers={"Accept": accept})
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
    return {"ok": 200 <= status_code < 400, "url": url, "status_code": status_code, "content_type": content_type, "body": body}


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
    return urlunsplit(("http", urlsplit(base_url).netloc, path, urlencode(params or {}), ""))


def parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def fail_result(code: str, message: str, base_url: str) -> dict[str, Any]:
    return {
        "schema_version": "local_html_smoke_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "base_url": base_url,
        "mutation_controls_found": False,
        "external_assets_found": False,
        "lan_enabled": False,
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
