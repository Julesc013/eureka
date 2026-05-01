#!/usr/bin/env python3
"""Validate Known Absence Page v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_known_absence_page import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "known_absence_page.v0.json"
GAP_CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "known_absence_gap.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "known_absence_page_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "known-absence-page-v0"
REPORT_PATH = AUDIT_DIR / "known_absence_page_report.json"

PRIOR_POLICY_PATHS = [
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "query_observation_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_result_cache_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_miss_ledger_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_need_record_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "probe_queue_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_index_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_promotion_policy.json",
]
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "KNOWN_ABSENCE_PAGE_SCHEMA.md",
    "SCOPED_ABSENCE_MODEL.md",
    "CHECKED_AND_NOT_CHECKED_MODEL.md",
    "NEAR_MISS_MODEL.md",
    "GAP_EXPLANATION_MODEL.md",
    "SAFE_NEXT_ACTION_MODEL.md",
    "USER_FACING_PAGE_SECTIONS.md",
    "API_RESPONSE_PROJECTION.md",
    "STATIC_DEMO_PROJECTION.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "RIGHTS_AND_RISK_POLICY.md",
    "NO_GLOBAL_ABSENCE_AND_NO_MUTATION_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_KNOWN_ABSENCE_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "known_absence_page_report.json",
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "absence_page_id",
    "absence_page_kind",
    "status",
    "created_by_tool",
    "query_context",
    "absence_summary",
    "checked_scope",
    "not_checked_scope",
    "near_misses",
    "weak_hits",
    "gap_explanations",
    "source_status_summary",
    "evidence_context",
    "candidate_context",
    "safe_next_actions",
    "user_facing_sections",
    "api_projection",
    "static_projection",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_global_absence_guarantees",
    "no_mutation_guarantees",
    "notes",
}
REQUIRED_POLICY_FALSE = {
    "runtime_known_absence_pages_implemented",
    "persistent_known_absence_store_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "global_absence_claims_allowed",
    "live_probe_execution_allowed",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "arbitrary_url_fetch_enabled",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "candidate_promotion_runtime_implemented",
    "master_index_mutation_allowed",
}
REQUIRED_POLICY_TRUE = {"privacy_filter_required", "scoped_absence_required"}
REQUIRED_REPORT_FALSE = {
    "runtime_known_absence_pages_implemented",
    "persistent_known_absence_store_implemented",
    "global_absence_claims_allowed",
    "global_absence_claimed",
    "exhaustive_search_claimed",
    "live_probe_execution_allowed",
    "live_probes_performed",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "candidate_promotion_runtime_implemented",
    "master_index_mutation_allowed",
    "external_calls_performed",
}
REQUIRED_RUNTIME_FALSE = {
    "runtime_known_absence_pages_implemented",
    "public_search_runtime_wired",
    "persistent_known_absence_store_implemented",
    "candidate_index_runtime_implemented",
    "candidate_promotion_runtime_implemented",
    "source_cache_runtime_implemented",
    "evidence_ledger_runtime_implemented",
    "telemetry_implemented",
}
REQUIRED_DOCS = {
    "docs/reference/KNOWN_ABSENCE_PAGE_CONTRACT.md": (
        "scoped absence, not global absence",
        "known absence page is not a runtime page yet",
        "known absence page is not evidence acceptance",
        "known absence page is not candidate promotion",
        "known absence page is not master-index mutation",
        "no download/install/upload/live fetch",
    ),
    "docs/reference/CANDIDATE_PROMOTION_POLICY.md": (
        "known absence page",
        "contract-only",
        "not candidate promotion",
    ),
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "known absence page v0",
        "scoped absence, not global absence",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "ip address",
        "account id",
        "private path",
        "known absence",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "no persistent query logging",
        "known absence",
        "contract-only",
    ),
    "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md": (
        "known absence",
        "future no-result",
        "contract-only",
    ),
    "docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md": (
        "known absence",
        "no download/install/upload/live fetch",
    ),
}
FORBIDDEN_CLAIMS = (
    "hosted query intelligence is live",
    "known absence runtime exists",
    "global absence claimed",
    "exhaustive search claimed",
    "source cache runtime exists",
    "evidence ledger runtime exists",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
    "live probes performed",
    "external calls were performed",
    "downloads enabled",
    "uploads enabled",
    "installs enabled",
    "master index was mutated",
)


def validate_known_absence_page_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/known_absence_page.v0.json")
    if contract:
        _validate_contract(contract, errors)

    gap_contract = _read_json_object(GAP_CONTRACT_PATH, errors, "contracts/query/known_absence_gap.v0.json")
    if gap_contract:
        _validate_gap_contract(gap_contract, errors)

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/known_absence_page_policy.json")
    if policy:
        _validate_policy(policy, errors)

    for path in PRIOR_POLICY_PATHS:
        if path.is_file():
            prior = _read_json_object(path, errors, _repo_relative(path))
            if prior and prior.get("known_absence_page_status") != "contract_only_p66":
                errors.append(f"{_repo_relative(path)} must reference P66 known absence pages as contract-only.")

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("known absence page examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    folded = _scan_governed_text().casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime, global-absence, mutation, action, or safety claim present: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "known_absence_page_contract_validator_v0",
        "contract_file": "contracts/query/known_absence_page.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("known_absence_page.v0.json x-status must be contract_only.")
    for key in (
        "x-runtime_known_absence_pages_implemented",
        "x-persistent_known_absence_store_implemented",
        "x-telemetry_implemented",
        "x-public_query_logging_enabled",
        "x-global_absence_claims_allowed",
        "x-live_probe_execution_allowed",
        "x-downloads_enabled",
        "x-uploads_enabled",
        "x-installs_enabled",
        "x-arbitrary_url_fetch_enabled",
        "x-source_cache_mutation_allowed",
        "x-evidence_ledger_mutation_allowed",
        "x-candidate_index_mutation_allowed",
        "x-candidate_promotion_runtime_implemented",
        "x-master_index_mutation_allowed",
        "x-external_calls_allowed",
    ):
        if contract.get(key) is not False:
            errors.append(f"known_absence_page.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"known_absence_page.v0.json missing required fields: {', '.join(missing)}")
    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("known_absence_page.v0.json properties must be an object.")
    else:
        for field in sorted(REQUIRED_CONTRACT_FIELDS):
            if field not in properties:
                errors.append(f"known_absence_page.v0.json properties missing {field}.")
    defs = contract.get("$defs")
    if not isinstance(defs, Mapping):
        errors.append("known_absence_page.v0.json $defs must be an object.")
        return
    for key in (
        "allowed_statuses",
        "allowed_absence_statuses",
        "allowed_checked_indexes",
        "allowed_gap_types",
        "allowed_action_types",
        "hard_no_global_false_fields",
        "hard_no_mutation_false_fields",
    ):
        if not isinstance(defs.get(key), list) or not defs.get(key):
            errors.append(f"known_absence_page.v0.json $defs.{key} must be a non-empty list.")


def _validate_gap_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("known_absence_gap.v0.json x-status must be contract_only.")
    for key in ("x-runtime_known_absence_pages_implemented", "x-global_absence_claims_allowed"):
        if contract.get(key) is not False:
            errors.append(f"known_absence_gap.v0.json {key} must be false.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("known_absence_page_policy status must be contract_only.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("known_absence_page_policy.raw_query_retention_default must be none.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"known_absence_page_policy.{key} must be false.")
    for key in sorted(REQUIRED_POLICY_TRUE):
        if policy.get(key) is not True:
            errors.append(f"known_absence_page_policy.{key} must be true.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list):
        errors.append("known_absence_page_policy.next_contracts must be a list.")
    else:
        for item in ("query_privacy_poisoning_guard", "demand_dashboard", "source_sync_worker", "source_cache_evidence_ledger"):
            if item not in next_contracts:
                errors.append(f"known_absence_page_policy.next_contracts missing {item}.")


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
        errors.append("control/audits/known-absence-page-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P66 audit files: {', '.join(missing)}")

    report = _read_json_object(REPORT_PATH, errors, "known_absence_page_report.json")
    if not report:
        return
    if report.get("report_id") != "known_absence_page_v0":
        errors.append("report_id must be known_absence_page_v0.")
    if report.get("contract_file") != "contracts/query/known_absence_page.v0.json":
        errors.append("report contract_file must point to contracts/query/known_absence_page.v0.json.")
    hard = report.get("no_global_absence_no_mutation_guarantees")
    if not isinstance(hard, Mapping):
        errors.append("report no_global_absence_no_mutation_guarantees must be present.")
    else:
        for key in sorted(REQUIRED_REPORT_FALSE):
            if hard.get(key) is not False:
                errors.append(f"report no_global_absence_no_mutation_guarantees.{key} must be false.")
    runtime = report.get("runtime_status")
    if not isinstance(runtime, Mapping):
        errors.append("report runtime_status must be present.")
    else:
        for key in sorted(REQUIRED_RUNTIME_FALSE):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P67 Query Privacy and Poisoning Guard v0":
        errors.append("next_recommended_branch must be P67 Query Privacy and Poisoning Guard v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P66 is contract-only; runtime known absence page serving remains deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        GAP_CONTRACT_PATH,
        POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "KNOWN_ABSENCE_PAGE_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_API_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md",
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


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Known Absence Page Contract validation",
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

    report = validate_known_absence_page_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
