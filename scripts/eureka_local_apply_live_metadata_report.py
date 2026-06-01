#!/usr/bin/env python3
"""Report the deterministic live metadata local-apply proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_apply import run_local_apply_live_metadata_previews  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Use committed examples only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    result = run_local_apply_live_metadata_previews(from_live_metadata_review_examples=True, use_temp_instance=True)
    report = {
        "schema_version": "local_apply_live_metadata_report.v0",
        "task": "LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00",
        "status": result["status"],
        "eligible_preview_count": result["eligible_preview_count"],
        "reviewed_metadata_records_created": result["reviewed_metadata_records_created"],
        "reviewed_source_leads_created": result["reviewed_source_leads_created"],
        "reviewed_record_delta_count": result["reviewed_record_delta_count"],
        "temp_instance_apply_passed": result["temp_instance_apply_passed"],
        "rollback_plan_created": result["rollback_plan_created"],
        "boundary_report": result["boundary_report"],
        "recommended_next_task": result["recommended_next_task"],
    }
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
