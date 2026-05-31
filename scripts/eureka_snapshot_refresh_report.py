#!/usr/bin/env python3
"""Summarize committed snapshot refresh examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots import run_snapshot_refresh, run_snapshot_refresh_01  # noqa: E402


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated snapshot refresh examples.")
    parser.add_argument(
        "--from-live-metadata-examples",
        action="store_true",
        help="Read generated SNAPSHOT-REFRESH-01 live metadata examples.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if args.from_live_metadata_examples:
        path = REPO_ROOT / "examples" / "snapshots" / "refresh" / "live_metadata" / "snapshot_refresh_01_result.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
        else:
            result = run_snapshot_refresh_01(from_live_metadata_pilot_examples=True)
        report = _report_01(result)
    elif args.from_examples:
        path = REPO_ROOT / "examples" / "snapshots" / "refresh" / "snapshot_refresh_result.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
        else:
            result = run_snapshot_refresh(from_seed_examples=True)
        report = _report(result)
    else:
        parser.error("--from-examples or --from-live-metadata-examples is required")
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0 if report["status"] == "pass" else 1


def _report(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_report.v0",
        "task": "SNAPSHOT-REFRESH-00",
        "status": "pass" if result.get("fixture_snapshot_refresh_passed") else result.get("status", "partial"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "review_queue_candidate_count": result.get("review_queue_candidate_count"),
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _report_01(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_01_report.v0",
        "task": "SNAPSHOT-REFRESH-01",
        "status": "pass" if result.get("fixture_snapshot_refresh_passed") else result.get("status", "partial"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "live_metadata_pilot_integrated": bool(result.get("live_metadata_pilot_integrated")),
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "review_queue_candidate_count": result.get("review_queue_candidate_count"),
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "live_metadata_candidate_promoted": False,
        "raw_live_response_included": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
