#!/usr/bin/env python3
"""Run the approval-gated live metadata pilot batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.seed_batches import run_live_metadata_pilot_batch  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Build request plans without network access.")
    mode.add_argument("--fixture", action="store_true", help="Run deterministic fixture transport.")
    mode.add_argument(
        "--operator-approved-live-metadata",
        action="store_true",
        help="Run live metadata only with a valid approval file.",
    )
    parser.add_argument("--approval", help="Approval file path for approved live metadata mode.")
    parser.add_argument("--write-examples", action="store_true", help="Write examples, inventory, and audit evidence.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if args.operator_approved_live_metadata and not args.approval:
        parser.error("--approval is required with --operator-approved-live-metadata")
    result = run_live_metadata_pilot_batch(
        approval_path=args.approval,
        dry_run=args.dry_run or not (args.fixture or args.operator_approved_live_metadata),
        fixture=args.fixture,
        operator_approved_live_metadata=args.operator_approved_live_metadata,
        write_examples=args.write_examples,
    )
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    if args.operator_approved_live_metadata and result.get("status") == "waiting_for_operator_live_metadata_approval":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
