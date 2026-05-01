#!/usr/bin/env python3
"""Validate Search Miss Ledger Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_search_miss_ledger_entry import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "search_miss_ledger_entry.v0.json"
CLASSIFICATION_PATH = REPO_ROOT / "contracts" / "query" / "search_miss_classification.v0.json"
CONTRACT_README = REPO_ROOT / "contracts" / "query" / "README.md"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_miss_ledger_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "search-miss-ledger-v0"
REPORT_PATH = AUDIT_DIR / "search_miss_ledger_report.json"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "MISS_LEDGER_ENTRY_SCHEMA.md",
    "MISS_CLASSIFICATION_TAXONOMY.md",
    "MISS_CAUSE_MODEL.md",
    "CHECKED_SCOPE_MODEL.md",
    "NEAR_MISS_AND_WEAK_HIT_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "SCOPED_ABSENCE_POLICY.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_MISS_ENTRY_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "search_miss_ledger_report.json",
}
REQUIRED_DOCS = {
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "search miss ledger",
        "contract-only",
        "fast learning, slow truth",
        "not master-index truth",
    ),
    "docs/reference/SEARCH_MISS_LEDGER_CONTRACT.md": (
        "raw query retention default",
        "miss classification",
        "scoped absence",
        "no runtime ledger writes",
    ),
    "docs/reference/SEARCH_RESULT_CACHE_CONTRACT.md": (
        "search miss ledger",
        "scoped absence",
        "contract-only",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "ip address",
        "account id",
        "private path",
        "search miss ledger",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "no persistent query logging",
        "no runtime ledger writes",
        "public aggregate",
    ),
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "miss_entry_id",
    "miss_entry_kind",
    "status",
    "query_ref",
    "miss_classification",
    "miss_causes",
    "checked_scope",
    "not_checked_scope",
    "near_misses",
    "weak_hits",
    "result_summary",
    "absence_summary",
    "suggested_next_steps",
    "privacy",
    "retention_policy",
    "aggregation_policy",
    "no_mutation_guarantees",
}
REQUIRED_POLICY_FALSE = {
    "runtime_ledger_implemented",
    "persistent_ledger_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "global_absence_claims_allowed",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "search_need_creation_allowed",
    "probe_enqueue_allowed",
    "result_cache_mutation_allowed",
    "external_calls_allowed",
    "live_probes_allowed",
}
REQUIRED_REPORT_FALSE = {
    "runtime_ledger_implemented",
    "persistent_ledger_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "search_need_creation_allowed",
    "probe_enqueue_allowed",
    "result_cache_mutation_allowed",
    "external_calls_performed",
    "live_probes_enabled",
}
FORBIDDEN_CLAIMS = (
    "miss ledger runtime exists",
    "runtime ledger is implemented",
    "persistent miss ledger is implemented",
    "hosted query intelligence is live",
    "global absence proof",
    "probe job created",
)


def validate_search_miss_ledger_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/search_miss_ledger_entry.v0.json")
    if contract:
        _validate_contract_schema(contract, errors)

    classification = _read_json_object(CLASSIFICATION_PATH, errors, "contracts/query/search_miss_classification.v0.json")
    if classification:
        _validate_classification_schema(classification, errors)

    if not CONTRACT_README.is_file():
        errors.append("contracts/query/README.md: missing.")

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/search_miss_ledger_policy.json")
    if policy:
        _validate_policy(policy, errors)

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("search miss ledger examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    folded = _scan_governed_text().casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime or global-absence claim present: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "search_miss_ledger_contract_validator_v0",
        "contract_file": "contracts/query/search_miss_ledger_entry.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract_schema(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("search_miss_ledger_entry.v0.json x-status must be contract_only.")
    for key in (
        "x-runtime_ledger_implemented",
        "x-persistent_ledger_implemented",
        "x-telemetry_implemented",
        "x-public_query_logging_enabled",
        "x-search_need_creation_implemented",
        "x-probe_queue_implemented",
        "x-candidate_index_mutation_allowed",
    ):
        if contract.get(key) is not False:
            errors.append(f"search_miss_ledger_entry.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"search_miss_ledger_entry.v0.json missing required fields: {', '.join(missing)}")
    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("search_miss_ledger_entry.v0.json properties must be an object.")
        return
    for field in sorted(REQUIRED_CONTRACT_FIELDS):
        if field not in properties:
            errors.append(f"search_miss_ledger_entry.v0.json properties missing {field}.")
    mutation = properties.get("no_mutation_guarantees")
    if isinstance(mutation, Mapping):
        mutation_required = set(mutation.get("required", []))
        for field in (
            "master_index_mutated",
            "local_index_mutated",
            "candidate_index_mutated",
            "search_need_created",
            "probe_enqueued",
            "result_cache_mutated",
            "query_observation_mutated",
            "telemetry_exported",
            "external_calls_performed",
        ):
            if field not in mutation_required:
                errors.append(f"no_mutation_guarantees must require {field}.")
    else:
        errors.append("no_mutation_guarantees schema missing.")


def _validate_classification_schema(classification: Mapping[str, Any], errors: list[str]) -> None:
    if classification.get("x-status") != "contract_only":
        errors.append("search_miss_classification.v0.json x-status must be contract_only.")
    if classification.get("x-runtime_ledger_implemented") is not False:
        errors.append("search_miss_classification.v0.json x-runtime_ledger_implemented must be false.")
    required = set(classification.get("required", []))
    for field in ("miss_type", "severity", "confidence", "scoped_absence", "global_absence_claimed"):
        if field not in required:
            errors.append(f"search_miss_classification.v0.json must require {field}.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("search_miss_ledger_policy status must be contract_only.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("raw_query_retention_default must be none.")
    if policy.get("privacy_filter_required") is not True:
        errors.append("privacy_filter_required must be true.")
    if policy.get("scoped_absence_required") is not True:
        errors.append("scoped_absence_required must be true.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"search_miss_ledger_policy.{key} must be false.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list) or "search_need_record" not in next_contracts:
        errors.append("search_miss_ledger_policy must list search_need_record as a next contract.")


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
        errors.append("control/audits/search-miss-ledger-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P61 audit files: {', '.join(missing)}")
    report = _read_json_object(REPORT_PATH, errors, "search_miss_ledger_report.json")
    if not report:
        return
    if report.get("report_id") != "search_miss_ledger_v0":
        errors.append("report_id must be search_miss_ledger_v0.")
    if report.get("contract_file") != "contracts/query/search_miss_ledger_entry.v0.json":
        errors.append("report contract_file must point to contracts/query/search_miss_ledger_entry.v0.json.")
    hard = report.get("hard_no_mutation_guarantees")
    if not isinstance(hard, Mapping):
        errors.append("report hard_no_mutation_guarantees must be present.")
    else:
        for key in sorted(REQUIRED_REPORT_FALSE):
            if hard.get(key) is not False:
                errors.append(f"report hard_no_mutation_guarantees.{key} must be false.")
    runtime = report.get("runtime_status")
    if not isinstance(runtime, Mapping):
        errors.append("report runtime_status must be present.")
    else:
        for key in ("runtime_ledger_implemented", "persistent_ledger_implemented", "telemetry_implemented", "public_query_logging_enabled"):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P62 Search Need Record v0":
        errors.append("next_recommended_branch must be P62 Search Need Record v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P61 is contract-only; miss ledger runtime writes remain deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        CLASSIFICATION_PATH,
        POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_OBSERVATION_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_RESULT_CACHE_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_MISS_LEDGER_CONTRACT.md",
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
        "Search Miss Ledger Contract validation",
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
    report = validate_search_miss_ledger_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
