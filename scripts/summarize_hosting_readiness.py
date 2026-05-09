#!/usr/bin/env python3
"""Summarize hosting readiness examples and audit outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_hosting_readiness import format_summary, summarize_hosting_examples, validate_output_path, write_json_output
except ModuleNotFoundError:  # pragma: no cover
    from scripts.validate_hosting_readiness import format_summary, summarize_hosting_examples, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    inputs = [Path(value) for value in args.input] or [Path("examples/hosting")]
    summary = summarize_hosting_examples(inputs)
    if args.output:
        write_json_output(validate_output_path(args.output), summary)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_summary(summary) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(format_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
