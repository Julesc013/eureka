#!/usr/bin/env python3
"""Apply the next eligible review-batch outputs to a temp explicit store."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_apply import run_review_batch_apply_next  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Use committed review/candidate examples.")
    parser.add_argument("--use-temp-instance", action="store_true", help="Prove apply only in a temporary explicit store.")
    parser.add_argument("--write-examples", action="store_true", help="Write examples, inventory, and audit evidence.")
    parser.add_argument("--apply", action="store_true", help="Reserved for future approved operator-instance apply; blocked here.")
    parser.add_argument("--operator-token", default="", help="Reserved for future operator-instance apply; never emitted.")
    parser.add_argument("--instance", default="", help="Reserved for future operator-instance apply; unused here.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if args.apply or args.operator_token or args.instance:
        parser.error("operator-instance apply is forbidden for REVIEW-BATCH-APPLY-NEXT-00")
    if not args.from_examples:
        parser.error("--from-examples is required")
    result = run_review_batch_apply_next(
        from_examples=True,
        use_temp_instance=bool(args.use_temp_instance),
        write_examples=bool(args.write_examples),
    )
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
