#!/usr/bin/env python3
"""Build deterministic G0 user-cost/actionability scores from a fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_eval.g0_quality import build_user_cost_score, load_quality_fixture  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="examples/search_quality/sample_quality_fixture.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    fixture = load_quality_fixture(args.fixture)
    scores = [build_user_cost_score(record, fixture.get("action_posture", {})) for record in fixture.get("records", [])]
    payload = {
        "schema_version": "g0_user_cost_output.v0",
        "user_cost_scores": scores,
        "user_cost_count": len(scores),
        "accepted_truth": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"G0 user_cost_count={len(scores)}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
