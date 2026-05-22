#!/usr/bin/env python3
"""Demonstrate local Search Hunt session persistence without external work."""

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
from runtime.search_hunt import SearchHuntError, build_local_absence_summary, build_reviewed_index_search_summary


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
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
        result = run_demo(runtime, args.query)
    except (LocalApplianceError, SearchHuntError, ValueError) as exc:
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


def run_demo(runtime: Any, query: str) -> dict[str, Any]:
    store = runtime.search_hunt
    before_work = runtime.workunit_queue.summarize().to_dict()
    before_public = runtime.public_index.summarize().to_dict()
    session = store.create_session_from_query(query, runtime=runtime)
    store.attach_search_summary(session.id, build_reviewed_index_search_summary(runtime, query))
    missing_query = f"{query}-not-present-search-hunt-demo"
    absence = store.attach_absence_summary(session.id, build_local_absence_summary(runtime, missing_query))
    states = ["running", "paused", "running", "complete"]
    for state in states:
        session = store.transition_session(session.id, state, f"demo {state}")
    invalid_transition_rejected = False
    try:
        store.transition_session(session.id, "running", "invalid after complete")
    except SearchHuntError:
        invalid_transition_rejected = True
    transitions = [item.to_dict() for item in store.list_transitions(session.id)]
    after_work = runtime.workunit_queue.summarize().to_dict()
    after_public = runtime.public_index.summarize().to_dict()
    return {
        "schema_version": "search_hunt_demo_result.v0",
        "status": "pass" if invalid_transition_rejected and before_work == after_work and before_public == after_public else "fail",
        "session": session.to_dict(),
        "absence_summary": absence.to_dict(),
        "transition_history": transitions,
        "invalid_transition_rejected": invalid_transition_rejected,
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
        "schema_version": "search_hunt_demo_result.v0",
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
