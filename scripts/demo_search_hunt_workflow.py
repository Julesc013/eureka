#!/usr/bin/env python3
"""Demonstrate the integrated local Search Hunt workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from eureka_hunt_workflow_smoke import (  # noqa: E402
    DEFAULT_QUERY,
    emit_result,
    fail_result,
    main as smoke_main,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", help="Explicit local appliance instance root.")
    parser.add_argument("--operator-token", help="Operator token for local mutations.")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if not args.instance:
        result = fail_result("missing_instance", "--instance is required")
        emit_result(result, args.json, args.output, stdout)
        print("ERROR: --instance is required", file=stderr)
        return 2
    smoke_args = [
        "--instance",
        args.instance,
        "--operator-token",
        str(args.operator_token or ""),
        "--query",
        args.query,
    ]
    if args.json:
        smoke_args.append("--json")
    if args.output:
        smoke_args.extend(["--output", args.output])
    return smoke_main(smoke_args, stdout=stdout, stderr=stderr)


if __name__ == "__main__":
    raise SystemExit(main())
