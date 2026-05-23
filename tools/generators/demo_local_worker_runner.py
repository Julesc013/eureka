#!/usr/bin/env python3
"""Demonstrate deterministic local worker execution."""

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
from runtime.local.worker import LocalWorkerRunner
from runtime.worker.workunit_queue import WorkUnit


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--operator-token")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance))
        result = run_demo(runtime, operator_token=args.operator_token)
    except Exception as exc:
        result = fail_result(str(exc))
        emit_result(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
    emit_result(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def run_demo(runtime: Any, operator_token: str | None = None) -> dict[str, Any]:
    samples = [
        create_sample(runtime, "regression_test", "Demo noop worker", "noop_worker", {}),
        create_sample(runtime, "evidence_review", "Demo review queue checker", "review_queue_checker", {}),
        create_sample(runtime, "search_need", "Demo absence report worker", "absence_report_worker", {"query": "definitely-not-present-local-09"}),
        create_sample(runtime, "regression_test", "Demo local status snapshot worker", "local_status_snapshot_worker", {}),
        create_sample(runtime, "source_probe", "Demo blocked source probe worker", "source_probe_worker", {}),
    ]
    if operator_token:
        samples.append(create_sample(runtime, "index_rebuild", "Demo reviewed index rebuild worker", "reviewed_index_rebuild_worker", {}))
    runner = LocalWorkerRunner(runtime)
    context = {
        "authorized": bool(operator_token),
        "operator_label": "local_worker_demo" if operator_token else "",
    }
    results = []
    for item in samples:
        results.append(runner.run_one(item.id, operator_context=context).to_dict())
    return {
        "schema_version": "local_worker_demo_result.v0",
        "status": "pass",
        "created_workunit_count": len(samples),
        "worker_results": results,
        "blocked_disabled_worker_kind": any(result["status"] == "blocked" for result in results),
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


def create_sample(runtime: Any, kind: str, title: str, worker_kind: str, payload: dict[str, Any]) -> Any:
    body = dict(payload)
    body["worker_kind"] = worker_kind
    workunit = WorkUnit.new(kind, title, payload=body, limitations=("local worker demo record",))
    return runtime.workunit_queue.create_workunit(workunit)


def fail_result(message: str) -> dict[str, Any]:
    return {
        "schema_version": "local_worker_demo_result.v0",
        "status": "fail",
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


if __name__ == "__main__":
    raise SystemExit(main())
