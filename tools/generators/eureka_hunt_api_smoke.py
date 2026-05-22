#!/usr/bin/env python3
"""Smoke-test integrated Search Hunt JSON API routes over localhost."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO
from urllib.parse import urlparse
from urllib.request import Request, urlopen


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
FORBIDDEN_CLAIMS = (
    "internet exhausted",
    "artifact does not exist globally",
    "rights cleared",
    "malware safe",
    "production ready",
    "public launch ready",
    "ai verified",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        base_url = validate_localhost_base_url(args.base_url)
        result = run_api_smoke(base_url)
    except Exception as exc:
        result = fail_result("hunt_api_smoke_failed", str(exc))
        print(f"ERROR: {exc}", file=stderr)
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
    return 0 if result.get("status") == "pass" else 1


def validate_localhost_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in LOCAL_HOSTS:
        raise ValueError("base-url must be http://127.0.0.1, http://localhost, or http://[::1]")
    return base_url.rstrip("/")


def run_api_smoke(base_url: str) -> dict[str, Any]:
    status = fetch_json(base_url, "/api/v1/status")
    hunts = fetch_json(base_url, "/api/v1/hunts")
    hunt_rows = hunts.get("hunts", [])
    if not hunt_rows:
        raise ValueError("no Search Hunt Sessions are available for API smoke")
    hunt_id, needs = discover_hunt_with_needs(base_url, hunt_rows)
    hunt = fetch_json(base_url, f"/api/v1/hunt/{hunt_id}")
    exhaustion = fetch_json(base_url, f"/api/v1/hunt/{hunt_id}/exhaustion")
    need_rows = needs.get("needs", [])
    if not need_rows:
        raise ValueError("no SearchNeeds are linked to the smoke hunt")
    need_id = str(need_rows[0].get("id") or "")
    need = fetch_json(base_url, f"/api/v1/need/{need_id}")
    need_workunits = fetch_json(base_url, f"/api/v1/need/{need_id}/workunits")
    runner = fetch_json(base_url, f"/api/v1/hunt/{hunt_id}/runner")
    payloads = {
        "status": status,
        "hunts": hunts,
        "hunt": hunt,
        "exhaustion": exhaustion,
        "hunt_needs": needs,
        "need": need,
        "need_workunits": need_workunits,
        "runner": runner,
    }
    forbidden_hits = forbidden_claim_hits(payloads)
    route_flags = {
        "status_route_passed": status.get("status") in {"pass", "pass_with_warnings"},
        "hunts_route_passed": hunts.get("status") == "pass" and bool(hunt_rows),
        "hunt_route_passed": hunt.get("status") == "pass" and hunt.get("hunt_id") == hunt_id,
        "exhaustion_route_passed": exhaustion.get("status") in {"pass", "not_found"} and exhaustion.get("hunt_id") == hunt_id,
        "hunt_needs_route_passed": needs.get("status") == "pass" and bool(need_rows),
        "need_route_passed": need.get("status") == "pass" and need.get("need_id") == need_id,
        "need_workunits_route_passed": need_workunits.get("status") == "pass",
        "runner_route_passed": runner.get("status") == "pass" and runner.get("hunt_id") == hunt_id,
    }
    return {
        "schema_version": "search_hunt_api_smoke_result.v0",
        "task": "HUNT-08",
        "status": "pass" if all(route_flags.values()) and not forbidden_hits else "fail",
        "base_url": base_url,
        "hunt_id": hunt_id,
        "need_id": need_id,
        "api_routes_passed": all(route_flags.values()),
        "forbidden_claim_hits": forbidden_hits,
        **route_flags,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def fetch_json(base_url: str, path: str) -> dict[str, Any]:
    request = Request(base_url + path, headers={"Accept": "application/json"})
    with urlopen(request, timeout=10) as response:  # nosec - localhost-only smoke
        data = response.read().decode("utf-8")
    return json.loads(data)


def discover_hunt_with_needs(base_url: str, hunt_rows: Sequence[Mapping[str, Any]]) -> tuple[str, dict[str, Any]]:
    last_payload: dict[str, Any] = {}
    for row in hunt_rows:
        hunt_id = str(row.get("id") or "")
        if not hunt_id:
            continue
        payload = fetch_json(base_url, f"/api/v1/hunt/{hunt_id}/needs")
        last_payload = payload
        if payload.get("needs"):
            return hunt_id, payload
    raise ValueError("no SearchNeeds are linked to any smoke hunt")


def forbidden_claim_hits(payloads: dict[str, Any]) -> list[str]:
    text = json.dumps(payloads, sort_keys=True).casefold()
    return [claim for claim in FORBIDDEN_CLAIMS if claim in text]


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "search_hunt_api_smoke_result.v0",
        "task": "HUNT-08",
        "status": "fail",
        "error": code,
        "message": message,
        "api_routes_passed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
