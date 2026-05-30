#!/usr/bin/env python3
"""Validate SEED-BATCH-FRONTIER-MEDIA-00."""

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
    FRONTIER_MEDIA_QUERIES,
    build_seed_batch_public_alpha_reassess_inputs,
    build_seed_batch_snapshot_refresh_handoff,
    run_seed_batch_frontier_media,
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
    "control/policies/seed_batch_frontier_media_policy.json",
    "control/policies/seed_batch_query_policy.json",
    "control/policies/seed_batch_candidate_policy.json",
    "control/policies/seed_batch_review_policy.json",
    "control/policies/seed_batch_non_claim_policy.json",
    "control/policies/seed_batch_live_metadata_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/seed_batch_frontier_media_input_state.json",
    "control/inventory/seed_batch_frontier_media_query_matrix.json",
    "control/inventory/seed_batch_frontier_media_source_plan_matrix.json",
    "control/inventory/seed_batch_frontier_media_candidate_matrix.json",
    "control/inventory/seed_batch_frontier_media_scout_matrix.json",
    "control/inventory/seed_batch_frontier_media_review_matrix.json",
    "control/inventory/seed_batch_frontier_media_need_absence_matrix.json",
    "control/inventory/seed_batch_frontier_media_snapshot_handoff_matrix.json",
    "control/inventory/seed_batch_frontier_media_public_alpha_reassess_matrix.json",
    "control/inventory/seed_batch_frontier_media_boundary_report.json",
]
REQUIRED_EXAMPLES = [
    "examples/seed_batches/frontier_media/query_set.json",
    "examples/seed_batches/frontier_media/query_plans.json",
    "examples/seed_batches/frontier_media/source_plans.json",
    "examples/seed_batches/frontier_media/candidate_summaries.json",
    "examples/seed_batches/frontier_media/candidate_index.json",
    "examples/seed_batches/frontier_media/scout_trails.json",
    "examples/seed_batches/frontier_media/review_batch_packet.json",
    "examples/seed_batches/frontier_media/known_needs.json",
    "examples/seed_batches/frontier_media/absence_summaries.json",
    "examples/seed_batches/frontier_media/snapshot_refresh_handoff.json",
    "examples/seed_batches/frontier_media/public_alpha_reassess_input.json",
    "examples/seed_batches/frontier_media/boundary_report.json",
    "examples/query_plans/frontier_media/query_plans.json",
    "examples/candidates/frontier_media/candidate_summaries.json",
    "examples/scout/frontier_media/scout_trails.json",
    "examples/review_batch/frontier_media/review_batch_packet.json",
    "examples/public_alpha/frontier_media/public_alpha_reassess_input.json",
]
REQUIRED_DOCS = [
    "docs/architecture/SEED_BATCH_FRONTIER_MEDIA.md",
    "docs/operations/SEED_BATCH_FRONTIER_MEDIA_RUNBOOK.md",
    "docs/operations/POST_SEED_BATCH_FRONTIER_MEDIA_PLAN.md",
    "docs/reference/FRONTIER_MEDIA_QUERY_SET.md",
    "docs/reference/SEED_BATCH_RECORD.md",
    "docs/reference/SEED_BATCH_REVIEW_PACKET.md",
]
REQUIRED_CLI = [
    "scripts/eureka_seed_batch_frontier_media.py",
    "scripts/eureka_seed_batch_run.py",
    "scripts/eureka_seed_batch_report.py",
]
REQUIRED_TRUE = [
    "seed_batch_outputs_are_not_truth",
    "candidates_require_review",
    "source_actions_bounded",
    "archive_org_metadata_candidates_allowed",
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
    "model_provider_enabled",
    "deployment_enabled",
]
REQUIRED_QUERIES = [item["raw_query"] for item in FRONTIER_MEDIA_QUERIES]


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
        "source_plan_matrix_safe": _source_plan_matrix_safe(),
        "cli_help_works": _cli_help_works(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, value in checks.items() if not value]
    return {
        "schema_version": "seed_batch_frontier_media_validation.v0",
        "task": "SEED-BATCH-FRONTIER-MEDIA-00",
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
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_seed_batch_frontier_media(fixture=True)
    review_packets = result["review_packets"]
    snapshot_handoff = build_seed_batch_snapshot_refresh_handoff(review_packets)
    public_alpha = build_seed_batch_public_alpha_reassess_inputs(result)
    boundary = result["boundary_report"]
    return {
        "fixture_run_works": result["fixture_seed_batch_passed"] is True,
        "query_plans_build": len(result["query_plans"]) == len(REQUIRED_QUERIES),
        "candidate_summaries_build": len(result["candidate_summaries"]) == len(REQUIRED_QUERIES),
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
        "no_download_extract_model_deploy": all(
            result.get(key) is False
            for key in ("download_performed", "extraction_executed", "model_provider_used", "deployment_performed")
        ),
        "no_raw_live_response": result["raw_live_response_committed"] is False,
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    paths = [
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
    review = _load_json("control/inventory/review_batch_result.json")
    return (
        review.get("accepted_truth_created") is False
        and review.get("reviewed_index_mutated") is False
        and review.get("master_index_mutated") is False
        and review.get("public_mutation_enabled") is False
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
    path = "control/inventory/seed_batch_frontier_media_query_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    queries = [item.get("raw_query") for item in payload.get("queries", [])]
    return queries == REQUIRED_QUERIES and all(
        item.get("domain_id") == "frontier_resolution_media"
        and item.get("intent") == "find_frontier_resolution_media"
        and item.get("accepted_truth") is False
        for item in payload.get("queries", [])
    )


def _source_plan_matrix_safe() -> bool:
    path = "control/inventory/seed_batch_frontier_media_source_plan_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    families = {item.get("source_family"): item for item in payload.get("source_families", [])}
    internet_archive = families.get("internet_archive_metadata", {})
    return (
        internet_archive.get("status") == "allowed"
        and internet_archive.get("metadata_only") is True
        and internet_archive.get("downloads_enabled") is False
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
