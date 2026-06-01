#!/usr/bin/env python3
"""Validate live metadata review previews before temp local apply."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_apply import (  # noqa: E402
    build_live_metadata_local_apply_plan,
    load_live_metadata_review_previews,
    select_eligible_live_metadata_previews,
    validate_live_metadata_apply_plan,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-live-metadata-review-examples", action="store_true", help="Use committed review-preview examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_live_metadata_review_examples:
        parser.error("--from-live-metadata-review-examples is required")
    input_state = load_live_metadata_review_previews()
    eligible = select_eligible_live_metadata_previews(input_state)
    plan = build_live_metadata_local_apply_plan(eligible)
    result = validate_live_metadata_apply_plan(plan)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
