#!/usr/bin/env python3
"""Dry-run or apply local reviewed public index rebuild."""

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
from runtime.local.operator import require_operator_token
from runtime.local.review import rebuild_reviewed_index


class _Request:
    def __init__(self, token: str):
        self.headers = {"x-eureka-operator-token": token}
        self.params = {}
        self.body_params = {}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--operator-token")
    parser.add_argument("--operator-label", default="local_operator")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    apply_rebuild = bool(args.apply)
    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=not apply_rebuild)
        if apply_rebuild:
            if not args.operator_token:
                raise ValueError("operator token is required for apply")
            require_operator_token(_Request(args.operator_token), runtime.config)
        result = rebuild_reviewed_index(runtime, operator_label=args.operator_label, dry_run=not apply_rebuild)
    except Exception as exc:
        result = {
            "schema_version": "local_reviewed_index_rebuild_cli_result.v0",
            "status": "fail",
            "error": "reviewed_index_rebuild_failed",
            "message": str(exc),
            "master_index_mutated": False,
            "site_dist_mutated": False,
            "deployment_performed": False,
            "warnings": [],
            "limitations": ["local reviewed public index rebuild only"],
        }
        emit(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    finally:
        if runtime is not None:
            close_local_appliance(runtime)
    emit(result, args.json, args.output, stdout)
    return 0 if result.get("status") == "pass" else 1


def emit(result: dict[str, Any], as_json: bool, output: str | None, stdout: TextIO) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
