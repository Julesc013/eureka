#!/usr/bin/env python3
"""Validate SEED-BATCH-LEGACY-SOFTWARE-00."""

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
    LEGACY_SOFTWARE_QUERIES,
    LEGACY_SOFTWARE_SUPPRESSIONS,
    build_legacy_software_public_alpha_reassess_inputs,
    build_legacy_software_snapshot_refresh_handoff,
    run_seed_batch_legacy_software,
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
    "control/policies/seed_batch_legacy_software_policy.json",
    "control/policies/seed_batch_legacy_query_policy.json",
    "control/policies/seed_batch_legacy_candidate_policy.json",
    "control/policies/seed_batch_legacy_review_policy.json",
    "control/policies/seed_batch_legacy_suppression_policy.json",
    "control/policies/seed_batch_legacy_non_claim_policy.json",
    "control/policies/seed_batch_legacy_live_metadata_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/seed_batch_legacy_software_input_state.json",
    "control/inventory/seed_batch_legacy_software_query_matrix.json",
    "control/inventory/seed_batch_legacy_software_source_plan_matrix.json",
    "control/inventory/seed_batch_legacy_software_candidate_matrix.json",
    "control/inventory/seed_batch_legacy_software_suppression_matrix.json",
    "control/inventory/seed_batch_legacy_software_scout_matrix.json",
    "control/inventory/seed_batch_legacy_software_review_matrix.json",
    "control/inventory/seed_batch_legacy_software_need_absence_matrix.json",
    "control/inventory/seed_batch_legacy_software_snapshot_handoff_matrix.json",
    "control/inventory/seed_batch_legacy_software_public_alpha_reassess_matrix.json",
    "control/inventory/seed_batch_legacy_software_boundary_report.json",
]
REQUIRED_EXAMPLES = [
    "examples/seed_batches/legacy_software/query_set.json",
    "examples/seed_batches/legacy_software/query_plans.json",
    "examples/seed_batches/legacy_software/source_plans.json",
    "examples/seed_batches/legacy_software/suppressions.json",
    "examples/seed_batches/legacy_software/candidate_summaries.json",
    "examples/seed_batches/legacy_software/candidate_index.json",
    "examples/seed_batches/legacy_software/scout_trails.json",
    "examples/seed_batches/legacy_software/review_batch_packet.json",
    "examples/seed_batches/legacy_software/known_needs.json",
    "examples/seed_batches/legacy_software/absence_summaries.json",
    "examples/seed_batches/legacy_software/snapshot_refresh_handoff.json",
    "examples/seed_batches/legacy_software/public_alpha_reassess_input.json",
    "examples/seed_batches/legacy_software/boundary_report.json",
    "examples/query_plans/legacy_software/query_plans.json",
    "examples/candidates/legacy_software/candidate_summaries.json",
    "examples/scout/legacy_software/scout_trails.json",
    "examples/review_batch/legacy_software/review_batch_packet.json",
    "examples/public_alpha/legacy_software/public_alpha_reassess_input.json",
]
REQUIRED_DOCS = [
    "docs/architecture/SEED_BATCH_LEGACY_SOFTWARE.md",
    "docs/operations/SEED_BATCH_LEGACY_SOFTWARE_RUNBOOK.md",
    "docs/operations/POST_SEED_BATCH_LEGACY_SOFTWARE_PLAN.md",
    "docs/reference/LEGACY_SOFTWARE_QUERY_SET.md",
    "docs/reference/LEGACY_SOFTWARE_SUPPRESSIONS.md",
    "docs/reference/SEED_BATCH_RECORD.md",
    "docs/reference/SEED_BATCH_REVIEW_PACKET.md",
]
REQUIRED_CLI = [
    "scripts/eureka_seed_batch_legacy_software.py",
    "scripts/eureka_seed_batch_run.py",
    "scripts/eureka_seed_batch_report.py",
]
REQUIRED_TRUE = [
    "seed_batch_outputs_are_not_truth",
    "candidates_require_review",
    "source_actions_bounded",
    "archive_org_metadata_candidates_allowed",
    "github_releases_metadata_fixture_allowed",
    "package_registry_metadata_fixture_allowed",
    "software_heritage_metadata_fixture_allowed",
    "live_metadata_optional_and_operator_gated",
]
REQUIRED_FALSE = [
    "reviewed_index_mutation_enabled",
    "public_index_mutation_enabled",
    "master_index_mutation_enabled",
    "automatic_candidate_acceptance_enabled",
    "raw_live_responses_committed",
    "downloads_enabled",
    "extraction_enabled",
    "install_execution_enabled",
    "model_provider_enabled",
    "deployment_enabled",
    "cracks_keygens_serials_supported",
    "malware_clean_claims_allowed",
]
REQUIRED_QUERIES = [item["raw_query"] for item in LEGACY_SOFTWARE_QUERIES]
REQUIRED_SUPPRESSIONS = [item["suppression_id"] for item in LEGACY_SOFTWARE_SUPPRESSIONS]


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
        "schema_version": "seed_batch_legacy_software_validation.v0",
        "task": "SEED-BATCH-LEGACY-SOFTWARE-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "operator_live_metadata_run_performed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "raw_live_response_committed": False,
        "download_performed": False,
        "extraction_executed": False,
        "install_execution_enabled": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "cracks_keygens_serials_supported": False,
        "malware_clean_claims_created": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_seed_batch_legacy_software(fixture=True)
    review_packets = result["review_packets"]
    snapshot_handoff = build_legacy_software_snapshot_refresh_handoff(review_packets)
    public_alpha = build_legacy_software_public_alpha_reassess_inputs(result)
    boundary = result["boundary_report"]
    candidate_summaries = result["candidate_summaries"]
    return {
        "fixture_run_works": result["fixture_seed_batch_passed"] is True,
        "query_plans_build": len(result["query_plans"]) == len(REQUIRED_QUERIES),
        "candidate_summaries_build": len(candidate_summaries) == len(REQUIRED_QUERIES),
        "suppressions_apply": all(item.get("suppressions") for item in candidate_summaries),
        "candidate_index_builds": result["candidate_index"]["candidate_count"] == len(REQUIRED_QUERIES),
        "scout_trails_build": bool(result["scout_trails"]["scout_runs"]),
        "review_batch_packet_builds": bool(review_packets["review_batch_packet"]["candidate_refs"]),
        "known_needs_build": len(result["known_needs"]) == len(REQUIRED_QUERIES),
        "absence_summaries_build": bool(result["absence_summaries"]),
        "snapshot_refresh_handoff_builds": snapshot_handoff["snapshot_refresh_executed"] is False,
        "public_alpha_reassess_input_builds": public_alpha["public_launch_readiness_claimed"] is False,
        "no_accepted_truth": boundary["accepted_truth_created"] is False and result["accepted_truth"] is False,
        "no_index_mutation": all(
            result.get(key) is False
            for key in ("reviewed_index_mutated", "master_index_mutated", "public_index_mutated")
        ),
        "no_download_extract_install_model_deploy": all(
            result.get(key) is False
            for key in (
                "download_performed",
                "extraction_executed",
                "install_execution_enabled",
                "model_provider_used",
                "deployment_performed",
            )
        ),
        "no_crack_keygen_serial_support": result["cracks_keygens_serials_supported"] is False,
        "no_malware_clean_claim": result["malware_clean_claims_created"] is False,
        "no_raw_live_response": result["raw_live_response_committed"] is False,
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    paths = [
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/review_batch_result.json",
        "control/inventory/scout_runtime_result.json",
        "control/inventory/candidate_index_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
        "control/inventory/source_action_kernel_result.json",
        "control/inventory/source_wave_result.json",
        "control/inventory/domain_foundation_result.json",
        "control/inventory/public_alpha_launch_defer_result.json",
    ]
    if not _paths_exist(paths):
        return False
    for path in paths:
        payload = _load_json(path)
        if payload.get("status") not in {"pass", "pass_with_warnings", "validated", "deferred"}:
            return False
    frontier = _load_json("control/inventory/seed_batch_frontier_media_result.json")
    return (
        frontier.get("accepted_truth_created") is False
        and frontier.get("reviewed_index_mutated") is False
        and frontier.get("master_index_mutated") is False
        and frontier.get("public_index_mutated") is False
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


def _query_matrix_has_required_queries() -> bool:
    path = "control/inventory/seed_batch_legacy_software_query_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    queries = [item.get("raw_query") for item in payload.get("queries", [])]
    return queries == REQUIRED_QUERIES and all(
        item.get("domain_id") in {"legacy_software", "driver_support_media"}
        and item.get("accepted_truth") is False
        for item in payload.get("queries", [])
    )


def _suppression_matrix_has_required_suppressions() -> bool:
    path = "control/inventory/seed_batch_legacy_software_suppression_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    suppressions = [item.get("suppression_id") for item in payload.get("suppressions", [])]
    return suppressions == REQUIRED_SUPPRESSIONS and all(
        item.get("review_override_allowed") is False for item in payload.get("suppressions", [])
    )


def _source_plan_matrix_safe() -> bool:
    path = "control/inventory/seed_batch_legacy_software_source_plan_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    families = {item.get("source_family"): item for item in payload.get("source_families", [])}
    internet_archive = families.get("internet_archive_metadata", {})
    package_registry = families.get("package_registry_metadata", {})
    return (
        internet_archive.get("status") == "allowed"
        and internet_archive.get("metadata_only") is True
        and internet_archive.get("downloads_enabled") is False
        and package_registry.get("package_download_enabled") is False
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
