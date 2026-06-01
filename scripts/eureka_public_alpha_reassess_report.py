#!/usr/bin/env python3
"""Summarize committed public alpha reassessment examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_alpha import (  # noqa: E402
    run_public_alpha_reassess,
    run_public_alpha_reassess_01,
    run_public_alpha_reassess_02,
    run_public_alpha_reassess_03,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated reassessment examples.")
    parser.add_argument(
        "--from-live-metadata-examples",
        action="store_true",
        help="Read generated PUBLIC-ALPHA-REASSESS-01 live metadata examples.",
    )
    parser.add_argument(
        "--from-live-metadata-review-examples",
        action="store_true",
        help="Read generated PUBLIC-ALPHA-REASSESS-02 live metadata review examples.",
    )
    parser.add_argument(
        "--from-local-apply-live-metadata-examples",
        action="store_true",
        help="Read generated PUBLIC-ALPHA-REASSESS-03 local apply live metadata examples.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if args.from_local_apply_live_metadata_examples:
        path = REPO_ROOT / "examples" / "public_alpha" / "reassess" / "local_apply_live_metadata" / "public_alpha_reassess_03_result.json"
        result = json.loads(path.read_text(encoding="utf-8")) if path.exists() else run_public_alpha_reassess_03(from_local_apply_live_metadata_refresh_examples=True)
        report = _report_03(result)
    elif args.from_live_metadata_review_examples:
        path = REPO_ROOT / "examples" / "public_alpha" / "reassess" / "live_metadata_review" / "public_alpha_reassess_02_result.json"
        result = json.loads(path.read_text(encoding="utf-8")) if path.exists() else run_public_alpha_reassess_02(from_live_metadata_review_refresh_examples=True)
        report = _report_02(result)
    elif args.from_live_metadata_examples:
        path = REPO_ROOT / "examples" / "public_alpha" / "reassess" / "live_metadata" / "public_alpha_reassess_01_result.json"
        result = json.loads(path.read_text(encoding="utf-8")) if path.exists() else run_public_alpha_reassess_01(from_live_metadata_refresh_examples=True)
        report = _report_01(result)
    elif args.from_examples:
        path = REPO_ROOT / "examples" / "public_alpha" / "reassess" / "public_alpha_reassess_result.json"
        result = json.loads(path.read_text(encoding="utf-8")) if path.exists() else run_public_alpha_reassess(from_snapshot_refresh_examples=True)
        report = _report(result)
    else:
        parser.error("--from-examples, --from-live-metadata-examples, --from-live-metadata-review-examples, or --from-local-apply-live-metadata-examples is required")
    print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    return 0 if report["status"] == "pass" else 1


def _report(result: dict[str, Any]) -> dict[str, Any]:
    return {
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


def _report_01(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_01_report.v0",
        "task": "PUBLIC-ALPHA-REASSESS-01",
        "status": result.get("status", "pass"),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "total_candidate_count": result.get("total_candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_summary_count": result.get("absence_summary_count"),
        "launch_recommended": result.get("launch_recommended"),
        "demo_mode_recommended": result.get("demo_mode_recommended"),
        "internal_review_recommended": result.get("internal_review_recommended"),
        "needs_more_reviewed_records": result.get("needs_more_reviewed_records"),
        "needs_live_candidate_review": result.get("needs_live_candidate_review"),
        "needs_snapshot_refresh_after_review": result.get("needs_snapshot_refresh_after_review"),
        "recommended_next_task": result.get("recommended_next_task", "REVIEW-LIVE-METADATA-CANDIDATES-00 - Review live metadata candidates for possible local promotion"),
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _report_02(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_02_report.v0",
        "task": "PUBLIC-ALPHA-REASSESS-02",
        "status": result.get("status", "pass"),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "total_candidate_count": result.get("total_candidate_count"),
        "reviewed_metadata_record_preview_count": result.get("reviewed_metadata_record_preview_count"),
        "reviewed_source_lead_preview_count": result.get("reviewed_source_lead_preview_count"),
        "useful_lead_count": result.get("useful_lead_count"),
        "needs_more_evidence_count": result.get("needs_more_evidence_count"),
        "rejected_or_duplicate_count": result.get("rejected_or_duplicate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_summary_count": result.get("absence_summary_count"),
        "launch_recommended": result.get("launch_recommended"),
        "demo_mode_recommended": result.get("demo_mode_recommended"),
        "internal_review_recommended": result.get("internal_review_recommended"),
        "needs_more_reviewed_records": result.get("needs_more_reviewed_records"),
        "needs_local_apply_of_review_previews": result.get("needs_local_apply_of_review_previews"),
        "needs_snapshot_refresh_after_apply": result.get("needs_snapshot_refresh_after_apply"),
        "needs_public_alpha_reassess_after_apply": result.get("needs_public_alpha_reassess_after_apply"),
        "recommended_next_task": result.get("recommended_next_task", "LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00 - Apply eligible live metadata review previews through local apply gate"),
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _report_03(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_03_report.v0",
        "task": "PUBLIC-ALPHA-REASSESS-03",
        "status": result.get("status", "pass"),
        "existing_reviewed_record_count": result.get("existing_reviewed_record_count"),
        "reviewed_metadata_record_count": result.get("reviewed_metadata_record_count"),
        "reviewed_source_lead_count": result.get("reviewed_source_lead_count"),
        "reviewed_record_delta_count": result.get("reviewed_record_delta_count"),
        "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "total_candidate_count": result.get("total_candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_summary_count": result.get("absence_summary_count"),
        "launch_recommended": result.get("launch_recommended"),
        "demo_mode_recommended": result.get("demo_mode_recommended"),
        "internal_review_recommended": result.get("internal_review_recommended"),
        "needs_more_reviewed_records": result.get("needs_more_reviewed_records"),
        "needs_more_domains": result.get("needs_more_domains"),
        "needs_more_seed_batches": result.get("needs_more_seed_batches"),
        "needs_more_reviewed_artifact_records": result.get("needs_more_reviewed_artifact_records"),
        "needs_seed_batch_manuals_scans": result.get("needs_seed_batch_manuals_scans"),
        "needs_seed_batch_driver_support": result.get("needs_seed_batch_driver_support"),
        "recommended_next_task": result.get("recommended_next_task", "SEED-BATCH-MANUALS-SCANS-00 - Add manuals and scanned-documents discovery batch"),
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
