#!/usr/bin/env python3
"""Validate REVIEW-BATCH-00."""

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

from runtime.review.batch import (  # noqa: E402
    BATCH_DECISIONS,
    CANDIDATE_CLUSTER_KINDS,
    STATE_TRANSITIONS,
    build_batch_local_apply_handoff,
    build_batch_snapshot_refresh_handoff,
    build_review_batch_boundary_report,
    project_review_batch,
    run_review_batch_from_examples,
)


REQUIRED_CONTRACTS = [
    "contracts/review/review_batch_packet.v0.json",
    "contracts/review/candidate_cluster.v0.json",
    "contracts/review/review_batch_decision.v0.json",
    "contracts/review/review_batch_state_update.v0.json",
    "contracts/review/batch_promotion_preview.v0.json",
    "contracts/review/batch_local_apply_handoff.v0.json",
    "contracts/review/batch_snapshot_refresh_handoff.v0.json",
    "contracts/review/review_batch_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/review_batch_policy.json",
    "control/policies/review_batch_operator_policy.json",
    "control/policies/review_batch_decision_policy.json",
    "control/policies/review_batch_promotion_preview_policy.json",
    "control/policies/review_batch_local_apply_handoff_policy.json",
    "control/policies/review_batch_snapshot_handoff_policy.json",
    "control/policies/review_batch_non_claim_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/review_batch_input_state.json",
    "control/inventory/review_batch_contract_authority_matrix.json",
    "control/inventory/review_batch_cluster_matrix.json",
    "control/inventory/review_batch_decision_matrix.json",
    "control/inventory/review_batch_state_transition_matrix.json",
    "control/inventory/review_batch_promotion_preview_matrix.json",
    "control/inventory/review_batch_local_apply_handoff_matrix.json",
    "control/inventory/review_batch_snapshot_handoff_matrix.json",
    "control/inventory/review_batch_projection_matrix.json",
    "control/inventory/review_batch_boundary_report.json",
]
REQUIRED_EXAMPLES = [
    "examples/review_batch/sample_candidate_cluster.json",
    "examples/review_batch/sample_review_batch_packet.json",
    "examples/review_batch/sample_review_batch_decision.json",
    "examples/review_batch/sample_candidate_state_updates.json",
    "examples/review_batch/sample_batch_promotion_preview.json",
    "examples/review_batch/sample_local_apply_handoff.json",
    "examples/review_batch/sample_snapshot_refresh_handoff.json",
    "examples/review_batch/sample_boundary_report.json",
]
REQUIRED_DOCS = [
    "docs/architecture/REVIEW_BATCH.md",
    "docs/architecture/BATCH_REVIEW_DECISION_MODEL.md",
    "docs/architecture/CANDIDATE_CLUSTER_REVIEW.md",
    "docs/architecture/BATCH_PROMOTION_PREVIEW.md",
    "docs/operations/REVIEW_BATCH_RUNBOOK.md",
    "docs/operations/POST_REVIEW_BATCH_PLAN.md",
    "docs/reference/REVIEW_BATCH_PACKET.md",
    "docs/reference/REVIEW_BATCH_DECISION.md",
    "docs/reference/BATCH_PROMOTION_PREVIEW.md",
]
REQUIRED_CLI = [
    "scripts/eureka_review_batch.py",
    "scripts/eureka_review_batch_decision.py",
    "scripts/eureka_review_batch_preview.py",
    "scripts/eureka_review_batch_handoff.py",
]
REQUIRED_TRUE = [
    "batch_review_requires_operator_context",
    "promotion_preview_is_not_promotion",
    "local_apply_handoff_only",
    "snapshot_refresh_handoff_only",
]
REQUIRED_FALSE = [
    "public_batch_review_enabled",
    "public_candidate_mutation_enabled",
    "automatic_candidate_acceptance_enabled",
    "reviewed_index_mutation_enabled",
    "master_index_mutation_enabled",
    "public_index_mutation_enabled",
    "accepted_truth_created",
    "downloads_enabled",
    "extraction_enabled",
    "model_provider_enabled",
    "deployment_enabled",
    "live_source_calls_enabled",
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
        "matrices_safe": _matrices_safe(),
        "cli_help_works": _cli_help_works(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, value in checks.items() if not value]
    return {
        "schema_version": "review_batch_validation.v0",
        "task": "REVIEW-BATCH-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_mutation_enabled": False,
        "live_source_call_performed": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    paths = [
        "control/inventory/scout_runtime_result.json",
        "control/inventory/candidate_index_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
        "control/inventory/source_action_kernel_result.json",
        "control/inventory/source_wave_result.json",
        "control/inventory/domain_foundation_result.json",
        "control/inventory/local_apply_gate_result.json",
        "control/inventory/snapshot_relay_result.json",
    ]
    if not _paths_exist(paths):
        return False
    for path in paths:
        payload = _load_json(path)
        if payload.get("status") not in {"pass", "pass_with_warnings", "validated"}:
            return False
    candidate = _load_json("control/inventory/candidate_index_result.json")
    scout = _load_json("control/inventory/scout_runtime_result.json")
    return (
        candidate.get("accepted_truth_created") is False
        and candidate.get("reviewed_index_mutated") is False
        and candidate.get("master_index_mutated") is False
        and scout.get("accepted_truth_created") is False
        and scout.get("reviewed_index_mutated") is False
        and scout.get("master_index_mutated") is False
    )


def _policies_safe() -> bool:
    for path in REQUIRED_POLICIES:
        payload = _load_json(path)
        if any(payload.get(key) is not True for key in REQUIRED_TRUE if key in payload):
            return False
        if any(payload.get(key) is not False for key in REQUIRED_FALSE if key in payload):
            return False
    return True


def _matrices_safe() -> bool:
    cluster = _load_json("control/inventory/review_batch_cluster_matrix.json")
    decision = _load_json("control/inventory/review_batch_decision_matrix.json")
    transition = _load_json("control/inventory/review_batch_state_transition_matrix.json")
    return (
        set(cluster.get("candidate_cluster_kinds", [])) == set(CANDIDATE_CLUSTER_KINDS)
        and set(decision.get("batch_decisions", [])) == set(BATCH_DECISIONS)
        and {tuple(item) for item in transition.get("batch_state_transitions", [])} == set(STATE_TRANSITIONS)
        and cluster.get("accepted_truth") is False
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


def _runtime_checks() -> dict[str, bool]:
    batch = run_review_batch_from_examples()
    packet = batch["review_batch_packet"]
    preview = run_review_batch_from_examples(
        "accept_local_reviewed_preview",
        {"projection_profile": "operator_workbench", "operator_token": "local-dev-token", "dry_run": True},
    )["decision_preview"]
    public_projection = project_review_batch(packet, "public_web")
    operator_projection = project_review_batch(packet, "operator_workbench")
    local_handoff = preview["local_apply_handoff"]
    snapshot_handoff = preview["snapshot_refresh_handoff"]
    boundary = build_review_batch_boundary_report(preview)
    no_preview_local = build_batch_local_apply_handoff([])
    no_preview_snapshot = build_batch_snapshot_refresh_handoff([])
    return {
        "clusters_build": batch["cluster_count"] >= 1,
        "batch_packets_build": packet["accepted_truth"] is False and len(packet["cluster_refs"]) >= 1,
        "decisions_validate": preview["decision"]["allowed"] is True
        and preview["decision"]["accepted_truth"] is False,
        "state_update_previews_build": len(preview["state_updates"]) >= 1
        and all(item["transition_applied"] is False for item in preview["state_updates"]),
        "promotion_previews_build": len(preview["promotion_previews"]) >= 1
        and all(item["promotion_preview_is_not_promotion"] for item in preview["promotion_previews"]),
        "local_apply_handoff_builds": local_handoff["local_apply_handoff_only"] is True
        and local_handoff["local_apply_executed"] is False
        and no_preview_local["handoff_status"] == "blocked_no_promotion_previews",
        "snapshot_refresh_handoff_builds": snapshot_handoff["snapshot_refresh_handoff_only"] is True
        and snapshot_handoff["snapshot_refresh_executed"] is False
        and no_preview_snapshot["handoff_status"] == "blocked_no_promotion_previews",
        "public_projection_read_only": public_projection["read_only"] is True
        and public_projection["decision_actions_visible"] is False
        and operator_projection["decision_actions_visible"] is True,
        "boundary_flags_false": all(
            boundary[key] is False
            for key in (
                "accepted_truth_created",
                "reviewed_index_mutated",
                "master_index_mutated",
                "public_mutation_enabled",
                "live_source_call_performed",
                "download_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
            )
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
