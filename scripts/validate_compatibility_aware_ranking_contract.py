#!/usr/bin/env python3
"""Validate Compatibility-Aware Ranking Contract v0 governance artifacts."""

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_compatibility_target_profile import validate_all_examples as validate_profiles
from scripts.validate_compatibility_aware_ranking_assessment import validate_all_examples as validate_assessments
from scripts.validate_compatibility_explanation import validate_all_examples as validate_explanations

SCHEMAS = [
    REPO_ROOT / "contracts" / "search" / "compatibility_aware_ranking_assessment.v0.json",
    REPO_ROOT / "contracts" / "search" / "compatibility_target_profile.v0.json",
    REPO_ROOT / "contracts" / "search" / "compatibility_explanation.v0.json",
    REPO_ROOT / "contracts" / "search" / "compatibility_factor.v0.json",
]
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "search" / "compatibility_aware_ranking_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "compatibility-aware-ranking-contract-v0"
REPORT_PATH = AUDIT_DIR / "compatibility_aware_ranking_report.json"
DOC_PATH = REPO_ROOT / "docs" / "reference" / "COMPATIBILITY_AWARE_RANKING_CONTRACT.md"
REQUIRED_AUDIT_FILES = {'REMAINING_BLOCKERS.md', 'compatibility_aware_ranking_report.json', 'INCOMPATIBILITY_AND_UNKNOWN_GAP_MODEL.md', 'ARCHITECTURE_CPU_ABI_API_MATCHING_MODEL.md', 'PLATFORM_OS_VERSION_MATCHING_MODEL.md', 'RUNTIME_AND_DEPENDENCY_REQUIREMENT_MODEL.md', 'NO_RUNTIME_NO_RANKING_CHANGE_NO_MUTATION_POLICY.md', 'ACTION_SAFETY_AND_INSTALLABILITY_CAUTION_MODEL.md', 'FUTURE_RUNTIME_PATH.md', 'README.md', 'EMULATOR_VM_RECONSTRUCTION_FEASIBILITY_MODEL.md', 'COMPATIBILITY_TARGET_PROFILE_SCHEMA.md', 'NO_INSTALLABILITY_WITHOUT_EVIDENCE_POLICY.md', 'COMPATIBILITY_RANKING_ASSESSMENT_SCHEMA.md', 'TIE_BREAK_POLICY.md', 'NEXT_STEPS.md', 'COMMAND_RESULTS.md', 'INTEGRATION_BOUNDARIES.md', 'SOURCE_PROVENANCE_CANDIDATE_CAUTION_MODEL.md', 'COMPATIBILITY_FACTOR_TAXONOMY.md', 'RIGHTS_RISK_CAUTION_MODEL.md', 'CONTRACT_SUMMARY.md', 'COMPATIBILITY_EVIDENCE_STRENGTH_MODEL.md', 'HARDWARE_PERIPHERAL_DRIVER_REQUIREMENT_MODEL.md', 'EXAMPLE_COMPATIBILITY_RANKING_REVIEW.md', 'COMPATIBILITY_EXPLANATION_SCHEMA.md'}
REPORT_FALSE_FIELDS = {
    "runtime_compatibility_ranking_implemented", "persistent_compatibility_ranking_store_implemented",
    "compatibility_ranking_applied_to_live_search", "public_search_order_changed", "result_suppressed",
    "hidden_suppression_performed", "candidate_promotion_performed", "installability_claimed",
    "compatibility_truth_claimed", "dependency_safety_claimed", "emulator_vm_launch_enabled",
    "package_manager_invoked", "executable_inspected", "downloads_enabled", "installs_enabled",
    "execution_enabled", "master_index_mutation_allowed", "public_index_mutation_allowed",
    "local_index_mutation_allowed", "source_cache_mutation_allowed", "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed", "live_source_called", "external_calls_performed",
    "telemetry_implemented", "popularity_signal_allowed", "user_profile_signal_allowed", "ad_signal_allowed",
    "random_tie_break_allowed",
}
POLICY_FALSE_FIELDS = {
    "runtime_compatibility_ranking_implemented", "persistent_compatibility_ranking_store_implemented",
    "public_search_order_changed", "compatibility_ranking_applied_to_live_search", "hidden_suppression_allowed",
    "result_suppression_allowed_without_explanation", "candidate_promotion_allowed",
    "master_index_mutation_allowed", "public_index_mutation_allowed", "local_index_mutation_allowed",
    "source_cache_mutation_allowed", "evidence_ledger_mutation_allowed", "candidate_index_mutation_allowed",
    "installability_claim_allowed_without_evidence", "dependency_safety_claim_allowed",
    "malware_safety_claim_allowed", "emulator_vm_launch_allowed", "package_manager_invocation_allowed",
    "executable_inspection_allowed", "popularity_signal_allowed", "user_profile_signal_allowed",
    "ad_signal_allowed", "telemetry_signal_allowed", "random_tie_break_allowed",
}
POLICY_TRUE_FIELDS = {"compatibility_evidence_required", "unknown_gap_transparency_required", "absence_of_evidence_is_not_incompatibility"}
DOC_PHRASES = {
    "contract-only", "compatibility-aware ranking is not runtime yet", "compatibility-aware ranking is not compatibility truth",
    "not installability proof", "not dependency safety proof", "not malware safety", "does not launch emulators/vms or package managers",
    "compatibility target profile", "platform/os/version", "architecture/cpu/abi/api", "runtime/dependency",
    "hardware/peripheral/driver", "emulator/vm/reconstruction", "compatibility evidence", "absence of evidence is not incompatibility",
    "source trust is not claimed", "candidate confidence is not compatibility truth", "no runtime ranking", "no public search order change",
    "no hidden suppression", "candidate promotion", "source cache", "evidence ledger", "candidate index", "no mutation",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_false(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not False:
            errors.append(f"{prefix}.{field} must be false")


def validate_contract() -> list[str]:
    errors: list[str] = []
    for schema in SCHEMAS:
        if not schema.exists():
            errors.append(f"missing schema: {schema}")
            continue
        try:
            data = load_json(schema)
        except Exception as exc:
            errors.append(f"{schema} failed to parse: {exc}")
            continue
        if not isinstance(data.get("required"), list):
            errors.append(f"{schema} required must be a list")
    for path in (POLICY_PATH, DOC_PATH, REPORT_PATH):
        if not path.exists():
            errors.append(f"missing required artifact: {path}")
    if AUDIT_DIR.exists():
        missing = sorted(name for name in REQUIRED_AUDIT_FILES if not (AUDIT_DIR / name).exists())
        if missing:
            errors.append(f"audit pack missing files: {', '.join(missing)}")
    else:
        errors.append(f"missing audit directory: {AUDIT_DIR}")
    if POLICY_PATH.exists():
        policy = load_json(POLICY_PATH)
        if isinstance(policy, Mapping):
            check_false(policy, POLICY_FALSE_FIELDS, "policy", errors)
            for field in POLICY_TRUE_FIELDS:
                if policy.get(field) is not True:
                    errors.append(f"policy.{field} must be true")
        else:
            errors.append("policy must be an object")
    if REPORT_PATH.exists():
        report = load_json(REPORT_PATH)
        if isinstance(report, Mapping):
            check_false(report, REPORT_FALSE_FIELDS, "report", errors)
            if report.get("runtime_status") != "contract_only_not_implemented":
                errors.append("report.runtime_status must be contract_only_not_implemented")
        else:
            errors.append("report must be an object")
    if DOC_PATH.exists():
        text = DOC_PATH.read_text(encoding="utf-8").lower()
        for phrase in sorted(DOC_PHRASES):
            if phrase not in text:
                errors.append(f"doc missing phrase: {phrase}")
    _, profile_errors = validate_profiles()
    _, assessment_errors = validate_assessments()
    _, explanation_errors = validate_explanations()
    errors.extend(profile_errors)
    errors.extend(assessment_errors)
    errors.extend(explanation_errors)
    return errors


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors = validate_contract()
    status = "invalid" if errors else "valid"
    if args.json:
        print(json.dumps({"status": status, "report_id": "compatibility_aware_ranking_contract_v0", "profile_example_count": len(validate_profiles()[0]), "assessment_example_count": len(validate_assessments()[0]), "explanation_example_count": len(validate_explanations()[0]), "contract_files": [str(p.relative_to(REPO_ROOT)) for p in SCHEMAS], "audit_dir": str(AUDIT_DIR.relative_to(REPO_ROOT)), "errors": errors}, indent=2), file=stdout)
    else:
        print(f"status: {status}", file=stdout)
        for error in errors:
            print(f"ERROR: {error}", file=stdout)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
