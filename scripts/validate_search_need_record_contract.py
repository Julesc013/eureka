#!/usr/bin/env python3
"""Validate Search Need Record Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_search_need_record import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "search_need_record.v0.json"
LIFECYCLE_PATH = REPO_ROOT / "contracts" / "query" / "search_need_lifecycle.v0.json"
CONTRACT_README = REPO_ROOT / "contracts" / "query" / "README.md"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_need_record_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "search-need-record-v0"
REPORT_PATH = AUDIT_DIR / "search_need_record_report.json"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "SEARCH_NEED_RECORD_SCHEMA.md",
    "NEED_IDENTITY_AND_FINGERPRINT_MODEL.md",
    "NEED_LIFECYCLE_MODEL.md",
    "NEED_AGGREGATION_MODEL.md",
    "TARGET_OBJECT_MODEL.md",
    "SOURCE_AND_CAPABILITY_GAP_MODEL.md",
    "INPUT_REFERENCE_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "SCOPED_ABSENCE_POLICY.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_NEED_RECORD_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "search_need_record_report.json",
}
REQUIRED_DOCS = {
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "search need record",
        "contract-only",
        "fast learning, slow truth",
        "not master-index truth",
    ),
    "docs/reference/SEARCH_NEED_RECORD_CONTRACT.md": (
        "raw query retention default",
        "need identity",
        "source and capability gap",
        "no runtime need store",
    ),
    "docs/reference/SEARCH_MISS_LEDGER_CONTRACT.md": (
        "search need record",
        "contract-only",
        "future-only",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "ip address",
        "account id",
        "private path",
        "search need record",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "no persistent query logging",
        "no runtime need store",
        "public aggregate",
    ),
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "search_need_id",
    "search_need_kind",
    "status",
    "need_identity",
    "target_object",
    "originating_inputs",
    "aggregate_summary",
    "source_and_capability_gaps",
    "checked_scope",
    "not_checked_scope",
    "evidence_and_result_context",
    "suggested_next_steps",
    "priority",
    "privacy",
    "retention_policy",
    "aggregation_policy",
    "no_mutation_guarantees",
}
REQUIRED_POLICY_FALSE = {
    "runtime_need_store_implemented",
    "persistent_need_store_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "global_absence_claims_allowed",
    "demand_counts_runtime_implemented",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "probe_enqueue_allowed",
    "result_cache_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "external_calls_allowed",
    "live_probes_allowed",
}
REQUIRED_REPORT_FALSE = {
    "runtime_need_store_implemented",
    "persistent_need_store_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "demand_counts_runtime_implemented",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "probe_enqueue_allowed",
    "result_cache_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "external_calls_performed",
    "live_probes_enabled",
}
FORBIDDEN_CLAIMS = (
    "search need runtime exists",
    "runtime need store is implemented",
    "persistent search need store is implemented",
    "hosted query intelligence is live",
    "demand dashboard exists",
    "probe job created",
    "candidate index runtime exists",
)


def validate_search_need_record_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/search_need_record.v0.json")
    if contract:
        _validate_contract_schema(contract, errors)

    lifecycle = _read_json_object(LIFECYCLE_PATH, errors, "contracts/query/search_need_lifecycle.v0.json")
    if lifecycle:
        _validate_lifecycle_schema(lifecycle, errors)

    if not CONTRACT_README.is_file():
        errors.append("contracts/query/README.md: missing.")

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/search_need_record_policy.json")
    if policy:
        _validate_policy(policy, errors)

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("search need examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    folded = _scan_governed_text().casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime or deployment claim present: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "search_need_record_contract_validator_v0",
        "contract_file": "contracts/query/search_need_record.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract_schema(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("search_need_record.v0.json x-status must be contract_only.")
    for key in (
        "x-runtime_need_store_implemented",
        "x-persistent_need_store_implemented",
        "x-telemetry_implemented",
        "x-public_query_logging_enabled",
        "x-demand_counts_runtime_implemented",
        "x-probe_queue_implemented",
        "x-candidate_index_implemented",
        "x-master_index_mutation_allowed",
    ):
        if contract.get(key) is not False:
            errors.append(f"search_need_record.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"search_need_record.v0.json missing required fields: {', '.join(missing)}")
    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("search_need_record.v0.json properties must be an object.")
        return
    for field in sorted(REQUIRED_CONTRACT_FIELDS):
        if field not in properties:
            errors.append(f"search_need_record.v0.json properties missing {field}.")
    mutation = properties.get("no_mutation_guarantees")
    if isinstance(mutation, Mapping):
        mutation_required = set(mutation.get("$ref", "") and contract.get("$defs", {}).get("no_mutation_guarantees", {}).get("required", []))
    else:
        mutation_required = set()
    for field in (
        "master_index_mutated",
        "local_index_mutated",
        "candidate_index_mutated",
        "probe_enqueued",
        "result_cache_mutated",
        "miss_ledger_mutated",
        "query_observation_mutated",
        "telemetry_exported",
        "external_calls_performed",
        "public_need_runtime_created",
    ):
        if field not in mutation_required:
            errors.append(f"no_mutation_guarantees must require {field}.")


def _validate_lifecycle_schema(lifecycle: Mapping[str, Any], errors: list[str]) -> None:
    if lifecycle.get("x-status") != "contract_only":
        errors.append("search_need_lifecycle.v0.json x-status must be contract_only.")
    for key in ("x-runtime_need_store_implemented", "x-telemetry_implemented", "x-probe_queue_implemented", "x-candidate_index_implemented", "x-master_index_mutation_allowed"):
        if lifecycle.get(key) is not False:
            errors.append(f"search_need_lifecycle.v0.json {key} must be false.")
    required = set(lifecycle.get("required", []))
    for field in ("status", "review_state", "resolution_state", "runtime_store_implemented", "probe_job_created", "candidate_record_created", "master_index_mutated"):
        if field not in required:
            errors.append(f"search_need_lifecycle.v0.json must require {field}.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("search_need_record_policy status must be contract_only.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("raw_query_retention_default must be none.")
    if policy.get("privacy_filter_required") is not True:
        errors.append("privacy_filter_required must be true.")
    if policy.get("scoped_absence_required") is not True:
        errors.append("scoped_absence_required must be true.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"search_need_record_policy.{key} must be false.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list) or "probe_queue" not in next_contracts:
        errors.append("search_need_record_policy must list probe_queue as a next contract.")


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
        errors.append("control/audits/search-need-record-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P62 audit files: {', '.join(missing)}")
    report = _read_json_object(REPORT_PATH, errors, "search_need_record_report.json")
    if not report:
        return
    if report.get("report_id") != "search_need_record_v0":
        errors.append("report_id must be search_need_record_v0.")
    if report.get("contract_file") != "contracts/query/search_need_record.v0.json":
        errors.append("report contract_file must point to contracts/query/search_need_record.v0.json.")
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
        for key in ("runtime_need_store_implemented", "persistent_need_store_implemented", "telemetry_implemented", "public_query_logging_enabled"):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P63 Probe Queue v0":
        errors.append("next_recommended_branch must be P63 Probe Queue v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P62 is contract-only; search need runtime storage remains deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        LIFECYCLE_PATH,
        POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_OBSERVATION_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_RESULT_CACHE_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_MISS_LEDGER_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_NEED_RECORD_CONTRACT.md",
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
        "Search Need Record Contract validation",
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
    report = validate_search_need_record_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
