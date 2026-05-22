#!/usr/bin/env python3
"""Demonstrate SearchNeed creation from a local Search Hunt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search_need import SearchNeedError


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for SearchNeed creation.")
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
    except (LocalApplianceError, LocalOperatorAuthError, SearchNeedError, ValueError) as exc:
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
    before_work = runtime.workunit_queue.summarize().to_dict()
    before_public = runtime.public_index.summarize().to_dict()
    hunt = runtime.search_hunt.create_session_from_query(query, runtime=runtime)
    need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="demo_operator")
    needs = [item.to_dict() for item in runtime.search_need.list_needs()]
    shown = runtime.search_need.get_need(need.id)
    transitioned = runtime.search_need.transition_need(need.id, "open", reason="demo open")
    after_work = runtime.workunit_queue.summarize().to_dict()
    after_public = runtime.public_index.summarize().to_dict()
    passed = (
        shown is not None
        and shown.id == need.id
        and transitioned.state.value == "open"
        and before_work == after_work
        and before_public == after_public
    )
    return {
        "schema_version": "search_need_demo_result.v0",
        "status": "pass" if passed else "fail",
        "hunt": hunt.to_dict(),
        "search_need": need.to_dict(),
        "search_need_list": needs,
        "transitioned_need": transitioned.to_dict(),
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
        "schema_version": "search_need_demo_result.v0",
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
    if result.get("search_need"):
        print(f"need: {result['search_need']['id']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
