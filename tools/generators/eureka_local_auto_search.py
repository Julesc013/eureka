#!/usr/bin/env python3
"""Run the fixed local auto-search suite against a loopback service."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO
import urllib.parse
import urllib.request


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval import get_default_query_suite, validate_localhost_base_url


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--query-file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        base_url = validate_localhost_base_url(args.base_url)
        queries = load_queries(Path(args.query_file)) if args.query_file else list(get_default_query_suite())
        result = run_auto_search(base_url, queries)
    except Exception as exc:
        result = fail_result("auto_search_failed", str(exc), args.base_url)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def load_queries(path: Path) -> list[str]:
    if not path:
        raise ValueError("query file path is required")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError("query file must contain a JSON list of strings")
    return [str(item) for item in payload]


def run_auto_search(base_url: str, queries: list[str]) -> dict[str, Any]:
    query_results = [run_query(base_url, query) for query in queries]
    failed = [item for item in query_results if not item.get("passed")]
    return {
        "schema_version": "local_auto_search_result.v0",
        "status": "pass" if not failed else "fail",
        "base_url": base_url,
        "query_count": len(query_results),
        "passed_query_count": len(query_results) - len(failed),
        "failed_query_count": len(failed),
        "queries": query_results,
        "local_reviewed_index_only": True,
        "synthetic_generation_enabled": False,
        "live_source_search_enabled": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "warnings": [],
        "limitations": ["auto-search uses fixed local queries only"],
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def run_query(base_url: str, query: str) -> dict[str, Any]:
    search = fetch_json(base_url, "/api/v1/search", {"q": query})
    result_count = 0
    if isinstance(search.get("payload"), dict):
        result_count = int(search["payload"].get("result_count", 0) or 0)
    search_status = int(search.get("status_code", 0) or 0)
    absence = None
    if (search_status == 200 and result_count == 0) or "definitely-not-present" in query:
        absence = fetch_json(base_url, "/api/v1/absence", {"q": query})
    search_ok = search_status == 200 or (len(query) > 256 and search_status in {400, 405})
    absence_ok = absence is None or bool(absence.get("ok"))
    return {
        "query": query if len(query) <= 80 else query[:80] + "...",
        "query_length": len(query),
        "search_status_code": search_status,
        "result_count": result_count,
        "absence_checked": absence is not None,
        "absence_status_code": int(absence.get("status_code", 0)) if absence else None,
        "passed": bool(search_ok and absence_ok),
        "local_reviewed_index_only": True,
        "no_global_absence_claim": True,
        "warnings": [] if search_ok else ["search route did not return expected bounded response"],
        "limitations": ["query checked against local reviewed index only"],
    }


def fetch_json(base_url: str, path: str, params: dict[str, str]) -> dict[str, Any]:
    url = urllib.parse.urlunsplit(("http", urllib.parse.urlsplit(base_url).netloc, path, urllib.parse.urlencode(params), ""))
    request = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            status_code = int(response.getcode())
            content_type = str(response.headers.get("Content-Type", ""))
    except Exception as exc:
        code = int(getattr(exc, "code", 0) or 0)
        if code:
            read = getattr(exc, "read", None)
            body = read().decode("utf-8") if callable(read) else ""
            headers = getattr(exc, "headers", {}) or {}
            status_code = code
            content_type = str(headers.get("Content-Type", "")) if hasattr(headers, "get") else ""
        else:
            return {"ok": False, "status_code": 0, "error": str(exc), "payload": None}
    payload = parse_json(body)
    return {"ok": 200 <= status_code < 400, "status_code": status_code, "content_type": content_type, "payload": payload}


def parse_json(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def fail_result(code: str, message: str, base_url: str) -> dict[str, Any]:
    return {
        "schema_version": "local_auto_search_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "base_url": base_url,
        "external_network_used": False,
        "source_probe_executed": False,
        "model_provider_used": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result.get('status')}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
