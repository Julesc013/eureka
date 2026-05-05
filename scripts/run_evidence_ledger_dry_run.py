#!/usr/bin/env python3
"""Run the P99 local evidence-ledger dry-run over approved examples."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.evidence_ledger.dry_run import run_evidence_ledger_dry_run  # noqa: E402
from runtime.evidence_ledger.errors import EvidenceLedgerPolicyError  # noqa: E402
from runtime.evidence_ledger.policy import (  # noqa: E402
    DRY_RUN_EXAMPLES_ROOT,
    assert_no_forbidden_cli_args,
    ensure_approved_output_path,
)
from runtime.evidence_ledger.report import report_to_json  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv if argv is not None else sys.argv[1:])
    try:
        assert_no_forbidden_cli_args(raw_args)
    except EvidenceLedgerPolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--example-root", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(raw_args)

    roots = [Path(item) for item in args.example_root]
    if args.all_examples or not roots:
        roots = [DRY_RUN_EXAMPLES_ROOT]

    report = run_evidence_ledger_dry_run(
        roots,
        strict=args.strict,
        enforce_approved_roots=True,
        allow_temp_roots=True,
    )
    payload = report_to_json(report)

    if args.output:
        try:
            output = ensure_approved_output_path(Path(args.output))
        except EvidenceLedgerPolicyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")

    if args.json:
        print(payload, end="")
    else:
        print(f"report_id: {report.report_id}")
        print("mode: local_dry_run")
        print(f"candidates_seen: {report.candidates_seen}")
        print(f"candidates_valid: {report.candidates_valid}")
        print(f"candidates_invalid: {report.candidates_invalid}")
        for warning in report.warnings:
            print(f"warning: {warning}")
        for error in report.errors:
            print(f"error: {error.message}")

    if args.strict and (report.candidates_invalid or report.errors):
        return 1
    return 0 if not report.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
