#!/usr/bin/env python3
"""Demonstrate local Search Hunt command and steering controls."""

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
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search_hunt import SearchHuntError


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for mutating commands.")
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
    except (LocalApplianceError, LocalOperatorAuthError, SearchHuntError, ValueError) as exc:
        result = fail_result("demo_failed", str(exc), instance=args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("demo_failed", str(exc), instance=args.instance)
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
    store = runtime.search_hunt
    before_work = runtime.workunit_queue.summarize().to_dict()
    before_public = runtime.public_index.summarize().to_dict()
    session = store.create_session_from_query(query, runtime=runtime)
    pause = store.apply_command(session.id, "pause", reason="demo pause", operator_label="demo_operator")
    resume = store.apply_command(session.id, "resume", reason="demo resume", operator_label="demo_operator")
    official = store.add_steering_preference(
        session.id,
        "prefer_official_sources",
        reason="demo preference",
        operator_label="demo_operator",
    )
    note = store.add_steering_preference(
        session.id,
        "add_note",
        value="keep future work metadata-only until a later gate",
        reason="demo note",
        operator_label="demo_operator",
    )
    deactivated = store.remove_steering_preference(
        session.id,
        note.id,
        reason="demo deactivation",
        operator_label="demo_operator",
    )
    invalid_command_rejected = False
    try:
        store.apply_command(session.id, "block", operator_label="demo_operator")
    except SearchHuntError:
        invalid_command_rejected = True
    commands = [item.to_dict() for item in store.list_commands(session.id)]
    steering = [item.to_dict() for item in store.list_steering_preferences(session.id, active_only=False)]
    after_work = runtime.workunit_queue.summarize().to_dict()
    after_public = runtime.public_index.summarize().to_dict()
    passed = (
        pause.command.resulting_state == "paused"
        and resume.command.resulting_state == "running"
        and official.active
        and deactivated.active is False
        and invalid_command_rejected
        and before_work == after_work
        and before_public == after_public
    )
    return {
        "schema_version": "search_hunt_command_demo_result.v0",
        "status": "pass" if passed else "fail",
        "session": store.get_session(session.id).to_dict(),
        "pause_result": pause.to_dict(),
        "resume_result": resume.to_dict(),
        "steering_preferences": steering,
        "command_history": commands,
        "invalid_command_rejected": invalid_command_rejected,
        "workunit_creation_performed": False,
        "workunit_queue_unchanged": before_work == after_work,
        "source_probe_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutation_performed": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "public_index_unchanged": before_public == after_public,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "search_hunt_command_demo_result.v0",
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
    if result.get("session"):
        print(f"session: {result['session']['id']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
