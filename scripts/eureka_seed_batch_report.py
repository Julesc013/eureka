#!/usr/bin/env python3
"""Summarize the frontier media seed-batch examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_RESULT = REPO_ROOT / "examples" / "seed_batches" / "frontier_media" / "seed_batch_result.json"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.seed_batches import run_seed_batch_frontier_media  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated fixture examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    result = _load_example_result() if EXAMPLE_RESULT.exists() else run_seed_batch_frontier_media(fixture=True)
    report = {
        "schema_version": "seed_batch_report.v0",
        "task": "SEED-BATCH-FRONTIER-MEDIA-00",
        "status": "pass" if result.get("fixture_seed_batch_passed") else "partial",
        "batch_id": result.get("batch_id"),
        "query_count": result.get("query_count"),
        "candidate_count": result.get("candidate_count"),
        "review_batch_refs": result.get("review_batch_refs", []),
        "snapshot_refresh_handoff_refs": result.get("snapshot_refresh_handoff_refs", []),
        "public_alpha_reassess_refs": result.get("public_alpha_reassess_refs", []),
        "operator_live_metadata_run_performed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0


def _load_example_result() -> dict[str, Any]:
    return json.loads(EXAMPLE_RESULT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
