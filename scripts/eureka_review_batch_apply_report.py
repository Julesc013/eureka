#!/usr/bin/env python3
"""Report the deterministic review-batch apply proof."""

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
    parser.add_argument("--from-examples", action="store_true", help="Use committed examples only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)
    report = {
        "schema_version": "review_batch_apply_next_report.v0",
        "task": "REVIEW-BATCH-APPLY-NEXT-00",
        "status": result["status"],
        "total_candidates_considered": result["total_candidates_considered"],
        "eligible_apply_count": result["eligible_apply_count"],
        "limited_reviewed_metadata_records_created": result["limited_reviewed_metadata_records_created"],
        "limited_reviewed_source_leads_created": result["limited_reviewed_source_leads_created"],
        "reviewed_known_needs_created": result["reviewed_known_needs_created"],
        "reviewed_bounded_absences_created": result["reviewed_bounded_absences_created"],
        "reviewed_record_delta_count": result["reviewed_record_delta_count"],
        "non_applied_count": result["non_applied_count"],
        "temp_instance_apply_passed": result["temp_instance_apply_passed"],
        "rollback_plan_created": result["rollback_plan_created"],
        "boundary_report": result["boundary_report"],
        "recommended_next_task": result["recommended_next_task"],
    }
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
