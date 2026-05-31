#!/usr/bin/env python3
"""Run the PUBLIC-ALPHA-REASSESS-00 example reassessment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_alpha import run_public_alpha_reassess  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-snapshot-refresh-examples",
        action="store_true",
        help="Use committed snapshot refresh examples.",
    )
    parser.add_argument("--write-examples", action="store_true", help="Write public-safe reassessment examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_snapshot_refresh_examples:
        parser.error("--from-snapshot-refresh-examples is required")
    result = run_public_alpha_reassess(
        from_snapshot_refresh_examples=True,
        write_examples=args.write_examples,
    )
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
