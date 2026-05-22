#!/usr/bin/env python3
"""Run the PLAY demo query/absence/hunt smoke pack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.paths import resolve_instance_root
from validate_play_seed_pack import (
    COMPATIBILITY_QUERY,
    EXTRACTION_QUERY,
    HARD_SOURCE_ROUTING_QUERY,
    KNOWN_ABSENCE_QUERY,
    KNOWN_HIT_QUERY,
    MEDIA_QUERY,
    blocked_workunits,
    demo_absence,
    demo_search,
    load_play_pack,
    smoke_report,
)


LOCAL_SERVER_HOSTS = {"127.0.0.1", "localhost", "::1"}
REPORT_SECTIONS = (
    "instance",
    "seed",
    "query_results",
    "absence_results",
    "hunts",
    "search_needs",
    "workunits",
    "blocked_future_actions",
    "routes",
    "validation",
    "boundaries",
    "warnings",
    "next_actions",
)
QUERY_ROLES = {
    "known_hit": KNOWN_HIT_QUERY,
    "known_absence": KNOWN_ABSENCE_QUERY,
    "media_search_need": MEDIA_QUERY,
    "extraction_search_need": EXTRACTION_QUERY,
    "hard_source_routing": HARD_SOURCE_ROUTING_QUERY,
    "compatibility": COMPATIBILITY_QUERY,
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run_play_smoke(args)
    except Exception as exc:  # pragma: no cover - CLI guardrail
        result = {
            "schema_version": "play_smoke_report.v2",
            "task": "PLAY-02",
            "status": "fail",
            "error": "play_smoke_failed",
            "message": str(exc),
            **boundary_report(),
        }
        print(f"ERROR: {exc}", file=stderr)
    if args.output:
        write_json(Path(args.output), result)
    if args.markdown_output:
        write_text(Path(args.markdown_output), render_markdown_report(result))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
        print(f"mode: {result.get('mode')}", file=stdout)
        print(f"instance: {result.get('instance', {}).get('root')}", file=stdout)
        print(f"known_hit: {result.get('validation', {}).get('checks', {}).get('known_hit_checked')}", file=stdout)
        print(f"known_absence: {result.get('validation', {}).get('checks', {}).get('known_absence_checked')}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local instance root, usually ../instances/default.")
    parser.add_argument("--operator-token", required=True, help="Operator token label for temp apply; not persisted.")
    parser.add_argument("--base-url", help="Optional localhost workbench URL for read-only route checks.")
    parser.add_argument("--use-temp-instance", action="store_true", help="Run smoke against a temporary explicit instance.")
    parser.add_argument(
        "--apply-demo-to-temp",
        action="store_true",
        help="Seed the PLAY demo into the temporary instance. Requires --use-temp-instance.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Read-only smoke mode. This is the default.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON report path.")
    parser.add_argument("--markdown-output", help="Optional Markdown report path.")
    parser.add_argument("--skip-server-routes", action="store_true", help="Skip optional localhost route checks.")
    parser.add_argument("--expect-server", action="store_true", help="Fail if supplied localhost route checks fail.")
    return parser


def run_play_smoke(args: argparse.Namespace) -> dict[str, Any]:
    if args.apply_demo_to_temp and not args.use_temp_instance:
        raise ValueError("--apply-demo-to-temp is only allowed with --use-temp-instance")
    if not args.use_temp_instance and not args.instance:
        raise ValueError("--instance is required unless --use-temp-instance is supplied")

    if args.use_temp_instance:
        return _run_with_temp_instance(args)
    instance_root = resolve_instance_root(str(args.instance), REPO_ROOT)
    session = _run_play_session(
        str(instance_root),
        args.operator_token,
        apply_mode=False,
        base_url=args.base_url,
        skip_server_routes=args.skip_server_routes,
        expect_server=args.expect_server,
    )
    return _build_report(
        args,
        instance_root=instance_root,
        mode="dry_run",
        seed={"status": "skipped", "mutation_performed": False, "reason": "operator instance smoke is dry-run only"},
        play_session=session,
        temp_instance=False,
    )


def _run_with_temp_instance(args: argparse.Namespace) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eureka-play-smoke-pack-") as tmp:
        instance_root = Path(tmp) / "instances" / "default"
        init = _run_json("scripts/eureka_init_instance.py", "--instance", str(instance_root), "--json")
        if init["returncode"] != 0 or init["payload"].get("status") != "pass":
            return _failure_report(args, str(instance_root), "temp_instance_init_failed", init["payload"])
        if args.apply_demo_to_temp:
            session = _run_play_session(
                str(instance_root),
                args.operator_token,
                apply_mode=True,
                base_url=args.base_url,
                skip_server_routes=args.skip_server_routes,
                expect_server=args.expect_server,
            )
            seed = session["payload"].get("seed_state", {})
            mode = "temp_apply"
        else:
            session = _run_play_session(
                str(instance_root),
                args.operator_token,
                apply_mode=False,
                base_url=args.base_url,
                skip_server_routes=args.skip_server_routes,
                expect_server=args.expect_server,
            )
            seed = {"status": "pass", "mutation_performed": False, "mode": "dry_run"}
            mode = "temp_dry_run"
        return _build_report(
            args,
            instance_root=instance_root,
            mode=mode,
            seed=seed,
            play_session=session,
            temp_instance=True,
        )


def _build_report(
    args: argparse.Namespace,
    *,
    instance_root: Path,
    mode: str,
    seed: Mapping[str, Any],
    play_session: Mapping[str, Any],
    temp_instance: bool,
) -> dict[str, Any]:
    pack = load_play_pack([])
    offline = smoke_report(str(instance_root), args.operator_token, args.base_url)
    query_results = build_query_results(pack)
    absence_results = build_absence_results(pack)
    needs = build_search_need_results(pack)
    workunits = build_workunit_results(pack)
    blocked = build_blocked_future_actions(pack)
    routes = check_route_matrix(
        args.base_url,
        skip_server_routes=bool(args.skip_server_routes),
        expect_server=bool(args.expect_server),
    )
    checks = {
        "known_hit_checked": bool(query_results["known_hit"]["results"]),
        "known_absence_checked": bool(absence_results["known_absence"]["record"]),
        "media_search_need_checked": needs["by_role"]["media_search_need"] is not None,
        "extraction_search_need_checked": needs["by_role"]["extraction_search_need"] is not None
        and bool(blocked["source_probe_ids"] or blocked["extraction_ids"]),
        "hard_source_routing_checked": needs["by_role"]["hard_source_routing"] is not None,
        "compatibility_query_checked": needs["by_role"]["compatibility"] is not None
        and needs["by_role"]["compatibility"].get("verified_result_created") is False,
        "demo_hunts_visible": bool(pack["hunts"]["hunts"]),
        "demo_search_needs_visible": bool(needs["records"]),
        "demo_workunits_visible": bool(workunits["records"]),
        "blocked_source_probe_checked": bool(blocked["source_probe_ids"]),
        "blocked_extraction_checked": bool(blocked["extraction_ids"]),
        "blocked_ai_checked": bool(blocked["ai_ids"]),
        "operator_instance_not_mutated": temp_instance or seed.get("mutation_performed") is False,
        "offline_pack_smoke_passed": offline.get("status") == "pass",
        "play_session_passed": play_session.get("returncode") == 0 and play_session.get("payload", {}).get("status") == "pass",
        "routes_passed": routes["status"] == "pass" or (routes["status"] in {"skipped", "warn"} and not args.expect_server),
    }
    errors = [name for name, passed in checks.items() if not passed]
    status = "fail" if errors else "pass"
    warnings = []
    if routes.get("warning"):
        warnings.append(routes["warning"])
    report: dict[str, Any] = {
        "schema_version": "play_smoke_report.v2",
        "task": "PLAY-02",
        "status": status,
        "mode": mode,
        "required_report_sections": list(REPORT_SECTIONS),
        "instance": {
            "root": str(instance_root),
            "temporary": temp_instance,
            "preferred_instance": "../instances/default",
            "operator_instance_mutated": False,
        },
        "seed": dict(seed),
        "query_results": query_results,
        "absence_results": absence_results,
        "hunts": {"count": len(pack["hunts"]["hunts"]), "records": pack["hunts"]["hunts"]},
        "search_needs": needs,
        "workunits": workunits,
        "blocked_future_actions": blocked,
        "routes": routes,
        "validation": {
            "checks": checks,
            "errors": errors,
            "offline_pack_smoke": offline,
            "play_session": compact_session(play_session.get("payload", {})),
        },
        "boundaries": boundary_report(),
        "warnings": warnings,
        "next_actions": [
            "Use this smoke before SYN, IA, F0, workbench, and source-pilot changes.",
            "Start IA-00 only after operator approval for connector metadata closure.",
        ],
        **boundary_report(),
    }
    report.update(
        {
            "operator_instance_mutated": False,
            "temp_instance_smoke_passed": temp_instance and status == "pass",
            "dry_run_smoke_passed": mode == "dry_run" and status == "pass",
            "known_hit_checked": checks["known_hit_checked"],
            "known_absence_checked": checks["known_absence_checked"],
            "media_search_need_checked": checks["media_search_need_checked"],
            "extraction_search_need_checked": checks["extraction_search_need_checked"],
            "hard_source_routing_checked": checks["hard_source_routing_checked"],
            "compatibility_query_checked": checks["compatibility_query_checked"],
            "blocked_source_probe_checked": checks["blocked_source_probe_checked"],
            "blocked_extraction_checked": checks["blocked_extraction_checked"],
            "blocked_ai_checked": checks["blocked_ai_checked"],
        }
    )
    return report


def build_query_results(pack: Mapping[str, Any]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for role, query in QUERY_ROLES.items():
        hits = demo_search(pack, query)
        results[role] = {
            "query": query,
            "results": hits,
            "result_count": len(hits),
            "reviewed_result_visible": bool(hits) if role == "known_hit" else False,
            "verified_record_created": False,
        }
    return results


def build_absence_results(pack: Mapping[str, Any]) -> dict[str, Any]:
    record = demo_absence(pack, KNOWN_ABSENCE_QUERY)
    return {
        "known_absence": {
            "query": KNOWN_ABSENCE_QUERY,
            "record": record,
            "result_count": int(record.get("result_count", 0)) if isinstance(record, Mapping) else None,
            "scope": record.get("absence_scope") if isinstance(record, Mapping) else None,
            "global_nonexistence_claimed": False,
        }
    }


def build_search_need_results(pack: Mapping[str, Any]) -> dict[str, Any]:
    records = [dict(item) for item in pack["search_needs"]["search_needs"]]
    by_role = {role: _need_for_query(pack, query) for role, query in QUERY_ROLES.items() if role not in {"known_hit", "known_absence"}}
    return {
        "count": len(records),
        "records": records,
        "by_role": by_role,
        "unresolved_verified_result_created": any(item.get("verified_result_created") is True for item in records),
    }


def build_workunit_results(pack: Mapping[str, Any]) -> dict[str, Any]:
    records = [dict(item) for item in pack["workunits"]["workunits"]]
    by_kind: dict[str, list[dict[str, Any]]] = {}
    for item in records:
        by_kind.setdefault(str(item.get("kind")), []).append(dict(item))
    return {"count": len(records), "records": records, "by_kind": by_kind, "executed_count": 0}


def build_blocked_future_actions(pack: Mapping[str, Any]) -> dict[str, Any]:
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


def check_route_matrix(base_url: str | None, *, skip_server_routes: bool, expect_server: bool) -> dict[str, Any]:
    routes = route_matrix_rows()
    if skip_server_routes:
        return {"status": "skipped", "checked": False, "reason": "--skip-server-routes supplied", "routes": []}
    if not base_url:
        return {
            "status": "fail" if expect_server else "skipped",
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
            "reason": "PLAY route checks are restricted to localhost URLs.",
            "routes": [],
            "warning": "Skipped non-local server URL to preserve PLAY boundaries.",
        }
    results = []
    failures = []
    for row in routes:
        route = row["route"]
        url = urllib.parse.urljoin(base_url.rstrip("/") + "/", route.lstrip("/"))
        result = _fetch_local_route(url, row["expected_status"])
        result["route_id"] = row["route_id"]
        result["route"] = route
        results.append(result)
        if not result["ok"]:
            failures.append(row["route_id"])
    status = "fail" if failures and expect_server else "warn" if failures else "pass"
    return {"status": status, "checked": True, "base_url": base_url, "routes": results, "failures": failures}


def route_matrix_rows() -> list[dict[str, Any]]:
    return [
        {"route_id": "root_page", "route": "/", "expected_status": [200]},
        {"route_id": "status_page", "route": "/status", "expected_status": [200]},
        {"route_id": "search_known_hit", "route": "/search?q=" + urllib.parse.quote(KNOWN_HIT_QUERY), "expected_status": [200]},
        {
            "route_id": "search_known_absence",
            "route": "/search?q=" + urllib.parse.quote(KNOWN_ABSENCE_QUERY),
            "expected_status": [200],
        },
        {"route_id": "hunts_page", "route": "/hunts", "expected_status": [200]},
        {"route_id": "hunt_detail_if_available", "route": "/hunt/play.hunt.sampleproject.v0", "expected_status": [200, 404]},
        {
            "route_id": "search_need_detail_if_available",
            "route": "/need/play.need.dtheater_source.v0",
            "expected_status": [200, 404],
        },
        {
            "route_id": "workunit_detail_or_list_if_available",
            "route": "/need/play.need.stylewriter_driver.v0/workunits",
            "expected_status": [200, 404],
        },
        {"route_id": "api_search", "route": "/api/v1/search?q=" + urllib.parse.quote(KNOWN_HIT_QUERY), "expected_status": [200]},
        {
            "route_id": "api_absence",
            "route": "/api/v1/absence?q=" + urllib.parse.quote(KNOWN_ABSENCE_QUERY),
            "expected_status": [200],
        },
        {"route_id": "api_hunts_if_available", "route": "/api/v1/hunts", "expected_status": [200]},
        {"route_id": "api_status", "route": "/api/v1/status", "expected_status": [200]},
    ]


def _fetch_local_route(url: str, expected_status: Sequence[int]) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            status_code = int(response.status)
            sample = response.read(512).decode("utf-8", errors="replace")
            return {
                "url": url,
                "ok": status_code in set(expected_status),
                "status_code": status_code,
                "expected_status": list(expected_status),
                "content_sample": sample[:160],
            }
    except urllib.error.HTTPError as exc:
        status_code = int(exc.code)
        return {
            "url": url,
            "ok": status_code in set(expected_status),
            "status_code": status_code,
            "expected_status": list(expected_status),
        }
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return {"url": url, "ok": False, "error": str(exc), "expected_status": list(expected_status)}


def _need_for_query(pack: Mapping[str, Any], query: str) -> dict[str, Any] | None:
    normalized = " ".join(str(query or "").strip().lower().split())
    for need in pack["search_needs"]["search_needs"]:
        if " ".join(str(need.get("query", "")).strip().lower().split()) == normalized:
            return dict(need)
    return None


def _run_play_session(
    instance: str,
    operator_token: str,
    *,
    apply_mode: bool,
    base_url: str | None,
    skip_server_routes: bool,
    expect_server: bool,
) -> dict[str, Any]:
    args = [
        "scripts/eureka_play_session.py",
        "--instance",
        instance,
        "--operator-token",
        operator_token,
        "--json",
    ]
    if apply_mode:
        args.append("--apply")
    else:
        args.append("--dry-run")
    if base_url:
        args.extend(["--base-url", base_url])
    if skip_server_routes:
        args.append("--no-server-check")
    if expect_server:
        args.append("--expect-server")
    return _run_json(*args)


def compact_session(payload: Mapping[str, Any]) -> dict[str, Any]:
    seed = payload.get("seed_state", {}) if isinstance(payload.get("seed_state"), Mapping) else {}
    validation = payload.get("validation", {}) if isinstance(payload.get("validation"), Mapping) else {}
    checks = validation.get("checks", {}) if isinstance(validation.get("checks"), Mapping) else {}
    return {
        "schema_version": payload.get("schema_version"),
        "task": payload.get("task"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "seed_mode": seed.get("mode"),
        "mutation_performed": seed.get("mutation_performed"),
        "known_hit_checked": checks.get("known_hit_checked"),
        "known_absence_checked": checks.get("known_absence_checked"),
        "demo_hunts_checked": checks.get("demo_hunts_checked"),
        "demo_search_needs_checked": checks.get("demo_search_needs_checked"),
        "demo_workunits_checked": checks.get("demo_workunits_checked"),
        "blocked_source_probe_checked": checks.get("blocked_source_probe_checked"),
        "blocked_extraction_checked": checks.get("blocked_extraction_checked"),
        "blocked_ai_checked": checks.get("blocked_ai_checked"),
        "source_probe_executed": payload.get("source_probe_executed"),
        "extraction_executed": payload.get("extraction_executed"),
        "model_provider_used": payload.get("model_provider_used"),
        "deployment_performed": payload.get("deployment_performed"),
    }


def _failure_report(args: argparse.Namespace, instance: str, reason: str, details: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "play_smoke_report.v2",
        "task": "PLAY-02",
        "status": "fail",
        "mode": "temp_apply" if args.apply_demo_to_temp else "temp_dry_run",
        "instance": {"root": instance, "temporary": True, "preferred_instance": "../instances/default"},
        "seed": {"status": "fail", "mutation_performed": False, "reason": reason, "details": dict(details)},
        "query_results": {},
        "absence_results": {},
        "hunts": {"count": 0, "records": []},
        "search_needs": {"count": 0, "records": []},
        "workunits": {"count": 0, "records": []},
        "blocked_future_actions": {},
        "routes": {"status": "skipped", "checked": False},
        "validation": {"checks": {}, "errors": [reason]},
        "boundaries": boundary_report(),
        "warnings": [],
        "next_actions": [],
        **boundary_report(),
    }


def render_markdown_report(report: Mapping[str, Any]) -> str:
    checks = report.get("validation", {}).get("checks", {}) if isinstance(report.get("validation"), Mapping) else {}
    lines = [
        "# PLAY-02 Smoke Report",
        "",
        f"- status: {report.get('status')}",
        f"- mode: {report.get('mode')}",
        f"- instance: {report.get('instance', {}).get('root') if isinstance(report.get('instance'), Mapping) else ''}",
        f"- known_hit_checked: {checks.get('known_hit_checked') if isinstance(checks, Mapping) else None}",
        f"- known_absence_checked: {checks.get('known_absence_checked') if isinstance(checks, Mapping) else None}",
        f"- media_search_need_checked: {checks.get('media_search_need_checked') if isinstance(checks, Mapping) else None}",
        f"- extraction_search_need_checked: {checks.get('extraction_search_need_checked') if isinstance(checks, Mapping) else None}",
        f"- blocked_source_probe_checked: {checks.get('blocked_source_probe_checked') if isinstance(checks, Mapping) else None}",
        f"- blocked_extraction_checked: {checks.get('blocked_extraction_checked') if isinstance(checks, Mapping) else None}",
        f"- blocked_ai_checked: {checks.get('blocked_ai_checked') if isinstance(checks, Mapping) else None}",
        "",
        "Boundaries: no live source calls, source probes, extraction, model/provider calls, downloads, deployment, or production/public-launch claim.",
        "",
    ]
    return "\n".join(lines)


def boundary_report() -> dict[str, bool]:
    return {
        "instance_state_committed": False,
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


def _run_json(*args: str) -> dict[str, Any]:
    completed = subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"status": "fail", "stdout": completed.stdout, "stderr": completed.stderr}
    return {"returncode": completed.returncode, "payload": payload, "stderr": completed.stderr}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
