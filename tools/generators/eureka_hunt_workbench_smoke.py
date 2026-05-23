#!/usr/bin/env python3
"""Smoke-test integrated Search Hunt workbench pages over localhost."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from eureka_hunt_workflow_smoke import run_workflow_smoke  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import close_local_appliance, open_local_appliance  # noqa: E402


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
REQUIRED_NAV_TEXT = (
    "Search Hunts",
    "SearchNeeds",
    "WorkUnits",
    "Auto-test/search",
    "Limitations",
)
REQUIRED_HUNT_TEXT = (
    "Operator state controls",
    "Steering preferences",
    "Exhaustion report",
    "Linked SearchNeeds",
    "Linked WorkUnits",
    "Background hunt runner",
    "Source probes, extraction, AI/model providers",
)
REQUIRED_NEED_TEXT = (
    "Linked hunt",
    "Linked exhaustion report",
    "WorkUnit plan preview",
    "Linked WorkUnits",
    "Policy-gated WorkUnits stay blocked",
)
FORBIDDEN_EXECUTION_CONTROLS = (
    "Run source probe",
    "Execute source probe",
    "Run extraction",
    "Execute extraction",
    "Run AI",
    "Call model provider",
    "Download artifact",
    "Install artifact",
    "Deploy now",
    "Start deployment",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--instance", help="Optional instance root used to seed data when needed.")
    parser.add_argument("--operator-token", help="Optional operator token for local data seeding.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        base_url = validate_localhost_base_url(args.base_url)
        result = run_workbench_smoke(base_url, instance=args.instance, operator_token=args.operator_token)
    except Exception as exc:
        result = fail_result("hunt_workbench_smoke_failed", str(exc))
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


def run_workbench_smoke(base_url: str, *, instance: str | None = None, operator_token: str | None = None) -> dict[str, Any]:
    hunt_id = discover_hunt_id(base_url)
    seeded = False
    if not hunt_id and instance and operator_token:
        runtime = open_local_appliance(Path(instance), read_only=False)
        try:
            seed = run_workflow_smoke(runtime)
            seeded = seed.get("status") == "pass"
        finally:
            close_local_appliance(runtime)
        hunt_id = discover_hunt_id(base_url)
    if not hunt_id:
        raise ValueError("no Search Hunt Sessions are available for workbench smoke")
    need_id = discover_need_id(base_url, hunt_id)
    if not need_id:
        raise ValueError("no SearchNeeds are linked to the smoke hunt")

    pages = {
        "home": fetch_text(base_url, "/"),
        "search": fetch_text(base_url, "/search?q=sampleproject"),
        "hunts": fetch_text(base_url, "/hunts"),
        "hunt_detail": fetch_text(base_url, f"/hunt/{hunt_id}"),
        "hunt_exhaustion": fetch_text(base_url, f"/hunt/{hunt_id}/exhaustion"),
        "need_detail": fetch_text(base_url, f"/need/{need_id}"),
        "need_workunits": fetch_text(base_url, f"/need/{need_id}/workunits"),
        "hunt_runner": fetch_text(base_url, f"/hunt/{hunt_id}/runner"),
        "status": fetch_text(base_url, "/status"),
    }
    combined_nav = pages["home"] + pages["status"] + pages["search"]
    navigation_missing = [text for text in REQUIRED_NAV_TEXT if text not in combined_nav]
    hunt_missing = [text for text in REQUIRED_HUNT_TEXT if text not in pages["hunt_detail"]]
    need_missing = [text for text in REQUIRED_NEED_TEXT if text not in pages["need_detail"]]
    forbidden_controls = [
        text
        for text in FORBIDDEN_EXECUTION_CONTROLS
        if text.casefold() in "\n".join(pages.values()).casefold()
    ]
    page_flags = {
        "workbench_pages_passed": all(bool(value.strip()) and "<html" in value.lower() for value in pages.values()),
        "navigation_links_passed": not navigation_missing,
        "hunt_page_passed": not hunt_missing,
        "need_page_passed": not need_missing,
        "disabled_future_action_sections_passed": "disabled" in pages["hunt_detail"].casefold()
        and "extraction" in pages["hunt_detail"].casefold()
        and "model" in pages["hunt_detail"].casefold(),
        "no_forbidden_execution_controls": not forbidden_controls,
        "non_claims_passed": "not global proof" in "\n".join(pages.values()).casefold()
        and "not evidence" in "\n".join(pages.values()).casefold()
        and "not production" in "\n".join(pages.values()).casefold()
        and "not public launch" in "\n".join(pages.values()).casefold(),
    }
    return {
        "schema_version": "search_hunt_workbench_smoke_result.v0",
        "task": "HUNT-08",
        "status": "pass" if all(page_flags.values()) else "fail",
        "base_url": base_url,
        "hunt_id": hunt_id,
        "need_id": need_id,
        "seeded_workflow": seeded,
        "navigation_missing": navigation_missing,
        "hunt_page_missing": hunt_missing,
        "need_page_missing": need_missing,
        "forbidden_execution_controls": forbidden_controls,
        **page_flags,
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


def discover_hunt_id(base_url: str) -> str:
    hunts = fetch_json(base_url, "/api/v1/hunts")
    rows = hunts.get("hunts", [])
    for row in rows:
        hunt_id = str(row.get("id") or "")
        if hunt_id and discover_need_id(base_url, hunt_id):
            return hunt_id
    return str(rows[0].get("id") or "") if rows else ""


def discover_need_id(base_url: str, hunt_id: str) -> str:
    needs = fetch_json(base_url, f"/api/v1/hunt/{hunt_id}/needs")
    rows = needs.get("needs", [])
    return str(rows[0].get("id") or "") if rows else ""


def fetch_text(base_url: str, path: str) -> str:
    request = Request(base_url + path)
    with urlopen(request, timeout=10) as response:  # nosec - localhost-only smoke
        return response.read().decode("utf-8")


def fetch_json(base_url: str, path: str) -> dict[str, Any]:
    request = Request(base_url + path, headers={"Accept": "application/json"})
    with urlopen(request, timeout=10) as response:  # nosec - localhost-only smoke
        return json.loads(response.read().decode("utf-8"))


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "search_hunt_workbench_smoke_result.v0",
        "task": "HUNT-08",
        "status": "fail",
        "error": code,
        "message": message,
        "workbench_pages_passed": False,
        "navigation_links_passed": False,
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
