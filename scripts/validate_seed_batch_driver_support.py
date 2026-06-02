#!/usr/bin/env python3
"""Validate SEED-BATCH-DRIVER-SUPPORT-00."""

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

from runtime.seed_batches import (  # noqa: E402
    DRIVER_SUPPORT_QUERIES,
    DRIVER_SUPPORT_SUPPRESSIONS,
    build_driver_support_inventory_packets,
    build_driver_support_public_alpha_reassess_inputs,
    build_driver_support_snapshot_refresh_handoff,
    run_seed_batch_driver_support,
)


REQUIRED_CONTRACTS = [
    "contracts/seed_batches/README.md",
    "contracts/seed_batches/seed_batch.v0.json",
    "contracts/seed_batches/seed_batch_query.v0.json",
    "contracts/seed_batches/seed_batch_run.v0.json",
    "contracts/seed_batches/seed_batch_result.v0.json",
    "contracts/seed_batches/seed_batch_candidate_summary.v0.json",
    "contracts/seed_batches/seed_batch_review_summary.v0.json",
    "contracts/seed_batches/seed_batch_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/seed_batch_driver_support_policy.json",
    "control/policies/seed_batch_driver_query_policy.json",
    "control/policies/seed_batch_driver_candidate_policy.json",
    "control/policies/seed_batch_driver_review_policy.json",
    "control/policies/seed_batch_driver_suppression_policy.json",
    "control/policies/seed_batch_driver_non_claim_policy.json",
    "control/policies/seed_batch_driver_live_metadata_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/seed_batch_driver_support_input_state.json",
    "control/inventory/seed_batch_driver_support_query_matrix.json",
    "control/inventory/seed_batch_driver_support_source_plan_matrix.json",
    "control/inventory/seed_batch_driver_support_candidate_matrix.json",
    "control/inventory/seed_batch_driver_support_suppression_matrix.json",
    "control/inventory/seed_batch_driver_support_scout_matrix.json",
    "control/inventory/seed_batch_driver_support_review_matrix.json",
    "control/inventory/seed_batch_driver_support_need_absence_matrix.json",
    "control/inventory/seed_batch_driver_support_snapshot_handoff_matrix.json",
    "control/inventory/seed_batch_driver_support_public_alpha_reassess_matrix.json",
    "control/inventory/seed_batch_driver_support_boundary_report.json",
    "control/inventory/seed_batch_driver_support_smoke_result.json",
    "control/inventory/seed_batch_driver_support_validation_matrix.json",
    "control/inventory/seed_batch_driver_support_result.json",
    "control/inventory/seed_batch_driver_support_next_task_decision.json",
    "control/inventory/seed_batch_driver_support_failure_repair_log.json",
]
REQUIRED_EXAMPLES = [
    "examples/seed_batches/driver_support/query_set.json",
    "examples/seed_batches/driver_support/query_plans.json",
    "examples/seed_batches/driver_support/source_plans.json",
    "examples/seed_batches/driver_support/suppressions.json",
    "examples/seed_batches/driver_support/candidate_summaries.json",
    "examples/seed_batches/driver_support/candidate_index.json",
    "examples/seed_batches/driver_support/scout_trails.json",
    "examples/seed_batches/driver_support/review_batch_packet.json",
    "examples/seed_batches/driver_support/known_needs.json",
    "examples/seed_batches/driver_support/absence_summaries.json",
    "examples/seed_batches/driver_support/snapshot_refresh_handoff.json",
    "examples/seed_batches/driver_support/public_alpha_reassess_input.json",
    "examples/seed_batches/driver_support/boundary_report.json",
    "examples/query_plans/driver_support/query_plans.json",
    "examples/candidates/driver_support/candidate_summaries.json",
    "examples/candidates/driver_support/candidate_index.json",
    "examples/scout/driver_support/scout_trails.json",
    "examples/review_batch/driver_support/review_batch_packet.json",
    "examples/public_alpha/driver_support/public_alpha_reassess_input.json",
]
REQUIRED_DOCS = [
    "docs/architecture/SEED_BATCH_DRIVER_SUPPORT.md",
    "docs/operations/SEED_BATCH_DRIVER_SUPPORT_RUNBOOK.md",
    "docs/operations/POST_SEED_BATCH_DRIVER_SUPPORT_PLAN.md",
    "docs/reference/DRIVER_SUPPORT_QUERY_SET.md",
    "docs/reference/DRIVER_SUPPORT_SUPPRESSIONS.md",
]
REQUIRED_CLI = [
    "scripts/eureka_seed_batch_driver_support.py",
    "scripts/eureka_seed_batch_run.py",
    "scripts/eureka_seed_batch_report.py",
    "scripts/validate_seed_batch_driver_support.py",
]
REQUIRED_TRUE = [
    "seed_batch_outputs_are_not_truth",
    "candidates_require_review",
    "source_actions_bounded",
    "archive_org_metadata_candidates_allowed",
    "wayback_cdx_metadata_fixture_allowed",
    "manual_source_pack_fixture_allowed",
    "vendor_support_url_metadata_fixture_allowed",
    "github_releases_metadata_fixture_allowed",
    "live_metadata_optional_and_operator_gated",
]
REQUIRED_FALSE = [
    "reviewed_index_mutation_enabled",
    "public_index_mutation_enabled",
    "master_index_mutation_enabled",
    "automatic_candidate_acceptance_enabled",
    "raw_live_responses_committed",
    "downloads_enabled",
    "file_fetches_enabled",
    "extraction_enabled",
    "install_execution_enabled",
    "model_provider_enabled",
    "deployment_enabled",
    "malware_clean_claims_allowed",
    "compatibility_guarantee_allowed",
    "rights_clearance_claims_allowed",
    "cracks_keygens_serials_supported",
    "driver_updater_spam_supported",
]
BOUNDARY_FALSE = [
    "accepted_truth_created",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "raw_live_response_committed",
    "download_performed",
    "file_fetch_performed",
    "extraction_executed",
    "install_execution_enabled",
    "model_provider_used",
    "deployment_performed",
    "malware_clean_claim_created",
    "compatibility_guarantee_created",
    "rights_clearance_claim_created",
    "cracks_keygens_serials_supported",
    "driver_updater_spam_supported",
]
REQUIRED_QUERIES = [item["raw_query"] for item in DRIVER_SUPPORT_QUERIES]
REQUIRED_SUPPRESSIONS = [item["suppression_id"] for item in DRIVER_SUPPORT_SUPPRESSIONS]
ALLOWED_SOURCE_FAMILIES = {
    "internet_archive_metadata",
    "wayback_cdx_metadata",
    "manual_source_pack",
    "vendor_support_url_metadata",
    "github_releases_metadata",
}


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
        "query_matrix_has_required_queries": _query_matrix_has_required_queries(),
        "suppression_matrix_has_required_suppressions": _suppression_matrix_has_required_suppressions(),
        "source_plan_matrix_safe": _source_plan_matrix_safe(),
        "cli_help_works": _cli_help_works(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, value in checks.items() if not value]
    return {
        "schema_version": "seed_batch_driver_support_validation.v0",
        "task": "SEED-BATCH-DRIVER-SUPPORT-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "operator_live_metadata_run_performed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "download_performed": False,
        "file_fetch_performed": False,
        "extraction_executed": False,
        "install_execution_enabled": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "malware_clean_claim_created": False,
        "compatibility_guarantee_created": False,
        "rights_clearance_claim_created": False,
        "cracks_keygens_serials_supported": False,
        "driver_updater_spam_supported": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_seed_batch_driver_support(fixture=True)
    review_packets = result["review_packets"]
    snapshot_handoff = build_driver_support_snapshot_refresh_handoff(review_packets)
    public_alpha = build_driver_support_public_alpha_reassess_inputs(result)
    boundary = result["boundary_report"]
    candidate_summaries = result["candidate_summaries"]
    inventory = build_driver_support_inventory_packets(result)
    return {
        "fixture_run_works": result["fixture_seed_batch_passed"] is True,
        "query_plans_build": len(result["query_plans"]) == len(REQUIRED_QUERIES),
        "source_plans_use_allowed_families": {
            item["source_family"] for item in result["source_plans"]
        }.issubset(ALLOWED_SOURCE_FAMILIES),
        "candidate_summaries_build": len(candidate_summaries) == len(REQUIRED_QUERIES),
        "suppressions_apply": all(item.get("suppressions") for item in candidate_summaries),
        "candidate_index_builds": result["candidate_index"]["candidate_count"] == len(REQUIRED_QUERIES),
        "scout_trails_build": bool(result["scout_trails"]["scout_runs"]),
        "review_batch_packet_builds": bool(review_packets["review_batch_packet"]["candidate_refs"]),
        "known_needs_build": len(result["known_needs"]) == len(REQUIRED_QUERIES),
        "absence_summaries_build": len(result["absence_summaries"]) >= 2,
        "snapshot_refresh_handoff_builds": snapshot_handoff["snapshot_refresh_executed"] is False,
        "public_alpha_reassess_input_builds": public_alpha["public_launch_readiness_claimed"] is False,
        "inventory_packets_build": "seed_batch_driver_support_result.json" in inventory,
        "no_accepted_truth": boundary["accepted_truth_created"] is False and result["accepted_truth"] is False,
        "no_index_mutation": all(result.get(key) is False for key in ("reviewed_index_mutated", "master_index_mutated", "public_index_mutated")),
        "no_download_fetch_extract_install_model_deploy": all(result.get(key) is False for key in BOUNDARY_FALSE if key in result),
        "no_driver_safety_or_rights_claims": all(
            result.get(key) is False
            for key in ("malware_clean_claim_created", "compatibility_guarantee_created", "rights_clearance_claim_created")
        ),
        "no_crack_keygen_serial_or_updater_support": all(
            result.get(key) is False for key in ("cracks_keygens_serials_supported", "driver_updater_spam_supported")
        ),
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    paths = [
        "control/inventory/public_alpha_reassess_03_result.json",
        "control/inventory/snapshot_refresh_03_result.json",
        "control/inventory/seed_batch_manuals_scans_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/review_batch_result.json",
        "control/inventory/scout_runtime_result.json",
        "control/inventory/candidate_index_result.json",
    ]
    if not _paths_exist(paths):
        return False
    for path in paths:
        payload = _load_json(path)
        if payload.get("status") not in {"pass", "pass_with_warnings", "validated", "deferred"}:
            return False
    public_alpha = _load_json("control/inventory/public_alpha_reassess_03_result.json")
    return public_alpha.get("launch_recommended") is False


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


def _query_matrix_has_required_queries() -> bool:
    path = "control/inventory/seed_batch_driver_support_query_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    queries = [item.get("raw_query") for item in payload.get("queries", [])]
    return queries == REQUIRED_QUERIES and all(
        item.get("domain_id") == "driver_support_media" and item.get("accepted_truth") is False
        for item in payload.get("queries", [])
    )


def _suppression_matrix_has_required_suppressions() -> bool:
    path = "control/inventory/seed_batch_driver_support_suppression_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    suppressions = [item.get("suppression_id") for item in payload.get("suppressions", [])]
    return suppressions == REQUIRED_SUPPRESSIONS and all(
        item.get("review_override_allowed") is False for item in payload.get("suppressions", [])
    )


def _source_plan_matrix_safe() -> bool:
    path = "control/inventory/seed_batch_driver_support_source_plan_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    families = {item.get("source_family"): item for item in payload.get("source_families", [])}
    return (
        set(families) == ALLOWED_SOURCE_FAMILIES
        and families["internet_archive_metadata"].get("status") == "allowed"
        and families["internet_archive_metadata"].get("metadata_only") is True
        and all(item.get("downloads_enabled") is False for item in families.values())
        and all(item.get("file_fetches_enabled", item.get("file_fetch_enabled")) is False for item in families.values())
        and payload.get("arbitrary_web_crawling_enabled") is False
    )


def _cli_help_works() -> bool:
    for path in REQUIRED_CLI:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / path), "--help"],
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
