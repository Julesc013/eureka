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
    build_public_alpha_reassess_inventory_packets,
    run_public_alpha_reassess,
    run_public_alpha_reassess_01,
    run_public_alpha_reassess_02,
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
    "contracts/publication/public_alpha_reassess_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/public_alpha_reassess_policy.json",
    "control/policies/public_alpha_reassess_threshold_policy.json",
    "control/policies/public_alpha_reassess_route_smoke_policy.json",
    "control/policies/public_alpha_reassess_live_metadata_policy.json",
    "control/policies/public_alpha_reassess_review_preview_policy.json",
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
]
REQUIRED_DOCS = [
    "docs/architecture/PUBLIC_ALPHA_REASSESS.md",
    "docs/architecture/PUBLIC_ALPHA_REASSESS_01.md",
    "docs/architecture/PUBLIC_ALPHA_REASSESS_02.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_01_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_02_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_PLAN.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_01_PLAN.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_02_PLAN.md",
    "docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md",
    "docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md",
    "docs/reference/PUBLIC_ALPHA_LIVE_METADATA_REASSESSMENT.md",
    "docs/reference/PUBLIC_ALPHA_REVIEW_PREVIEW_REASSESSMENT.md",
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
    "needs_and_absences_are_useful_but_not_launch_sufficient",
]
REQUIRED_FALSE = [
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "downloads_enabled",
    "extraction_enabled",
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
        "public_search_view_model_examples_exist": _paths_exist(
            [
                "examples/public_alpha/reassess/live_metadata/public_alpha_public_search_view_models.json",
                "examples/public_alpha/reassess/live_metadata_review/public_alpha_public_search_view_models.json",
                "examples/view_models/public_search/search_page_view_model.json",
            ]
        ),
    }
    checks.update(_runtime_checks())
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "public_alpha_reassess_validation.v0",
        "task": "PUBLIC-ALPHA-REASSESS-00+01+02",
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
    route_smoke = smoke_public_alpha_routes_from_examples()
    inventory = build_public_alpha_reassess_inventory_packets(result)
    inventory_01 = build_public_alpha_reassess_01_inventory_packets(result_01)
    inventory_02 = build_public_alpha_reassess_02_inventory_packets(result_02)
    return {
        "reassessment_example_builds": result["status"] == "pass",
        "live_metadata_reassessment_example_builds": result_01["status"] == "pass",
        "review_preview_reassessment_example_builds": result_02["status"] == "pass",
        "route_smoke_example_builds": route_smoke["route_smoke_status"] == "pass",
        "decision_exists": result["decision"]["decision"] == "remain_deferred",
        "live_metadata_decision_exists": result_01["decision"]["decision"] == "remain_deferred",
        "review_preview_decision_exists": result_02["decision"]["decision"] == "remain_deferred",
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
        "launch_false_when_thresholds_unmet": result["launch_recommended"] is False,
        "live_metadata_launch_false_when_thresholds_unmet": result_01["launch_recommended"] is False,
        "review_preview_launch_false_when_thresholds_unmet": result_02["launch_recommended"] is False,
        "demo_mode_recommended": result["demo_mode_recommended"] is True,
        "live_metadata_demo_mode_recommended": result_01["demo_mode_recommended"] is True,
        "review_preview_demo_mode_recommended": result_02["demo_mode_recommended"] is True,
        "internal_review_recommended": result_01["internal_review_recommended"] is True,
        "review_preview_internal_review_recommended": result_02["internal_review_recommended"] is True,
        "needs_live_candidate_review": result_01["needs_live_candidate_review"] is True,
        "needs_snapshot_refresh_after_review": result_01["needs_snapshot_refresh_after_review"] is True,
        "needs_local_apply_of_review_previews": result_02["needs_local_apply_of_review_previews"] is True,
        "needs_snapshot_refresh_after_apply": result_02["needs_snapshot_refresh_after_apply"] is True,
        "needs_public_alpha_reassess_after_apply": result_02["needs_public_alpha_reassess_after_apply"] is True,
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
        "no_deployment_or_launch": all(
            result.get(key) is False for key in ("deployment_performed", "public_launch_performed")
        )
        and all(result_01.get(key) is False for key in ("deployment_performed", "public_launch_performed"))
        and all(result_02.get(key) is False for key in ("deployment_performed", "public_launch_performed")),
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
        ),
        "no_live_source_calls": (
            result_01.get("live_source_call_performed") is False
            and result_02.get("live_source_call_performed") is False
        ),
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    required = [
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
    snapshot_02 = _load_json("control/inventory/snapshot_refresh_02_result.json")
    live_review = _load_json("control/inventory/live_metadata_review_result.json")
    snapshot_01 = _load_json("control/inventory/snapshot_refresh_01_result.json")
    live_pilot = _load_json("control/inventory/live_metadata_pilot_result.json")
    return (
        launch_defer.get("public_launch_performed") is False
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
