#!/usr/bin/env python3
"""Plan and run safe local workers for a Search Hunt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local.operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search.hunt import (
    SearchHuntError,
    build_background_hunt_plan,
    list_background_hunt_runs,
    run_background_hunt_batch,
    run_next_hunt_workunit,
    summarize_background_hunt,
)


MUTATION_COMMANDS = {"run-next", "run-batch"}
MAX_BATCH = 10


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.command:
        result = fail_result("missing_command", "background hunt runner command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: background hunt runner command is required", file=stderr)
        return 2
    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=args.command not in MUTATION_COMMANDS)
        if args.command in MUTATION_COMMANDS:
            require_cli_operator_token(runtime, args.operator_token)
        result = dispatch(runtime, args)
    except (LocalApplianceError, LocalOperatorAuthError, SearchHuntError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("background_hunt_runner_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("background_hunt_runner_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--hunt-id", required=True)
    parser.add_argument("--operator-token")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    subparsers = parser.add_subparsers(dest="command")
    for name in ("plan", "runs", "summary", "run-next"):
        command = subparsers.add_parser(name)
        add_output_options(command)
    batch = subparsers.add_parser("run-batch")
    batch.add_argument("--limit", type=int, default=1)
    add_output_options(batch)
    return parser


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--output", default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def require_cli_operator_token(runtime: Any, token: str | None) -> None:
    if not token:
        raise LocalOperatorAuthError("operator token is required")
    state = build_operator_auth_state(runtime.config)
    if not state.configured:
        raise LocalOperatorAuthError("operator token is not configured")
    if not verify_operator_token(str(token), state.token_hash, state.token_salt):
        raise LocalOperatorAuthError("operator token is invalid")


def dispatch(runtime: Any, args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "plan":
        plan = build_background_hunt_plan(runtime, args.hunt_id)
        return ok_result("background_hunt_runner_plan", {"hunt_id": args.hunt_id, "plan": plan.to_dict(), "runner_execution_performed": False})
    if args.command == "runs":
        runs = [item.to_dict() for item in list_background_hunt_runs(runtime, hunt_id=args.hunt_id)]
        return ok_result("background_hunt_runner_runs", {"hunt_id": args.hunt_id, "run_count": len(runs), "runs": runs})
    if args.command == "summary":
        return ok_result("background_hunt_runner_summary", {"hunt_id": args.hunt_id, "summary": summarize_background_hunt(runtime, args.hunt_id)})
    context = {
        "authorized": True,
        "operator_label": "local_operator",
        "raw_token_stored": False,
    }
    if args.command == "run-next":
        result = run_next_hunt_workunit(runtime, args.hunt_id, operator_context=context)
        return ok_result("background_hunt_runner_run_next", {"hunt_id": args.hunt_id, "result": result.to_dict(), "runner_execution_performed": True})
    if args.command == "run-batch":
        limit = max(1, min(int(args.limit or 1), MAX_BATCH))
        result = run_background_hunt_batch(runtime, args.hunt_id, limit=limit, operator_context=context)
        return ok_result("background_hunt_runner_run_batch", {"hunt_id": args.hunt_id, "result": result.to_dict(), "runner_execution_performed": True})
    raise ValueError(f"unsupported command: {args.command}")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "background_hunt_runner_cli_result.v0",
        "status": "pass",
        "action": action,
        "operator_token_required_for_execution": True,
        "localhost_only_execution": True,
        "lan_execution_enabled": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "review_mutation_performed": False,
        "public_index_mutated_except_allowed_rebuild_worker": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    result.update(payload)
    return result


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "background_hunt_runner_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "runner_execution_performed": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "review_mutation_performed": False,
        "public_index_mutated_except_allowed_rebuild_worker": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    if instance is not None:
        result["instance"] = instance
    return result


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)
    if result.get("action"):
        print(f"action: {result['action']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
