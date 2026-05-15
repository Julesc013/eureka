#!/usr/bin/env python3
"""Demonstrate deterministic local Search Hunt replay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from eureka_hunt_workflow_smoke import run_workflow_smoke
from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search_hunt import build_replay_fixture_from_hunt, run_hunt_replay, verify_existing_hunt_against_replay


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token.")
    parser.add_argument("--query", default="sampleproject")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance))
        require_cli_operator_token(runtime, args.operator_token)
        result = run_demo(runtime, args.query)
    except (LocalApplianceError, LocalOperatorAuthError, ValueError) as exc:
        result = fail_result("hunt_replay_demo_failed", str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("hunt_replay_demo_failed", str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def require_cli_operator_token(runtime: Any, token: str | None) -> None:
    if not token:
        raise LocalOperatorAuthError("operator token is required")
    state = build_operator_auth_state(runtime.config)
    if not state.configured:
        raise LocalOperatorAuthError("operator token is not configured")
    if not verify_operator_token(str(token), state.token_hash, state.token_salt):
        raise LocalOperatorAuthError("operator token is invalid")


def run_demo(runtime: Any, query: str) -> dict[str, Any]:
    workflow = run_workflow_smoke(runtime, query, "definitely-not-present-hunt-10")
    hunt_id = str(workflow.get("hunt_id") or "")
    need_id = str(workflow.get("search_need_id") or "")
    if need_id and not runtime.agent_research.list_tasks(need_id=need_id, limit=1):
        runtime.agent_research.draft_task_from_need(runtime, need_id, operator_label="local_operator")
    fixture = build_replay_fixture_from_hunt(runtime, hunt_id)
    plan = run_hunt_replay(runtime, fixture, mode="plan_only")
    replay = run_hunt_replay(
        runtime,
        fixture,
        operator_context={"authorized": True, "operator_label": "local_operator", "raw_token_stored": False},
        mode="replay_local",
    )
    verify = verify_existing_hunt_against_replay(runtime, hunt_id, fixture)
    blocked_kinds = {item.kind.value for item in replay.record.blocked_steps}
    passed = (
        plan.record.status == "planned"
        and replay.record.status in {"pass", "pass_with_warnings"}
        and verify.record.status == "pass"
        and {"run_source_probe", "run_extraction", "run_ai_model"}.issubset(blocked_kinds)
        and replay.record.to_dict().get("source_probe_executed") is False
        and replay.record.to_dict().get("model_provider_used") is False
    )
    return {
        "schema_version": "hunt_replay_demo_result.v0",
        "status": "pass" if passed else "fail",
        "hunt_id": hunt_id,
        "search_need_id": need_id,
        "workflow": workflow,
        "fixture": fixture.to_dict(),
        "plan": plan.to_dict(),
        "replay": replay.to_dict(),
        "verify_existing": verify.to_dict(),
        "replay_diff": replay.record.diff_summary.to_dict(),
        "blocked_source_probe_remained_blocked": "run_source_probe" in blocked_kinds,
        "blocked_extraction_remained_blocked": "run_extraction" in blocked_kinds,
        "blocked_ai_model_remained_blocked": "run_ai_model" in blocked_kinds,
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


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "hunt_replay_demo_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
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


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("hunt_id"):
        print(f"hunt_id: {result['hunt_id']}", file=stdout)
    replay = result.get("replay", {})
    if replay.get("replay_id"):
        print(f"replay_id: {replay['replay_id']}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
