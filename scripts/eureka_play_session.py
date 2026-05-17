#!/usr/bin/env python3
"""Emit an operator play-session report over the deterministic demo pack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.paths import describe_instance_layout, resolve_instance_root
from validate_play_seed_pack import (
    EXTRACTION_QUERY,
    KNOWN_ABSENCE_QUERY,
    KNOWN_HIT_QUERY,
    MEDIA_QUERY,
    blocked_workunits,
    build_seed_plan,
    demo_absence,
    demo_search,
    load_play_pack,
    smoke_report,
    validate_play_seed_pack,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="Explicit local instance root, usually ../instances/default.")
    parser.add_argument("--operator-token", required=True, help="Operator token for optional apply mode; not persisted by dry-run.")
    parser.add_argument("--base-url", help="Optional local workbench URL. PLAY-00 does not contact it by default.")
    parser.add_argument("--apply-seed", action="store_true", help="Explicitly load demo state into --instance before reporting.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON report path.")
    args = parser.parse_args(argv)

    try:
        result = build_play_session(args)
    except Exception as exc:  # pragma: no cover - CLI safety boundary
        result = {
            "schema_version": "play_session_report.v0",
            "task": "PLAY-00",
            "status": "fail",
            "error": "play_session_failed",
            "message": str(exc),
            "source_probe_executed": False,
            "extraction_executed": False,
            "model_provider_used": False,
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
        print(f"known_hit: {bool(result.get('known_hit_result'))}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def build_play_session(args: argparse.Namespace) -> dict[str, Any]:
    instance_root = resolve_instance_root(args.instance, REPO_ROOT)
    pack = load_play_pack([])
    validation = validate_play_seed_pack(run_script_smokes=False)
    seed_result = _run_seed(args) if args.apply_seed else _run_seed_dry(args)
    smoke = smoke_report(str(instance_root), args.operator_token, args.base_url)
    known_hit = demo_search(pack, KNOWN_HIT_QUERY)
    known_absence = demo_absence(pack, KNOWN_ABSENCE_QUERY)
    media_need = _need(pack, MEDIA_QUERY)
    extraction_need = _need(pack, EXTRACTION_QUERY)
    blocked_source = blocked_workunits(pack, kind="source_probe")
    blocked_extraction = blocked_workunits(pack, kind="extraction_task")
    blocked_ai = blocked_workunits(pack, kind="agent_task")
    status = "pass" if validation["status"] == "pass" and seed_result.get("status") == "pass" and smoke["status"] == "pass" else "fail"
    return {
        "schema_version": "play_session_report.v0",
        "task": "PLAY-00",
        "status": status,
        "instance": str(instance_root),
        "layout": describe_instance_layout(REPO_ROOT, instance_root),
        "base_url": args.base_url,
        "base_url_contacted": False,
        "seed_mode": "apply" if args.apply_seed else "dry_run",
        "seed_result": seed_result,
        "seed_plan": build_seed_plan(pack),
        "known_hit_query": KNOWN_HIT_QUERY,
        "known_hit_result": known_hit[0] if known_hit else None,
        "known_absence_query": KNOWN_ABSENCE_QUERY,
        "known_absence_result": known_absence,
        "demo_hunts": pack["hunts"]["hunts"],
        "media_search_need": media_need,
        "extraction_search_need": extraction_need,
        "demo_workunits": pack["workunits"]["workunits"],
        "blocked_source_probe_workunit_ids": [item["id"] for item in blocked_source],
        "blocked_extraction_workunit_ids": [item["id"] for item in blocked_extraction],
        "blocked_ai_workunit_ids": [item["id"] for item in blocked_ai],
        "deterministic_local_worker_run": False,
        "deterministic_local_worker_reason": "PLAY-00 reports queued/blocked state only; it does not execute WorkUnits.",
        "live_source_call_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _run_seed(args: argparse.Namespace) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/eureka_seed_play_demo.py",
            "--instance",
            args.instance,
            "--operator-token",
            args.operator_token,
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


def _need(pack: dict[str, Any], query: str) -> dict[str, Any] | None:
    normalized = " ".join(query.strip().lower().split())
    for item in pack["search_needs"]["search_needs"]:
        if item["normalized_query"] == normalized:
            return dict(item)
    return None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
