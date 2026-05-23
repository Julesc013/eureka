#!/usr/bin/env python3
"""Run deterministic local workers over queued WorkUnits."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.worker import LocalWorkerRunner, get_default_worker_registry


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.command:
        result = fail_result("missing_command", "worker runner command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: worker runner command is required", file=stderr)
        return 2
    runtime = None
    try:
        read_only = args.command in {"list-workers", "plan"}
        runtime = open_local_appliance(Path(args.instance), read_only=read_only)
        result = dispatch(runtime, args)
    except Exception as exc:
        result = fail_result("worker_runner_failed", str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") in {"pass", "pass_with_warnings"} else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local instance root.")
    parser.add_argument("--operator-token", help="Explicit operator token for token-gated workers.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON output path.")
    subparsers = parser.add_subparsers(dest="command")

    list_workers = subparsers.add_parser("list-workers")
    add_output_options(list_workers)

    plan = subparsers.add_parser("plan")
    plan.add_argument("--id", required=True)
    add_output_options(plan)

    run_one = subparsers.add_parser("run-one")
    run_one.add_argument("--id", required=True)
    run_one.add_argument("--kind")
    add_output_options(run_one)

    run_next = subparsers.add_parser("run-next")
    run_next.add_argument("--kind")
    run_next.add_argument("--limit", type=int, default=1)
    add_output_options(run_next)
    return parser


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--output", default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def dispatch(runtime: Any, args: argparse.Namespace) -> dict[str, Any]:
    registry = get_default_worker_registry()
    if args.command == "list-workers":
        return ok_result(
            "worker_list",
            {
                "enabled_worker_kinds": list(registry.enabled_kinds()),
                "blocked_worker_kinds": list(registry.blocked_kinds()),
                "workers": registry.list_workers(),
            },
        )
    if getattr(args, "kind", None) and not registry.is_worker_enabled(args.kind):
        return fail_result("disabled_worker_kind", f"worker kind is disabled: {args.kind}")
    runner = LocalWorkerRunner(runtime, registry=registry)
    operator_context = build_operator_context(args.operator_token)
    if args.command == "plan":
        result = runner.plan_run(args.id)
        return ok_result("worker_plan", {"worker_result": result.to_dict()})
    if args.command == "run-one":
        result = runner.run_one(args.id, worker_kind=args.kind, operator_context=operator_context)
        return ok_result("worker_run_one", {"worker_result": result.to_dict()})
    if args.command == "run-next":
        results = runner.run_next(kind=args.kind, limit=args.limit, operator_context=operator_context)
        return ok_result("worker_run_next", {"count": len(results), "worker_results": [item.to_dict() for item in results]})
    raise ValueError(f"unsupported command: {args.command}")


def build_operator_context(token: str | None) -> dict[str, Any]:
    token_present = bool(str(token or "").strip())
    return {
        "authorized": token_present,
        "operator_label": "local_worker_operator" if token_present else "",
        "token_provided": token_present,
        "raw_token_stored": False,
    }


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "local_worker_runner_cli_result.v0",
        "status": "pass",
        "action": action,
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "lan_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    result.update(payload)
    return result


def fail_result(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": "local_worker_runner_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "external_network_used": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "lan_enabled": False,
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
    else:
        print(f"status: {result['status']}", file=stdout)
        if result.get("action"):
            print(f"action: {result['action']}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
