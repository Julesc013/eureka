#!/usr/bin/env python3
"""Smoke test the localhost review/rebuild loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
FORBIDDEN_HOSTS = {"0.0.0.0", "::", "", "*"}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--operator-token", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        base_url = validate_base_url(args.base_url)
        result = run_smoke(base_url, args.operator_token)
    except ValueError as exc:
        result = fail_result("base_url_rejected", str(exc), args.base_url)
        emit(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:
        result = fail_result("local_review_smoke_failed", str(exc), args.base_url)
        emit(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    emit(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def run_smoke(base_url: str, operator_token: str) -> dict[str, Any]:
    review_page = fetch(base_url, "GET", "/review", accept="text/html")
    rebuild_page = fetch(base_url, "GET", "/rebuild", accept="text/html")
    review_api = fetch(base_url, "GET", "/api/v1/review", accept="application/json")
    rebuild_missing = fetch(base_url, "POST", "/rebuild", data={"operator_label": "smoke"}, accept="application/json")
    rebuild_invalid = fetch(
        base_url,
        "POST",
        "/rebuild",
        data={"operator_token": "invalid-token", "operator_label": "smoke"},
        accept="application/json",
    )
    rebuild_valid = fetch(
        base_url,
        "POST",
        "/rebuild",
        data={"operator_token": operator_token, "operator_label": "smoke"},
        accept="application/json",
    )
    review_item_checks: dict[str, Any] = {"checked": False}
    payload = review_api.get("payload") if isinstance(review_api.get("payload"), dict) else {}
    items = payload.get("review_items", []) if isinstance(payload, dict) else []
    if items and isinstance(items[0], dict):
        review_item_id = str(items[0].get("review_item_id", ""))
        if review_item_id:
            review_item_checks = {
                "checked": True,
                "missing_token": fetch(base_url, "POST", f"/review/{review_item_id}/decision", data={"decision": "note_only"}),
                "invalid_token": fetch(
                    base_url,
                    "POST",
                    f"/review/{review_item_id}/decision",
                    data={"operator_token": "invalid-token", "decision": "note_only"},
                ),
            }
    ok = (
        review_page.get("ok")
        and rebuild_page.get("ok")
        and review_api.get("ok")
        and rebuild_missing.get("status_code") == 401
        and rebuild_invalid.get("status_code") == 401
        and rebuild_valid.get("ok")
    )
    if review_item_checks.get("checked"):
        ok = ok and review_item_checks["missing_token"].get("status_code") == 401 and review_item_checks["invalid_token"].get("status_code") == 401
    return {
        "schema_version": "local_review_smoke_result.v0",
        "status": "pass" if ok else "fail",
        "base_url": base_url,
        "review_page_passed": bool(review_page.get("ok")),
        "rebuild_page_passed": bool(rebuild_page.get("ok")),
        "review_api_passed": bool(review_api.get("ok")),
        "review_decision_requires_token": bool(not review_item_checks.get("checked") or review_item_checks["missing_token"].get("status_code") == 401),
        "rebuild_requires_token": bool(rebuild_missing.get("status_code") == 401 and rebuild_invalid.get("status_code") == 401),
        "rebuild_with_token_passed": bool(rebuild_valid.get("ok")),
        "routes": {
            "/review": review_page,
            "/rebuild": rebuild_page,
            "/api/v1/review": review_api,
            "POST /rebuild missing": rebuild_missing,
            "POST /rebuild invalid": rebuild_invalid,
            "POST /rebuild valid": rebuild_valid,
            "POST /review decision": review_item_checks,
        },
        "lan_enabled": False,
        "source_probe_executed": False,
        "workunit_execution_performed": False,
        "agent_execution_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": [],
        "limitations": ["smoke checks loopback review routes only"],
    }


def fetch(base_url: str, method: str, path: str, data: dict[str, str] | None = None, accept: str = "application/json") -> dict[str, Any]:
    body = urlencode(data or {}).encode("utf-8") if data is not None else None
    request = Request(
        build_url(base_url, path),
        data=body,
        method=method,
        headers={"Accept": accept, "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            text = response.read().decode("utf-8")
            status_code = int(response.getcode())
            content_type = str(response.headers.get("Content-Type", ""))
    except HTTPError as exc:
        text = exc.read().decode("utf-8")
        status_code = int(exc.code)
        content_type = str(exc.headers.get("Content-Type", ""))
    except URLError as exc:
        return {"ok": False, "status_code": 0, "error": str(exc)}
    payload = parse_json(text) if "application/json" in content_type else None
    return {
        "ok": 200 <= status_code < 400,
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


def build_url(base_url: str, path: str) -> str:
    return urlunsplit(("http", urlsplit(base_url).netloc, path, "", ""))


def parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def fail_result(code: str, message: str, base_url: str) -> dict[str, Any]:
    return {
        "schema_version": "local_review_smoke_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "base_url": base_url,
        "lan_enabled": False,
        "deployment_performed": False,
        "warnings": [],
        "limitations": ["smoke script refuses non-loopback URLs"],
    }


def emit(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
