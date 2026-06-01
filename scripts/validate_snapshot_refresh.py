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
    build_snapshot_refresh_inventory_packets,
    run_snapshot_refresh_02,
    run_snapshot_refresh_01,
    run_snapshot_refresh,
)


REQUIRED_CONTRACTS = [
    "contracts/snapshot/snapshot_refresh_plan.v0.json",
    "contracts/snapshot/snapshot_refresh_result.v0.json",
    "contracts/snapshot/snapshot_candidate_section.v0.json",
    "contracts/snapshot/snapshot_live_metadata_candidate_section.v0.json",
    "contracts/snapshot/snapshot_live_metadata_review_section.v0.json",
    "contracts/snapshot/snapshot_reviewed_metadata_preview_section.v0.json",
    "contracts/snapshot/snapshot_reviewed_source_lead_preview_section.v0.json",
    "contracts/snapshot/snapshot_review_queue_section.v0.json",
    "contracts/snapshot/snapshot_need_absence_section.v0.json",
    "contracts/snapshot/snapshot_seed_batch_summary.v0.json",
    "contracts/snapshot/snapshot_refresh_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/snapshot_refresh_policy.json",
    "control/policies/snapshot_refresh_reviewed_record_policy.json",
    "control/policies/snapshot_refresh_candidate_policy.json",
    "control/policies/snapshot_refresh_live_metadata_policy.json",
    "control/policies/snapshot_refresh_live_metadata_review_policy.json",
    "control/policies/snapshot_refresh_review_preview_policy.json",
    "control/policies/snapshot_refresh_need_absence_policy.json",
    "control/policies/snapshot_refresh_relay_policy.json",
    "control/policies/snapshot_refresh_non_claim_policy.json",
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
    "examples/relay/refresh/refreshed_relay_projection.json",
    "examples/relay/refresh/live_metadata_refreshed_relay_projection.json",
    "examples/relay/refresh/live_metadata_review_refreshed_relay_projection.json",
    "examples/public_alpha/reassess/snapshot_refresh_reassess_input.json",
    "examples/public_alpha/reassess/live_metadata/snapshot_refresh_01_reassess_input.json",
    "examples/public_alpha/reassess/live_metadata/snapshot_refresh_02_reassess_input.json",
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
]
REQUIRED_CLI = [
    "scripts/eureka_snapshot_refresh.py",
    "scripts/eureka_snapshot_refresh_report.py",
]
REQUIRED_TRUE = [
    "snapshot_refresh_is_projection",
    "review_previews_are_not_truth",
    "reviewed_metadata_previews_require_local_apply",
    "reviewed_source_lead_previews_require_local_apply",
    "live_metadata_candidates_remain_candidates_until_applied",
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
    "no_deployment",
    "no_public_launch_claim",
    "no_production_claim",
]
REQUIRED_FALSE = [
    "downloads_enabled",
    "extraction_enabled",
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
        "task": "SNAPSHOT-REFRESH-00+01+02",
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
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
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
    candidate_sections = list(result.get("candidate_sections") or [])
    live_section = live_result["live_metadata_candidate_section"]
    live_cards = live_result["public_search_view_model_projection"]["result_cards"]
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
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    required = [
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/live_metadata_pilot_result.json",
        "control/inventory/live_metadata_review_result.json",
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
    for path in (
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/live_metadata_pilot_result.json",
    ):
        payload = _load_json(path)
        if any(
            payload.get(key) is not False
            for key in ("accepted_truth_created", "reviewed_index_mutated", "master_index_mutated", "public_index_mutated")
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
