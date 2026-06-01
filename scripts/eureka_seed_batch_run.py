#!/usr/bin/env python3
"""Run a governed seed batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.seed_batches import (  # noqa: E402
    run_seed_batch_frontier_media,
    run_seed_batch_legacy_software,
    run_seed_batch_manuals_scans,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-media", action="store_true", help="Run SEED-BATCH-FRONTIER-MEDIA-00.")
    parser.add_argument("--legacy-software", action="store_true", help="Run SEED-BATCH-LEGACY-SOFTWARE-00.")
    parser.add_argument("--manuals-scans", action="store_true", help="Run SEED-BATCH-MANUALS-SCANS-00.")
    parser.add_argument("--fixture", action="store_true", help="Use deterministic fixture mode.")
    parser.add_argument("--write-examples", action="store_true", help="Write public-safe example packets.")
    parser.add_argument("--write-inventory", action="store_true", help="Write inventory and audit evidence packets.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    selected = [args.frontier_media, args.legacy_software, args.manuals_scans]
    if sum(1 for item in selected if item) != 1:
        parser.error("choose exactly one of --frontier-media, --legacy-software, or --manuals-scans")
    if args.manuals_scans:
        result = run_seed_batch_manuals_scans(
            fixture=True,
            write_examples=args.write_examples,
            write_inventory=args.write_inventory,
        )
    elif args.legacy_software:
        result = run_seed_batch_legacy_software(fixture=True, write_examples=args.write_examples)
    else:
        result = run_seed_batch_frontier_media(fixture=True, write_examples=args.write_examples)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
