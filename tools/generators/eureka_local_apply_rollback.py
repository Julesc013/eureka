#!/usr/bin/env python3
"""Run or preview a local apply rollback plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.apply import ROLLBACK_CONFIRMATION, run_rollback


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--rollback-plan", required=True)
    parser.add_argument("--dry-run", action="store_true", help="Preview only. This is the default.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--operator-token", default="")
    parser.add_argument("--confirm", default="", help=f"Required confirmation string for rollback: {ROLLBACK_CONFIRMATION}.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        rollback_plan = json.loads(Path(args.rollback_plan).read_text(encoding="utf-8"))
        rollback_plan["target_instance_path"] = str(Path(args.instance))
        result = run_rollback(
            rollback_plan,
            operator_context={
                "apply": bool(args.apply),
                "operator_token": args.operator_token,
                "confirmation": args.confirm,
            },
        )
    except Exception as exc:
        result = {
            "schema_version": "local_apply_rollback_cli_result.v0",
            "status": "fail",
            "error": "rollback_failed",
            "message": str(exc),
            "operator_instance_mutated": False,
            "master_index_mutated": False,
            "committed_data_public_index_mutated": False,
        }
        emit(result, args, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    emit(result, args, stdout)
    if result.get("status") in {"pass", "dry_run"}:
        return 0
    return 2 if result.get("status") == "blocked" else 1


def emit(result: Mapping[str, Any], args: argparse.Namespace, stdout: TextIO) -> None:
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(dict(result), indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result.get('status', 'unknown')}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
