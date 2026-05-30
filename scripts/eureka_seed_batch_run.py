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

from runtime.seed_batches import run_seed_batch_frontier_media  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-media", action="store_true", help="Run SEED-BATCH-FRONTIER-MEDIA-00.")
    parser.add_argument("--fixture", action="store_true", help="Use deterministic fixture mode.")
    parser.add_argument("--write-examples", action="store_true", help="Write public-safe example packets.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.frontier_media:
        parser.error("--frontier-media is required")
    result = run_seed_batch_frontier_media(fixture=True, write_examples=args.write_examples)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
