#!/usr/bin/env python3
"""Validate SNAPSHOT-REFRESH-00."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots import (  # noqa: E402
    build_snapshot_refresh_01_inventory_packets,
    build_snapshot_refresh_02_inventory_packets,
    build_snapshot_refresh_03_inventory_packets,
    build_snapshot_refresh_04_inventory_packets,
    build_snapshot_refresh_05_inventory_packets,
    build_snapshot_refresh_inventory_packets,
    run_snapshot_refresh_05,
    run_snapshot_refresh_04,
    run_snapshot_refresh_03,
    run_snapshot_refresh_02,
    run_snapshot_refresh_01,
    run_snapshot_refresh,
)


REQUIRED_CONTRACTS = [
    "contracts/snapshot/snapshot_refresh_plan.v0.json",
    "contracts/snapshot/snapshot_refresh_result.v0.json",
    "contracts/snapshot/snapshot_reviewed_record_section.v0.json",
    "contracts/snapshot/snapshot_reviewed_metadata_record_section.v0.json",
    "contracts/snapshot/snapshot_reviewed_source_lead_section.v0.json",
    "contracts/snapshot/snapshot_candidate_section.v0.json",
    "contracts/snapshot/snapshot_manuals_scans_candidate_section.v0.json",
    "contracts/snapshot/snapshot_driver_support_candidate_section.v0.json",
    "contracts/snapshot/snapshot_live_metadata_candidate_section.v0.json",
    "contracts/snapshot/snapshot_live_metadata_review_section.v0.json",
    "contracts/snapshot/snapshot_local_apply_section.v0.json",
    "contracts/snapshot/snapshot_reviewed_metadata_preview_section.v0.json",
    "contracts/snapshot/snapshot_reviewed_source_lead_preview_section.v0.json",
    "contracts/snapshot/snapshot_review_queue_section.v0.json",
    "contracts/snapshot/snapshot_need_absence_section.v0.json",
    "contracts/snapshot/snapshot_seed_batch_summary.v0.json",
    "contracts/snapshot/snapshot_refresh_boundary_report.v0.json",
    "contracts/snapshot/snapshot_public_search_ux_section.v0.json",
    "contracts/snapshot/snapshot_public_route_section.v0.json",
    "contracts/snapshot/snapshot_result_card_section.v0.json",
    "contracts/snapshot/snapshot_no_results_section.v0.json",
    "contracts/snapshot/snapshot_text_projection_section.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/snapshot_refresh_policy.json",
    "control/policies/snapshot_refresh_reviewed_record_policy.json",
    "control/policies/snapshot_refresh_candidate_policy.json",
    "control/policies/snapshot_refresh_manuals_scans_policy.json",
    "control/policies/snapshot_refresh_driver_support_policy.json",
    "control/policies/snapshot_refresh_live_metadata_policy.json",
    "control/policies/snapshot_refresh_live_metadata_review_policy.json",
    "control/policies/snapshot_refresh_review_preview_policy.json",
    "control/policies/snapshot_refresh_local_apply_policy.json",
    "control/policies/snapshot_refresh_reviewed_metadata_policy.json",
    "control/policies/snapshot_refresh_reviewed_source_lead_policy.json",
    "control/policies/snapshot_refresh_need_absence_policy.json",
    "control/policies/snapshot_refresh_relay_policy.json",
    "control/policies/snapshot_refresh_non_claim_policy.json",
    "control/policies/snapshot_refresh_public_search_ux_policy.json",
    "control/policies/snapshot_refresh_public_projection_policy.json",
    "control/policies/snapshot_refresh_result_card_policy.json",
    "control/policies/snapshot_refresh_no_results_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/snapshot_refresh_input_state.json",
    "control/inventory/snapshot_refresh_source_matrix.json",
    "control/inventory/snapshot_refresh_reviewed_record_matrix.json",
    "control/inventory/snapshot_refresh_candidate_matrix.json",
    "control/inventory/snapshot_refresh_need_absence_matrix.json",
    "control/inventory/snapshot_refresh_review_queue_matrix.json",
    "control/inventory/snapshot_refresh_relay_projection_matrix.json",
    "control/inventory/snapshot_refresh_public_alpha_reassess_matrix.json",
    "control/inventory/snapshot_refresh_boundary_report.json",
    "control/inventory/snapshot_refresh_01_input_state.json",
    "control/inventory/snapshot_refresh_01_source_matrix.json",
    "control/inventory/snapshot_refresh_01_reviewed_record_matrix.json",
    "control/inventory/snapshot_refresh_01_candidate_matrix.json",
    "control/inventory/snapshot_refresh_01_live_metadata_candidate_matrix.json",
    "control/inventory/snapshot_refresh_01_need_absence_matrix.json",
    "control/inventory/snapshot_refresh_01_review_queue_matrix.json",
    "control/inventory/snapshot_refresh_01_relay_projection_matrix.json",
    "control/inventory/snapshot_refresh_01_public_search_view_model_matrix.json",
    "control/inventory/snapshot_refresh_01_public_alpha_reassess_matrix.json",
    "control/inventory/snapshot_refresh_01_boundary_report.json",
    "control/inventory/snapshot_refresh_02_input_state.json",
    "control/inventory/snapshot_refresh_02_source_matrix.json",
    "control/inventory/snapshot_refresh_02_reviewed_record_matrix.json",
    "control/inventory/snapshot_refresh_02_candidate_matrix.json",
    "control/inventory/snapshot_refresh_02_live_metadata_candidate_matrix.json",
    "control/inventory/snapshot_refresh_02_live_metadata_review_matrix.json",
    "control/inventory/snapshot_refresh_02_reviewed_preview_matrix.json",
    "control/inventory/snapshot_refresh_02_need_absence_matrix.json",
    "control/inventory/snapshot_refresh_02_review_queue_matrix.json",
    "control/inventory/snapshot_refresh_02_relay_projection_matrix.json",
    "control/inventory/snapshot_refresh_02_public_search_view_model_matrix.json",
    "control/inventory/snapshot_refresh_02_public_alpha_reassess_matrix.json",
    "control/inventory/snapshot_refresh_02_boundary_report.json",
    "control/inventory/snapshot_refresh_03_input_state.json",
    "control/inventory/snapshot_refresh_03_source_matrix.json",
    "control/inventory/snapshot_refresh_03_reviewed_record_matrix.json",
    "control/inventory/snapshot_refresh_03_reviewed_metadata_record_matrix.json",
    "control/inventory/snapshot_refresh_03_reviewed_source_lead_matrix.json",
    "control/inventory/snapshot_refresh_03_candidate_matrix.json",
    "control/inventory/snapshot_refresh_03_live_metadata_candidate_matrix.json",
    "control/inventory/snapshot_refresh_03_live_metadata_review_matrix.json",
    "control/inventory/snapshot_refresh_03_local_apply_matrix.json",
    "control/inventory/snapshot_refresh_03_need_absence_matrix.json",
    "control/inventory/snapshot_refresh_03_review_queue_matrix.json",
    "control/inventory/snapshot_refresh_03_relay_projection_matrix.json",
    "control/inventory/snapshot_refresh_03_public_search_view_model_matrix.json",
    "control/inventory/snapshot_refresh_03_public_alpha_reassess_matrix.json",
    "control/inventory/snapshot_refresh_03_boundary_report.json",
    "control/inventory/snapshot_refresh_03_smoke_result.json",
    "control/inventory/snapshot_refresh_03_validation_matrix.json",
    "control/inventory/snapshot_refresh_03_result.json",
    "control/inventory/snapshot_refresh_03_next_task_decision.json",
    "control/inventory/snapshot_refresh_03_failure_repair_log.json",
    "control/inventory/snapshot_refresh_04_input_state.json",
    "control/inventory/snapshot_refresh_04_source_matrix.json",
    "control/inventory/snapshot_refresh_04_reviewed_record_matrix.json",
    "control/inventory/snapshot_refresh_04_reviewed_metadata_record_matrix.json",
    "control/inventory/snapshot_refresh_04_reviewed_source_lead_matrix.json",
    "control/inventory/snapshot_refresh_04_candidate_matrix.json",
    "control/inventory/snapshot_refresh_04_manuals_scans_candidate_matrix.json",
    "control/inventory/snapshot_refresh_04_driver_support_candidate_matrix.json",
    "control/inventory/snapshot_refresh_04_live_metadata_candidate_matrix.json",
    "control/inventory/snapshot_refresh_04_local_apply_matrix.json",
    "control/inventory/snapshot_refresh_04_need_absence_matrix.json",
    "control/inventory/snapshot_refresh_04_review_queue_matrix.json",
    "control/inventory/snapshot_refresh_04_relay_projection_matrix.json",
    "control/inventory/snapshot_refresh_04_public_search_view_model_matrix.json",
    "control/inventory/snapshot_refresh_04_public_alpha_reassess_matrix.json",
    "control/inventory/snapshot_refresh_04_boundary_report.json",
    "control/inventory/snapshot_refresh_04_smoke_result.json",
    "control/inventory/snapshot_refresh_04_validation_matrix.json",
    "control/inventory/snapshot_refresh_04_result.json",
    "control/inventory/snapshot_refresh_04_next_task_decision.json",
    "control/inventory/snapshot_refresh_04_failure_repair_log.json",
    "control/inventory/snapshot_refresh_05_input_state.json",
    "control/inventory/snapshot_refresh_05_source_matrix.json",
    "control/inventory/snapshot_refresh_05_reviewed_record_matrix.json",
    "control/inventory/snapshot_refresh_05_candidate_matrix.json",
    "control/inventory/snapshot_refresh_05_domain_candidate_matrix.json",
    "control/inventory/snapshot_refresh_05_public_search_ux_matrix.json",
    "control/inventory/snapshot_refresh_05_public_route_matrix.json",
    "control/inventory/snapshot_refresh_05_result_card_matrix.json",
    "control/inventory/snapshot_refresh_05_no_results_matrix.json",
    "control/inventory/snapshot_refresh_05_text_projection_matrix.json",
    "control/inventory/snapshot_refresh_05_relay_projection_matrix.json",
    "control/inventory/snapshot_refresh_05_public_alpha_reassess_matrix.json",
    "control/inventory/snapshot_refresh_05_boundary_report.json",
    "control/inventory/snapshot_refresh_05_smoke_result.json",
    "control/inventory/snapshot_refresh_05_validation_matrix.json",
    "control/inventory/snapshot_refresh_05_result.json",
    "control/inventory/snapshot_refresh_05_next_task_decision.json",
    "control/inventory/snapshot_refresh_05_failure_repair_log.json",
]
REQUIRED_EXAMPLES = [
    "examples/snapshots/refresh/snapshot_refresh_plan.json",
    "examples/snapshots/refresh/reviewed_record_section.json",
    "examples/snapshots/refresh/candidate_section_frontier_media.json",
    "examples/snapshots/refresh/candidate_section_legacy_software.json",
    "examples/snapshots/refresh/review_queue_section.json",
    "examples/snapshots/refresh/need_absence_section.json",
    "examples/snapshots/refresh/seed_batch_summary_section.json",
    "examples/snapshots/refresh/refreshed_relay_projection.json",
    "examples/snapshots/refresh/public_alpha_reassess_input.json",
    "examples/snapshots/refresh/boundary_report.json",
    "examples/snapshots/refresh/live_metadata/snapshot_refresh_plan.json",
    "examples/snapshots/refresh/live_metadata/reviewed_record_section.json",
    "examples/snapshots/refresh/live_metadata/candidate_section_frontier_media.json",
    "examples/snapshots/refresh/live_metadata/candidate_section_legacy_software.json",
    "examples/snapshots/refresh/live_metadata/live_metadata_candidate_section.json",
    "examples/snapshots/refresh/live_metadata/review_queue_section.json",
    "examples/snapshots/refresh/live_metadata/need_absence_section.json",
    "examples/snapshots/refresh/live_metadata/seed_batch_summary_section.json",
    "examples/snapshots/refresh/live_metadata/refreshed_relay_projection.json",
    "examples/snapshots/refresh/live_metadata/public_search_view_model_projection.json",
    "examples/snapshots/refresh/live_metadata/public_alpha_reassess_input.json",
    "examples/snapshots/refresh/live_metadata/boundary_report.json",
    "examples/snapshots/refresh/live_metadata_review/snapshot_refresh_plan.json",
    "examples/snapshots/refresh/live_metadata_review/reviewed_record_section.json",
    "examples/snapshots/refresh/live_metadata_review/candidate_section_frontier_media.json",
    "examples/snapshots/refresh/live_metadata_review/candidate_section_legacy_software.json",
    "examples/snapshots/refresh/live_metadata_review/live_metadata_candidate_section.json",
    "examples/snapshots/refresh/live_metadata_review/live_metadata_review_section.json",
    "examples/snapshots/refresh/live_metadata_review/reviewed_metadata_preview_section.json",
    "examples/snapshots/refresh/live_metadata_review/reviewed_source_lead_preview_section.json",
    "examples/snapshots/refresh/live_metadata_review/review_queue_section.json",
    "examples/snapshots/refresh/live_metadata_review/need_absence_section.json",
    "examples/snapshots/refresh/live_metadata_review/refreshed_relay_projection.json",
    "examples/snapshots/refresh/live_metadata_review/public_search_view_model_projection.json",
    "examples/snapshots/refresh/live_metadata_review/public_alpha_reassess_input.json",
    "examples/snapshots/refresh/live_metadata_review/boundary_report.json",
    "examples/snapshots/refresh/local_apply_live_metadata/snapshot_refresh_plan.json",
    "examples/snapshots/refresh/local_apply_live_metadata/existing_reviewed_record_section.json",
    "examples/snapshots/refresh/local_apply_live_metadata/reviewed_metadata_record_section.json",
    "examples/snapshots/refresh/local_apply_live_metadata/reviewed_source_lead_section.json",
    "examples/snapshots/refresh/local_apply_live_metadata/candidate_section_frontier_media.json",
    "examples/snapshots/refresh/local_apply_live_metadata/candidate_section_legacy_software.json",
    "examples/snapshots/refresh/local_apply_live_metadata/live_metadata_candidate_section.json",
    "examples/snapshots/refresh/local_apply_live_metadata/local_apply_section.json",
    "examples/snapshots/refresh/local_apply_live_metadata/review_queue_section.json",
    "examples/snapshots/refresh/local_apply_live_metadata/need_absence_section.json",
    "examples/snapshots/refresh/local_apply_live_metadata/refreshed_relay_projection.json",
    "examples/snapshots/refresh/local_apply_live_metadata/public_search_view_model_projection.json",
    "examples/snapshots/refresh/local_apply_live_metadata/public_alpha_reassess_input.json",
    "examples/snapshots/refresh/local_apply_live_metadata/boundary_report.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/snapshot_refresh_plan.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/existing_reviewed_record_section.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/reviewed_metadata_record_section.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/reviewed_source_lead_section.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/candidate_section_frontier_media.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/candidate_section_legacy_software.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/candidate_section_manuals_scans.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/candidate_section_driver_support.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/live_metadata_candidate_section.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/review_queue_section.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/need_absence_section.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/refreshed_relay_projection.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/public_search_view_model_projection.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/public_alpha_reassess_input.json",
    "examples/snapshots/refresh/manuals_scans_driver_support/boundary_report.json",
    "examples/relay/refresh/refreshed_relay_projection.json",
    "examples/relay/refresh/live_metadata_refreshed_relay_projection.json",
    "examples/relay/refresh/live_metadata_review_refreshed_relay_projection.json",
    "examples/relay/refresh/local_apply_live_metadata_refreshed_relay_projection.json",
    "examples/relay/refresh/manuals_scans_driver_support_refreshed_relay_projection.json",
    "examples/snapshots/refresh/public_search_ux_mvp/snapshot_refresh_plan.json",
    "examples/snapshots/refresh/public_search_ux_mvp/public_search_ux_section.json",
    "examples/snapshots/refresh/public_search_ux_mvp/public_route_section.json",
    "examples/snapshots/refresh/public_search_ux_mvp/result_card_section.json",
    "examples/snapshots/refresh/public_search_ux_mvp/no_results_section.json",
    "examples/snapshots/refresh/public_search_ux_mvp/text_projection_section.json",
    "examples/snapshots/refresh/public_search_ux_mvp/refreshed_relay_projection.json",
    "examples/snapshots/refresh/public_search_ux_mvp/public_alpha_reassess_input.json",
    "examples/snapshots/refresh/public_search_ux_mvp/boundary_report.json",
    "examples/snapshots/refresh/public_search_ux_mvp/snapshot_refresh_05_result.json",
    "examples/relay/refresh/public_search_ux_mvp_refreshed_relay_projection.json",
    "examples/public_alpha/reassess/snapshot_refresh_reassess_input.json",
    "examples/public_alpha/reassess/live_metadata/snapshot_refresh_01_reassess_input.json",
    "examples/public_alpha/reassess/live_metadata/snapshot_refresh_02_reassess_input.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/snapshot_refresh_03_reassess_input.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/snapshot_refresh_04_reassess_input.json",
    "examples/public_alpha/reassess/public_search_ux_mvp/snapshot_refresh_05_reassess_input.json",
]
REQUIRED_DOCS = [
    "docs/architecture/SNAPSHOT_REFRESH.md",
    "docs/architecture/SNAPSHOT_SEED_BATCH_HANDOFFS.md",
    "docs/architecture/CANDIDATE_SNAPSHOT_SECTION.md",
    "docs/operations/SNAPSHOT_REFRESH_RUNBOOK.md",
    "docs/operations/POST_SNAPSHOT_REFRESH_PLAN.md",
    "docs/reference/SNAPSHOT_REFRESH_PLAN.md",
    "docs/reference/SNAPSHOT_CANDIDATE_SECTION.md",
    "docs/reference/SNAPSHOT_NEED_ABSENCE_SECTION.md",
    "docs/architecture/SNAPSHOT_REFRESH_01.md",
    "docs/architecture/SNAPSHOT_LIVE_METADATA_HANDOFFS.md",
    "docs/architecture/LIVE_METADATA_CANDIDATE_SNAPSHOT_SECTION.md",
    "docs/operations/SNAPSHOT_REFRESH_01_RUNBOOK.md",
    "docs/operations/POST_SNAPSHOT_REFRESH_01_PLAN.md",
    "docs/reference/SNAPSHOT_LIVE_METADATA_SECTION.md",
    "docs/architecture/SNAPSHOT_REFRESH_02.md",
    "docs/architecture/SNAPSHOT_LIVE_METADATA_REVIEW_HANDOFFS.md",
    "docs/architecture/REVIEWED_METADATA_PREVIEW_SNAPSHOT_SECTION.md",
    "docs/architecture/REVIEWED_SOURCE_LEAD_PREVIEW_SNAPSHOT_SECTION.md",
    "docs/operations/SNAPSHOT_REFRESH_02_RUNBOOK.md",
    "docs/operations/POST_SNAPSHOT_REFRESH_02_PLAN.md",
    "docs/reference/SNAPSHOT_LIVE_METADATA_REVIEW_SECTION.md",
    "docs/reference/SNAPSHOT_REVIEWED_METADATA_PREVIEW_SECTION.md",
    "docs/reference/SNAPSHOT_REVIEWED_SOURCE_LEAD_PREVIEW_SECTION.md",
    "docs/architecture/SNAPSHOT_REFRESH_03.md",
    "docs/architecture/SNAPSHOT_LOCAL_APPLY_LIVE_METADATA_HANDOFFS.md",
    "docs/architecture/REVIEWED_METADATA_RECORD_SNAPSHOT_SECTION.md",
    "docs/architecture/REVIEWED_SOURCE_LEAD_SNAPSHOT_SECTION.md",
    "docs/operations/SNAPSHOT_REFRESH_03_RUNBOOK.md",
    "docs/operations/POST_SNAPSHOT_REFRESH_03_PLAN.md",
    "docs/reference/SNAPSHOT_REVIEWED_METADATA_RECORD_SECTION.md",
    "docs/reference/SNAPSHOT_REVIEWED_SOURCE_LEAD_SECTION.md",
    "docs/reference/SNAPSHOT_LOCAL_APPLY_SECTION.md",
    "docs/architecture/SNAPSHOT_REFRESH_04.md",
    "docs/architecture/SNAPSHOT_MANUALS_SCANS_SECTION.md",
    "docs/architecture/SNAPSHOT_DRIVER_SUPPORT_SECTION.md",
    "docs/operations/SNAPSHOT_REFRESH_04_RUNBOOK.md",
    "docs/operations/POST_SNAPSHOT_REFRESH_04_PLAN.md",
    "docs/reference/SNAPSHOT_MANUALS_SCANS_SECTION.md",
    "docs/reference/SNAPSHOT_DRIVER_SUPPORT_SECTION.md",
    "docs/architecture/SNAPSHOT_REFRESH_05.md",
    "docs/architecture/SNAPSHOT_PUBLIC_SEARCH_UX_PROJECTION.md",
    "docs/architecture/SNAPSHOT_RESULT_CARD_PROJECTION.md",
    "docs/operations/SNAPSHOT_REFRESH_05_RUNBOOK.md",
    "docs/operations/POST_SNAPSHOT_REFRESH_05_PLAN.md",
    "docs/reference/SNAPSHOT_PUBLIC_SEARCH_UX_SECTION.md",
    "docs/reference/SNAPSHOT_RESULT_CARD_SECTION.md",
    "docs/reference/SNAPSHOT_NO_RESULTS_SECTION.md",
]
REQUIRED_CLI = [
    "scripts/eureka_snapshot_refresh.py",
    "scripts/eureka_snapshot_refresh_report.py",
]
REQUIRED_TRUE = [
    "snapshot_refresh_is_projection",
    "seed_batch_candidates_remain_candidates",
    "manuals_scans_candidates_are_not_downloaded_documents",
    "manuals_scans_candidates_are_not_ocr_text",
    "manuals_scans_candidates_are_not_rights_cleared",
    "driver_support_candidates_are_not_driver_downloads",
    "driver_support_candidates_are_not_safe_installers",
    "driver_support_candidates_are_not_compatibility_guarantees",
    "public_ux_projection_is_read_only",
    "public_search_ux_does_not_own_search_behavior",
    "no_js_public_search_required",
    "candidate_verified_distinction_required",
    "limited_reviewed_record_distinction_required",
    "no_results_need_projection_required",
    "review_previews_are_not_truth",
    "reviewed_metadata_previews_require_local_apply",
    "reviewed_source_lead_previews_require_local_apply",
    "live_metadata_candidates_remain_candidates_until_applied",
    "local_apply_outputs_may_project_as_limited_reviewed_records",
    "reviewed_metadata_records_are_limited_claims",
    "reviewed_source_leads_are_limited_claims",
    "reviewed_metadata_records_are_not_verified_artifacts",
    "reviewed_source_leads_are_not_verified_artifacts",
    "no_verified_download_claim",
    "no_malware_clean_claim",
    "no_rights_clearance_claim",
    "live_metadata_candidates_remain_candidates",
    "candidates_remain_candidates",
    "seed_outputs_are_not_truth",
    "reviewed_records_only_from_existing_reviewed_sources",
    "no_candidate_auto_acceptance",
    "no_live_metadata_auto_acceptance",
    "no_reviewed_index_mutation",
    "no_master_index_mutation",
    "no_public_index_mutation",
    "no_public_mutation",
    "no_public_live_source_fanout",
    "no_deployment",
    "no_site_dist_write",
    "no_public_launch_claim",
    "no_production_claim",
]
REQUIRED_FALSE = [
    "downloads_enabled",
    "file_fetches_enabled",
    "ocr_enabled",
    "extraction_enabled",
    "install_execution_enabled",
    "model_provider_enabled",
    "raw_live_response_included",
    "verified_download_claim_allowed",
    "malware_clean_claim_allowed",
    "rights_clearance_claim_allowed",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.parse_args(argv)
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate() -> dict[str, Any]:
    checks: dict[str, bool] = {
        "contracts_exist": _paths_exist(REQUIRED_CONTRACTS),
        "policies_exist": _paths_exist(REQUIRED_POLICIES),
        "matrices_exist": _paths_exist(REQUIRED_MATRICES),
        "examples_exist": _paths_exist(REQUIRED_EXAMPLES),
        "docs_exist": _paths_exist(REQUIRED_DOCS),
        "cli_exist": _paths_exist(REQUIRED_CLI),
        "prior_results_present": _prior_results_present(),
        "policies_safe": _policies_safe(),
        "cli_help_works": _cli_help_works(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "snapshot_refresh_validation.v0",
        "task": "SNAPSHOT-REFRESH-00+01+02+03+04+05",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "extraction_executed": False,
        "install_execution_enabled": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "public_launch_performed": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_snapshot_refresh(from_seed_examples=True)
    inventory = build_snapshot_refresh_inventory_packets(result)
    live_result = run_snapshot_refresh_01(from_live_metadata_pilot_examples=True)
    live_inventory = build_snapshot_refresh_01_inventory_packets(live_result)
    review_result = run_snapshot_refresh_02(from_live_metadata_review_examples=True)
    review_inventory = build_snapshot_refresh_02_inventory_packets(review_result)
    local_apply_result = run_snapshot_refresh_03(from_local_apply_live_metadata_examples=True)
    local_apply_inventory = build_snapshot_refresh_03_inventory_packets(local_apply_result)
    manuals_driver_result = run_snapshot_refresh_04(from_manuals_driver_examples=True)
    manuals_driver_inventory = build_snapshot_refresh_04_inventory_packets(manuals_driver_result)
    ux_refresh_result = run_snapshot_refresh_05(from_public_search_ux_examples=True)
    ux_refresh_inventory = build_snapshot_refresh_05_inventory_packets(ux_refresh_result)
    candidate_sections = list(result.get("candidate_sections") or [])
    live_section = live_result["live_metadata_candidate_section"]
    live_cards = live_result["public_search_view_model_projection"]["result_cards"]
    manuals_section = manuals_driver_result["manuals_scans_candidate_section"]
    driver_section = manuals_driver_result["driver_support_candidate_section"]
    manuals_driver_projection = manuals_driver_result["public_search_view_model_projection"]
    manuals_driver_cards = manuals_driver_projection["result_cards"]
    ux_section = ux_refresh_result["public_search_ux_section"]
    route_section = ux_refresh_result["public_route_section"]
    result_card_section = ux_refresh_result["result_card_section"]
    no_results_section = ux_refresh_result["no_results_section"]
    text_projection_section = ux_refresh_result["text_projection_section"]
    ux_cards = result_card_section["cards"]
    boundary = result["boundary_report"]
    return {
        "snapshot_refresh_example_builds": result["fixture_snapshot_refresh_passed"] is True,
        "candidate_sections_exist": len(candidate_sections) == 2,
        "candidate_sections_keep_candidates_review_only": all(
            section.get("accepted_truth") is False
            and section.get("candidate_promoted_to_reviewed") is False
            and all(
                candidate.get("accepted_truth") is False
                and candidate.get("reviewed_record_ref") is None
                for candidate in section.get("candidates", [])
            )
            for section in candidate_sections
        ),
        "review_queue_section_exists": result["review_queue_section"]["candidate_count"] == result["candidate_count"],
        "need_absence_section_exists": result["need_absence_section"]["known_need_count"] > 0,
        "relay_projection_exists": result["refreshed_relay_projection"]["read_only"] is True,
        "public_alpha_reassess_input_exists": result["public_alpha_reassess_input"]["public_launch_readiness_claimed"] is False,
        "inventory_packets_build": {
            "snapshot_refresh_candidate_matrix.json",
            "snapshot_refresh_relay_projection_matrix.json",
        }.issubset(set(inventory)),
        "live_metadata_refresh_example_builds": live_result["fixture_snapshot_refresh_passed"] is True,
        "live_metadata_candidate_section_exists": live_section["candidate_count"] > 0,
        "live_metadata_candidates_review_only": live_section["accepted_truth"] is False
        and live_section["raw_response_included"] is False
        and all(
            candidate.get("accepted_truth") is False
            and candidate.get("reviewed_record_ref") is None
            and candidate.get("raw_response_included") is False
            and candidate.get("public_search_status") == "candidate"
            for candidate in live_section.get("candidates", [])
        ),
        "public_search_view_model_projection_exists": len(live_cards) == live_section["candidate_count"]
        and all(card.get("status") == "candidate" and card.get("accepted_truth") is False for card in live_cards),
        "live_metadata_inventory_packets_build": {
            "snapshot_refresh_01_live_metadata_candidate_matrix.json",
            "snapshot_refresh_01_public_search_view_model_matrix.json",
        }.issubset(set(live_inventory)),
        "no_accepted_truth": result["accepted_truth_created"] is False,
        "no_candidate_promotion": result["candidate_promoted_to_reviewed"] is False,
        "no_index_mutation": all(
            result.get(key) is False
            for key in ("reviewed_index_mutated", "master_index_mutated", "public_index_mutated")
        ),
        "no_site_dist_write": result["site_dist_written"] is False,
        "no_download_extract_model_deploy": all(
            result.get(key) is False
            for key in ("download_performed", "extraction_executed", "model_provider_used", "deployment_performed")
        ),
        "no_readiness_claims": all(
            boundary.get(key) is False
            for key in ("production_readiness_claimed", "public_launch_readiness_claimed")
        ),
        "live_metadata_no_boundaries_crossed": all(
            live_result.get(key) is False
            for key in (
                "accepted_truth_created",
                "candidate_promoted_to_reviewed",
                "live_metadata_candidate_promoted",
                "raw_live_response_included",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_index_mutated",
                "site_dist_written",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
            )
        ),
        "live_metadata_review_refresh_example_builds": review_result["fixture_snapshot_refresh_passed"] is True,
        "live_metadata_review_section_exists": review_result["live_metadata_review_section"]["review_decision_count"] == 8,
        "reviewed_metadata_preview_section_exists": (
            review_result["reviewed_metadata_preview_section"]["preview_count"] == 1
            and review_result["reviewed_metadata_preview_section"]["accepted_truth"] is False
            and review_result["reviewed_metadata_preview_section"]["local_apply_required"] is True
        ),
        "reviewed_source_lead_preview_section_exists": (
            review_result["reviewed_source_lead_preview_section"]["source_lead_preview_count"] == 2
            and review_result["reviewed_source_lead_preview_section"]["accepted_truth"] is False
            and review_result["reviewed_source_lead_preview_section"]["local_apply_required"] is True
        ),
        "preview_counts_match_review_result": (
            review_result["reviewed_metadata_record_preview_count"] == 1
            and review_result["reviewed_source_lead_preview_count"] == 2
            and review_result["useful_lead_count"] == 1
            and review_result["needs_more_evidence_count"] == 2
            and review_result["rejected_or_duplicate_count"] == 2
        ),
        "review_previews_not_claimed_as_artifacts": all(
            preview.get("accepted_truth") is False
            and preview.get("verified_download_claim_created") is False
            and preview.get("malware_clean_claim_created") is False
            and preview.get("rights_clearance_claim_created") is False
            for section in (
                review_result["reviewed_metadata_preview_section"],
                review_result["reviewed_source_lead_preview_section"],
            )
            for preview in section.get("previews", [])
        ),
        "live_metadata_review_public_search_projection_exists": (
            review_result["public_search_view_model_projection"]["read_only"] is True
            and review_result["public_search_view_model_projection"]["status_counts"]["source_lead"] == 3
            and all(
                card.get("status") != "verified"
                for card in review_result["public_search_view_model_projection"].get("result_cards", [])
            )
        ),
        "live_metadata_review_inventory_packets_build": {
            "snapshot_refresh_02_live_metadata_review_matrix.json",
            "snapshot_refresh_02_reviewed_preview_matrix.json",
            "snapshot_refresh_02_public_search_view_model_matrix.json",
        }.issubset(set(review_inventory)),
        "live_metadata_review_no_boundaries_crossed": all(
            review_result.get(key) is False
            for key in (
                "accepted_truth_created",
                "candidate_promoted_to_reviewed",
                "live_metadata_candidate_promoted",
                "review_preview_applied",
                "raw_live_response_included",
                "verified_download_claim_created",
                "malware_clean_claim_created",
                "rights_clearance_claim_created",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_index_mutated",
                "site_dist_written",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
            )
        ),
        "local_apply_refresh_example_builds": local_apply_result["fixture_snapshot_refresh_passed"] is True,
        "local_apply_result_exists": (REPO_ROOT / "control/inventory/local_apply_live_metadata_result.json").exists(),
        "reviewed_metadata_record_section_exists": (
            local_apply_result["reviewed_metadata_record_section"]["reviewed_metadata_record_count"] == 1
            and local_apply_result["reviewed_metadata_record_section"]["artifact_verified"] is False
            and local_apply_result["reviewed_metadata_record_section"]["verified_download_claim"] is False
            and local_apply_result["reviewed_metadata_record_section"]["malware_clean_claim"] is False
            and local_apply_result["reviewed_metadata_record_section"]["rights_clearance_claim"] is False
        ),
        "reviewed_source_lead_section_exists": (
            local_apply_result["reviewed_source_lead_section"]["reviewed_source_lead_count"] == 2
            and local_apply_result["reviewed_source_lead_section"]["artifact_verified"] is False
            and local_apply_result["reviewed_source_lead_section"]["verified_download_claim"] is False
            and local_apply_result["reviewed_source_lead_section"]["malware_clean_claim"] is False
            and local_apply_result["reviewed_source_lead_section"]["rights_clearance_claim"] is False
        ),
        "local_apply_counts_match_result": (
            local_apply_result["existing_reviewed_record_count"] == 1
            and local_apply_result["reviewed_metadata_record_count"] == 1
            and local_apply_result["reviewed_source_lead_count"] == 2
            and local_apply_result["reviewed_record_delta_count"] == 3
            and local_apply_result["total_limited_reviewed_record_projection_count"] == 4
        ),
        "local_apply_records_not_artifact_claims": all(
            record.get("artifact_verified") is False
            and record.get("verified_download_claim") is False
            and record.get("malware_clean_claim") is False
            and record.get("rights_clearance_claim") is False
            for section in (
                local_apply_result["reviewed_metadata_record_section"],
                local_apply_result["reviewed_source_lead_section"],
            )
            for record in section.get("records", [])
        ),
        "local_apply_public_search_projection_exists": (
            local_apply_result["public_search_view_model_projection"]["read_only"] is True
            and local_apply_result["public_search_view_model_projection"]["status_counts"]["source_lead"] == 3
            and all(
                card.get("status") != "verified"
                for card in local_apply_result["public_search_view_model_projection"].get("result_cards", [])
                if card.get("object_type") in {"reviewed_metadata_record_limited", "reviewed_source_lead_limited"}
            )
        ),
        "local_apply_inventory_packets_build": {
            "snapshot_refresh_03_reviewed_metadata_record_matrix.json",
            "snapshot_refresh_03_reviewed_source_lead_matrix.json",
            "snapshot_refresh_03_local_apply_matrix.json",
            "snapshot_refresh_03_public_search_view_model_matrix.json",
        }.issubset(set(local_apply_inventory)),
        "local_apply_refresh_no_boundaries_crossed": all(
            local_apply_result.get(key) is False
            for key in (
                "artifact_verified_claim_created",
                "verified_download_claim_created",
                "malware_clean_claim_created",
                "rights_clearance_claim_created",
                "operator_instance_mutated",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_index_mutated",
                "site_dist_written",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
            )
        ),
        "manuals_driver_refresh_example_builds": manuals_driver_result["fixture_snapshot_refresh_passed"] is True,
        "manuals_scans_candidate_section_exists": (
            manuals_section["candidate_count"] == 16
            and manuals_section["accepted_truth"] is False
            and manuals_section["download_performed"] is False
            and manuals_section["file_fetch_performed"] is False
            and manuals_section["ocr_performed"] is False
            and manuals_section["rights_clearance_claim_created"] is False
            and manuals_section["scan_completeness_claim_created"] is False
            and manuals_section["ocr_quality_claim_created"] is False
        ),
        "driver_support_candidate_section_exists": (
            driver_section["candidate_count"] == 16
            and driver_section["accepted_truth"] is False
            and driver_section["download_performed"] is False
            and driver_section["file_fetch_performed"] is False
            and driver_section["install_execution_enabled"] is False
            and driver_section["malware_clean_claim_created"] is False
            and driver_section["compatibility_guarantee_created"] is False
            and driver_section["rights_clearance_claim_created"] is False
        ),
        "manuals_driver_counts_match_seed_results": (
            manuals_driver_result["existing_reviewed_record_count"] == 1
            and manuals_driver_result["reviewed_metadata_record_count"] == 1
            and manuals_driver_result["reviewed_source_lead_count"] == 2
            and manuals_driver_result["total_limited_reviewed_record_projection_count"] == 4
            and manuals_driver_result["manuals_scans_candidate_count"] == 16
            and manuals_driver_result["driver_support_candidate_count"] == 16
            and manuals_driver_result["additional_seed_candidate_count"] == 32
            and manuals_driver_result["fixture_candidate_count"] == 60
            and manuals_driver_result["live_metadata_candidate_count"] == 8
            and manuals_driver_result["total_candidate_count"] == 68
        ),
        "manuals_driver_candidates_review_only": all(
            section.get("accepted_truth") is False
            and section.get("candidate_promoted_to_reviewed") is False
            and all(
                candidate.get("accepted_truth") is False
                and candidate.get("reviewed_record_ref") is None
                and candidate.get("public_search_status") == "candidate"
                for candidate in section.get("candidates", [])
            )
            for section in manuals_driver_result.get("candidate_sections", [])
        ),
        "manuals_driver_public_search_projection_exists": (
            manuals_driver_projection["read_only"] is True
            and manuals_driver_projection["status_counts"]["candidate"] == 68
            and manuals_driver_projection["manuals_scans_cards_remain_candidates"] is True
            and manuals_driver_projection["driver_support_cards_remain_candidates"] is True
            and all(
                card.get("status") == "candidate"
                and card.get("accepted_truth") is False
                and card.get("artifact_verified") is False
                and card.get("verified_download_claim") is False
                for card in manuals_driver_cards
                if card.get("object_type") in {"manuals_scans_candidate", "driver_support_candidate"}
            )
        ),
        "manuals_driver_inventory_packets_build": {
            "snapshot_refresh_04_manuals_scans_candidate_matrix.json",
            "snapshot_refresh_04_driver_support_candidate_matrix.json",
            "snapshot_refresh_04_public_search_view_model_matrix.json",
            "snapshot_refresh_04_result.json",
        }.issubset(set(manuals_driver_inventory)),
        "manuals_driver_refresh_no_boundaries_crossed": all(
            manuals_driver_result.get(key) is False
            for key in (
                "accepted_truth_created",
                "candidate_promoted_to_reviewed",
                "artifact_verified_claim_created",
                "verified_download_claim_created",
                "malware_clean_claim_created",
                "compatibility_guarantee_created",
                "rights_clearance_claim_created",
                "scan_completeness_claim_created",
                "ocr_quality_claim_created",
                "file_fetch_performed",
                "ocr_performed",
                "install_execution_enabled",
                "operator_instance_mutated",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_index_mutated",
                "site_dist_written",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
                "production_readiness_claimed",
                "public_launch_readiness_claimed",
            )
        ),
        "public_search_ux_refresh_example_builds": ux_refresh_result["fixture_snapshot_refresh_passed"] is True,
        "public_search_ux_section_exists": (
            ux_section["route_count"] == 8
            and ux_section["result_card_count"] == 87
            and ux_section["no_js_required"] is True
            and ux_section["public_read_only"] is True
            and ux_section["mutation_enabled"] is False
            and ux_section["live_source_fanout_enabled"] is False
        ),
        "public_route_section_no_js_read_only": (
            route_section["route_count"] == 8
            and route_section["all_routes_get"] is True
            and route_section["all_routes_no_js"] is True
            and route_section["all_routes_read_only"] is True
        ),
        "public_result_card_projection_exists": (
            result_card_section["result_card_count"] == 87
            and result_card_section["result_card_states_count"] == 8
            and result_card_section["candidate_verified_distinction_passed"] is True
            and result_card_section["limited_reviewed_record_distinction_passed"] is True
            and all(
                card.get("accepted_truth") is False
                and card.get("verified_download_claim") is False
                and card.get("malware_clean_claim") is False
                and card.get("rights_clearance_claim") is False
                for card in ux_cards
                if card.get("status") in {"candidate", "near_miss", "known_need", "absence"}
            )
        ),
        "public_no_results_projection_exists": (
            no_results_section["no_results_sections_count"] == 1
            and no_results_section["known_need_projection_visible"] is True
            and no_results_section["public_mutation_enabled"] is False
            and no_results_section["live_source_fanout_enabled"] is False
        ),
        "public_text_projection_exists": (
            text_projection_section["text_projection_available"] is True
            and text_projection_section["classic_html_examples_available"] is True
            and text_projection_section["public_read_only"] is True
        ),
        "public_search_ux_counts_match_prior_snapshot": (
            ux_refresh_result["total_limited_reviewed_record_projection_count"] == 4
            and ux_refresh_result["total_candidate_count"] == 68
            and ux_refresh_result["public_ux_routes_count"] == 8
            and ux_refresh_result["result_card_states_count"] == 8
        ),
        "public_search_ux_inventory_packets_build": {
            "snapshot_refresh_05_public_search_ux_matrix.json",
            "snapshot_refresh_05_public_route_matrix.json",
            "snapshot_refresh_05_result_card_matrix.json",
            "snapshot_refresh_05_no_results_matrix.json",
            "snapshot_refresh_05_text_projection_matrix.json",
            "snapshot_refresh_05_result.json",
        }.issubset(set(ux_refresh_inventory)),
        "public_search_ux_refresh_no_boundaries_crossed": all(
            ux_refresh_result.get(key) is False
            for key in (
                "accepted_truth_created",
                "candidate_promoted_to_reviewed",
                "artifact_verified_claim_created",
                "verified_download_claim_created",
                "malware_clean_claim_created",
                "compatibility_guarantee_created",
                "rights_clearance_claim_created",
                "scan_completeness_claim_created",
                "ocr_quality_claim_created",
                "file_fetch_performed",
                "ocr_performed",
                "install_execution_enabled",
                "operator_instance_mutated",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_index_mutated",
                "site_dist_written",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
                "public_launch_performed",
                "production_readiness_claimed",
                "public_launch_readiness_claimed",
                "public_mutation_enabled",
                "public_live_source_fanout_enabled",
            )
        ),
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    required = [
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/seed_batch_manuals_scans_result.json",
        "control/inventory/seed_batch_driver_support_result.json",
        "control/inventory/live_metadata_pilot_result.json",
        "control/inventory/live_metadata_review_result.json",
        "control/inventory/local_apply_live_metadata_result.json",
        "control/inventory/snapshot_refresh_03_result.json",
        "control/inventory/snapshot_refresh_04_result.json",
        "control/inventory/review_batch_result.json",
        "control/inventory/scout_runtime_result.json",
        "control/inventory/candidate_index_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
        "control/inventory/snapshot_relay_result.json",
        "control/inventory/public_search_ux_model_result.json",
        "control/inventory/public_search_ux_mvp_result.json",
        "control/inventory/public_alpha_readonly_00_result.json",
        "control/inventory/public_alpha_launch_defer_result.json",
    ]
    if not _paths_exist(required):
        return False
    for path in required:
        payload = _load_json(path)
        if payload.get("status") not in {"pass", "pass_with_warnings", "deferred", "validated"}:
            return False
    for path in (
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/seed_batch_manuals_scans_result.json",
        "control/inventory/seed_batch_driver_support_result.json",
        "control/inventory/live_metadata_pilot_result.json",
    ):
        payload = _load_json(path)
        if any(
            payload.get(key) is not False
            for key in ("accepted_truth_created", "reviewed_index_mutated", "master_index_mutated", "public_index_mutated")
        ):
            return False
        if path.endswith("seed_batch_manuals_scans_result.json") and any(
            payload.get(key) is not False
            for key in (
                "download_performed",
                "file_fetch_performed",
                "ocr_performed",
                "rights_clearance_claim_created",
                "scan_completeness_claim_created",
                "ocr_quality_claim_created",
            )
        ):
            return False
        if path.endswith("seed_batch_driver_support_result.json") and any(
            payload.get(key) is not False
            for key in (
                "download_performed",
                "file_fetch_performed",
                "install_execution_enabled",
                "malware_clean_claim_created",
                "compatibility_guarantee_created",
                "rights_clearance_claim_created",
            )
        ):
            return False
    return True


def _policies_safe() -> bool:
    if not _paths_exist(REQUIRED_POLICIES):
        return False
    for path in REQUIRED_POLICIES:
        payload = _load_json(path)
        if any(payload.get(key) is not True for key in REQUIRED_TRUE if key in payload):
            return False
        if any(payload.get(key) is not False for key in REQUIRED_FALSE if key in payload):
            return False
    return True


def _cli_help_works() -> bool:
    for script in REQUIRED_CLI:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / script), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
