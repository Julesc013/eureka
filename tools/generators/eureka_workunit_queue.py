#!/usr/bin/env python3
"""Manage the durable local WorkUnit queue without executing work."""

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
from runtime.worker.workunit_queue import (
    ALLOWED_WORKUNIT_PRIORITIES,
    ALLOWED_WORKUNIT_STATES,
    ALLOWED_WORKUNIT_TYPES,
    WorkUnit,
    WorkUnitQueueError,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.command:
        result = fail_result("missing_command", "a queue command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: a queue command is required", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance))
        result = dispatch(runtime.workunit_queue, args)
    except (LocalApplianceError, WorkUnitQueueError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("workunit_queue_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("workunit_queue_failed", str(exc), instance=args.instance)
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
    parser.add_argument("--instance", help="Explicit local instance root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--output", help="Optional JSON output path.")
    subparsers = parser.add_subparsers(dest="command")

    create = subparsers.add_parser("create", help="Create a queued WorkUnit record.")
    create.add_argument("--kind", required=True, choices=ALLOWED_WORKUNIT_TYPES)
    create.add_argument("--title", required=True)
    create.add_argument("--payload-json", default="{}")
    create.add_argument("--priority", default="normal", choices=ALLOWED_WORKUNIT_PRIORITIES)
    create.add_argument("--idempotency-key")
    create.add_argument("--parent-id")
    add_output_options(create)

    list_cmd = subparsers.add_parser("list", help="List WorkUnit records.")
    list_cmd.add_argument("--state", choices=ALLOWED_WORKUNIT_STATES)
    list_cmd.add_argument("--kind", choices=ALLOWED_WORKUNIT_TYPES)
    list_cmd.add_argument("--limit", type=int, default=100)
    add_output_options(list_cmd)

    show = subparsers.add_parser("show", help="Show one WorkUnit record.")
    show.add_argument("--id", required=True)
    show.add_argument("--with-transitions", action="store_true")
    add_output_options(show)

    transition = subparsers.add_parser("transition", help="Record a state transition.")
    transition.add_argument("--id", required=True)
    transition.add_argument("--state", required=True, choices=ALLOWED_WORKUNIT_STATES)
    transition.add_argument("--reason")
    add_output_options(transition)

    for name in ("pause", "resume", "cancel", "complete"):
        item = subparsers.add_parser(name, help=f"{name} one WorkUnit record.")
        item.add_argument("--id", required=True)
        item.add_argument("--reason")
        add_output_options(item)

    block = subparsers.add_parser("block", help="Block one WorkUnit record.")
    block.add_argument("--id", required=True)
    block.add_argument("--reason", required=True)
    add_output_options(block)

    fail = subparsers.add_parser("fail", help="Fail one WorkUnit record.")
    fail.add_argument("--id", required=True)
    fail.add_argument("--reason", required=True)
    add_output_options(fail)

    summary = subparsers.add_parser("summary", help="Summarize the WorkUnit queue.")
    add_output_options(summary)
    return parser


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--output", default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def dispatch(queue: Any, args: argparse.Namespace) -> dict[str, Any]:
    command = args.command
    if command == "create":
        payload = json.loads(args.payload_json)
        if not isinstance(payload, dict):
            raise ValueError("--payload-json must contain a JSON object")
        workunit = WorkUnit.new(
            args.kind,
            args.title,
            payload=payload,
            priority=args.priority,
            idempotency_key=args.idempotency_key,
            parent_id=args.parent_id,
            limitations=("Record only; no work execution is performed.",),
        )
        created = queue.create_workunit(workunit)
        return ok_result("workunit_created", {"workunit": created.to_dict()})
    if command == "list":
        records = [item.to_dict() for item in queue.list_workunits(state=args.state, kind=args.kind, limit=args.limit)]
        return ok_result("workunit_list", {"count": len(records), "workunits": records})
    if command == "show":
        workunit = queue.get_workunit(args.id)
        if workunit is None:
            return fail_result("workunit_not_found", f"workunit not found: {args.id}")
        payload = {"workunit": workunit.to_dict()}
        if args.with_transitions:
            payload["transitions"] = [item.to_dict() for item in queue.list_transitions(args.id)]
        return ok_result("workunit_show", payload)
    if command == "transition":
        return ok_result("workunit_transitioned", {"workunit": queue.transition_workunit(args.id, args.state, args.reason).to_dict()})
    if command == "pause":
        return ok_result("workunit_paused", {"workunit": queue.pause_workunit(args.id, args.reason).to_dict()})
    if command == "resume":
        return ok_result("workunit_resumed", {"workunit": queue.resume_workunit(args.id, args.reason).to_dict()})
    if command == "cancel":
        return ok_result("workunit_cancelled", {"workunit": queue.cancel_workunit(args.id, args.reason).to_dict()})
    if command == "block":
        return ok_result("workunit_blocked", {"workunit": queue.block_workunit(args.id, args.reason).to_dict()})
    if command == "complete":
        return ok_result("workunit_completed", {"workunit": queue.complete_workunit(args.id, args.reason).to_dict()})
    if command == "fail":
        return ok_result("workunit_failed", {"workunit": queue.fail_workunit(args.id, args.reason).to_dict()})
    if command == "summary":
        return ok_result("workunit_summary", {"summary": queue.summarize().to_dict()})
    raise ValueError(f"unsupported command: {command}")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "local_workunit_queue_cli_result.v0",
        "status": "pass",
        "action": action,
        "work_execution_performed": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    result.update(payload)
    return result


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "local_workunit_queue_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "work_execution_performed": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
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
