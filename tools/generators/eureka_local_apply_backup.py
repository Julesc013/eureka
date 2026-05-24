#!/usr/bin/env python3
"""Create a pre-apply backup for a local apply plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.apply import create_pre_apply_backup


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    try:
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        plan["target_instance_path"] = str(Path(args.instance))
        manifest = create_pre_apply_backup(plan)
    except Exception as exc:
        result = {
            "schema_version": "local_apply_backup_cli_result.v0",
            "status": "fail",
            "error": "backup_failed",
            "message": str(exc),
            "operator_instance_mutated": False,
        }
        emit(result, args, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    emit(manifest, args, stdout)
    return 0


def emit(result: Mapping[str, Any], args: argparse.Namespace, stdout: TextIO) -> None:
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(dict(result), indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result.get('status', 'pass')}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
