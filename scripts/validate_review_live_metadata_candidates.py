#!/usr/bin/env python3
"""Validate REVIEW-LIVE-METADATA-CANDIDATES-00."""

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

from runtime.review.live_metadata import run_live_metadata_candidate_review  # noqa: E402


REQUIRED_CONTRACTS = [
    "contracts/review/live_metadata_candidate_review_packet.v0.json",
    "contracts/review/live_metadata_evidence_sufficiency.v0.json",
    "contracts/review/live_metadata_review_decision.v0.json",
    "contracts/review/live_metadata_promotion_preview.v0.json",
    "contracts/review/live_metadata_local_apply_handoff.v0.json",
    "contracts/review/live_metadata_snapshot_refresh_handoff.v0.json",
    "contracts/review/live_metadata_review_boundary_report.v0.json",
    "contracts/candidates/reviewed_metadata_record.v0.json",
    "contracts/candidates/reviewed_source_lead.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/review_live_metadata_candidates_policy.json",
    "control/policies/live_metadata_evidence_sufficiency_policy.json",
    "control/policies/live_metadata_promotion_preview_policy.json",
    "control/policies/live_metadata_review_non_claim_policy.json",
    "control/policies/live_metadata_local_apply_handoff_policy.json",
    "control/policies/live_metadata_snapshot_handoff_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/review_live_metadata_candidates_input_state.json",
    "control/inventory/live_metadata_candidate_review_matrix.json",
    "control/inventory/live_metadata_evidence_sufficiency_matrix.json",
    "control/inventory/live_metadata_review_decision_matrix.json",
    "control/inventory/live_metadata_promotion_preview_matrix.json",
    "control/inventory/live_metadata_local_apply_handoff_matrix.json",
    "control/inventory/live_metadata_snapshot_handoff_matrix.json",
    "control/inventory/live_metadata_public_alpha_reassess_handoff_matrix.json",
    "control/inventory/live_metadata_review_boundary_report.json",
    "control/inventory/live_metadata_review_smoke_result.json",
    "control/inventory/live_metadata_review_validation_matrix.json",
    "control/inventory/live_metadata_review_result.json",
    "control/inventory/live_metadata_review_next_task_decision.json",
    "control/inventory/live_metadata_review_failure_repair_log.json",
]
REQUIRED_EXAMPLES = [
    "examples/review/live_metadata/review_packet.json",
    "examples/review/live_metadata/evidence_sufficiency_matrix.json",
    "examples/review/live_metadata/review_decisions.json",
    "examples/review/live_metadata/promotion_previews.json",
    "examples/review/live_metadata/reviewed_metadata_record_previews.json",
    "examples/review/live_metadata/reviewed_source_lead_previews.json",
    "examples/review/live_metadata/local_apply_handoff.json",
    "examples/review/live_metadata/snapshot_refresh_handoff.json",
    "examples/review/live_metadata/public_alpha_reassess_handoff.json",
    "examples/review/live_metadata/boundary_report.json",
]
REQUIRED_DOCS = [
    "docs/architecture/REVIEW_LIVE_METADATA_CANDIDATES.md",
    "docs/architecture/LIVE_METADATA_EVIDENCE_SUFFICIENCY.md",
    "docs/architecture/LIVE_METADATA_PROMOTION_PREVIEW.md",
    "docs/operations/REVIEW_LIVE_METADATA_CANDIDATES_RUNBOOK.md",
    "docs/operations/POST_REVIEW_LIVE_METADATA_PLAN.md",
    "docs/reference/LIVE_METADATA_REVIEW_DECISION.md",
    "docs/reference/REVIEWED_METADATA_RECORD.md",
    "docs/reference/REVIEWED_SOURCE_LEAD.md",
]
REQUIRED_CLI = [
    "scripts/eureka_review_live_metadata_candidates.py",
    "scripts/eureka_live_metadata_review_report.py",
    "scripts/eureka_live_metadata_promotion_preview.py",
    "scripts/eureka_live_metadata_local_apply_handoff.py",
]
REQUIRED_TRUE = [
    "metadata_only_review",
    "reviewed_metadata_record_allowed",
    "reviewed_source_lead_allowed",
    "local_apply_required_for_any_reviewed_record",
]
REQUIRED_FALSE = [
    "raw_live_response_required",
    "raw_live_response_commit_allowed",
    "verified_download_claim_allowed",
    "malware_clean_claim_allowed",
    "rights_clearance_claim_allowed",
    "automatic_promotion_enabled",
    "reviewed_index_mutation_enabled_by_default",
    "public_index_mutation_enabled",
    "master_index_mutation_enabled",
    "downloads_enabled",
    "extraction_enabled",
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
        "cli_help_works": _cli_help_works(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "live_metadata_review_validation.v0",
        "task": "REVIEW-LIVE-METADATA-CANDIDATES-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "new_live_source_calls_performed": False,
        "raw_live_response_committed": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_live_metadata_candidate_review(from_live_metadata_examples=True)
    boundary = result["boundary_report"]
    decisions = result["review_decisions"]
    previews = result["promotion_previews"]
    return {
        "review_packet_builds": result["review_packet_created"] is True,
        "evidence_sufficiency_builds": len(result["evidence_sufficiency"]) == 8,
        "decisions_build": len(decisions) == 8,
        "promotion_previews_build": len(previews) == 3,
        "local_apply_handoff_builds": result["local_apply_handoff"]["local_apply_executed"] is False,
        "snapshot_refresh_handoff_builds": result["snapshot_refresh_handoff"]["snapshot_refresh_executed"] is False,
        "public_alpha_reassess_handoff_builds": result["public_alpha_reassess_handoff"]["public_alpha_reassess_handoff_only"] is True,
        "candidate_count_recorded": result["live_metadata_candidates_reviewed"] == 8,
        "preview_counts_recorded": (
            result["reviewed_metadata_record_preview_count"] == 1
            and result["reviewed_source_lead_preview_count"] == 2
        ),
        "decision_branch_counts_recorded": (
            result["useful_lead_count"] == 1
            and result["needs_more_evidence_count"] == 2
            and result["rejected_or_duplicate_count"] == 2
        ),
        "prohibited_claims_false": _prohibited_claims_false(result),
        "no_new_live_calls": boundary["new_live_source_calls_performed"] is False,
        "no_raw_responses": boundary["raw_live_response_committed"] is False,
        "no_download_extract_model_deploy": all(
            boundary[key] is False
            for key in ("download_performed", "extraction_executed", "model_provider_used", "deployment_performed")
        ),
        "no_index_mutation": all(
            boundary[key] is False
            for key in ("reviewed_index_mutated", "master_index_mutated", "public_index_mutated")
        ),
        "no_public_launch_claim": boundary["public_launch_readiness_claimed"] is False,
    }


def _prohibited_claims_false(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key in (
            "verified_download_claim_created",
            "malware_clean_claim_created",
            "rights_clearance_claim_created",
            "reviewed_artifact_claim",
            "download_claim",
            "extraction_claim",
            "malware_clean_claim",
            "rights_clearance_claim",
            "accepted_truth_created",
            "accepted_truth",
        ):
            if key in value and value[key] is not False:
                return False
        return all(_prohibited_claims_false(item) for item in value.values())
    if isinstance(value, list):
        return all(_prohibited_claims_false(item) for item in value)
    return True


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prior_results_present() -> bool:
    required = [
        "control/inventory/public_alpha_reassess_01_result.json",
        "control/inventory/snapshot_refresh_01_result.json",
        "control/inventory/live_metadata_pilot_result.json",
        "control/inventory/public_alpha_reassess_result.json",
        "control/inventory/snapshot_refresh_result.json",
        "control/inventory/review_batch_result.json",
        "control/inventory/candidate_index_result.json",
        "control/inventory/scout_runtime_result.json",
        "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
    ]
    if not _paths_exist(required):
        return False
    for path in required:
        payload = _load_json(path)
        if payload.get("status") not in {"pass", "pass_with_warnings", "deferred", "validated"}:
            return False
    pilot = _load_json("control/inventory/live_metadata_pilot_result.json")
    snapshot = _load_json("control/inventory/snapshot_refresh_01_result.json")
    reassess = _load_json("control/inventory/public_alpha_reassess_01_result.json")
    return (
        pilot.get("operator_live_metadata_run_performed") is True
        and pilot.get("raw_live_response_committed") is False
        and snapshot.get("live_metadata_candidate_promoted") is False
        and reassess.get("needs_live_candidate_review") is True
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
