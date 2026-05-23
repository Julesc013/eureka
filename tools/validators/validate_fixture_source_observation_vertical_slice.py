#!/usr/bin/env python3
"""Validate Q58 fixture source observation vertical slice behavior."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.foundry.fixture_source_observation_slice import (
    run_fixture_source_observation_slice,
    validate_fixture_slice_report,
    write_json,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", help="Directory for isolated fixture SQLite stores.")
    parser.add_argument("--output", help="Optional JSON report path.")
    parser.add_argument("--json", action="store_true", help="Print the JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        report = run_fixture_source_observation_slice(args.output_root)
    except Exception as exc:  # pragma: no cover - command boundary
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2, sort_keys=True), file=stderr)
        return 2

    errors = validate_fixture_slice_report(report)
    if errors:
        report = dict(report)
        report["status"] = "fail"
        report["errors"] = errors
    if args.output:
        write_json(args.output, report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("fixture source observation vertical slice", file=stdout)
        print(f"status: {report.get('status')}", file=stdout)
        print(f"search_results: {report.get('search', {}).get('result_count')}", file=stdout)
        print(f"absence_results: {report.get('absence', {}).get('result_count')}", file=stdout)
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
