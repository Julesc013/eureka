#!/usr/bin/env python3
"""Run public alpha reassessment examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_alpha import (  # noqa: E402
    run_public_alpha_reassess,
    run_public_alpha_reassess_01,
    run_public_alpha_reassess_02,
    run_public_alpha_reassess_03,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-snapshot-refresh-examples",
        action="store_true",
        help="Use committed snapshot refresh examples.",
    )
    parser.add_argument(
        "--from-live-metadata-refresh-examples",
        action="store_true",
        help="Use committed live metadata snapshot refresh examples.",
    )
    parser.add_argument(
        "--from-live-metadata-review-refresh-examples",
        action="store_true",
        help="Use committed live metadata review snapshot refresh examples.",
    )
    parser.add_argument(
        "--from-local-apply-live-metadata-refresh-examples",
        action="store_true",
        help="Use committed local-apply live metadata snapshot refresh examples.",
    )
    parser.add_argument("--write-examples", action="store_true", help="Write public-safe reassessment examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if args.from_local_apply_live_metadata_refresh_examples:
        result = run_public_alpha_reassess_03(
            from_local_apply_live_metadata_refresh_examples=True,
            write_examples=args.write_examples,
        )
    elif args.from_live_metadata_review_refresh_examples:
        result = run_public_alpha_reassess_02(
            from_live_metadata_review_refresh_examples=True,
            write_examples=args.write_examples,
        )
    elif args.from_live_metadata_refresh_examples:
        result = run_public_alpha_reassess_01(
            from_live_metadata_refresh_examples=True,
            write_examples=args.write_examples,
        )
    elif args.from_snapshot_refresh_examples:
        result = run_public_alpha_reassess(
            from_snapshot_refresh_examples=True,
            write_examples=args.write_examples,
        )
    else:
        parser.error("--from-snapshot-refresh-examples, --from-live-metadata-refresh-examples, --from-live-metadata-review-refresh-examples, or --from-local-apply-live-metadata-refresh-examples is required")
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
