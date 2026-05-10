#!/usr/bin/env python3
"""Summarize public alpha rehearsal examples and audit outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.hosting.summaries import format_public_alpha_summary, summarize_public_alpha_readiness
from scripts.validate_hosted_wrapper_rehearsal import validate_output_path, write_json_output


def expand_inputs(values: list[str]) -> list[Path]:
    files: list[Path] = []
    for value in values or ["examples/hosting"]:
        path = REPO_ROOT / value
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in expand_inputs(args.input or ["examples/hosting"])]
    summary = summarize_public_alpha_readiness(payloads, {})
    if args.output:
        write_json_output(validate_output_path(args.output), summary)
    if args.summary_output:
        validate_output_path(args.summary_output).write_text(format_public_alpha_summary(summary) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif args.check:
        print(f"Public alpha readiness summary status: {summary['status']}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
