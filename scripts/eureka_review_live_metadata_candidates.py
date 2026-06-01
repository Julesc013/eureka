#!/usr/bin/env python3
"""Review redacted live metadata candidates from bundled examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.review.live_metadata import run_live_metadata_candidate_review  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-live-metadata-examples", action="store_true", help="Use redacted live metadata examples.")
    parser.add_argument("--write-examples", action="store_true", help="Write examples, inventory, and audit evidence.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_live_metadata_examples:
        parser.error("--from-live-metadata-examples is required")
    result = run_live_metadata_candidate_review(
        from_live_metadata_examples=True,
        write_examples=args.write_examples,
    )
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
