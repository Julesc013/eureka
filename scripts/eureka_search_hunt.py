#!/usr/bin/env python3
"""Manage local Search Hunt sessions without executing investigation work."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.search_hunt import (
    ALLOWED_SEARCH_HUNT_DESTINATIONS,
    ALLOWED_SEARCH_HUNT_INTENTS,
    ALLOWED_SEARCH_HUNT_STATES,
    SearchHuntError,
    SearchHuntSession,
    build_local_absence_summary,
    build_reviewed_index_search_summary,
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
        result = fail_result("missing_command", "a Search Hunt command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: a Search Hunt command is required", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance))
        result = dispatch(runtime, args)
    except (LocalApplianceError, SearchHuntError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("search_hunt_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("search_hunt_failed", str(exc), instance=args.instance)
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

    create = subparsers.add_parser("create", help="Create a Search Hunt session.")
    create.add_argument("--query", required=True)
    create.add_argument("--intent", choices=ALLOWED_SEARCH_HUNT_INTENTS, default="unknown")
    create.add_argument("--destination", choices=ALLOWED_SEARCH_HUNT_DESTINATIONS, default="unknown")
    create.add_argument("--idempotency-key")
    create.add_argument("--parent-id")
    add_output_options(create)

    list_cmd = subparsers.add_parser("list", help="List Search Hunt sessions.")
    list_cmd.add_argument("--state", choices=ALLOWED_SEARCH_HUNT_STATES)
    list_cmd.add_argument("--limit", type=int, default=100)
    add_output_options(list_cmd)

    show = subparsers.add_parser("show", help="Show one Search Hunt session.")
    show.add_argument("--id", required=True)
    show.add_argument("--with-transitions", action="store_true")
    show.add_argument("--with-summaries", action="store_true")
    show.add_argument("--with-commands", action="store_true")
    show.add_argument("--with-steering", action="store_true")
    add_output_options(show)

    transition = subparsers.add_parser("transition", help="Record a Search Hunt state transition.")
    transition.add_argument("--id", required=True)
    transition.add_argument("--state", required=True, choices=ALLOWED_SEARCH_HUNT_STATES)
    transition.add_argument("--reason")
    add_output_options(transition)

    summary = subparsers.add_parser("summary", help="Attach local summaries or summarize the store.")
    summary.add_argument("--id")
    summary.add_argument("--query")
    summary.add_argument("--kind", choices=("store", "search", "absence"), default="store")
    add_output_options(summary)
    return parser


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    parser.add_argument("--output", default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def dispatch(runtime: Any, args: argparse.Namespace) -> dict[str, Any]:
    store = runtime.search_hunt
    if args.command == "create":
        session = store.create_session_from_query(
            args.query,
            runtime=runtime,
            idempotency_key=args.idempotency_key,
            intent=args.intent,
            destination=args.destination,
            parent_id=args.parent_id,
        )
        return ok_result("search_hunt_created", {"session": session.to_dict()})
    if args.command == "list":
        records = [item.to_dict() for item in store.list_sessions(state=args.state, limit=args.limit)]
        return ok_result("search_hunt_list", {"count": len(records), "sessions": records})
    if args.command == "show":
        session = store.get_session(args.id)
        if session is None:
            return fail_result("search_hunt_not_found", f"Search Hunt session not found: {args.id}")
        payload: dict[str, Any] = {"session": session.to_dict()}
        if args.with_transitions:
            payload["transitions"] = [item.to_dict() for item in store.list_transitions(args.id)]
        if args.with_summaries:
            payload["summaries"] = [item.to_dict() for item in store.list_summaries(args.id)]
        if args.with_commands:
            payload["commands"] = [item.to_dict() for item in store.list_commands(args.id)]
        if args.with_steering:
            payload["steering_preferences"] = [item.to_dict() for item in store.list_steering_preferences(args.id, active_only=False)]
        return ok_result("search_hunt_show", payload)
    if args.command == "transition":
        session = store.transition_session(args.id, args.state, args.reason)
        return ok_result("search_hunt_transitioned", {"session": session.to_dict()})
    if args.command == "summary":
        return summary_command(runtime, args)
    raise ValueError(f"unsupported command: {args.command}")


def summary_command(runtime: Any, args: argparse.Namespace) -> dict[str, Any]:
    store = runtime.search_hunt
    if args.kind == "store":
        return ok_result("search_hunt_summary", {"summary": store.summarize()})
    if not args.id:
        raise ValueError("--id is required for search and absence summaries")
    session = store.get_session(args.id)
    if session is None:
        return fail_result("search_hunt_not_found", f"Search Hunt session not found: {args.id}")
    query = args.query or session.query
    if args.kind == "search":
        summary = store.attach_search_summary(args.id, build_reviewed_index_search_summary(runtime, query))
        return ok_result("search_hunt_search_summary_attached", {"summary": summary.to_dict()})
    if args.kind == "absence":
        summary = store.attach_absence_summary(args.id, build_local_absence_summary(runtime, query))
        return ok_result("search_hunt_absence_summary_attached", {"summary": summary.to_dict()})
    raise ValueError(f"unsupported summary kind: {args.kind}")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "search_hunt_cli_result.v0",
        "status": "pass",
        "action": action,
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
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
        "schema_version": "search_hunt_cli_result.v0",
        "status": "fail",
        "error": code,
        "message": message,
        "workunit_creation_performed": False,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
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
    if result.get("action"):
        print(f"action: {result['action']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
