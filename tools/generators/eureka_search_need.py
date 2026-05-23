#!/usr/bin/env python3
"""Inspect and update local SearchNeeds without creating work."""

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
from runtime.search.need import ALLOWED_SEARCH_NEED_KINDS, ALLOWED_SEARCH_NEED_STATES, SearchNeedError, list_workunits_for_need


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    if not args.command:
        result = fail_result("missing_command", "a SearchNeed command is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: a SearchNeed command is required", file=stderr)
        return 2

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=args.command != "transition")
        if args.command == "transition":
            require_cli_operator_token(runtime, args.operator_token)
        result = dispatch(runtime, args)
    except (LocalApplianceError, LocalOperatorAuthError, SearchNeedError, ValueError, json.JSONDecodeError) as exc:
        result = fail_result("search_need_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("search_need_failed", str(exc), instance=args.instance)
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

    list_cmd = subparsers.add_parser("list", help="List local SearchNeeds.")
    list_cmd.add_argument("--state", choices=ALLOWED_SEARCH_NEED_STATES)
    list_cmd.add_argument("--kind", choices=ALLOWED_SEARCH_NEED_KINDS)
    list_cmd.add_argument("--limit", type=int, default=100)
    add_output_options(list_cmd)

    show = subparsers.add_parser("show", help="Show one SearchNeed.")
    show.add_argument("--id", required=True)
    show.add_argument("--with-transitions", action="store_true")
    add_output_options(show)

    transition = subparsers.add_parser("transition", help="Update SearchNeed state.")
    transition.add_argument("--id", required=True)
    transition.add_argument("--state", required=True, choices=ALLOWED_SEARCH_NEED_STATES)
    transition.add_argument("--reason")
    transition.add_argument("--operator-token", required=True)
    add_output_options(transition)

    summary = subparsers.add_parser("summary", help="Summarize the SearchNeed store.")
    add_output_options(summary)

    workunits = subparsers.add_parser("workunits", help="List WorkUnits linked to a SearchNeed.")
    workunits.add_argument("--id", required=True)
    workunits.add_argument("--limit", type=int, default=100)
    add_output_options(workunits)
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
    store = runtime.search_need
    if args.command == "list":
        needs = [item.to_dict() for item in store.list_needs(state=args.state, kind=args.kind, limit=args.limit)]
        return ok_result("search_need_list", {"count": len(needs), "needs": needs})
    if args.command == "show":
        need = store.get_need(args.id)
        if need is None:
            return fail_result("search_need_not_found", f"SearchNeed not found: {args.id}")
        payload: dict[str, Any] = {"need": need.to_dict()}
        if args.with_transitions:
            payload["transitions"] = [item.to_dict() for item in store.list_transitions(args.id)]
        return ok_result("search_need_show", payload)
    if args.command == "transition":
        need = store.transition_need(args.id, args.state, reason=args.reason)
        return ok_result("search_need_transitioned", {"need": need.to_dict()})
    if args.command == "summary":
        return ok_result("search_need_summary", {"summary": store.summarize()})
    if args.command == "workunits":
        if store.get_need(args.id) is None:
            return fail_result("search_need_not_found", f"SearchNeed not found: {args.id}")
        workunits = list_workunits_for_need(runtime, args.id, limit=args.limit)
        return ok_result("search_need_workunits", {"need_id": args.id, "workunit_count": len(workunits), "workunits": workunits})
    raise ValueError(f"unsupported command: {args.command}")


def ok_result(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": "search_need_cli_result.v0",
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
        "schema_version": "search_need_cli_result.v0",
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
