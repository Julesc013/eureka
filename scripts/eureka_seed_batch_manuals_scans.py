#!/usr/bin/env python3
"""Run the fixture-first manuals/scans seed batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.seed_batches import run_seed_batch_manuals_scans  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true", help="Run deterministic fixture seed batch.")
    mode.add_argument(
        "--metadata-descriptors",
        action="store_true",
        help="Build bounded metadata descriptor dry-run posture without live calls.",
    )
    parser.add_argument("--write-examples", action="store_true", help="Write public-safe example packets.")
    parser.add_argument("--write-inventory", action="store_true", help="Write inventory and audit evidence packets.")
    parser.add_argument("--dry-run", action="store_true", help="Record dry-run posture for operator readability.")
    parser.add_argument(
        "--operator-approved-live-metadata",
        action="store_true",
        help="Record that an operator approved a future bounded metadata pilot. This CLI still commits no raw response.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    fixture = args.fixture or not args.metadata_descriptors
    result = run_seed_batch_manuals_scans(
        fixture=fixture,
        metadata_descriptors=args.metadata_descriptors,
        operator_approved_live_metadata=args.operator_approved_live_metadata,
        write_examples=args.write_examples,
        write_inventory=args.write_inventory,
    )
    result["dry_run"] = bool(args.dry_run or args.metadata_descriptors or fixture)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
