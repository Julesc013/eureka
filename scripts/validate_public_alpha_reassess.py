#!/usr/bin/env python3
"""Validate public alpha reassessment packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.public_alpha import (  # noqa: E402
    build_public_alpha_reassess_01_inventory_packets,
    build_public_alpha_reassess_02_inventory_packets,
    build_public_alpha_reassess_03_inventory_packets,
    build_public_alpha_reassess_04_inventory_packets,
    build_public_alpha_reassess_inventory_packets,
    run_public_alpha_reassess,
    run_public_alpha_reassess_01,
    run_public_alpha_reassess_02,
    run_public_alpha_reassess_03,
    run_public_alpha_reassess_04,
    smoke_public_alpha_routes_from_examples,
)


REQUIRED_CONTRACTS = [
    "contracts/publication/public_alpha_reassess.v0.json",
    "contracts/publication/public_alpha_usefulness_metrics.v0.json",
    "contracts/publication/public_alpha_reassess_decision.v0.json",
    "contracts/publication/public_alpha_launch_blocker.v0.json",
    "contracts/publication/public_alpha_next_work_recommendation.v0.json",
    "contracts/publication/public_alpha_live_metadata_reassess.v0.json",
    "contracts/publication/public_alpha_review_preview_reassess.v0.json",
    "contracts/publication/public_alpha_limited_reviewed_record_reassess.v0.json",
    "contracts/publication/public_alpha_domain_coverage_reassess.v0.json",
    "contracts/publication/public_alpha_ux_readiness_reassess.v0.json",
    "contracts/publication/public_alpha_reassess_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/public_alpha_reassess_policy.json",
    "control/policies/public_alpha_reassess_threshold_policy.json",
    "control/policies/public_alpha_reassess_route_smoke_policy.json",
    "control/policies/public_alpha_reassess_live_metadata_policy.json",
    "control/policies/public_alpha_reassess_review_preview_policy.json",
    "control/policies/public_alpha_reassess_limited_reviewed_record_policy.json",
    "control/policies/public_alpha_reassess_domain_coverage_policy.json",
    "control/policies/public_alpha_reassess_ux_policy.json",
    "control/policies/public_alpha_reassess_non_claim_policy.json",
    "control/policies/public_alpha_reassess_next_work_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/public_alpha_reassess_input_state.json",
    "control/inventory/public_alpha_reassess_snapshot_metrics.json",
    "control/inventory/public_alpha_reassess_query_coverage_matrix.json",
    "control/inventory/public_alpha_reassess_route_matrix.json",
    "control/inventory/public_alpha_reassess_candidate_usefulness_matrix.json",
    "control/inventory/public_alpha_reassess_reviewed_record_matrix.json",
    "control/inventory/public_alpha_reassess_need_absence_matrix.json",
    "control/inventory/public_alpha_reassess_launch_blocker_matrix.json",
    "control/inventory/public_alpha_reassess_next_work_matrix.json",
    "control/inventory/public_alpha_reassess_boundary_report.json",
    "control/inventory/public_alpha_reassess_smoke_result.json",
    "control/inventory/public_alpha_reassess_validation_matrix.json",
    "control/inventory/public_alpha_reassess_result.json",
    "control/inventory/public_alpha_reassess_next_task_decision.json",
    "control/inventory/public_alpha_reassess_failure_repair_log.json",
    "control/inventory/public_alpha_reassess_01_input_state.json",
    "control/inventory/public_alpha_reassess_01_snapshot_metrics.json",
    "control/inventory/public_alpha_reassess_01_query_coverage_matrix.json",
    "control/inventory/public_alpha_reassess_01_route_matrix.json",
    "control/inventory/public_alpha_reassess_01_candidate_usefulness_matrix.json",
    "control/inventory/public_alpha_reassess_01_live_metadata_candidate_matrix.json",
    "control/inventory/public_alpha_reassess_01_reviewed_record_matrix.json",
    "control/inventory/public_alpha_reassess_01_need_absence_matrix.json",
    "control/inventory/public_alpha_reassess_01_public_search_view_model_matrix.json",
    "control/inventory/public_alpha_reassess_01_launch_blocker_matrix.json",
    "control/inventory/public_alpha_reassess_01_next_work_matrix.json",
    "control/inventory/public_alpha_reassess_01_boundary_report.json",
    "control/inventory/public_alpha_reassess_01_smoke_result.json",
    "control/inventory/public_alpha_reassess_01_validation_matrix.json",
    "control/inventory/public_alpha_reassess_01_result.json",
    "control/inventory/public_alpha_reassess_01_next_task_decision.json",
    "control/inventory/public_alpha_reassess_01_failure_repair_log.json",
    "control/inventory/public_alpha_reassess_02_input_state.json",
    "control/inventory/public_alpha_reassess_02_snapshot_metrics.json",
    "control/inventory/public_alpha_reassess_02_query_coverage_matrix.json",
    "control/inventory/public_alpha_reassess_02_route_matrix.json",
    "control/inventory/public_alpha_reassess_02_candidate_usefulness_matrix.json",
    "control/inventory/public_alpha_reassess_02_live_metadata_candidate_matrix.json",
    "control/inventory/public_alpha_reassess_02_review_preview_matrix.json",
    "control/inventory/public_alpha_reassess_02_reviewed_record_matrix.json",
    "control/inventory/public_alpha_reassess_02_need_absence_matrix.json",
    "control/inventory/public_alpha_reassess_02_public_search_view_model_matrix.json",
    "control/inventory/public_alpha_reassess_02_launch_blocker_matrix.json",
    "control/inventory/public_alpha_reassess_02_next_work_matrix.json",
    "control/inventory/public_alpha_reassess_02_boundary_report.json",
    "control/inventory/public_alpha_reassess_02_smoke_result.json",
    "control/inventory/public_alpha_reassess_02_validation_matrix.json",
    "control/inventory/public_alpha_reassess_02_result.json",
    "control/inventory/public_alpha_reassess_02_next_task_decision.json",
    "control/inventory/public_alpha_reassess_02_failure_repair_log.json",
    "control/inventory/public_alpha_reassess_03_input_state.json",
    "control/inventory/public_alpha_reassess_03_snapshot_metrics.json",
    "control/inventory/public_alpha_reassess_03_query_coverage_matrix.json",
    "control/inventory/public_alpha_reassess_03_route_matrix.json",
    "control/inventory/public_alpha_reassess_03_candidate_usefulness_matrix.json",
    "control/inventory/public_alpha_reassess_03_limited_reviewed_record_matrix.json",
    "control/inventory/public_alpha_reassess_03_reviewed_record_matrix.json",
    "control/inventory/public_alpha_reassess_03_need_absence_matrix.json",
    "control/inventory/public_alpha_reassess_03_public_search_view_model_matrix.json",
    "control/inventory/public_alpha_reassess_03_launch_blocker_matrix.json",
    "control/inventory/public_alpha_reassess_03_next_work_matrix.json",
    "control/inventory/public_alpha_reassess_03_boundary_report.json",
    "control/inventory/public_alpha_reassess_03_smoke_result.json",
    "control/inventory/public_alpha_reassess_03_validation_matrix.json",
    "control/inventory/public_alpha_reassess_03_result.json",
    "control/inventory/public_alpha_reassess_03_next_task_decision.json",
    "control/inventory/public_alpha_reassess_03_failure_repair_log.json",
    "control/inventory/public_alpha_reassess_04_input_state.json",
    "control/inventory/public_alpha_reassess_04_snapshot_metrics.json",
    "control/inventory/public_alpha_reassess_04_query_coverage_matrix.json",
    "control/inventory/public_alpha_reassess_04_route_matrix.json",
    "control/inventory/public_alpha_reassess_04_domain_coverage_matrix.json",
    "control/inventory/public_alpha_reassess_04_candidate_usefulness_matrix.json",
    "control/inventory/public_alpha_reassess_04_limited_reviewed_record_matrix.json",
    "control/inventory/public_alpha_reassess_04_reviewed_record_matrix.json",
    "control/inventory/public_alpha_reassess_04_need_absence_matrix.json",
    "control/inventory/public_alpha_reassess_04_public_search_view_model_matrix.json",
    "control/inventory/public_alpha_reassess_04_ux_readiness_matrix.json",
    "control/inventory/public_alpha_reassess_04_launch_blocker_matrix.json",
    "control/inventory/public_alpha_reassess_04_next_work_matrix.json",
    "control/inventory/public_alpha_reassess_04_boundary_report.json",
    "control/inventory/public_alpha_reassess_04_smoke_result.json",
    "control/inventory/public_alpha_reassess_04_validation_matrix.json",
    "control/inventory/public_alpha_reassess_04_result.json",
    "control/inventory/public_alpha_reassess_04_next_task_decision.json",
    "control/inventory/public_alpha_reassess_04_failure_repair_log.json",
]
REQUIRED_EXAMPLES = [
    "examples/public_alpha/reassess/public_alpha_reassess_metrics.json",
    "examples/public_alpha/reassess/public_alpha_route_smoke.json",
    "examples/public_alpha/reassess/public_alpha_launch_blockers.json",
    "examples/public_alpha/reassess/public_alpha_next_work.json",
    "examples/public_alpha/reassess/public_alpha_reassess_decision.json",
    "examples/public_alpha/reassess/public_alpha_boundary_report.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_reassess_metrics.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_route_smoke.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_query_coverage.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_candidate_usefulness.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_live_metadata_candidates.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_public_search_view_models.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_launch_blockers.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_next_work.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_reassess_decision.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_boundary_report.json",
    "examples/public_alpha/reassess/live_metadata/public_alpha_reassess_01_result.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_reassess_metrics.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_route_smoke.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_query_coverage.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_candidate_usefulness.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_live_metadata_candidates.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_review_previews.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_public_search_view_models.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_launch_blockers.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_next_work.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_reassess_decision.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_boundary_report.json",
    "examples/public_alpha/reassess/live_metadata_review/public_alpha_reassess_02_result.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_reassess_metrics.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_route_smoke.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_query_coverage.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_candidate_usefulness.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_limited_reviewed_records.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_public_search_view_models.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_launch_blockers.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_next_work.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_reassess_decision.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_boundary_report.json",
    "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_reassess_03_result.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_reassess_metrics.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_route_smoke.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_query_coverage.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_domain_coverage.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_candidate_usefulness.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_limited_reviewed_records.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_public_search_view_models.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_ux_readiness.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_launch_blockers.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_next_work.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_reassess_decision.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_boundary_report.json",
    "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_reassess_04_result.json",
]
REQUIRED_DOCS = [
    "docs/architecture/PUBLIC_ALPHA_REASSESS.md",
    "docs/architecture/PUBLIC_ALPHA_REASSESS_01.md",
    "docs/architecture/PUBLIC_ALPHA_REASSESS_02.md",
    "docs/architecture/PUBLIC_ALPHA_REASSESS_03.md",
    "docs/architecture/PUBLIC_ALPHA_REASSESS_04.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_01_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_02_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_03_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_04_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_PLAN.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_01_PLAN.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_02_PLAN.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_03_PLAN.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_04_PLAN.md",
    "docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md",
    "docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md",
    "docs/reference/PUBLIC_ALPHA_LIVE_METADATA_REASSESSMENT.md",
    "docs/reference/PUBLIC_ALPHA_REVIEW_PREVIEW_REASSESSMENT.md",
    "docs/reference/PUBLIC_ALPHA_LIMITED_REVIEWED_RECORD_REASSESSMENT.md",
    "docs/reference/PUBLIC_ALPHA_DOMAIN_COVERAGE_REASSESSMENT.md",
    "docs/reference/PUBLIC_ALPHA_UX_READINESS_REASSESSMENT.md",
]
REQUIRED_CLI = [
    "scripts/eureka_public_alpha_reassess.py",
    "scripts/eureka_public_alpha_reassess_report.py",
    "scripts/eureka_public_alpha_route_smoke.py",
]
REQUIRED_TRUE = [
    "reassessment_is_not_launch",
    "reassessment_must_not_deploy",
    "launch_requires_explicit_future_manual_approval",
    "review_previews_do_not_count_as_reviewed_records",
    "review_previews_improve_readiness_but_require_local_apply",
    "live_metadata_candidates_improve_discovery_but_are_not_reviewed_truth",
    "candidate_only_snapshot_not_enough_for_launch",
    "preview_only_snapshot_not_enough_for_launch",
    "limited_reviewed_metadata_records_count_for_usefulness_but_not_artifact_verification",
    "reviewed_source_leads_count_for_usefulness_but_not_artifact_verification",
    "four_limited_reviewed_records_not_enough_for_launch",
    "public_alpha_min_ux_mvp_required",
    "public_search_view_models_are_not_full_public_ux",
    "public_search_ux_mvp_required_before_launch",
    "needs_and_absences_are_useful_but_not_launch_sufficient",
]
REQUIRED_FALSE = [
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "downloads_enabled",
    "file_fetches_enabled",
    "ocr_enabled",
    "extraction_enabled",
    "install_execution_enabled",
    "model_provider_enabled",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
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
        "live_metadata_metrics_included": _live_metadata_metrics_included(),
        "review_preview_metrics_included": _review_preview_metrics_included(),
        "limited_reviewed_record_metrics_included": _limited_reviewed_record_metrics_included(),
        "manuals_driver_metrics_included": _manuals_driver_metrics_included(),
        "public_search_view_model_examples_exist": _paths_exist(
            [
                "examples/public_alpha/reassess/live_metadata/public_alpha_public_search_view_models.json",
                "examples/public_alpha/reassess/live_metadata_review/public_alpha_public_search_view_models.json",
                "examples/public_alpha/reassess/local_apply_live_metadata/public_alpha_public_search_view_models.json",
                "examples/public_alpha/reassess/manuals_scans_driver_support/public_alpha_public_search_view_models.json",
                "examples/view_models/public_search/search_page_view_model.json",
            ]
        ),
    }
    checks.update(_runtime_checks())
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "public_alpha_reassess_validation.v0",
        "task": "PUBLIC-ALPHA-REASSESS-00+01+02+03+04",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_public_alpha_reassess(from_snapshot_refresh_examples=True)
    result_01 = run_public_alpha_reassess_01(from_live_metadata_refresh_examples=True)
    result_02 = run_public_alpha_reassess_02(from_live_metadata_review_refresh_examples=True)
    result_03 = run_public_alpha_reassess_03(from_local_apply_live_metadata_refresh_examples=True)
    result_04 = run_public_alpha_reassess_04(from_manuals_driver_snapshot_examples=True)
    route_smoke = smoke_public_alpha_routes_from_examples()
    inventory = build_public_alpha_reassess_inventory_packets(result)
    inventory_01 = build_public_alpha_reassess_01_inventory_packets(result_01)
    inventory_02 = build_public_alpha_reassess_02_inventory_packets(result_02)
    inventory_03 = build_public_alpha_reassess_03_inventory_packets(result_03)
    inventory_04 = build_public_alpha_reassess_04_inventory_packets(result_04)
    return {
        "reassessment_example_builds": result["status"] == "pass",
        "live_metadata_reassessment_example_builds": result_01["status"] == "pass",
        "review_preview_reassessment_example_builds": result_02["status"] == "pass",
        "limited_reviewed_record_reassessment_example_builds": result_03["status"] == "pass",
        "manuals_driver_reassessment_example_builds": result_04["status"] == "pass",
        "route_smoke_example_builds": route_smoke["route_smoke_status"] == "pass",
        "decision_exists": result["decision"]["decision"] == "remain_deferred",
        "live_metadata_decision_exists": result_01["decision"]["decision"] == "remain_deferred",
        "review_preview_decision_exists": result_02["decision"]["decision"] == "remain_deferred",
        "limited_reviewed_record_decision_exists": result_03["decision"]["decision"] == "remain_deferred",
        "manuals_driver_decision_exists": result_04["decision"]["decision"] == "remain_deferred",
        "current_evidence_counts_recorded": (
            result["reviewed_record_count"] == 1
            and result["candidate_count"] == 28
            and result["known_need_count"] == 28
            and result["absence_summary_count"] == 2
        ),
        "live_metadata_evidence_counts_recorded": (
            result_01["reviewed_record_count"] == 1
            and result_01["fixture_candidate_count"] == 28
            and result_01["live_metadata_candidate_count"] == 8
            and result_01["total_candidate_count"] == 36
            and result_01["known_need_count"] == 28
            and result_01["absence_summary_count"] == 2
        ),
        "review_preview_evidence_counts_recorded": (
            result_02["reviewed_record_count"] == 1
            and result_02["fixture_candidate_count"] == 28
            and result_02["live_metadata_candidate_count"] == 8
            and result_02["total_candidate_count"] == 36
            and result_02["reviewed_metadata_record_preview_count"] == 1
            and result_02["reviewed_source_lead_preview_count"] == 2
            and result_02["useful_lead_count"] == 1
            and result_02["needs_more_evidence_count"] == 2
            and result_02["rejected_or_duplicate_count"] == 2
            and result_02["known_need_count"] == 28
            and result_02["absence_summary_count"] == 2
        ),
        "limited_reviewed_record_evidence_counts_recorded": (
            result_03["existing_reviewed_record_count"] == 1
            and result_03["reviewed_metadata_record_count"] == 1
            and result_03["reviewed_source_lead_count"] == 2
            and result_03["reviewed_record_delta_count"] == 3
            and result_03["total_limited_reviewed_record_projection_count"] == 4
            and result_03["fixture_candidate_count"] == 28
            and result_03["live_metadata_candidate_count"] == 8
            and result_03["total_candidate_count"] == 36
            and result_03["known_need_count"] == 28
            and result_03["absence_summary_count"] == 2
        ),
        "manuals_driver_evidence_counts_recorded": (
            result_04["existing_reviewed_record_count"] == 1
            and result_04["reviewed_metadata_record_count"] == 1
            and result_04["reviewed_source_lead_count"] == 2
            and result_04["total_limited_reviewed_record_projection_count"] == 4
            and result_04["candidate_count"] == 68
            and result_04["manuals_scans_candidate_count"] == 16
            and result_04["driver_support_candidate_count"] == 16
            and result_04["domain_count"] == 4
        ),
        "launch_false_when_thresholds_unmet": result["launch_recommended"] is False,
        "live_metadata_launch_false_when_thresholds_unmet": result_01["launch_recommended"] is False,
        "review_preview_launch_false_when_thresholds_unmet": result_02["launch_recommended"] is False,
        "limited_reviewed_record_launch_false_when_thresholds_unmet": result_03["launch_recommended"] is False,
        "manuals_driver_launch_false_when_thresholds_unmet": result_04["launch_recommended"] is False,
        "demo_mode_recommended": result["demo_mode_recommended"] is True,
        "live_metadata_demo_mode_recommended": result_01["demo_mode_recommended"] is True,
        "review_preview_demo_mode_recommended": result_02["demo_mode_recommended"] is True,
        "limited_reviewed_record_demo_mode_recommended": result_03["demo_mode_recommended"] is True,
        "manuals_driver_demo_mode_recommended": result_04["demo_mode_recommended"] is True,
        "internal_review_recommended": result_01["internal_review_recommended"] is True,
        "review_preview_internal_review_recommended": result_02["internal_review_recommended"] is True,
        "limited_reviewed_record_internal_review_recommended": result_03["internal_review_recommended"] is True,
        "manuals_driver_internal_review_recommended": result_04["internal_review_recommended"] is True,
        "needs_live_candidate_review": result_01["needs_live_candidate_review"] is True,
        "needs_snapshot_refresh_after_review": result_01["needs_snapshot_refresh_after_review"] is True,
        "needs_local_apply_of_review_previews": result_02["needs_local_apply_of_review_previews"] is True,
        "needs_snapshot_refresh_after_apply": result_02["needs_snapshot_refresh_after_apply"] is True,
        "needs_public_alpha_reassess_after_apply": result_02["needs_public_alpha_reassess_after_apply"] is True,
        "needs_more_domains": result_03["needs_more_domains"] is True,
        "needs_seed_batch_manuals_scans": result_03["needs_seed_batch_manuals_scans"] is True,
        "needs_seed_batch_driver_support": result_03["needs_seed_batch_driver_support"] is True,
        "needs_public_search_ux_mvp": result_04["needs_public_search_ux_mvp"] is True,
        "needs_snapshot_refresh_after_ux": result_04["needs_snapshot_refresh_after_ux"] is True,
        "needs_public_alpha_reassess_after_ux": result_04["needs_public_alpha_reassess_after_ux"] is True,
        "needs_review_batch_apply_next": result_04["needs_review_batch_apply_next"] is True,
        "live_metadata_candidates_not_counted_as_reviewed": (
            result_01["live_metadata_candidate_usefulness"]["review_only_candidate_count"] == 8
            and result_01["candidate_usefulness"]["live_metadata_candidates_counted_as_reviewed"] is False
            and result_01["metrics"]["reviewed_record_count"] == 1
        ),
        "review_previews_not_counted_as_reviewed": (
            result_02["review_preview_usefulness"]["review_previews_counted_as_reviewed_records"] is False
            and result_02["metrics"]["reviewed_record_count"] == 1
            and result_02["metrics"]["review_preview_count"] == 3
        ),
        "limited_reviewed_records_not_verified_artifacts": (
            result_03["limited_reviewed_record_usefulness"]["limited_reviewed_records_are_verified_artifacts"] is False
            and result_03["limited_reviewed_record_usefulness"]["artifact_verified"] is False
            and result_03["limited_reviewed_record_usefulness"]["verified_download_claim"] is False
            and result_03["limited_reviewed_record_usefulness"]["malware_clean_claim"] is False
            and result_03["limited_reviewed_record_usefulness"]["rights_clearance_claim"] is False
            and result_03["metrics"]["total_limited_reviewed_record_projection_count"] == 4
        ),
        "manuals_driver_limited_reviewed_records_not_verified_artifacts": (
            result_04["limited_reviewed_record_usefulness"]["limited_reviewed_records_are_verified_artifacts"] is False
            and result_04["limited_reviewed_record_usefulness"]["artifact_verified"] is False
            and result_04["limited_reviewed_record_usefulness"]["verified_download_claim"] is False
            and result_04["limited_reviewed_record_usefulness"]["malware_clean_claim"] is False
            and result_04["limited_reviewed_record_usefulness"]["rights_clearance_claim"] is False
        ),
        "manuals_driver_domain_coverage_metrics_included": (
            result_04["domain_coverage"]["four_domains_represented"] is True
            and result_04["domain_coverage"]["domain_count"] == 4
            and result_04["domain_coverage"]["domain_coverage_launch_sufficient"] is False
        ),
        "manuals_driver_ux_readiness_metrics_included": (
            result_04["ux_readiness"]["public_search_ux_mvp_implemented"] is False
            and result_04["ux_readiness"]["public_search_view_models_are_not_full_public_ux"] is True
            and result_04["ux_readiness"]["needs_public_search_ux_mvp"] is True
        ),
        "public_search_view_models_assessed": (
            result_01["public_search_view_models"]["public_search_view_models_available"] is True
            and result_01["public_search_view_models"]["live_metadata_candidate_status"] == "candidate"
            and result_01["public_search_view_models"]["required_states_available"] is True
        ),
        "review_preview_public_search_view_models_assessed": (
            result_02["public_search_view_models"]["public_search_view_models_available"] is True
            and result_02["public_search_view_models"]["required_states_available"] is True
            and result_02["public_search_view_models"]["preview_related_cards_available"] is True
            and result_02["public_search_view_models"]["review_previews_visible_as_source_leads"] is True
        ),
        "limited_reviewed_record_public_search_view_models_assessed": (
            result_03["public_search_view_models"]["public_search_view_models_available"] is True
            and result_03["public_search_view_models"]["required_states_available"] is True
            and result_03["public_search_view_models"]["limited_reviewed_records_visible"] is True
            and result_03["public_search_view_models"]["limited_records_distinct_from_verified_artifacts"] is True
        ),
        "manuals_driver_public_search_view_models_assessed": (
            result_04["public_search_view_models"]["public_search_view_models_available"] is True
            and result_04["public_search_view_models"]["required_states_available"] is True
            and result_04["public_search_view_models"]["manuals_scans_candidate_cards"] == 16
            and result_04["public_search_view_models"]["driver_support_candidate_cards"] == 16
            and result_04["public_search_view_models"]["public_search_view_models_are_not_full_public_ux"] is True
        ),
        "inventory_packets_build": {
            "public_alpha_reassess_result.json",
            "public_alpha_reassess_boundary_report.json",
            "public_alpha_reassess_launch_blocker_matrix.json",
        }.issubset(set(inventory)),
        "live_metadata_inventory_packets_build": {
            "public_alpha_reassess_01_result.json",
            "public_alpha_reassess_01_boundary_report.json",
            "public_alpha_reassess_01_live_metadata_candidate_matrix.json",
            "public_alpha_reassess_01_public_search_view_model_matrix.json",
        }.issubset(set(inventory_01)),
        "review_preview_inventory_packets_build": {
            "public_alpha_reassess_02_result.json",
            "public_alpha_reassess_02_boundary_report.json",
            "public_alpha_reassess_02_review_preview_matrix.json",
            "public_alpha_reassess_02_public_search_view_model_matrix.json",
        }.issubset(set(inventory_02)),
        "limited_reviewed_record_inventory_packets_build": {
            "public_alpha_reassess_03_result.json",
            "public_alpha_reassess_03_boundary_report.json",
            "public_alpha_reassess_03_limited_reviewed_record_matrix.json",
            "public_alpha_reassess_03_public_search_view_model_matrix.json",
        }.issubset(set(inventory_03)),
        "manuals_driver_inventory_packets_build": {
            "public_alpha_reassess_04_result.json",
            "public_alpha_reassess_04_domain_coverage_matrix.json",
            "public_alpha_reassess_04_ux_readiness_matrix.json",
            "public_alpha_reassess_04_public_search_view_model_matrix.json",
        }.issubset(set(inventory_04)),
        "no_deployment_or_launch": all(
            result.get(key) is False for key in ("deployment_performed", "public_launch_performed")
        )
        and all(result_01.get(key) is False for key in ("deployment_performed", "public_launch_performed"))
        and all(result_02.get(key) is False for key in ("deployment_performed", "public_launch_performed"))
        and all(result_03.get(key) is False for key in ("deployment_performed", "public_launch_performed")),
        "manuals_driver_no_deployment_or_launch": all(
            result_04.get(key) is False for key in ("deployment_performed", "public_launch_performed")
        ),
        "no_readiness_claims": all(
            result.get(key) is False
            for key in ("production_readiness_claimed", "public_launch_readiness_claimed")
        )
        and all(
            result_01.get(key) is False
            for key in ("production_readiness_claimed", "public_launch_readiness_claimed")
        )
        and all(
            result_02.get(key) is False
            for key in ("production_readiness_claimed", "public_launch_readiness_claimed")
        )
        and all(
            result_03.get(key) is False
            for key in ("production_readiness_claimed", "public_launch_readiness_claimed")
        ),
        "manuals_driver_no_readiness_claims": all(
            result_04.get(key) is False
            for key in ("production_readiness_claimed", "public_launch_readiness_claimed")
        ),
        "no_mutation_or_site_dist": all(
            result.get(key) is False
            for key in ("site_dist_written", "public_mutation_enabled", "public_live_source_fanout_enabled")
        )
        and all(
            result_01.get(key) is False
            for key in ("site_dist_written", "public_mutation_enabled", "public_live_source_fanout_enabled")
        )
        and all(
            result_02.get(key) is False
            for key in ("site_dist_written", "public_mutation_enabled", "public_live_source_fanout_enabled")
        )
        and all(
            result_03.get(key) is False
            for key in ("site_dist_written", "public_mutation_enabled", "public_live_source_fanout_enabled")
        ),
        "manuals_driver_no_mutation_or_site_dist": all(
            result_04.get(key) is False
            for key in ("site_dist_written", "public_mutation_enabled", "public_live_source_fanout_enabled")
        ),
        "no_download_extract_model": all(
            result.get(key) is False
            for key in ("download_performed", "extraction_executed", "model_provider_used")
        )
        and all(
            result_01.get(key) is False
            for key in ("download_performed", "extraction_executed", "model_provider_used")
        )
        and all(
            result_02.get(key) is False
            for key in ("download_performed", "extraction_executed", "model_provider_used")
        )
        and all(
            result_03.get(key) is False
            for key in ("download_performed", "extraction_executed", "model_provider_used")
        ),
        "manuals_driver_no_download_fetch_ocr_extract_model": all(
            result_04.get(key) is False
            for key in (
                "download_performed",
                "file_fetch_performed",
                "ocr_performed",
                "extraction_executed",
                "install_execution_enabled",
                "model_provider_used",
            )
        ),
        "no_live_source_calls": (
            result_01.get("live_source_call_performed") is False
            and result_02.get("live_source_call_performed") is False
            and result_03.get("live_source_call_performed") is False
            and result_04.get("live_source_call_performed") is False
        ),
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    required = [
        "control/inventory/snapshot_refresh_04_result.json",
        "control/inventory/seed_batch_manuals_scans_result.json",
        "control/inventory/seed_batch_driver_support_result.json",
        "control/inventory/snapshot_refresh_03_result.json",
        "control/inventory/local_apply_live_metadata_result.json",
        "control/inventory/public_alpha_reassess_02_result.json",
        "control/inventory/snapshot_refresh_02_result.json",
        "control/inventory/live_metadata_review_result.json",
        "control/inventory/public_alpha_reassess_01_result.json",
        "control/inventory/snapshot_refresh_01_result.json",
        "control/inventory/live_metadata_pilot_result.json",
        "control/inventory/public_alpha_reassess_result.json",
        "control/inventory/snapshot_refresh_result.json",
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/review_batch_result.json",
        "control/inventory/scout_runtime_result.json",
        "control/inventory/candidate_index_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
        "control/inventory/snapshot_relay_result.json",
        "control/inventory/public_search_ux_model_result.json",
        "control/inventory/public_alpha_readonly_00_result.json",
        "control/inventory/public_alpha_launch_defer_result.json",
    ]
    if not _paths_exist(required):
        return False
    for path in required:
        payload = _load_json(path)
        if payload.get("status") not in {"pass", "pass_with_warnings", "deferred", "validated"}:
            return False
    launch_defer = _load_json("control/inventory/public_alpha_launch_defer_result.json")
    snapshot_04 = _load_json("control/inventory/snapshot_refresh_04_result.json")
    manuals_scans = _load_json("control/inventory/seed_batch_manuals_scans_result.json")
    driver_support = _load_json("control/inventory/seed_batch_driver_support_result.json")
    snapshot_03 = _load_json("control/inventory/snapshot_refresh_03_result.json")
    local_apply = _load_json("control/inventory/local_apply_live_metadata_result.json")
    snapshot_02 = _load_json("control/inventory/snapshot_refresh_02_result.json")
    live_review = _load_json("control/inventory/live_metadata_review_result.json")
    snapshot_01 = _load_json("control/inventory/snapshot_refresh_01_result.json")
    live_pilot = _load_json("control/inventory/live_metadata_pilot_result.json")
    return (
        launch_defer.get("public_launch_performed") is False
        and snapshot_04.get("total_limited_reviewed_record_projection_count") == 4
        and snapshot_04.get("manuals_scans_candidate_count") == 16
        and snapshot_04.get("driver_support_candidate_count") == 16
        and snapshot_04.get("additional_seed_candidate_count") == 32
        and snapshot_04.get("total_candidate_count") == 68
        and snapshot_04.get("artifact_verified_claim_created") is False
        and snapshot_04.get("verified_download_claim_created") is False
        and snapshot_04.get("malware_clean_claim_created") is False
        and snapshot_04.get("compatibility_guarantee_created") is False
        and snapshot_04.get("rights_clearance_claim_created") is False
        and snapshot_04.get("scan_completeness_claim_created") is False
        and snapshot_04.get("ocr_quality_claim_created") is False
        and snapshot_04.get("download_performed") is False
        and snapshot_04.get("file_fetch_performed") is False
        and snapshot_04.get("ocr_performed") is False
        and snapshot_04.get("extraction_executed") is False
        and snapshot_04.get("install_execution_enabled") is False
        and snapshot_04.get("deployment_performed") is False
        and manuals_scans.get("fixture_seed_batch_passed") is True
        and manuals_scans.get("download_performed") is False
        and manuals_scans.get("file_fetch_performed") is False
        and manuals_scans.get("ocr_performed") is False
        and driver_support.get("fixture_seed_batch_passed") is True
        and driver_support.get("download_performed") is False
        and driver_support.get("file_fetch_performed") is False
        and driver_support.get("install_execution_enabled") is False
        and snapshot_03.get("total_limited_reviewed_record_projection_count") == 4
        and snapshot_03.get("reviewed_metadata_record_count") == 1
        and snapshot_03.get("reviewed_source_lead_count") == 2
        and snapshot_03.get("artifact_verified_claim_created") is False
        and snapshot_03.get("verified_download_claim_created") is False
        and snapshot_03.get("malware_clean_claim_created") is False
        and snapshot_03.get("rights_clearance_claim_created") is False
        and snapshot_03.get("reviewed_index_mutated") is False
        and snapshot_03.get("master_index_mutated") is False
        and snapshot_03.get("public_index_mutated") is False
        and local_apply.get("reviewed_record_delta_count") == 3
        and local_apply.get("operator_instance_mutated") is False
        and local_apply.get("public_index_mutated") is False
        and local_apply.get("master_index_mutated") is False
        and snapshot_02.get("reviewed_metadata_record_preview_count") == 1
        and snapshot_02.get("reviewed_source_lead_preview_count") == 2
        and snapshot_02.get("review_preview_applied") is False
        and snapshot_02.get("accepted_truth_created") is False
        and snapshot_02.get("reviewed_index_mutated") is False
        and live_review.get("reviewed_metadata_record_preview_count") == 1
        and live_review.get("reviewed_source_lead_preview_count") == 2
        and live_review.get("accepted_truth_created") is False
        and snapshot_01.get("accepted_truth_created") is False
        and snapshot_01.get("live_metadata_candidate_promoted") is False
        and live_pilot.get("operator_live_metadata_run_performed") is True
        and live_pilot.get("raw_live_response_committed") is False
    )


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


def _live_metadata_metrics_included() -> bool:
    path = "control/inventory/public_alpha_reassess_01_result.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    return (
        payload.get("reviewed_record_count") == 1
        and payload.get("fixture_candidate_count") == 28
        and payload.get("live_metadata_candidate_count") == 8
        and payload.get("total_candidate_count") == 36
        and payload.get("launch_recommended") is False
        and payload.get("needs_live_candidate_review") is True
        and payload.get("deployment_performed") is False
        and payload.get("public_launch_performed") is False
    )


def _review_preview_metrics_included() -> bool:
    path = "control/inventory/public_alpha_reassess_02_result.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    return (
        payload.get("reviewed_record_count") == 1
        and payload.get("fixture_candidate_count") == 28
        and payload.get("live_metadata_candidate_count") == 8
        and payload.get("total_candidate_count") == 36
        and payload.get("reviewed_metadata_record_preview_count") == 1
        and payload.get("reviewed_source_lead_preview_count") == 2
        and payload.get("useful_lead_count") == 1
        and payload.get("needs_more_evidence_count") == 2
        and payload.get("rejected_or_duplicate_count") == 2
        and payload.get("launch_recommended") is False
        and payload.get("needs_local_apply_of_review_previews") is True
        and payload.get("deployment_performed") is False
        and payload.get("public_launch_performed") is False
    )


def _limited_reviewed_record_metrics_included() -> bool:
    path = "control/inventory/public_alpha_reassess_03_result.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    return (
        payload.get("existing_reviewed_record_count") == 1
        and payload.get("reviewed_metadata_record_count") == 1
        and payload.get("reviewed_source_lead_count") == 2
        and payload.get("reviewed_record_delta_count") == 3
        and payload.get("total_limited_reviewed_record_projection_count") == 4
        and payload.get("fixture_candidate_count") == 28
        and payload.get("live_metadata_candidate_count") == 8
        and payload.get("total_candidate_count") == 36
        and payload.get("launch_recommended") is False
        and payload.get("needs_more_domains") is True
        and payload.get("needs_seed_batch_manuals_scans") is True
        and payload.get("needs_seed_batch_driver_support") is True
        and payload.get("deployment_performed") is False
        and payload.get("public_launch_performed") is False
    )


def _manuals_driver_metrics_included() -> bool:
    path = "control/inventory/public_alpha_reassess_04_result.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    return (
        payload.get("existing_reviewed_record_count") == 1
        and payload.get("reviewed_metadata_record_count") == 1
        and payload.get("reviewed_source_lead_count") == 2
        and payload.get("total_limited_reviewed_record_projection_count") == 4
        and payload.get("candidate_count") == 68
        and payload.get("manuals_scans_candidate_count") == 16
        and payload.get("driver_support_candidate_count") == 16
        and payload.get("domain_count") == 4
        and payload.get("public_search_view_models_available") is True
        and payload.get("public_search_ux_mvp_implemented") is False
        and payload.get("launch_recommended") is False
        and payload.get("needs_public_search_ux_mvp") is True
        and payload.get("needs_snapshot_refresh_after_ux") is True
        and payload.get("needs_public_alpha_reassess_after_ux") is True
        and payload.get("deployment_performed") is False
        and payload.get("public_launch_performed") is False
        and payload.get("download_performed") is False
        and payload.get("file_fetch_performed") is False
        and payload.get("ocr_performed") is False
        and payload.get("extraction_executed") is False
        and payload.get("install_execution_enabled") is False
        and payload.get("model_provider_used") is False
    )


def _cli_help_works() -> bool:
    for path in REQUIRED_CLI:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / path), "--help"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
