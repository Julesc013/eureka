#!/usr/bin/env python3
"""Validate Query Privacy and Poisoning Guard v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_query_guard_decision import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "query_guard_decision.v0.json"
PRIVACY_RISK_PATH = REPO_ROOT / "contracts" / "query" / "query_privacy_risk.v0.json"
POISONING_RISK_PATH = REPO_ROOT / "contracts" / "query" / "query_poisoning_risk.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "query_privacy_poisoning_guard_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "query-privacy-poisoning-guard-v0"
REPORT_PATH = AUDIT_DIR / "query_privacy_poisoning_guard_report.json"
PRIOR_POLICY_PATHS = [
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "query_observation_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_result_cache_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_miss_ledger_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_need_record_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "probe_queue_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_index_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_promotion_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "known_absence_page_policy.json",
]
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "QUERY_GUARD_DECISION_SCHEMA.md",
    "PRIVACY_RISK_TAXONOMY.md",
    "POISONING_RISK_TAXONOMY.md",
    "POLICY_ACTION_MODEL.md",
    "REDACTION_MODEL.md",
    "AGGREGATE_ELIGIBILITY_MODEL.md",
    "FAKE_DEMAND_AND_SPAM_MODEL.md",
    "SOURCE_STUFFING_AND_CANDIDATE_POISONING_MODEL.md",
    "PRIVATE_DATA_DETECTION_POLICY.md",
    "RAW_QUERY_RETENTION_POLICY.md",
    "QUERY_INTELLIGENCE_OBJECT_GUARD_POLICY.md",
    "PUBLIC_SEARCH_INTEGRATION_BOUNDARIES.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "EXAMPLE_GUARD_DECISION_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "query_privacy_poisoning_guard_report.json",
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "guard_decision_id",
    "guard_decision_kind",
    "status",
    "created_by_tool",
    "input_context",
    "privacy_risks",
    "poisoning_risks",
    "policy_actions",
    "redaction",
    "aggregate_eligibility",
    "retention_policy",
    "query_intelligence_eligibility",
    "public_search_effect",
    "review_requirements",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
CONTRACT_FALSE_KEYS = {
    "x-runtime_guard_implemented",
    "x-persistent_guard_store_implemented",
    "x-telemetry_implemented",
    "x-account_tracking_implemented",
    "x-ip_tracking_implemented",
    "x-public_query_logging_enabled",
    "x-automatic_acceptance_allowed",
    "x-query_intelligence_mutation_allowed",
    "x-public_search_mutation_allowed",
    "x-master_index_mutation_allowed",
    "x-external_calls_allowed",
}
REQUIRED_POLICY_FALSE = {
    "runtime_guard_implemented",
    "persistent_guard_store_implemented",
    "telemetry_implemented",
    "account_tracking_implemented",
    "ip_tracking_implemented",
    "public_query_logging_enabled",
    "automatic_acceptance_allowed",
    "query_observation_mutation_allowed",
    "result_cache_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "search_need_mutation_allowed",
    "probe_queue_mutation_allowed",
    "candidate_index_mutation_allowed",
    "known_absence_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "high_privacy_risk_public_aggregate_allowed",
    "high_poisoning_risk_public_aggregate_allowed",
}
REQUIRED_POLICY_TRUE = {
    "privacy_filter_required",
    "poisoning_guard_required_before_public_aggregation",
}
REQUIRED_REPORT_FALSE = {
    "runtime_guard_implemented",
    "persistent_guard_store_implemented",
    "telemetry_implemented",
    "account_tracking_implemented",
    "ip_tracking_implemented",
    "public_query_logging_enabled",
    "automatic_acceptance_allowed",
    "query_observation_mutation_allowed",
    "result_cache_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "search_need_mutation_allowed",
    "probe_queue_mutation_allowed",
    "candidate_index_mutation_allowed",
    "known_absence_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "external_calls_performed",
    "live_probes_enabled",
}
REQUIRED_RUNTIME_FALSE = {
    "public_search_runtime_wired",
    "guard_runtime_implemented",
    "persistent_store_implemented",
    "telemetry_implemented",
    "account_tracking_implemented",
    "ip_tracking_implemented",
}
REQUIRED_DOCS = {
    "docs/reference/QUERY_PRIVACY_POISONING_GUARD_CONTRACT.md": (
        "guard is not runtime yet",
        "guard is not telemetry",
        "guard is not waf",
        "raw query retention default none",
        "privacy risks",
        "poisoning risks",
        "policy actions",
        "redaction model",
        "aggregate eligibility",
        "fake demand",
        "source-stuffing",
        "candidate-poisoning",
        "automatic acceptance is forbidden",
    ),
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "query privacy and poisoning guard v0",
        "privacy before learning",
        "poisoning defense before aggregation",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "ip address",
        "account id",
        "private path",
        "query privacy and poisoning guard",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "persistent query logging",
        "poisoning guard",
        "contract-only",
    ),
    "docs/reference/KNOWN_ABSENCE_PAGE_CONTRACT.md": (
        "query privacy and poisoning guard",
        "contract-only",
    ),
    "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md": (
        "query privacy and poisoning guard",
        "contract-only",
    ),
}
FORBIDDEN_CLAIMS = (
    "hosted query intelligence is live",
    "query guard runtime exists",
    "poisoning guard is sufficient for production abuse protection",
    "waf/rate limiting exists",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
    "telemetry enabled",
    "account tracking enabled",
    "ip tracking enabled",
    "master index was mutated",
)
PRIVATE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path_backslash", re.compile(r"\b[A-Za-z]:\\+(?:Users|Documents|Temp|Windows|Projects|Private|Local)\\+", re.IGNORECASE)),
    ("windows_absolute_path_slash", re.compile(r"\b[A-Za-z]:/+(?:Users|Documents|Temp|Windows|Projects|Private|Local)/+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
)


def validate_query_privacy_poisoning_guard_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/query_guard_decision.v0.json")
    if contract:
        _validate_contract(contract, errors)

    privacy_risk = _read_json_object(PRIVACY_RISK_PATH, errors, "contracts/query/query_privacy_risk.v0.json")
    if privacy_risk:
        _validate_taxonomy(privacy_risk, "privacy", errors)

    poisoning_risk = _read_json_object(POISONING_RISK_PATH, errors, "contracts/query/query_poisoning_risk.v0.json")
    if poisoning_risk:
        _validate_taxonomy(poisoning_risk, "poisoning", errors)

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/query_privacy_poisoning_guard_policy.json")
    if policy:
        _validate_policy(policy, errors)

    for path in PRIOR_POLICY_PATHS:
        if path.is_file():
            prior = _read_json_object(path, errors, _repo_relative(path))
            if prior and prior.get("query_privacy_poisoning_guard_status") != "contract_only_p67":
                errors.append(f"{_repo_relative(path)} must reference P67 query privacy and poisoning guard as contract-only.")

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("query guard examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    folded = _scan_governed_text().casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime, telemetry, tracking, mutation, or production claim present: {phrase}")
    governed_text = _scan_governed_text()
    for label, pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(governed_text):
            errors.append(f"governed P67 artifacts contain prohibited private path pattern: {label}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "query_privacy_poisoning_guard_contract_validator_v0",
        "contract_file": "contracts/query/query_guard_decision.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("query_guard_decision.v0.json x-status must be contract_only.")
    for key in sorted(CONTRACT_FALSE_KEYS):
        if contract.get(key) is not False:
            errors.append(f"query_guard_decision.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"query_guard_decision.v0.json missing required fields: {', '.join(missing)}")
    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("query_guard_decision.v0.json properties must be an object.")
    else:
        for field in sorted(REQUIRED_CONTRACT_FIELDS):
            if field not in properties:
                errors.append(f"query_guard_decision.v0.json properties missing {field}.")
    defs = contract.get("$defs")
    if not isinstance(defs, Mapping):
        errors.append("query_guard_decision.v0.json $defs must be an object.")
        return
    for key in (
        "allowed_statuses",
        "allowed_input_kinds",
        "allowed_privacy_risks",
        "allowed_poisoning_risks",
        "allowed_severities",
        "allowed_policy_actions",
        "allowed_redaction_strategies",
        "allowed_aggregate_fields",
        "disallowed_aggregate_fields",
        "hard_no_runtime_false_fields",
        "hard_no_mutation_false_fields",
    ):
        if not isinstance(defs.get(key), list) or not defs.get(key):
            errors.append(f"query_guard_decision.v0.json $defs.{key} must be a non-empty list.")


def _validate_taxonomy(contract: Mapping[str, Any], label: str, errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append(f"query_{label}_risk.v0.json x-status must be contract_only.")
    if contract.get("x-runtime_guard_implemented") is not False:
        errors.append(f"query_{label}_risk.v0.json x-runtime_guard_implemented must be false.")
    if contract.get("x-telemetry_implemented") is not False:
        errors.append(f"query_{label}_risk.v0.json x-telemetry_implemented must be false.")
    defs = contract.get("$defs")
    if not isinstance(defs, Mapping):
        errors.append(f"query_{label}_risk.v0.json $defs must be present.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("query_privacy_poisoning_guard_policy status must be contract_only.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("query_privacy_poisoning_guard_policy.raw_query_retention_default must be none.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"query_privacy_poisoning_guard_policy.{key} must be false.")
    for key in sorted(REQUIRED_POLICY_TRUE):
        if policy.get(key) is not True:
            errors.append(f"query_privacy_poisoning_guard_policy.{key} must be true.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list):
        errors.append("query_privacy_poisoning_guard_policy.next_contracts must be a list.")
    else:
        for item in ("demand_dashboard", "source_sync_worker", "source_cache_evidence_ledger"):
            if item not in next_contracts:
                errors.append(f"query_privacy_poisoning_guard_policy.next_contracts missing {item}.")


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
        errors.append("control/audits/query-privacy-poisoning-guard-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P67 audit files: {', '.join(missing)}")

    report = _read_json_object(REPORT_PATH, errors, "query_privacy_poisoning_guard_report.json")
    if not report:
        return
    if report.get("report_id") != "query_privacy_poisoning_guard_v0":
        errors.append("report_id must be query_privacy_poisoning_guard_v0.")
    if report.get("contract_file") != "contracts/query/query_guard_decision.v0.json":
        errors.append("report contract_file must point to contracts/query/query_guard_decision.v0.json.")
    hard = report.get("no_runtime_no_mutation_guarantees")
    if not isinstance(hard, Mapping):
        errors.append("report no_runtime_no_mutation_guarantees must be present.")
    else:
        for key in sorted(REQUIRED_REPORT_FALSE):
            if hard.get(key) is not False:
                errors.append(f"report no_runtime_no_mutation_guarantees.{key} must be false.")
        if hard.get("raw_query_retention_default_none") is not True:
            errors.append("report no_runtime_no_mutation_guarantees.raw_query_retention_default_none must be true.")
    runtime = report.get("runtime_status")
    if not isinstance(runtime, Mapping):
        errors.append("report runtime_status must be present.")
    else:
        for key in sorted(REQUIRED_RUNTIME_FALSE):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P68 Demand Dashboard v0":
        errors.append("next_recommended_branch must be P68 Demand Dashboard v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P67 is contract-only; runtime query privacy and poisoning guard remains deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        PRIVACY_RISK_PATH,
        POISONING_RISK_PATH,
        POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_PRIVACY_POISONING_GUARD_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
        REPO_ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
        REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_API_CONTRACT.md",
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
        "Query Privacy and Poisoning Guard Contract validation",
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

    report = validate_query_privacy_poisoning_guard_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
