#!/usr/bin/env python3
"""Run and inspect the isolated synthetic E2E truth path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.synthetic_truth_path import (
    DEFAULT_OUTPUT_ROOT,
    SyntheticTruthPathError,
    SyntheticTruthPathOptions,
    rollback_synthetic_truth_path,
    run_synthetic_truth_path,
    status_synthetic_truth_path,
    validate_synthetic_truth_path,
    verify_synthetic_truth_snapshot,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the complete isolated synthetic truth-path scenario.")
    run_parser.add_argument("--scenario", default="minimal-success")
    run_parser.add_argument("--out", default=str(DEFAULT_OUTPUT_ROOT))
    run_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a generated synthetic truth-path scenario.")
    validate_parser.add_argument("--scenario-dir", required=True)
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print synthetic truth-path scenario status.")
    status_parser.add_argument("--scenario-dir", required=True)
    status_parser.add_argument("--json", action="store_true")

    rollback_parser = subparsers.add_parser("rollback", help="Restore active synthetic materialization/index pointers to baseline.")
    rollback_parser.add_argument("--scenario-dir", required=True)
    rollback_parser.add_argument("--json", action="store_true")

    snapshot_parser = subparsers.add_parser("verify-snapshot", help="Verify the synthetic test snapshot.")
    snapshot_parser.add_argument("--scenario-dir", required=True)
    snapshot_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            payload = run_synthetic_truth_path(SyntheticTruthPathOptions(scenario=args.scenario, out_root=Path(args.out)))
            _print_payload(payload, json_output=args.json, stdout=stdout)
            return 0 if payload["status"] == "PASS" else 1
        if args.command == "validate":
            payload = validate_synthetic_truth_path(args.scenario_dir, strict=args.strict)
            _print_payload(payload, json_output=args.json, stdout=stdout)
            return 0 if payload["status"] == "pass" else 1
        if args.command == "status":
            payload = status_synthetic_truth_path(args.scenario_dir)
            _print_payload(payload, json_output=args.json, stdout=stdout)
            return 0 if payload["status"] == "pass" else 1
        if args.command == "rollback":
            payload = rollback_synthetic_truth_path(args.scenario_dir)
            _print_payload(payload, json_output=args.json, stdout=stdout)
            return 0
        if args.command == "verify-snapshot":
            payload = verify_synthetic_truth_snapshot(args.scenario_dir)
            _print_payload(payload, json_output=args.json, stdout=stdout)
            return 0 if payload["verification_status"] == "verified_local" else 1
    except (OSError, ValueError, SyntheticTruthPathError) as exc:
        print(f"synthetic truth path failed: {exc}", file=stderr)
        return 1
    return 1


def _print_payload(payload: dict[str, object], *, json_output: bool, stdout: TextIO) -> None:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        return
    print(f"status: {payload.get('status', payload.get('verification_status', 'unknown'))}", file=stdout)
    for key in ("scenario_dir", "scenario_id", "reviewed_record_id", "snapshot_verification_status"):
        if payload.get(key):
            print(f"{key}: {payload[key]}", file=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
