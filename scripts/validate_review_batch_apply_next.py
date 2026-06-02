#!/usr/bin/env python3
"""Validate REVIEW-BATCH-APPLY-NEXT-00."""

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

from runtime.local_apply import run_review_batch_apply_next  # noqa: E402


REQUIRED_CONTRACTS = [
    "contracts/local_apply/review_batch_apply_plan.v0.json",
    "contracts/local_apply/review_batch_apply_eligibility.v0.json",
    "contracts/local_apply/review_batch_apply_decision.v0.json",
    "contracts/local_apply/review_batch_apply_result.v0.json",
    "contracts/review/limited_reviewed_metadata_record.v0.json",
    "contracts/review/limited_reviewed_source_lead.v0.json",
    "contracts/review/reviewed_known_need.v0.json",
    "contracts/review/reviewed_bounded_absence.v0.json",
    "contracts/local_apply/review_batch_apply_boundary_report.v0.json",
    "contracts/local_apply/review_batch_apply_rollback_plan.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/review_batch_apply_next_policy.json",
    "control/policies/review_batch_apply_eligibility_policy.json",
    "control/policies/review_batch_apply_evidence_sufficiency_policy.json",
    "control/policies/review_batch_apply_local_apply_policy.json",
    "control/policies/review_batch_apply_known_need_policy.json",
    "control/policies/review_batch_apply_absence_policy.json",
    "control/policies/review_batch_apply_non_claim_policy.json",
    "control/policies/review_batch_apply_rollback_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/review_batch_apply_next_input_state.json",
    "control/inventory/review_batch_apply_next_candidate_matrix.json",
    "control/inventory/review_batch_apply_next_eligibility_matrix.json",
    "control/inventory/review_batch_apply_next_evidence_sufficiency_matrix.json",
    "control/inventory/review_batch_apply_next_decision_matrix.json",
    "control/inventory/review_batch_apply_next_apply_plan_matrix.json",
    "control/inventory/review_batch_apply_next_temp_apply_matrix.json",
    "control/inventory/review_batch_apply_next_reviewed_record_matrix.json",
    "control/inventory/review_batch_apply_next_known_need_matrix.json",
    "control/inventory/review_batch_apply_next_absence_matrix.json",
    "control/inventory/review_batch_apply_next_non_applied_matrix.json",
    "control/inventory/review_batch_apply_next_snapshot_handoff_matrix.json",
    "control/inventory/review_batch_apply_next_public_alpha_reassess_handoff_matrix.json",
    "control/inventory/review_batch_apply_next_boundary_report.json",
    "control/inventory/review_batch_apply_next_smoke_result.json",
    "control/inventory/review_batch_apply_next_validation_matrix.json",
    "control/inventory/review_batch_apply_next_result.json",
    "control/inventory/review_batch_apply_next_next_task_decision.json",
    "control/inventory/review_batch_apply_next_failure_repair_log.json",
]
REQUIRED_EXAMPLES = [
    "examples/review_batch/apply_next/apply_inputs.json",
    "examples/review_batch/apply_next/eligibility_matrix.json",
    "examples/review_batch/apply_next/evidence_sufficiency_matrix.json",
    "examples/review_batch/apply_next/apply_plan.json",
    "examples/review_batch/apply_next/apply_validation.json",
    "examples/review_batch/apply_next/temp_apply_result.json",
    "examples/review_batch/apply_next/limited_reviewed_metadata_records.json",
    "examples/review_batch/apply_next/limited_reviewed_source_leads.json",
    "examples/review_batch/apply_next/reviewed_known_needs.json",
    "examples/review_batch/apply_next/reviewed_bounded_absences.json",
    "examples/review_batch/apply_next/non_applied_candidates.json",
    "examples/review_batch/apply_next/rollback_plan.json",
    "examples/review_batch/apply_next/snapshot_refresh_handoff.json",
    "examples/review_batch/apply_next/public_alpha_reassess_handoff.json",
    "examples/review_batch/apply_next/boundary_report.json",
]
REQUIRED_DOCS = [
    "docs/architecture/REVIEW_BATCH_APPLY_NEXT.md",
    "docs/architecture/REVIEW_BATCH_APPLY_ELIGIBILITY.md",
    "docs/architecture/LIMITED_REVIEWED_RECORD_MODEL.md",
    "docs/operations/REVIEW_BATCH_APPLY_NEXT_RUNBOOK.md",
    "docs/operations/POST_REVIEW_BATCH_APPLY_NEXT_PLAN.md",
    "docs/reference/REVIEW_BATCH_APPLY_PLAN.md",
    "docs/reference/REVIEW_BATCH_APPLY_DECISION.md",
    "docs/reference/LIMITED_REVIEWED_RECORD.md",
]
REQUIRED_CLI = [
    "scripts/eureka_review_batch_apply_validate.py",
    "scripts/eureka_review_batch_apply_next.py",
    "scripts/eureka_review_batch_apply_report.py",
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
        "cli_help_works": _cli_help_works(),
        "policies_safe": _policies_safe(),
    }
    checks.update(_runtime_checks())
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "review_batch_apply_next_validation_result.v0",
        "task": "REVIEW-BATCH-APPLY-NEXT-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "artifact_verified_claim_created": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "compatibility_guarantee_claim_created": False,
        "scan_completeness_claim_created": False,
        "ocr_quality_claim_created": False,
        "download_performed": False,
        "file_fetch_performed": False,
        "ocr_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)
    boundary = result["boundary_report"]
    return {
        "input_collection_builds": result["total_candidates_considered"] == 68,
        "eligibility_matrix_exists": len(result["eligibility_matrix"]) == 68,
        "evidence_sufficiency_builds": len(result["evidence_sufficiency_matrix"]) == 68,
        "apply_plan_builds": result["eligible_apply_count"] == 12,
        "apply_validation_passes": result["apply_validation"]["status"] == "pass",
        "temp_apply_proof_exists": result["temp_instance_apply_passed"] is True,
        "reviewed_record_counts_match": (
            result["limited_reviewed_metadata_records_created"] == 4
            and result["limited_reviewed_source_leads_created"] == 4
            and result["reviewed_record_delta_count"] == 8
        ),
        "known_need_absence_counts_match": (
            result["reviewed_known_needs_created"] == 2
            and result["reviewed_bounded_absences_created"] == 2
        ),
        "non_applied_report_exists": result["non_applied_count"] == 60,
        "rollback_plan_created": result["rollback_plan_created"] is True,
        "handoffs_exist": (
            result["snapshot_refresh_handoff"]["snapshot_refresh_handoff_only"] is True
            and result["public_alpha_reassess_handoff"]["public_alpha_reassess_handoff_only"] is True
        ),
        "prohibited_claims_false": _prohibited_claims_false(result),
        "no_operator_instance_mutation": boundary["operator_instance_mutated"] is False,
        "no_public_or_master_mutation": (
            boundary["public_index_mutated"] is False and boundary["master_index_mutated"] is False
        ),
        "no_site_dist_write": boundary["site_dist_written"] is False,
        "no_download_fetch_ocr_extract_model_deploy": all(
            boundary[key] is False
            for key in (
                "download_performed",
                "file_fetch_performed",
                "ocr_performed",
                "extraction_executed",
                "model_provider_used",
                "deployment_performed",
            )
        ),
    }


def _policies_safe() -> bool:
    if not _paths_exist(REQUIRED_POLICIES):
        return False
    for path in REQUIRED_POLICIES:
        payload = _load_json(path)
        if payload.get("eligible_record_kinds") != [
            "limited_reviewed_metadata_record",
            "limited_reviewed_source_lead",
            "reviewed_known_need",
            "reviewed_bounded_absence",
        ]:
            return False
        for key in (
            "apply_requires_review_batch_decision",
            "apply_requires_evidence_sufficiency",
            "operator_instance_apply_requires_explicit_approval",
            "rollback_plan_required",
        ):
            if key in payload and payload.get(key) is not True:
                return False
        for key in (
            "public_apply_enabled",
            "public_mutation_enabled",
            "master_index_mutation_enabled",
            "public_index_mutation_enabled",
            "reviewed_index_mutation_enabled_by_default",
            "reviewed_artifact_record_creation_enabled",
            "artifact_verification_claim_allowed",
            "verified_download_claim_allowed",
            "malware_clean_claim_allowed",
            "rights_clearance_claim_allowed",
            "compatibility_guarantee_claim_allowed",
            "scan_completeness_claim_allowed",
            "ocr_quality_claim_allowed",
            "downloads_enabled",
            "extraction_enabled",
            "file_fetch_enabled",
            "ocr_enabled",
            "install_execution_enabled",
            "model_provider_enabled",
            "deployment_enabled",
        ):
            if key in payload and payload.get(key) is not False:
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


def _paths_exist(paths: Sequence[str]) -> bool:
    return all((REPO_ROOT / path).exists() for path in paths)


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _prohibited_claims_false(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key in (
            "artifact_verified",
            "artifact_verified_claim_created",
            "verified_download_claim",
            "verified_download_claim_created",
            "malware_clean_claim",
            "malware_clean_claim_created",
            "rights_clearance_claim",
            "rights_clearance_claim_created",
            "compatibility_guarantee_claim",
            "compatibility_guarantee_claim_created",
            "scan_completeness_claim",
            "scan_completeness_claim_created",
            "ocr_quality_claim",
            "ocr_quality_claim_created",
            "download_claim",
            "extraction_claim",
            "accepted_truth_created",
        ):
            if key in value and value[key] is not False:
                return False
        return all(_prohibited_claims_false(item) for item in value.values())
    if isinstance(value, list):
        return all(_prohibited_claims_false(item) for item in value)
    return True


if __name__ == "__main__":
    raise SystemExit(main())
