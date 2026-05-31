#!/usr/bin/env python3
"""Summarize live metadata pilot examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.seed_batches import run_live_metadata_pilot_batch  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    path = REPO_ROOT / "examples" / "live_metadata_pilot" / "live_metadata_pilot_result.json"
    result: dict[str, Any]
    if path.exists():
        result = json.loads(path.read_text(encoding="utf-8"))
    else:
        result = run_live_metadata_pilot_batch(fixture=True)
    report = {
        "schema_version": "live_metadata_pilot_report.v0",
        "task": "LIVE-METADATA-PILOT-BATCH-00",
        "status": result.get("status", "waiting_for_operator_live_metadata_approval"),
        "approval_verified": bool(result.get("approval_verified", False)),
        "source_family": result.get("source_family", "internet_archive_metadata"),
        "selected_query_count": result.get("selected_query_count", 0),
        "total_live_requests": result.get("total_live_requests", 0),
        "operator_live_metadata_run_performed": bool(result.get("operator_live_metadata_run_performed", False)),
        "candidate_summaries_created": bool(result.get("candidate_summaries_created", False)),
        "raw_live_response_committed": False,
        "download_performed": False,
        "extraction_executed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
