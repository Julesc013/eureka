#!/usr/bin/env python3
"""Run the P104 local pack import dry-run over approved examples."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.packs.dry_run import run_pack_import_dry_run  # noqa: E402
from runtime.packs.errors import PackImportPolicyError  # noqa: E402
from runtime.packs.policy import (  # noqa: E402
    assert_no_forbidden_cli_args,
    default_example_roots,
    ensure_approved_output_path,
)
from runtime.packs.report import report_to_json  # noqa: E402


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv if argv is not None else sys.argv[1:])
    try:
        assert_no_forbidden_cli_args(raw_args)
    except PackImportPolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--example-root", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--no-validator-commands", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(raw_args)

    roots = [Path(item) for item in args.example_root]
    if args.all_examples or not roots:
        roots = list(default_example_roots())

    report = run_pack_import_dry_run(
        roots,
        strict=args.strict,
        run_validators=not args.no_validator_commands,
        enforce_approved_roots=True,
        allow_temp_roots=True,
    )
    payload = report_to_json(report)

    if args.output:
        try:
            output = ensure_approved_output_path(Path(args.output))
        except PackImportPolicyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")

    if args.json:
        print(payload, end="")
    else:
        print(f"report_id: {report.report_id}")
        print("mode: local_dry_run")
        print(f"packs_seen: {report.packs_seen}")
        print(f"packs_valid: {report.packs_valid}")
        print(f"packs_invalid: {report.packs_invalid}")
        for warning in report.warnings:
            print(f"warning: {warning}")
        for error in report.errors:
            print(f"error: {error.message}")

    if args.strict and (report.packs_invalid or report.errors):
        return 1
    return 0 if not report.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
