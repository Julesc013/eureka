#!/usr/bin/env python3
"""Validate PUBLIC-ALPHA-REASSESS-00."""

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
    build_public_alpha_reassess_inventory_packets,
    run_public_alpha_reassess,
    smoke_public_alpha_routes_from_examples,
)


REQUIRED_CONTRACTS = [
    "contracts/publication/public_alpha_reassess.v0.json",
    "contracts/publication/public_alpha_usefulness_metrics.v0.json",
    "contracts/publication/public_alpha_reassess_decision.v0.json",
    "contracts/publication/public_alpha_launch_blocker.v0.json",
    "contracts/publication/public_alpha_next_work_recommendation.v0.json",
    "contracts/publication/public_alpha_reassess_boundary_report.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/public_alpha_reassess_policy.json",
    "control/policies/public_alpha_reassess_threshold_policy.json",
    "control/policies/public_alpha_reassess_route_smoke_policy.json",
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
]
REQUIRED_EXAMPLES = [
    "examples/public_alpha/reassess/public_alpha_reassess_metrics.json",
    "examples/public_alpha/reassess/public_alpha_route_smoke.json",
    "examples/public_alpha/reassess/public_alpha_launch_blockers.json",
    "examples/public_alpha/reassess/public_alpha_next_work.json",
    "examples/public_alpha/reassess/public_alpha_reassess_decision.json",
    "examples/public_alpha/reassess/public_alpha_boundary_report.json",
]
REQUIRED_DOCS = [
    "docs/architecture/PUBLIC_ALPHA_REASSESS.md",
    "docs/operations/PUBLIC_ALPHA_REASSESS_RUNBOOK.md",
    "docs/operations/PUBLIC_ALPHA_USEFULNESS_THRESHOLDS.md",
    "docs/operations/POST_PUBLIC_ALPHA_REASSESS_PLAN.md",
    "docs/reference/PUBLIC_ALPHA_REASSESS_DECISION.md",
    "docs/reference/PUBLIC_ALPHA_USEFULNESS_METRICS.md",
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
    "candidate_only_snapshot_not_enough_for_launch",
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
    }
    checks.update(_runtime_checks())
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "public_alpha_reassess_validation.v0",
        "task": "PUBLIC-ALPHA-REASSESS-00",
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
    route_smoke = smoke_public_alpha_routes_from_examples()
    inventory = build_public_alpha_reassess_inventory_packets(result)
    return {
        "reassessment_example_builds": result["status"] == "pass",
        "route_smoke_example_builds": route_smoke["route_smoke_status"] == "pass",
        "decision_exists": result["decision"]["decision"] == "remain_deferred",
        "current_evidence_counts_recorded": (
            result["reviewed_record_count"] == 1
            and result["candidate_count"] == 28
            and result["known_need_count"] == 28
            and result["absence_summary_count"] == 2
        ),
        "launch_false_when_thresholds_unmet": result["launch_recommended"] is False,
        "demo_mode_recommended": result["demo_mode_recommended"] is True,
        "inventory_packets_build": {
            "public_alpha_reassess_result.json",
            "public_alpha_reassess_boundary_report.json",
            "public_alpha_reassess_launch_blocker_matrix.json",
        }.issubset(set(inventory)),
        "no_deployment_or_launch": all(
            result.get(key) is False for key in ("deployment_performed", "public_launch_performed")
        ),
        "no_readiness_claims": all(
            result.get(key) is False
            for key in ("production_readiness_claimed", "public_launch_readiness_claimed")
        ),
        "no_mutation_or_site_dist": all(
            result.get(key) is False
            for key in ("site_dist_written", "public_mutation_enabled", "public_live_source_fanout_enabled")
        ),
        "no_download_extract_model": all(
            result.get(key) is False
            for key in ("download_performed", "extraction_executed", "model_provider_used")
        ),
    }


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    required = [
        "control/inventory/snapshot_refresh_result.json",
        "control/inventory/seed_batch_frontier_media_result.json",
        "control/inventory/seed_batch_legacy_software_result.json",
        "control/inventory/review_batch_result.json",
        "control/inventory/scout_runtime_result.json",
        "control/inventory/candidate_index_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
        "control/inventory/snapshot_relay_result.json",
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
    return launch_defer.get("public_launch_performed") is False


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
