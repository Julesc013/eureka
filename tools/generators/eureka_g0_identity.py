#!/usr/bin/env python3
"""Build provisional G0 identity and near-miss candidates from a fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.eval.g0_quality import build_identity_cluster_candidates, build_near_miss_candidates, load_quality_fixture  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="examples/search/quality/sample_quality_fixture.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    fixture = load_quality_fixture(args.fixture)
    identity = build_identity_cluster_candidates(fixture.get("records", []))
    near_misses = build_near_miss_candidates(fixture.get("records", []), fixture.get("query_context", {}))
    payload = {
        "schema_version": "g0_identity_output.v0",
        **identity,
        "near_miss_candidates": near_misses["near_miss_candidates"],
        "accepted_identity_merge_created": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "G0 identity candidates built", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
