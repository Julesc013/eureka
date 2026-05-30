#!/usr/bin/env python3
"""Run deterministic SCOUT over bundled candidate examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.scout import build_scout_run, load_candidate_index_from_examples  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-candidate-examples", action="store_true", help="Use bundled candidate examples.")
    parser.add_argument("--seed", required=True, help="Seed candidate id.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_candidate_examples:
        parser.error("--from-candidate-examples is required for this offline CLI")
    payload = build_scout_run(args.seed, load_candidate_index_from_examples())
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
