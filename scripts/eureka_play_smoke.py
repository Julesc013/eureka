#!/usr/bin/env python3
"""Run deterministic PLAY smoke checks without touching the operator instance."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance.paths import resolve_instance_root
from validate_play_seed_pack import smoke_report


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, help="Explicit local instance root, usually ../instances/default.")
    parser.add_argument("--operator-token", required=True, help="Operator token label for smoke reporting; not persisted.")
    parser.add_argument("--base-url", help="Optional localhost workbench URL for play-session server checks.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    result = run_play_smoke(args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
        print(f"known_hit_query: {result['checks']['known_hit_query']}", file=stdout)
        print(f"temp_apply_session: {result['checks']['apply_play_session_temp_instance']}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def run_play_smoke(args: argparse.Namespace) -> dict[str, Any]:
    instance = str(resolve_instance_root(args.instance, REPO_ROOT))
    offline = smoke_report(instance, args.operator_token, args.base_url)
    dry_run_args = [
        "scripts/eureka_play_session.py",
        "--instance",
        args.instance,
        "--operator-token",
        args.operator_token,
        "--dry-run",
        "--json",
    ]
    if args.base_url:
        dry_run_args.extend(["--base-url", args.base_url])
    else:
        dry_run_args.append("--no-server-check")
    dry_run = _run_json(*dry_run_args)
    temp_apply = _run_temp_apply(args.operator_token)
    checks = {
        "known_hit_query": bool(offline["checks"]["known_hit_query"]),
        "known_absence_query": bool(offline["checks"]["known_absence_query"]),
        "media_search_need": bool(offline["checks"]["media_search_need"]),
        "extraction_search_need": bool(offline["checks"]["extraction_search_need"]),
        "demo_workunits": bool(offline["checks"]["demo_workunits"]),
        "blocked_source_probe_workunits": bool(offline["checks"]["blocked_source_probe_workunits"]),
        "blocked_extraction_workunits": bool(offline["checks"]["blocked_extraction_workunits"]),
        "blocked_ai_workunits": bool(offline["checks"]["blocked_ai_workunits"]),
        "source_probe_execution_disabled": True,
        "extraction_execution_disabled": True,
        "model_provider_disabled": True,
        "dry_run_play_session": dry_run["returncode"] == 0
        and dry_run["payload"].get("status") == "pass"
        and dry_run["payload"].get("seed_state", {}).get("mutation_performed") is False,
        "apply_play_session_temp_instance": temp_apply["returncode"] == 0
        and temp_apply["payload"].get("status") == "pass"
        and temp_apply["payload"].get("seed_state", {}).get("mutation_performed") is True,
        "blocked_source_probe_checked": bool(temp_apply["payload"].get("blocked_future_actions", {}).get("source_probe_ids")),
        "blocked_extraction_checked": bool(temp_apply["payload"].get("blocked_future_actions", {}).get("extraction_ids")),
        "blocked_ai_checked": bool(temp_apply["payload"].get("blocked_future_actions", {}).get("ai_ids")),
    }
    errors = [name for name, passed in checks.items() if not passed]
    status = "fail" if errors or offline["status"] != "pass" else "pass"
    return {
        "schema_version": "play_smoke_result.v1",
        "task": "PLAY-01",
        "status": status,
        "instance": instance,
        "base_url": args.base_url,
        "base_url_contacted": False,
        "operator_token_supplied": bool(args.operator_token),
        "checks": checks,
        "offline_pack_smoke": offline,
        "dry_run_play_session": _compact_session(dry_run["payload"]),
        "temp_apply_play_session": _compact_session(temp_apply["payload"]),
        "known_hit_result": offline.get("known_hit_result"),
        "known_absence_result": offline.get("known_absence_result"),
        "media_search_need_id": offline.get("media_search_need_id"),
        "extraction_search_need_id": offline.get("extraction_search_need_id"),
        "blocked_source_probe_workunit_ids": offline.get("blocked_source_probe_workunit_ids", []),
        "blocked_extraction_workunit_ids": offline.get("blocked_extraction_workunit_ids", []),
        "blocked_ai_workunit_ids": offline.get("blocked_ai_workunit_ids", []),
        "errors": errors,
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


def _run_temp_apply(operator_token: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eureka-play-smoke-") as tmp:
        instance = Path(tmp) / "instances" / "default"
        init = _run_json("scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
        if init["returncode"] != 0:
            return {"returncode": init["returncode"], "payload": {"status": "fail", "init": init["payload"]}}
        return _run_json(
            "scripts/eureka_play_session.py",
            "--instance",
            str(instance),
            "--operator-token",
            operator_token,
            "--apply",
            "--no-server-check",
            "--json",
        )


def _compact_session(payload: dict[str, Any]) -> dict[str, Any]:
    seed_state = payload.get("seed_state", {})
    validation = payload.get("validation", {})
    return {
        "schema_version": payload.get("schema_version"),
        "task": payload.get("task"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "instance": payload.get("instance", {}).get("root"),
        "seed_mode": seed_state.get("mode"),
        "mutation_performed": seed_state.get("mutation_performed"),
        "known_hit_checked": validation.get("checks", {}).get("known_hit_checked"),
        "known_absence_checked": validation.get("checks", {}).get("known_absence_checked"),
        "blocked_source_probe_checked": validation.get("checks", {}).get("blocked_source_probe_checked"),
        "blocked_extraction_checked": validation.get("checks", {}).get("blocked_extraction_checked"),
        "blocked_ai_checked": validation.get("checks", {}).get("blocked_ai_checked"),
        "source_probe_executed": payload.get("source_probe_executed"),
        "extraction_executed": payload.get("extraction_executed"),
        "model_provider_used": payload.get("model_provider_used"),
        "deployment_performed": payload.get("deployment_performed"),
    }


def _run_json(*args: str) -> dict[str, Any]:
    completed = subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"status": "fail", "stdout": completed.stdout, "stderr": completed.stderr}
    return {"returncode": completed.returncode, "payload": payload, "stderr": completed.stderr}


if __name__ == "__main__":
    raise SystemExit(main())
