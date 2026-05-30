#!/usr/bin/env python3
"""Search review-only local candidate examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.candidate_store import build_candidate_lane_packet, sample_candidate_index, search_candidates  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Candidate search query.")
    parser.add_argument("--from-examples", action="store_true", help="Search bundled examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)

    if not args.from_examples:
        parser.error("--from-examples is required for this offline CLI")
    result = search_candidates(args.query, sample_candidate_index())
    lane_packet = build_candidate_lane_packet(result, "public_web")
    payload = {
        "schema_version": "candidate_search_cli_result.v0",
        "search_result": result,
        "candidate_lane_packet": lane_packet,
        "accepted_truth": False,
        "public_mutation_enabled": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
