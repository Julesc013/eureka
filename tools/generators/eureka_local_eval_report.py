#!/usr/bin/env python3
"""Convert a local eval JSON report to a Markdown summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_eval import build_markdown_summary, validate_eval_report, validate_no_forbidden_eval_effects


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = json.loads(Path(args.input).read_text(encoding="utf-8"))
        validate_no_forbidden_eval_effects(validate_eval_report(report))
        summary = build_markdown_summary(report)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(summary, encoding="utf-8")
        result = {
            "schema_version": "local_eval_report_summary_result.v0",
            "status": "pass",
            "input": args.input,
            "output": args.output,
            "report_status": report.get("status"),
            "warnings": [],
            "limitations": ["summary generation is read-only except explicit output"],
        }
    except Exception as exc:
        result = {
            "schema_version": "local_eval_report_summary_result.v0",
            "status": "fail",
            "error": "eval_report_generation_failed",
            "message": str(exc),
            "input": args.input,
            "output": args.output,
        }
        print(f"ERROR: {exc}", file=stderr)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {result['status']}", file=stdout)
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
