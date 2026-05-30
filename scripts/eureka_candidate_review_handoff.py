#!/usr/bin/env python3
"""Create a review-only handoff packet for an example candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.candidate_store import build_candidate_review_handoff, sample_candidate_index  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-id", required=True, help="Candidate id from the example index.")
    parser.add_argument("--from-examples", action="store_true", help="Load bundled example candidate records.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)

    if not args.from_examples:
        parser.error("--from-examples is required for this offline CLI")
    candidates = sample_candidate_index()["candidates"]
    candidate = next((item for item in candidates if item["candidate_id"] == args.candidate_id), None)
    if candidate is None:
        parser.error(f"candidate not found: {args.candidate_id}")
    payload = build_candidate_review_handoff(candidate)
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
