#!/usr/bin/env python3
"""Validate LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00."""

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

from runtime.local_apply import run_local_apply_live_metadata_previews  # noqa: E402


REQUIRED_CONTRACTS = [
    "contracts/local_apply/live_metadata_local_apply_plan.v0.json",
    "contracts/local_apply/live_metadata_local_apply_validation.v0.json",
    "contracts/local_apply/live_metadata_local_apply_result.v0.json",
    "contracts/local_apply/live_metadata_apply_boundary_report.v0.json",
    "contracts/local_apply/live_metadata_apply_rollback_plan.v0.json",
    "contracts/review/live_metadata_reviewed_record.v0.json",
    "contracts/review/live_metadata_source_lead.v0.json",
]
REQUIRED_POLICIES = [
    "control/policies/local_apply_live_metadata_previews_policy.json",
    "control/policies/live_metadata_apply_validation_policy.json",
    "control/policies/live_metadata_reviewed_record_policy.json",
    "control/policies/live_metadata_source_lead_policy.json",
    "control/policies/live_metadata_apply_non_claim_policy.json",
    "control/policies/live_metadata_operator_instance_apply_policy.json",
    "control/policies/live_metadata_apply_rollback_policy.json",
]
REQUIRED_MATRICES = [
    "control/inventory/local_apply_live_metadata_input_state.json",
    "control/inventory/local_apply_live_metadata_preview_matrix.json",
    "control/inventory/local_apply_live_metadata_eligibility_matrix.json",
    "control/inventory/local_apply_live_metadata_apply_plan_matrix.json",
    "control/inventory/local_apply_live_metadata_validation_matrix.json",
    "control/inventory/local_apply_live_metadata_temp_apply_matrix.json",
    "control/inventory/local_apply_live_metadata_reviewed_record_matrix.json",
    "control/inventory/local_apply_live_metadata_source_lead_matrix.json",
    "control/inventory/local_apply_live_metadata_snapshot_handoff_matrix.json",
    "control/inventory/local_apply_live_metadata_public_alpha_reassess_handoff_matrix.json",
    "control/inventory/local_apply_live_metadata_boundary_report.json",
    "control/inventory/local_apply_live_metadata_smoke_result.json",
    "control/inventory/local_apply_live_metadata_result.json",
    "control/inventory/local_apply_live_metadata_next_task_decision.json",
    "control/inventory/local_apply_live_metadata_failure_repair_log.json",
]
REQUIRED_EXAMPLES = [
    "examples/local_apply/live_metadata/apply_plan.json",
    "examples/local_apply/live_metadata/apply_validation.json",
    "examples/local_apply/live_metadata/temp_apply_result.json",
    "examples/local_apply/live_metadata/reviewed_metadata_records.json",
    "examples/local_apply/live_metadata/reviewed_source_leads.json",
    "examples/local_apply/live_metadata/rollback_plan.json",
    "examples/local_apply/live_metadata/snapshot_refresh_handoff.json",
    "examples/local_apply/live_metadata/public_alpha_reassess_handoff.json",
    "examples/local_apply/live_metadata/boundary_report.json",
]
REQUIRED_DOCS = [
    "docs/architecture/LOCAL_APPLY_LIVE_METADATA_PREVIEWS.md",
    "docs/architecture/LIVE_METADATA_REVIEWED_RECORD_MODEL.md",
    "docs/architecture/LIVE_METADATA_SOURCE_LEAD_MODEL.md",
    "docs/operations/LOCAL_APPLY_LIVE_METADATA_PREVIEWS_RUNBOOK.md",
    "docs/operations/POST_LOCAL_APPLY_LIVE_METADATA_PLAN.md",
    "docs/reference/LIVE_METADATA_LOCAL_APPLY_PLAN.md",
    "docs/reference/LIVE_METADATA_REVIEWED_RECORD.md",
    "docs/reference/LIVE_METADATA_SOURCE_LEAD.md",
]
REQUIRED_CLI = [
    "scripts/eureka_local_apply_preview_validate.py",
    "scripts/eureka_local_apply_live_metadata_previews.py",
    "scripts/eureka_local_apply_live_metadata_report.py",
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
        "schema_version": "local_apply_live_metadata_validation_result.v0",
        "task": "LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00",
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "operator_instance_mutated": False,
        "committed_instance_state": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "verified_download_claim_created": False,
        "malware_clean_claim_created": False,
        "rights_clearance_claim_created": False,
        "artifact_verified_claim_created": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _runtime_checks() -> dict[str, bool]:
    result = run_local_apply_live_metadata_previews(from_live_metadata_review_examples=True, use_temp_instance=True)
    boundary = result["boundary_report"]
    return {
        "apply_plan_builds": result["apply_plan"]["eligible_preview_count"] == 3,
        "apply_validation_passes": result["apply_validation"]["status"] == "pass",
        "temp_apply_proof_exists": result["temp_instance_apply_passed"] is True,
        "reviewed_metadata_record_count": result["reviewed_metadata_records_created"] == 1,
        "reviewed_source_lead_count": result["reviewed_source_leads_created"] == 2,
        "non_eligible_not_applied": (
            result["useful_leads_not_applied"] == 1
            and result["needs_more_evidence_not_applied"] == 2
            and result["rejected_or_duplicate_not_applied"] == 2
        ),
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
        "no_download_extract_model_deploy": all(
            boundary[key] is False
            for key in ("download_performed", "extraction_executed", "model_provider_used", "deployment_performed")
        ),
    }


def _policies_safe() -> bool:
    if not _paths_exist(REQUIRED_POLICIES):
        return False
    for path in REQUIRED_POLICIES:
        payload = _load_json(path)
        if payload.get("eligible_preview_kinds") != ["reviewed_metadata_record_preview", "reviewed_source_lead_preview"]:
            return False
        for key in (
            "useful_leads_not_auto_applied",
            "needs_more_evidence_not_applied",
            "rejected_or_duplicate_not_applied",
            "local_apply_required",
            "operator_instance_apply_requires_explicit_approval",
            "reviewed_record_scope_limited_to_metadata_or_source_lead",
            "rollback_plan_required",
        ):
            if key in payload and payload.get(key) is not True:
                return False
        for key in (
            "public_apply_enabled",
            "public_mutation_enabled",
            "verified_download_claim_allowed",
            "malware_clean_claim_allowed",
            "rights_clearance_claim_allowed",
            "artifact_verification_claim_allowed",
            "downloads_enabled",
            "extraction_enabled",
            "model_provider_enabled",
            "public_index_mutation_enabled",
            "master_index_mutation_enabled",
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
            "verified_download_claim",
            "verified_download_claim_created",
            "malware_clean_claim",
            "malware_clean_claim_created",
            "rights_clearance_claim",
            "rights_clearance_claim_created",
            "artifact_verified",
            "artifact_verified_claim_created",
            "download_claim",
            "extraction_claim",
            "accepted_truth",
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
