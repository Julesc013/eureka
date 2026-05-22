#!/usr/bin/env python3
"""Demonstrate durable local WorkUnit queue records without executing work."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eureka_init_instance import initialize_instance
from runtime.local_appliance import LocalApplianceError, close_local_appliance, open_local_appliance
from runtime.workunit_queue import WorkUnit, WorkUnitQueueError


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit initialized local instance root. If omitted, a temporary instance is used.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    runtime = None
    try:
        if args.instance:
            instance = Path(args.instance)
            if not (instance / "config" / "instance.json").is_file():
                raise ValueError("instance is not initialized; run eureka_init_instance.py first")
        else:
            temp_dir = tempfile.TemporaryDirectory(prefix="eureka-workunit-demo-")
            instance = Path(temp_dir.name) / "eureka-instance"
            init = initialize_instance(instance)
            if init.get("status") not in {"pass", "pass_with_warnings"}:
                raise ValueError("temporary instance initialization failed")
        runtime = open_local_appliance(instance)
        result = run_demo(runtime.workunit_queue, instance)
    except (LocalApplianceError, WorkUnitQueueError, ValueError) as exc:
        result = fail_result("workunit_demo_failed", str(exc), args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = fail_result("workunit_demo_failed", str(exc), args.instance)
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
        if temp_dir is not None:
            temp_dir.cleanup()

    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def run_demo(queue: Any, instance: Path) -> dict[str, Any]:
    primary = queue.create_workunit(
        WorkUnit.new(
            "search_need",
            "Sample local search need",
            payload={"query": "sampleproject"},
            limitations=("Demonstration record only; no work execution is performed.",),
        )
    )
    paused = queue.create_workunit(WorkUnit.new("source_probe", "Sample source probe proposal"))
    blocked = queue.create_workunit(WorkUnit.new("evidence_review", "Sample evidence review proposal"))
    cancelled = queue.create_workunit(WorkUnit.new("regression_test", "Sample regression check proposal"))

    queue.transition_workunit(primary.id, "running", "operator selected sample")
    queue.complete_workunit(primary.id, "recorded completion state only")
    before_terminal_repeat = len(queue.list_transitions(primary.id))
    queue.complete_workunit(primary.id, "idempotent repeat")
    after_terminal_repeat = len(queue.list_transitions(primary.id))

    queue.pause_workunit(paused.id, "operator pause demo")
    queue.resume_workunit(paused.id, "operator resume demo")
    queue.block_workunit(blocked.id, "waiting for future review UI")
    queue.resume_workunit(blocked.id, "operator returned to queue")
    queue.cancel_workunit(cancelled.id, "operator cancelled sample")

    invalid_rejected = False
    invalid_message = ""
    invalid = queue.create_workunit(WorkUnit.new("index_rebuild", "Invalid transition sample"))
    try:
        queue.complete_workunit(invalid.id, "queued records cannot complete directly")
    except WorkUnitQueueError as exc:
        invalid_rejected = True
        invalid_message = str(exc)

    records = [item.to_dict() for item in queue.list_workunits(limit=100)]
    transitions = [item.to_dict() for item in queue.list_transitions(limit=100)]
    return {
        "schema_version": "local_workunit_queue_demo_result.v0",
        "status": "pass" if invalid_rejected and before_terminal_repeat == after_terminal_repeat else "fail",
        "instance_root": str(instance),
        "created_count": len(records),
        "workunits": records,
        "transition_history": transitions,
        "summary": queue.summarize().to_dict(),
        "invalid_transition_rejected": invalid_rejected,
        "invalid_transition_message": invalid_message,
        "idempotency_checked": before_terminal_repeat == after_terminal_repeat,
        "work_execution_performed": False,
        "source_probe_executed": False,
        "review_mutation_performed": False,
        "index_rebuild_performed": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def fail_result(code: str, message: str, instance: str | None) -> dict[str, Any]:
    result = {
        "schema_version": "local_workunit_queue_demo_result.v0",
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
    if instance:
        result["instance"] = instance
    return result


def emit_result(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        write_json(Path(output), result)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
        return
    print(f"status: {result['status']}", file=stdout)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
