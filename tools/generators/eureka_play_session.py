#!/usr/bin/env python3
"""Run a repeatable operator PLAY session over the deterministic demo pack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance.paths import describe_instance_layout, resolve_instance_root
from validate_play_seed_pack import (
    COMPATIBILITY_QUERY,
    EXTRACTION_QUERY,
    HARD_SOURCE_ROUTING_QUERY,
    KNOWN_ABSENCE_QUERY,
    KNOWN_HIT_QUERY,
    LEGACY_COMPATIBLE_QUERY,
    MEDIA_QUERY,
    blocked_workunits,
    build_seed_plan,
    demo_absence,
    demo_search,
    load_play_pack,
    smoke_report,
    validate_play_seed_pack,
)


REPORT_SECTIONS = (
    "instance",
    "seed_state",
    "queries",
    "search_results",
    "absence",
    "absence_results",
    "hunts",
    "search_needs",
    "workunits",
    "blocked_future_actions",
    "server_routes_if_checked",
    "server",
    "validation",
    "warnings",
    "boundaries",
    "next_suggested_actions",
    "next_actions",
)

LOCAL_SERVER_HOSTS = {"127.0.0.1", "localhost", "::1"}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = build_play_session(args)
    except Exception as exc:  # pragma: no cover - CLI safety boundary
        result = {
            "schema_version": "play_session_report.v1",
            "task": "PLAY-01",
            "status": "fail",
            "error": "play_session_failed",
            "message": str(exc),
            "fake_evidence_created": False,
            "fake_verified_records_created": False,
            "live_source_call_performed": False,
            "source_probe_executed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "download_install_execute_performed": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
        print(f"ERROR: {exc}", file=stderr)
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
        print(f"mode: {result.get('seed_mode')}", file=stdout)
        print(f"instance: {result.get('instance_root')}", file=stdout)
        print(f"known_hit: {bool(result.get('known_hit_result'))}", file=stdout)
        print(f"known_absence: {bool(result.get('known_absence_result'))}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="Explicit local instance root, usually ../instances/default.")
    parser.add_argument("--operator-token", help="Operator token required for --apply; not persisted by dry-run.")
    parser.add_argument("--base-url", help="Optional localhost workbench URL to check, for example http://127.0.0.1:8765.")
    parser.add_argument("--seed-demo", action="store_true", help="Include demo seed planning; dry-run unless --apply is also supplied.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Read-only session mode. This is the default.")
    mode.add_argument("--apply", action="store_true", help="Write demo state to the explicit --instance path.")
    parser.add_argument(
        "--apply-seed",
        action="store_true",
        help="Deprecated alias for --seed-demo --apply, retained for PLAY-00 compatibility.",
    )
    parser.add_argument("--query", action="append", default=[], help="Additional local demo query to include in the report.")
    parser.add_argument("--no-server-check", action="store_true", help="Skip optional localhost workbench route checks.")
    parser.add_argument("--expect-server", action="store_true", help="Fail if --base-url localhost route checks do not pass.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON report path.")
    return parser


def build_play_session(args: argparse.Namespace) -> dict[str, Any]:
    instance_root = resolve_instance_root(args.instance, REPO_ROOT)
    pack = load_play_pack([])
    validation = validate_play_seed_pack(run_script_smokes=False)
    apply_mode = bool(args.apply or args.apply_seed)
    dry_run = not apply_mode
    warnings: list[str] = []
    if args.apply_seed:
        warnings.append("--apply-seed is deprecated; use --seed-demo --apply for PLAY-01.")
    if apply_mode and not str(args.operator_token or "").strip():
        raise ValueError("--operator-token is required with --apply")

    seed_result = _run_seed_apply(args) if apply_mode else _run_seed_dry(args)
    smoke = smoke_report(str(instance_root), str(args.operator_token or ""), args.base_url)
    query_report = build_query_report(pack, extra_queries=list(args.query or []))
    hunts = {"count": len(pack["hunts"]["hunts"]), "records": pack["hunts"]["hunts"]}
    needs = build_need_report(pack)
    workunits = build_workunit_report(pack)
    blocked = build_blocked_report(pack)
    server = check_server_routes(args.base_url, no_server_check=args.no_server_check, expect_server=args.expect_server)
    if server.get("warning"):
        warnings.append(str(server["warning"]))

    checks = {
        "seed_pack_valid": validation["status"] == "pass",
        "seed_step_passed": seed_result.get("status") == "pass",
        "smoke_report_passed": smoke["status"] == "pass",
        "known_hit_checked": bool(query_report["required"]["known_hit_query"]["results"]),
        "known_absence_checked": bool(query_report["absence"]["known_absence_query"]),
        "demo_hunts_checked": bool(hunts["records"]),
        "demo_search_needs_checked": bool(needs["records"]),
        "demo_workunits_checked": bool(workunits["records"]),
        "media_search_need_checked": needs["by_query"].get(MEDIA_QUERY) is not None,
        "extraction_search_need_checked": needs["by_query"].get(EXTRACTION_QUERY) is not None,
        "hard_source_routing_checked": needs["by_query"].get(HARD_SOURCE_ROUTING_QUERY) is not None,
        "compatibility_checked": needs["by_query"].get(COMPATIBILITY_QUERY) is not None,
        "blocked_source_probe_checked": bool(blocked["source_probe"]),
        "blocked_extraction_checked": bool(blocked["extraction"]),
        "blocked_ai_checked": bool(blocked["ai"]),
        "server_check_passed": server["status"] == "pass"
        or (server["status"] in {"skipped", "warn"} and not args.expect_server),
    }
    status = "pass" if all(checks.values()) else "fail"

    boundaries = boundary_report()
    next_actions = [
        "Open the local workbench if the server is running.",
        "Inspect demo Hunts, SearchNeeds, and blocked WorkUnits.",
        "Proceed to PLAY-02 for a tighter demo query/absence/hunt smoke pack.",
    ]
    report: dict[str, Any] = {
        "schema_version": "play_session_report.v1",
        "task": "PLAY-01",
        "status": status,
        "mode": "apply" if apply_mode else "dry_run",
        "instance": {
            "root": str(instance_root),
            "exists": instance_root.exists(),
            "layout": describe_instance_layout(REPO_ROOT, instance_root),
            "preferred_instance": "../instances/default",
        },
        "seed_state": {
            "requested": bool(args.seed_demo or apply_mode),
            "mode": "apply" if apply_mode else "dry_run",
            "dry_run": dry_run,
            "apply": apply_mode,
            "result": seed_result,
            "plan": build_seed_plan(pack),
            "mutation_performed": bool(seed_result.get("mutation_performed")),
        },
        "search_results": query_report["search_results"],
        "absence_results": query_report["absence"],
        "queries": query_report["required"],
        "absence": query_report["absence"],
        "hunts": hunts,
        "search_needs": needs,
        "workunits": workunits,
        "blocked_future_actions": blocked,
        "server_routes_if_checked": server,
        "server": server,
        "validation": {
            "seed_pack": validation,
            "smoke": smoke,
            "checks": checks,
        },
        "warnings": warnings,
        "boundaries": boundaries,
        "next_suggested_actions": next_actions,
        "next_actions": next_actions,
        "required_report_sections": list(REPORT_SECTIONS),
    }
    report.update(backwards_compatible_fields(report, args.base_url))
    report.update(boundaries)
    return report


def build_query_report(pack: Mapping[str, Any], *, extra_queries: list[str]) -> dict[str, Any]:
    required_queries = {
        "known_hit_query": KNOWN_HIT_QUERY,
        "media_search_need_query": MEDIA_QUERY,
        "extraction_search_need_query": EXTRACTION_QUERY,
        "hard_source_routing_query": HARD_SOURCE_ROUTING_QUERY,
        "compatibility_query": COMPATIBILITY_QUERY,
        "legacy_compatible_query": LEGACY_COMPATIBLE_QUERY,
    }
    required: dict[str, dict[str, Any]] = {}
    search_results: dict[str, list[dict[str, Any]]] = {}
    for role, query in required_queries.items():
        results = demo_search(pack, query)
        required[role] = {"query": query, "results": results}
        search_results[query] = results
    for query in extra_queries:
        search_results[query] = demo_search(pack, query)
    absence_record = demo_absence(pack, KNOWN_ABSENCE_QUERY)
    return {
        "required": required,
        "search_results": search_results,
        "absence": {
            "known_absence_query": absence_record,
            KNOWN_ABSENCE_QUERY: absence_record,
        },
    }


def build_need_report(pack: Mapping[str, Any]) -> dict[str, Any]:
    records = [dict(item) for item in pack["search_needs"]["search_needs"]]
    by_query = {str(item["query"]): dict(item) for item in records}
    return {
        "count": len(records),
        "records": records,
        "by_query": by_query,
        "unresolved_verified_result_created": any(item.get("verified_result_created") is True for item in records),
    }


def build_workunit_report(pack: Mapping[str, Any]) -> dict[str, Any]:
    records = [dict(item) for item in pack["workunits"]["workunits"]]
    by_kind: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        by_kind.setdefault(str(item.get("kind")), []).append(dict(item))
    return {
        "count": len(records),
        "records": records,
        "by_kind": by_kind,
        "executed_count": 0,
    }


def build_blocked_report(pack: Mapping[str, Any]) -> dict[str, Any]:
    source = blocked_workunits(pack, kind="source_probe")
    extraction = blocked_workunits(pack, kind="extraction_task")
    ai = blocked_workunits(pack, kind="agent_task")
    return {
        "source_probe": source,
        "extraction": extraction,
        "ai": ai,
        "source_probe_ids": [item["id"] for item in source],
        "extraction_ids": [item["id"] for item in extraction],
        "ai_ids": [item["id"] for item in ai],
        "all_remain_blocked_by_policy": all(item.get("blocked_by_policy") is True for item in source + extraction + ai),
    }


def check_server_routes(base_url: str | None, *, no_server_check: bool, expect_server: bool) -> dict[str, Any]:
    if no_server_check:
        return {"status": "skipped", "checked": False, "reason": "--no-server-check supplied", "routes": []}
    if not base_url:
        status = "fail" if expect_server else "skipped"
        return {
            "status": status,
            "checked": False,
            "reason": "--base-url not supplied",
            "routes": [],
            "warning": "Server was expected but --base-url was not supplied." if expect_server else None,
        }
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in LOCAL_SERVER_HOSTS:
        return {
            "status": "fail",
            "checked": False,
            "reason": "PLAY server checks are restricted to localhost URLs.",
            "routes": [],
            "warning": "Skipped non-local server URL to preserve PLAY boundaries.",
        }
    routes = [
        ("status", "/status"),
        ("known_hit_search_page", "/search?q=" + urllib.parse.quote(KNOWN_HIT_QUERY)),
        ("hunts_page", "/hunts"),
    ]
    route_results = []
    failures = []
    for route_id, path in routes:
        url = urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        result = _fetch_local_route(url)
        result["route_id"] = route_id
        route_results.append(result)
        if not result["ok"]:
            failures.append(route_id)
    if failures and expect_server:
        status = "fail"
    elif failures:
        status = "warn"
    else:
        status = "pass"
    return {"status": status, "checked": True, "base_url": base_url, "routes": route_results, "failures": failures}


def _fetch_local_route(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return {"url": url, "ok": 200 <= int(response.status) < 400, "status_code": int(response.status)}
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return {"url": url, "ok": False, "error": str(exc)}


def _run_seed_apply(args: argparse.Namespace) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/eureka_seed_play_demo.py",
            "--instance",
            args.instance,
            "--operator-token",
            str(args.operator_token or ""),
            "--apply",
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return _payload(completed)


def _run_seed_dry(args: argparse.Namespace) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_seed_play_demo.py", "--instance", args.instance, "--dry-run", "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return _payload(completed)


def _payload(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"status": "fail", "stdout": completed.stdout, "stderr": completed.stderr}
    payload["returncode"] = completed.returncode
    return payload


def backwards_compatible_fields(report: Mapping[str, Any], base_url: str | None) -> dict[str, Any]:
    hit_results = report["search_results"].get(KNOWN_HIT_QUERY, [])
    absence_result = report["absence_results"].get("known_absence_query")
    needs_by_query = report["search_needs"]["by_query"]
    blocked = report["blocked_future_actions"]
    return {
        "instance_root": report["instance"]["root"],
        "layout": report["instance"]["layout"],
        "base_url": base_url,
        "base_url_contacted": bool(report["server_routes_if_checked"].get("checked")),
        "seed_mode": report["seed_state"]["mode"],
        "seed_result": report["seed_state"]["result"],
        "seed_plan": report["seed_state"]["plan"],
        "known_hit_query": KNOWN_HIT_QUERY,
        "known_hit_result": hit_results[0] if hit_results else None,
        "known_absence_query": KNOWN_ABSENCE_QUERY,
        "known_absence_result": absence_result,
        "demo_hunts": report["hunts"]["records"],
        "media_search_need": needs_by_query.get(MEDIA_QUERY),
        "extraction_search_need": needs_by_query.get(EXTRACTION_QUERY),
        "demo_workunits": report["workunits"]["records"],
        "blocked_source_probe_workunit_ids": blocked["source_probe_ids"],
        "blocked_extraction_workunit_ids": blocked["extraction_ids"],
        "blocked_ai_workunit_ids": blocked["ai_ids"],
        "deterministic_local_worker_run": False,
        "deterministic_local_worker_reason": "PLAY-01 inspects queued/blocked state only; it does not execute WorkUnits.",
    }


def boundary_report() -> dict[str, bool]:
    return {
        "fake_evidence_created": False,
        "fake_verified_records_created": False,
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "instance_state_committed": False,
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
