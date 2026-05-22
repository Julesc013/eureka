#!/usr/bin/env python3
"""Audit Track C first-wave native integration readiness."""

from __future__ import annotations

import argparse
import json

try:
    from validate_native_packaging_manifests import build_track_c_integration_audit, format_summary, summarize_native_examples, validate_output_path, write_json_output
except ModuleNotFoundError:  # pragma: no cover - package import path for tests.
    from scripts.validate_native_packaging_manifests import build_track_c_integration_audit, format_summary, summarize_native_examples, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    audit = build_track_c_integration_audit()
    if args.json_output:
        write_json_output(validate_output_path(args.json_output), audit)
    if args.summary_output:
        summary = summarize_native_examples([])
        validate_output_path(args.summary_output).write_text(format_summary(summary) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True))
    else:
        print("Track C integration audit")
        print(f"track_c_exit_gate: {audit['track_c_exit_gate']}")
        print(f"next_phase_recommendation: {audit['next_phase_recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
