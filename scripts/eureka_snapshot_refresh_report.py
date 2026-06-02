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

from runtime.snapshots import (  # noqa: E402
    run_snapshot_refresh,
    run_snapshot_refresh_01,
    run_snapshot_refresh_02,
    run_snapshot_refresh_03,
    run_snapshot_refresh_04,
    run_snapshot_refresh_05,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-examples", action="store_true", help="Read generated snapshot refresh examples.")
    parser.add_argument(
        "--from-live-metadata-examples",
        action="store_true",
        help="Read generated SNAPSHOT-REFRESH-01 live metadata examples.",
    )
    parser.add_argument(
        "--from-live-metadata-review-examples",
        action="store_true",
        help="Read generated SNAPSHOT-REFRESH-02 live metadata review examples.",
    )
    parser.add_argument(
        "--from-local-apply-live-metadata-examples",
        action="store_true",
        help="Read generated SNAPSHOT-REFRESH-03 local-apply live metadata examples.",
    )
    parser.add_argument(
        "--from-manuals-driver-examples",
        action="store_true",
        help="Read generated SNAPSHOT-REFRESH-04 manuals/scans and driver/support examples.",
    )
    parser.add_argument(
        "--from-public-search-ux-examples",
        action="store_true",
        help="Read generated SNAPSHOT-REFRESH-05 public search UX projection examples.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default shape.")
    args = parser.parse_args(argv)
    if args.from_public_search_ux_examples:
        path = REPO_ROOT / "examples" / "snapshots" / "refresh" / "public_search_ux_mvp" / "snapshot_refresh_05_result.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
        else:
            result = run_snapshot_refresh_05(from_public_search_ux_examples=True)
        report = _report_05(result)
    elif args.from_manuals_driver_examples:
        path = REPO_ROOT / "examples" / "snapshots" / "refresh" / "manuals_scans_driver_support" / "snapshot_refresh_04_result.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
        else:
            result = run_snapshot_refresh_04(from_manuals_driver_examples=True)
        report = _report_04(result)
    elif args.from_local_apply_live_metadata_examples:
        path = REPO_ROOT / "examples" / "snapshots" / "refresh" / "local_apply_live_metadata" / "snapshot_refresh_03_result.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
        else:
            result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
        report = _report_03(result)
    elif args.from_live_metadata_review_examples:
        path = REPO_ROOT / "examples" / "snapshots" / "refresh" / "live_metadata_review" / "snapshot_refresh_02_result.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
        else:
            result = run_snapshot_refresh_02(from_live_metadata_review_examples=True)
        report = _report_02(result)
    elif args.from_live_metadata_examples:
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
        parser.error("--from-examples, --from-live-metadata-examples, --from-live-metadata-review-examples, --from-local-apply-live-metadata-examples, --from-manuals-driver-examples, or --from-public-search-ux-examples is required")
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


def _report_02(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_02_report.v0",
        "task": "SNAPSHOT-REFRESH-02",
        "status": "pass" if result.get("fixture_snapshot_refresh_passed") else result.get("status", "partial"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "live_metadata_review_integrated": bool(result.get("live_metadata_review_integrated")),
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "reviewed_metadata_record_preview_count": result.get("reviewed_metadata_record_preview_count"),
        "reviewed_source_lead_preview_count": result.get("reviewed_source_lead_preview_count"),
        "useful_lead_count": result.get("useful_lead_count"),
        "needs_more_evidence_count": result.get("needs_more_evidence_count"),
        "rejected_or_duplicate_count": result.get("rejected_or_duplicate_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "live_metadata_candidate_promoted": False,
        "review_preview_applied": False,
        "raw_live_response_included": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
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


def _report_03(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_03_report.v0",
        "task": "SNAPSHOT-REFRESH-03",
        "status": "pass" if result.get("fixture_snapshot_refresh_passed") else result.get("status", "partial"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "local_apply_live_metadata_integrated": bool(result.get("local_apply_live_metadata_integrated")),
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "existing_reviewed_record_count": result.get("existing_reviewed_record_count"),
        "reviewed_metadata_record_count": result.get("reviewed_metadata_record_count"),
        "reviewed_source_lead_count": result.get("reviewed_source_lead_count"),
        "reviewed_record_delta_count": result.get("reviewed_record_delta_count"),
        "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
        "fixture_candidate_count": result.get("fixture_candidate_count"),
        "live_metadata_candidate_count": result.get("live_metadata_candidate_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "operator_instance_mutated": False,
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


def _report_04(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_04_report.v0",
        "task": "SNAPSHOT-REFRESH-04",
        "status": "pass" if result.get("fixture_snapshot_refresh_passed") else result.get("status", "partial"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "manuals_scans_integrated": bool(result.get("manuals_scans_integrated")),
        "driver_support_integrated": bool(result.get("driver_support_integrated")),
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "existing_reviewed_record_count": result.get("existing_reviewed_record_count"),
        "reviewed_metadata_record_count": result.get("reviewed_metadata_record_count"),
        "reviewed_source_lead_count": result.get("reviewed_source_lead_count"),
        "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
        "manuals_scans_candidate_count": result.get("manuals_scans_candidate_count"),
        "driver_support_candidate_count": result.get("driver_support_candidate_count"),
        "additional_seed_candidate_count": result.get("additional_seed_candidate_count"),
        "total_candidate_count": result.get("total_candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "compatibility_guarantee_created": False,
        "rights_clearance_claim_created": False,
        "scan_completeness_claim_created": False,
        "ocr_quality_claim_created": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "install_execution_enabled": False,
        "operator_instance_mutated": False,
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


def _report_05(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_05_report.v0",
        "task": "SNAPSHOT-REFRESH-05",
        "status": "pass" if result.get("fixture_snapshot_refresh_passed") else result.get("status", "partial"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "public_search_ux_integrated": bool(result.get("public_search_ux_integrated")),
        "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
        "total_candidate_count": result.get("total_candidate_count"),
        "public_ux_routes_count": result.get("public_ux_routes_count"),
        "result_card_states_count": result.get("result_card_states_count"),
        "no_js_required": bool(result.get("no_js_required")),
        "public_projection_read_only": bool(result.get("public_projection_read_only")),
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
