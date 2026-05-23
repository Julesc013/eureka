#!/usr/bin/env python3
"""Inspect and update the local review queue."""

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
from runtime.local.operator import LocalOperatorError, require_operator_token
from runtime.local.review import get_review_item, list_review_items, record_review_decision


class _Request:
    def __init__(self, token: str):
        self.headers = {"x-eureka-operator-token": token}
        self.params = {}
        self.body_params = {}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    sub = parser.add_subparsers(dest="command", required=True)
    list_parser = sub.add_parser("list")
    list_parser.add_argument("--status")
    list_parser.add_argument("--limit", type=int, default=100)
    show_parser = sub.add_parser("show")
    show_parser.add_argument("--id", required=True)
    decide_parser = sub.add_parser("decide")
    decide_parser.add_argument("--id", required=True)
    decide_parser.add_argument("--decision", required=True)
    decide_parser.add_argument("--reason")
    decide_parser.add_argument("--operator-label", default="local_operator")
    decide_parser.add_argument("--operator-token", required=True)
    decide_parser.add_argument("--local-only-confirmed", action="store_true")
    args = parser.parse_args(argv)

    runtime = None
    try:
        runtime = open_local_appliance(Path(args.instance), read_only=args.command != "decide")
        if args.command == "list":
            result = list_review_items(runtime, status=args.status, limit=args.limit)
        elif args.command == "show":
            result = get_review_item(runtime, args.id)
        else:
            require_operator_token(_Request(args.operator_token), runtime.config)
            result = record_review_decision(
                runtime,
                args.id,
                args.decision,
                args.reason,
                args.operator_label,
                args.local_only_confirmed,
            )
    except (LocalOperatorError, Exception) as exc:
        result = {
            "schema_version": "local_review_queue_cli_result.v0",
            "status": "fail",
            "error": "review_queue_command_failed",
            "message": str(exc),
            "lan_enabled": False,
            "deployment_performed": False,
            "warnings": [],
            "limitations": ["no source probes or background execution were run"],
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
