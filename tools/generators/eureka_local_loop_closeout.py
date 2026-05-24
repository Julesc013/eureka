#!/usr/bin/env python3
"""Run the Workbench local loop closeout proof."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_loop import APPLY_CONFIRMATION, build_local_loop_plan, run_local_loop_dry_run, run_local_loop_temp_instance
from scripts.eureka_init_instance import initialize_instance


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument(
        "--projection",
        default="operator_workbench",
        choices=("operator_workbench", "public_web", "native_desktop_read_only"),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-temp-instance", action="store_true")
    parser.add_argument("--apply-to-temp", action="store_true")
    parser.add_argument("--operator-token", default="")
    parser.add_argument("--confirm", default="", help=f"Required confirmation string for temp apply: {APPLY_CONFIRMATION}.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--proof-output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    temp: tempfile.TemporaryDirectory[str] | None = None
    try:
        if args.apply_to_temp:
            if not args.use_temp_instance:
                result = blocked_result(args, "automated local loop apply requires --use-temp-instance")
                emit(result, args, stdout)
                return 2
            temp = tempfile.TemporaryDirectory(prefix="eureka-local-loop-")
            target_instance = Path(temp.name) / "instance"
            init = initialize_instance(target_instance)
            if init.get("status") not in {"pass", "pass_with_warnings"}:
                result = blocked_result(args, "temp instance initialization failed")
                result["init_result"] = init
                emit(result, args, stdout)
                return 1
        else:
            target_instance = Path(tempfile.gettempdir()) / "eureka-local-loop-preview-instance"

        plan = build_local_loop_plan(args.query, target_instance, args.projection)
        if args.apply_to_temp:
            result = run_local_loop_temp_instance(
                plan,
                {
                    "use_temp_instance": args.use_temp_instance,
                    "apply_to_temp": args.apply_to_temp,
                    "operator_token": args.operator_token,
                    "confirmation": args.confirm,
                    "projection_profile": args.projection,
                },
            )
        else:
            result = run_local_loop_dry_run(plan)
    except Exception as exc:
        result = {
            "schema_version": "workbench_local_loop_cli_result.v0",
            "status": "fail",
            "error": "workbench_local_loop_failed",
            "message": str(exc),
            "operator_instance_mutated": False,
            "committed_instance_state": False,
            "master_index_mutated": False,
            "committed_data_public_index_mutated": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
        emit(result, args, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 1
    finally:
        if temp is not None:
            temp.cleanup()

    emit(result, args, stdout)
    if result.get("status") in {"pass", "dry_run"}:
        return 0
    return 2 if result.get("status") == "blocked" else 1


def blocked_result(args: argparse.Namespace, reason: str) -> dict[str, Any]:
    return {
        "schema_version": "workbench_local_loop_cli_result.v0",
        "status": "blocked",
        "query": args.query,
        "projection_profile": args.projection,
        "blocked_reasons": [reason],
        "public_projection_blocked": args.projection == "public_web",
        "native_read_only_projection_blocked": args.projection == "native_desktop_read_only",
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def emit(result: Mapping[str, Any], args: argparse.Namespace, stdout: TextIO) -> None:
    if args.output:
        write_json(Path(args.output), result)
    if args.proof_output:
        write_json(
            Path(args.proof_output),
            {
                "schema_version": "workbench_local_loop_proofs.v0",
                "apply_proof": dict(result.get("apply_proof") or {}),
                "rollback_proof": dict(result.get("rollback_proof") or {}),
                "search_after_apply_proof": dict(result.get("search_after_apply_proof") or {}),
            },
        )
    if args.boundary_output:
        write_json(Path(args.boundary_output), dict(result.get("boundary_report") or {}))
    if args.json:
        print(json.dumps(dict(result), indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result.get('status', 'unknown')}", file=stdout)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
