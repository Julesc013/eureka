#!/usr/bin/env python3
"""Build snapshot refresh fixture projections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots import run_snapshot_refresh, run_snapshot_refresh_01  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-seed-examples", action="store_true", help="Use committed seed-batch example handoffs.")
    parser.add_argument(
        "--from-live-metadata-pilot-examples",
        action="store_true",
        help="Use committed redacted live metadata pilot handoffs.",
    )
    parser.add_argument("--write-examples", action="store_true", help="Write public-safe snapshot refresh examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if args.from_live_metadata_pilot_examples:
        result = run_snapshot_refresh_01(
            from_live_metadata_pilot_examples=True,
            write_examples=args.write_examples,
        )
    elif args.from_seed_examples:
        result = run_snapshot_refresh(from_seed_examples=True, write_examples=args.write_examples)
    else:
        parser.error("--from-seed-examples or --from-live-metadata-pilot-examples is required")
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
