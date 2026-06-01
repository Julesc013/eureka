#!/usr/bin/env python3
"""Summarize live metadata candidate review examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.review.live_metadata import run_live_metadata_candidate_review  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    path = REPO_ROOT / "examples" / "review" / "live_metadata" / "live_metadata_review_result.json"
    if path.exists():
        result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    else:
        result = run_live_metadata_candidate_review(from_live_metadata_examples=True)
    report = {
        "schema_version": "live_metadata_review_report.v0",
        "task": "REVIEW-LIVE-METADATA-CANDIDATES-00",
        "status": result.get("status", "pass"),
        "live_metadata_candidates_reviewed": result.get("live_metadata_candidates_reviewed", 0),
        "reviewed_metadata_record_preview_count": result.get("reviewed_metadata_record_preview_count", 0),
        "reviewed_source_lead_preview_count": result.get("reviewed_source_lead_preview_count", 0),
        "useful_lead_count": result.get("useful_lead_count", 0),
        "needs_more_evidence_count": result.get("needs_more_evidence_count", 0),
        "rejected_or_duplicate_count": result.get("rejected_or_duplicate_count", 0),
        "new_live_source_calls_performed": False,
        "raw_live_response_committed": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "accepted_truth_created": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
