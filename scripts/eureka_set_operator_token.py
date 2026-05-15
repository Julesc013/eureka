#!/usr/bin/env python3
"""Set a local operator token hash for an explicit Eureka instance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_appliance import load_instance_config
from runtime.local_operator import LocalOperatorError, write_operator_token_record


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        config = load_instance_config(Path(args.instance))
        record = write_operator_token_record(config.instance_root, args.token)
        result = {
            "schema_version": "local_operator_token_set_result.v0",
            "status": "pass",
            "instance_root": str(config.instance_root),
            "token_hash_configured": bool(record.get("token_hash")),
            "raw_token_stored": False,
            "token_printed": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "warnings": [],
            "limitations": ["operator token hash is local instance state only"],
        }
    except (LocalOperatorError, Exception) as exc:
        result = {
            "schema_version": "local_operator_token_set_result.v0",
            "status": "fail",
            "error": "operator_token_not_set",
            "message": str(exc),
            "raw_token_stored": False,
            "token_printed": False,
            "lan_enabled": False,
            "deployment_performed": False,
            "warnings": [],
            "limitations": ["operator token was not printed"],
        }
        emit(result, args.json, args.output, stdout)
        print(f"ERROR: {exc}", file=stderr)
        return 2
    emit(result, args.json, args.output, stdout)
    return 0


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
