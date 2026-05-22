#!/usr/bin/env python3
"""Build native smoke evidence packet previews without running native apps."""

from __future__ import annotations

import argparse
import json

try:
    from validate_native_packaging_manifests import build_smoke_evidence_packet, format_summary, summarize_native_examples, validate_output_path, write_json_output
except ModuleNotFoundError:  # pragma: no cover - package import path for tests.
    from scripts.validate_native_packaging_manifests import build_smoke_evidence_packet, format_summary, summarize_native_examples, validate_output_path, write_json_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", default="win.winforms")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packet = build_smoke_evidence_packet(args.lane)
    if args.output:
        write_json_output(validate_output_path(args.output), packet)
    if args.summary_output:
        summary = summarize_native_examples([])
        validate_output_path(args.summary_output).write_text(format_summary(summary) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"Native smoke evidence packet\nstatus: {packet['smoke_status']}\nlane_id: {packet['lane_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
