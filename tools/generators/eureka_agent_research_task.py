#!/usr/bin/env python3
"""Inspect and draft disabled agent research task records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.agent_research import (
    ALLOWED_AGENT_RESEARCH_TASK_STATES,
    AgentResearchError,
    build_agent_research_report_schema,
)
from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.instance and args.command != "report-schema":
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.command:
        result = fail_result("missing_command", "an agent research task command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: an agent research task command is required", file=stderr)
        return 2

    runtime = None
    try:
        if args.command == "report-schema" and not args.instance:
            result = ok_result("agent_research_report_schema", {"report_schema": build_agent_research_report_schema().to_dict()})
        else:
            runtime = open_local_appliance(Path(args.instance), read_only=args.command in {"list", "show", "report-schema"})
            if args.command in {"draft-from-hunt", "draft-from-need", "cancel"}:
                require_cli_operator_token(runtime, args.operator_token)
            result = dispatch(runtime, args)
    except (LocalApplianceError, LocalOperatorAuthError, AgentResearchError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("agent_research_task_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("agent_research_task_failed", str(exc), instance=args.instance)
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
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON output path.")
    subparsers = parser.add_subparsers(dest="command")

    draft_hunt = subparsers.add_parser("draft-from-hunt", help="Draft a disabled task from a Search Hunt.")
    draft_hunt.add_argument("--hunt-id", required=True)
    draft_hunt.add_argument("--operator-token", required=True)
    add_output_options(draft_hunt)

    draft_need = subparsers.add_parser("draft-from-need", help="Draft a disabled task from a SearchNeed.")
    draft_need.add_argument("--need-id", required=True)
    draft_need.add_argument("--operator-token", required=True)
    add_output_options(draft_need)

    list_cmd = subparsers.add_parser("list", help="List disabled agent research tasks.")
    list_cmd.add_argument("--state", choices=ALLOWED_AGENT_RESEARCH_TASK_STATES)
    list_cmd.add_argument("--hunt-id")
    list_cmd.add_argument("--need-id")
    list_cmd.add_argument("--limit", type=int, default=100)
    add_output_options(list_cmd)

    show = subparsers.add_parser("show", help="Show one disabled agent research task.")
    show.add_argument("--id", required=True)
    add_output_options(show)

    schema = subparsers.add_parser("report-schema", help="Show the future candidate-only report schema.")
    add_output_options(schema)

    cancel = subparsers.add_parser("cancel", help="Cancel a disabled local task record.")
    cancel.add_argument("--id", required=True)
    cancel.add_argument("--reason")
    cancel.add_argument("--operator-token", required=True)
    add_output_options(cancel)
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
    if args.command == "draft-from-hunt":
        task = runtime.agent_research.draft_task_from_hunt(runtime, args.hunt_id, operator_label="local_operator")
        return ok_result("agent_research_task_drafted_from_hunt", {"agent_research_task": task.to_dict(), "hunt_id": args.hunt_id})
    if args.command == "draft-from-need":
        task = runtime.agent_research.draft_task_from_need(runtime, args.need_id, operator_label="local_operator")
        return ok_result("agent_research_task_drafted_from_need", {"agent_research_task": task.to_dict(), "need_id": args.need_id})
    if args.command == "list":
        tasks = [
            item.to_dict()
            for item in runtime.agent_research.list_tasks(
                state=args.state,
                hunt_id=args.hunt_id,
                need_id=args.need_id,
                limit=args.limit,
            )
        ]
        return ok_result("agent_research_task_list", {"task_count": len(tasks), "agent_research_tasks": tasks})
    if args.command == "show":
        task = runtime.agent_research.get_task(args.id)
        if task is None:
            return fail_result("agent_research_task_not_found", f"Agent research task not found: {args.id}")
        return ok_result("agent_research_task_show", {"agent_research_task": task.to_dict()})
    if args.command == "report-schema":
        return ok_result("agent_research_report_schema", {"report_schema": build_agent_research_report_schema().to_dict()})
    if args.command == "cancel":
        task = runtime.agent_research.cancel_task(args.id, reason=args.reason)
        return ok_result("agent_research_task_cancelled", {"agent_research_task": task.to_dict()})
    raise ValueError(f"unsupported command: {args.command}")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "agent_research_task_cli_result.v0",
        "status": "pass",
        "action": action,
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "source_probe_enabled": False,
        "output_candidate_only": True,
        "review_required": True,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    result.update(payload)
    return result


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "agent_research_task_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_enabled": False,
        "source_probe_enabled": False,
        "model_provider_used": False,
        "external_network_used": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
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
    if result.get("agent_research_task"):
        print(f"task: {result['agent_research_task']['task_id']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
