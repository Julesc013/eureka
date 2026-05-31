#!/usr/bin/env python3
"""Validate LIVE-METADATA-PILOT-BATCH-00."""

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
    approval_template,
    build_live_metadata_request_plans,
    load_live_metadata_pilot_approval,
    run_live_metadata_pilot_batch,
    select_live_metadata_seed_queries,
    validate_live_metadata_pilot_approval,
)


REQUIRED_CONTRACTS = [
    "contracts/source/action/live_metadata_pilot_approval.v0.json",
    "contracts/source/action/live_metadata_pilot_request_plan.v0.json",
    "contracts/source/action/live_metadata_pilot_result.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/live_metadata_pilot_policy.json",
    "control/policies/live_metadata_pilot_approval_policy.json",
    "control/policies/live_metadata_pilot_source_policy.json",
    "control/policies/live_metadata_pilot_redaction_policy.json",
    "control/policies/live_metadata_pilot_candidate_policy.json",
    "control/policies/live_metadata_pilot_non_claim_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/live_metadata_pilot_batch_input_state.json",
    "control/inventory/live_metadata_pilot_batch_approval_state.json",
    "control/inventory/live_metadata_pilot_seed_query_matrix.json",
    "control/inventory/live_metadata_pilot_source_plan_matrix.json",
    "control/inventory/live_metadata_pilot_request_plan_matrix.json",
    "control/inventory/live_metadata_pilot_transport_summary.json",
    "control/inventory/live_metadata_pilot_redaction_summary.json",
    "control/inventory/live_metadata_pilot_candidate_matrix.json",
    "control/inventory/live_metadata_pilot_scout_matrix.json",
    "control/inventory/live_metadata_pilot_review_matrix.json",
    "control/inventory/live_metadata_pilot_snapshot_handoff_matrix.json",
    "control/inventory/live_metadata_pilot_public_alpha_reassess_matrix.json",
    "control/inventory/live_metadata_pilot_boundary_report.json",
    "control/inventory/live_metadata_pilot_smoke_result.json",
    "control/inventory/live_metadata_pilot_validation_matrix.json",
    "control/inventory/live_metadata_pilot_result.json",
    "control/inventory/live_metadata_pilot_next_task_decision.json",
    "control/inventory/live_metadata_pilot_failure_repair_log.json",
]
REQUIRED_EXAMPLES = [
    "examples/live_metadata_pilot/approval_template.json",
    "examples/live_metadata_pilot/dry_run_request_plans.json",
    "examples/live_metadata_pilot/fixture_transport_summary.json",
    "examples/live_metadata_pilot/redacted_metadata_summary.json",
    "examples/live_metadata_pilot/candidate_summaries.json",
    "examples/live_metadata_pilot/scout_trails.json",
    "examples/live_metadata_pilot/review_batch_packet.json",
    "examples/live_metadata_pilot/snapshot_refresh_handoff.json",
    "examples/live_metadata_pilot/public_alpha_reassess_input.json",
    "examples/live_metadata_pilot/boundary_report.json",
]
REQUIRED_DOCS = [
    "docs/architecture/LIVE_METADATA_PILOT_BATCH.md",
    "docs/operations/LIVE_METADATA_PILOT_BATCH_RUNBOOK.md",
    "docs/operations/LIVE_METADATA_PILOT_APPROVAL.md",
    "docs/operations/POST_LIVE_METADATA_PILOT_PLAN.md",
    "docs/reference/LIVE_METADATA_PILOT_RESULT.md",
    "docs/reference/LIVE_METADATA_REDACTION_POLICY.md",
]
REQUIRED_CLI = [
    "scripts/eureka_live_metadata_pilot_approval.py",
    "scripts/eureka_live_metadata_pilot_batch.py",
    "scripts/eureka_live_metadata_pilot_report.py",
]
REQUIRED_TRUE = [
    "live_metadata_requires_operator_approval",
    "metadata_only",
    "rate_limit_required",
    "redaction_required",
    "review_required",
]
REQUIRED_FALSE = [
    "raw_live_response_commit_allowed",
    "downloads_enabled",
    "extraction_enabled",
    "accepted_truth_created",
    "reviewed_index_mutation_enabled",
    "public_index_mutation_enabled",
    "master_index_mutation_enabled",
    "public_live_source_fanout_enabled",
    "public_mutation_enabled",
    "model_provider_enabled",
    "deployment_enabled",
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
        "seed_query_matrix_safe": _seed_query_matrix_safe(),
        "request_plan_matrix_safe": _request_plan_matrix_safe(),
        "cli_help_works": _cli_help_works(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "live_metadata_pilot_validation.v0",
        "task": "LIVE-METADATA-PILOT-BATCH-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "operator_live_metadata_run_performed": False,
        "raw_live_response_committed": False,
        "download_performed": False,
        "extraction_executed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _runtime_checks() -> dict[str, bool]:
    approval = load_live_metadata_pilot_approval()
    approval_state = validate_live_metadata_pilot_approval(approval) if approval.get("approval_phrase") else approval
    approval_present = bool(approval.get("approval_phrase"))
    approval_gate_valid = (
        approval_state.get("approval_verified") is True
        if approval_present
        else approval_state.get("approval_verified") is not True
    )
    queries = select_live_metadata_seed_queries()
    plans = build_live_metadata_request_plans(queries)
    dry_run = run_live_metadata_pilot_batch(dry_run=True)
    fixture = run_live_metadata_pilot_batch(fixture=True)
    template = approval_template()
    boundary = fixture["boundary_report"]
    return {
        "approval_template_builds": template["approval_phrase"] == "RUN_BOUNDED_LIVE_METADATA_PILOT",
        "approval_gate_state_valid": approval_gate_valid,
        "selected_query_mix": (
            len([item for item in queries if item["seed_batch_id"] == "seed_batch_frontier_media_00"]) >= 4
            and len([item for item in queries if item["seed_batch_id"] == "seed_batch_legacy_software_00"]) >= 4
        ),
        "request_plans_build": len(plans) == len(queries),
        "request_plans_metadata_only": all(plan["metadata_only"] is True for plan in plans),
        "dry_run_works": dry_run["dry_run_passed"] is True,
        "fixture_mode_works": fixture["fixture_mode_passed"] is True and fixture["candidate_summaries_created"] is True,
        "redaction_builds": fixture["redaction_summary"]["raw_live_response_committed"] is False,
        "candidates_review_only": all(item["accepted_truth"] is False for item in fixture["candidate_packet"]["candidates"]),
        "scout_trails_build": fixture["scout_trails_created"] is True,
        "review_batch_builds": fixture["review_batch_packet_created"] is True,
        "snapshot_handoff_builds": fixture["snapshot_refresh_handoff_created"] is True,
        "public_alpha_reassess_input_builds": fixture["public_alpha_reassess_input_created"] is True,
        "no_accepted_truth": boundary["accepted_truth_created"] is False,
        "no_index_mutation": all(
            boundary[key] is False
            for key in ("reviewed_index_mutated", "master_index_mutated", "public_index_mutated")
        ),
        "no_download_extract_model_deploy": all(
            boundary[key] is False
            for key in ("download_performed", "extraction_executed", "model_provider_used", "deployment_performed")
        ),
        "no_raw_live_response": boundary["raw_live_response_committed"] is False,
        "no_live_run_without_approval": fixture["operator_live_metadata_run_performed"] is False,
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    required = [
        "control/inventory/public_alpha_reassess_result.json",
        "control/inventory/snapshot_refresh_result.json",
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/review_batch_result.json",
        "control/inventory/scout_runtime_result.json",
        "control/inventory/candidate_index_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
        "control/inventory/source_action_kernel_result.json",
        "control/inventory/source_wave_result.json",
        "control/inventory/public_search_ux_model_result.json",
    ]
    if not _paths_exist(required):
        return False
    for path in required:
        payload = _load_json(path)
        if payload.get("status") not in {"pass", "pass_with_warnings", "deferred", "validated"}:
            return False
    reassess = _load_json("control/inventory/public_alpha_reassess_result.json")
    return reassess.get("launch_recommended") is False and reassess.get("needs_live_metadata_pilot") is True


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


def _seed_query_matrix_safe() -> bool:
    path = "control/inventory/live_metadata_pilot_seed_query_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    queries = payload.get("queries", [])
    return (
        len(queries) >= 8
        and sum(1 for item in queries if item.get("seed_batch_id") == "seed_batch_frontier_media_00") >= 4
        and sum(1 for item in queries if item.get("seed_batch_id") == "seed_batch_legacy_software_00") >= 4
        and all(item.get("accepted_truth") is False for item in queries)
    )


def _request_plan_matrix_safe() -> bool:
    path = "control/inventory/live_metadata_pilot_request_plan_matrix.json"
    if not (REPO_ROOT / path).exists():
        return False
    payload = _load_json(path)
    plans = payload.get("request_plans", [])
    return bool(plans) and all(
        plan.get("metadata_only") is True
        and plan.get("downloads_enabled") is False
        and plan.get("raw_response_commit_allowed") is False
        for plan in plans
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
