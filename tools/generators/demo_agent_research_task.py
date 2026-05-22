#!/usr/bin/env python3
"""Demonstrate disabled agent research task drafting from local hunt state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.agent_research import build_agent_research_report_schema
from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.local_operator import LocalOperatorAuthError, build_operator_auth_state, verify_operator_token
from runtime.search_hunt import build_hunt_exhaustion_report


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for draft creation.")
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
    public_before = runtime.public_index.summarize().to_dict()
    hunt = runtime.search_hunt.create_session_from_query(query, runtime=runtime)
    exhaustion = runtime.search_hunt.attach_exhaustion_report(
        hunt.id,
        build_hunt_exhaustion_report(runtime, hunt.id, operator_label="demo_operator"),
    )
    need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="demo_operator")
    task_from_hunt = runtime.agent_research.draft_task_from_hunt(runtime, hunt.id, operator_label="demo_operator")
    task_from_need = runtime.agent_research.draft_task_from_need(runtime, need.id, operator_label="demo_operator")
    schema = build_agent_research_report_schema().to_dict()
    public_after = runtime.public_index.summarize().to_dict()
    passed = (
        task_from_hunt.provider_enabled is False
        and task_from_hunt.execution_enabled is False
        and task_from_need.provider_enabled is False
        and task_from_need.execution_enabled is False
        and schema.get("candidate_only") is True
        and public_before == public_after
    )
    return {
        "schema_version": "agent_research_demo_result.v0",
        "status": "pass" if passed else "fail",
        "hunt": hunt.to_dict(),
        "exhaustion_report": exhaustion.to_dict(),
        "search_need": need.to_dict(),
        "task_from_hunt": task_from_hunt.to_dict(),
        "task_from_need": task_from_need.to_dict(),
        "report_schema": schema,
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
        "public_index_unchanged": public_before == public_after,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def fail_result(code: str, message: str, *, instance: str | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "agent_research_demo_result.v0",
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
    if result.get("task_from_need"):
        print(f"task: {result['task_from_need']['task_id']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
