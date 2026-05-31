#!/usr/bin/env python3
"""Summarize committed PUBLIC-ALPHA-REASSESS-00 examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_alpha import run_public_alpha_reassess  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated reassessment examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if not args.from_examples:
        parser.error("--from-examples is required")
    path = REPO_ROOT / "examples" / "public_alpha" / "reassess" / "public_alpha_reassess_result.json"
    result: dict[str, Any]
    if path.exists():
        result = json.loads(path.read_text(encoding="utf-8"))
    else:
        result = run_public_alpha_reassess(from_snapshot_refresh_examples=True)
    report = {
        "schema_version": "public_alpha_reassess_report.v0",
        "task": "PUBLIC-ALPHA-REASSESS-00",
        "status": result.get("status", "pass"),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_summary_count": result.get("absence_summary_count"),
        "launch_recommended": result.get("launch_recommended"),
        "demo_mode_recommended": result.get("demo_mode_recommended"),
        "needs_more_reviewed_records": result.get("needs_more_reviewed_records"),
        "recommended_next_task": result.get(
            "recommended_next_task",
            "LIVE-METADATA-PILOT-BATCH-00 - Operator-approved live metadata pilot over seed queries",
        ),
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
