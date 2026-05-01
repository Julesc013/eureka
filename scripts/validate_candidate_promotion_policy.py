#!/usr/bin/env python3
"""Validate Candidate Promotion Policy v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_candidate_promotion_assessment import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "candidate_promotion_assessment.v0.json"
DECISION_PATH = REPO_ROOT / "contracts" / "query" / "candidate_promotion_decision.v0.json"
POLICY_CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "candidate_promotion_policy.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_promotion_policy.json"
CANDIDATE_INDEX_POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_index_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "candidate-promotion-policy-v0"
REPORT_PATH = AUDIT_DIR / "candidate_promotion_policy_report.json"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "POLICY_SUMMARY.md",
    "PROMOTION_ASSESSMENT_SCHEMA.md",
    "PROMOTION_DECISION_TAXONOMY.md",
    "ELIGIBILITY_GATES.md",
    "REJECTION_QUARANTINE_SUPERSESSION_GATES.md",
    "EVIDENCE_SUFFICIENCY_MODEL.md",
    "PROVENANCE_SUFFICIENCY_MODEL.md",
    "SOURCE_POLICY_GATES.md",
    "PRIVACY_RIGHTS_RISK_GATES.md",
    "CONFLICT_AND_DUPLICATE_GATES.md",
    "CONFIDENCE_AND_REVIEW_MODEL.md",
    "HUMAN_POLICY_OPERATOR_APPROVAL_MODEL.md",
    "NO_AUTO_PROMOTION_AND_NO_MUTATION_POLICY.md",
    "PUBLIC_VISIBILITY_AND_RESULT_SURFACING_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_PROMOTION_ASSESSMENT_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "candidate_promotion_policy_report.json",
}

REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "assessment_id",
    "assessment_kind",
    "status",
    "created_by_tool",
    "candidate_ref",
    "candidate_summary",
    "assessment_scope",
    "eligibility_gates",
    "evidence_sufficiency",
    "provenance_sufficiency",
    "source_policy_assessment",
    "privacy_assessment",
    "rights_and_risk_assessment",
    "conflict_assessment",
    "confidence_assessment",
    "review_requirements",
    "recommended_decision",
    "decision_rationale",
    "future_outputs",
    "limitations",
    "no_auto_promotion_guarantees",
    "no_mutation_guarantees",
    "notes",
}

REQUIRED_POLICY_FALSE = {
    "runtime_promotion_implemented",
    "automatic_promotion_allowed",
    "candidate_promotion_runtime_implemented",
    "master_index_mutation_allowed",
    "source_registry_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_search_candidate_injection_allowed",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "destructive_merge_allowed",
}

REQUIRED_POLICY_TRUE = {
    "privacy_filter_required",
    "evidence_required_for_promotion_review",
    "provenance_required_for_promotion_review",
    "human_or_policy_review_required",
    "rights_risk_review_required",
    "conflict_review_required",
}

REQUIRED_REPORT_FALSE = {
    "runtime_promotion_implemented",
    "automatic_promotion_allowed",
    "candidate_promotion_runtime_implemented",
    "promotion_performed",
    "accepted_as_truth",
    "promoted_to_master_index",
    "master_index_mutation_allowed",
    "source_registry_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_search_candidate_injection_allowed",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "external_calls_performed",
    "live_probes_enabled",
}

REQUIRED_RUNTIME_FALSE = {
    "runtime_promotion_implemented",
    "automatic_promotion_allowed",
    "candidate_promotion_runtime_implemented",
    "review_queue_runtime_implemented",
    "candidate_index_runtime_implemented",
    "source_cache_runtime_implemented",
    "evidence_ledger_runtime_implemented",
    "telemetry_implemented",
    "public_search_runtime_wired",
}

REQUIRED_DOCS = {
    "docs/reference/CANDIDATE_PROMOTION_POLICY.md": (
        "promotion policy is not promotion runtime",
        "candidate promotion runtime is not implemented",
        "candidate confidence is not truth",
        "promotion assessment is not master-index mutation",
        "automatic promotion is forbidden",
        "destructive merge is forbidden",
        "rights clearance and malware safety are not claimed",
    ),
    "docs/reference/CANDIDATE_INDEX_CONTRACT.md": (
        "candidate promotion policy",
        "does not implement candidate promotion runtime",
        "candidate confidence remains not truth",
    ),
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "candidate promotion policy v0",
        "candidate confidence is not truth",
        "automatic promotion is forbidden",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "ip address",
        "account id",
        "private path",
        "candidate promotion",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "no persistent query logging",
        "candidate promotion",
        "contract-only",
    ),
}

FORBIDDEN_CLAIMS = (
    "hosted query intelligence is live",
    "candidate promotion runtime exists",
    "candidate promotion has occurred",
    "source cache runtime exists",
    "evidence ledger runtime exists",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
    "automatic promotion is enabled",
    "master index was mutated",
    "external calls were performed",
)


def validate_candidate_promotion_policy() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/candidate_promotion_assessment.v0.json")
    if contract:
        _validate_assessment_contract(contract, errors)

    decision = _read_json_object(DECISION_PATH, errors, "contracts/query/candidate_promotion_decision.v0.json")
    if decision:
        _validate_auxiliary_contract(decision, "candidate_promotion_decision.v0.json", errors)

    policy_contract = _read_json_object(POLICY_CONTRACT_PATH, errors, "contracts/query/candidate_promotion_policy.v0.json")
    if policy_contract:
        _validate_auxiliary_contract(policy_contract, "candidate_promotion_policy.v0.json", errors)

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/candidate_promotion_policy.json")
    if policy:
        _validate_policy(policy, errors)

    candidate_index_policy = _read_json_object(CANDIDATE_INDEX_POLICY_PATH, errors, "control/inventory/query_intelligence/candidate_index_policy.json")
    if candidate_index_policy:
        notes = "\n".join(str(note).casefold() for note in candidate_index_policy.get("notes", []))
        if "candidate promotion policy" not in notes and candidate_index_policy.get("candidate_promotion_policy_status") != "contract_only_p65":
            errors.append("candidate_index_policy must reference P65 candidate promotion policy as contract-only.")

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("candidate promotion examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    folded = _scan_governed_text().casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime, acceptance, mutation, or safety claim present: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "candidate_promotion_policy_validator_v0",
        "contract_file": "contracts/query/candidate_promotion_assessment.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_assessment_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("candidate_promotion_assessment.v0.json x-status must be contract_only.")
    for key in (
        "x-runtime_promotion_implemented",
        "x-automatic_promotion_allowed",
        "x-candidate_promotion_runtime_implemented",
        "x-master_index_mutation_allowed",
        "x-source_registry_mutation_allowed",
        "x-source_cache_mutation_allowed",
        "x-evidence_ledger_mutation_allowed",
        "x-public_index_mutation_allowed",
        "x-local_index_mutation_allowed",
        "x-candidate_index_mutation_allowed",
        "x-public_search_candidate_injection_allowed",
        "x-telemetry_implemented",
        "x-external_calls_allowed",
        "x-live_probes_allowed",
    ):
        if contract.get(key) is not False:
            errors.append(f"candidate_promotion_assessment.v0.json {key} must be false.")

    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"candidate_promotion_assessment.v0.json missing required fields: {', '.join(missing)}")

    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("candidate_promotion_assessment.v0.json properties must be an object.")
    else:
        for field in sorted(REQUIRED_CONTRACT_FIELDS):
            if field not in properties:
                errors.append(f"candidate_promotion_assessment.v0.json properties missing {field}.")

    defs = contract.get("$defs")
    if not isinstance(defs, Mapping):
        errors.append("candidate_promotion_assessment.v0.json $defs must be an object.")
        return
    for key in (
        "allowed_statuses",
        "allowed_decisions",
        "allowed_gate_types",
        "allowed_evidence_statuses",
        "allowed_provenance_statuses",
        "allowed_source_policy_statuses",
        "allowed_privacy_statuses",
        "allowed_rights_statuses",
        "allowed_risk_statuses",
        "allowed_conflict_statuses",
        "allowed_future_outputs",
    ):
        if not isinstance(defs.get(key), list) or not defs.get(key):
            errors.append(f"candidate_promotion_assessment.v0.json $defs.{key} must be a non-empty list.")


def _validate_auxiliary_contract(contract: Mapping[str, Any], label: str, errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append(f"{label} x-status must be contract_only.")
    for key in ("x-runtime_promotion_implemented", "x-automatic_promotion_allowed", "x-master_index_mutation_allowed"):
        if key in contract and contract.get(key) is not False:
            errors.append(f"{label} {key} must be false.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("candidate_promotion_policy status must be contract_only.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"candidate_promotion_policy.{key} must be false.")
    for key in sorted(REQUIRED_POLICY_TRUE):
        if policy.get(key) is not True:
            errors.append(f"candidate_promotion_policy.{key} must be true.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list):
        errors.append("candidate_promotion_policy.next_contracts must be a list.")
    else:
        for item in ("known_absence_page", "query_privacy_poisoning_guard", "demand_dashboard", "source_sync_worker", "source_cache_evidence_ledger"):
            if item not in next_contracts:
                errors.append(f"candidate_promotion_policy.next_contracts missing {item}.")


def _validate_docs(errors: list[str]) -> None:
    for rel_path, phrases in sorted(REQUIRED_DOCS.items()):
        path = REPO_ROOT / rel_path
        if not path.is_file():
            errors.append(f"{rel_path}: missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase.casefold() not in text:
                errors.append(f"{rel_path}: missing phrase '{phrase}'.")


def _validate_audit_pack(errors: list[str], warnings: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/candidate-promotion-policy-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P65 audit files: {', '.join(missing)}")

    report = _read_json_object(REPORT_PATH, errors, "candidate_promotion_policy_report.json")
    if not report:
        return
    if report.get("report_id") != "candidate_promotion_policy_v0":
        errors.append("report_id must be candidate_promotion_policy_v0.")
    if report.get("contract_file") != "contracts/query/candidate_promotion_assessment.v0.json":
        errors.append("report contract_file must point to contracts/query/candidate_promotion_assessment.v0.json.")

    hard = report.get("no_auto_promotion_no_mutation_guarantees")
    if not isinstance(hard, Mapping):
        errors.append("report no_auto_promotion_no_mutation_guarantees must be present.")
    else:
        for key in sorted(REQUIRED_REPORT_FALSE):
            if hard.get(key) is not False:
                errors.append(f"report no_auto_promotion_no_mutation_guarantees.{key} must be false.")

    runtime = report.get("runtime_status")
    if not isinstance(runtime, Mapping):
        errors.append("report runtime_status must be present.")
    else:
        for key in sorted(REQUIRED_RUNTIME_FALSE):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")

    if report.get("next_recommended_branch") != "P66 Known Absence Page v0":
        errors.append("next_recommended_branch must be P66 Known Absence Page v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P65 is contract-only; candidate promotion runtime remains deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        DECISION_PATH,
        POLICY_CONTRACT_PATH,
        POLICY_PATH,
        CANDIDATE_INDEX_POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "CANDIDATE_PROMOTION_POLICY.md",
        REPO_ROOT / "docs" / "reference" / "CANDIDATE_INDEX_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
        REPO_ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.is_file())


def _report_id() -> str | None:
    if not REPORT_PATH.is_file():
        return None
    try:
        payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload.get("report_id") if isinstance(payload, Mapping) else None


def _read_json_object(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"{label}: missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{label}: top-level JSON must be an object.")
        return {}
    return payload


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Candidate Promotion Policy validation",
        f"status: {report['status']}",
        f"contract_file: {report.get('contract_file')}",
        f"report_id: {report.get('report_id')}",
        f"example_count: {report.get('example_count')}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_candidate_promotion_policy()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
