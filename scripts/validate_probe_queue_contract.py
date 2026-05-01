#!/usr/bin/env python3
"""Validate Probe Queue Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_probe_queue_item import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "probe_queue_item.v0.json"
PROBE_KIND_PATH = REPO_ROOT / "contracts" / "query" / "probe_kind.v0.json"
CONTRACT_README = REPO_ROOT / "contracts" / "query" / "README.md"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "probe_queue_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "probe-queue-v0"
REPORT_PATH = AUDIT_DIR / "probe_queue_report.json"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "PROBE_QUEUE_ITEM_SCHEMA.md",
    "PROBE_KIND_TAXONOMY.md",
    "QUEUE_LIFECYCLE_MODEL.md",
    "PRIORITY_AND_SCHEDULING_MODEL.md",
    "SOURCE_POLICY_AND_APPROVAL_MODEL.md",
    "INPUT_REFERENCE_MODEL.md",
    "EXPECTED_OUTPUT_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_EXECUTION_AND_NO_MUTATION_POLICY.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_PROBE_ITEM_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "probe_queue_report.json",
}
REQUIRED_DOCS = {
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "probe queue",
        "contract-only",
        "fast learning, slow truth",
        "not master-index truth",
    ),
    "docs/reference/PROBE_QUEUE_CONTRACT.md": (
        "raw query retention default",
        "probe kind taxonomy",
        "source policy",
        "no runtime probe queue",
    ),
    "docs/reference/SEARCH_NEED_RECORD_CONTRACT.md": (
        "probe queue",
        "contract-only",
        "future-only",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "ip address",
        "account id",
        "private path",
        "probe queue",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "no persistent query logging",
        "no runtime probe queue",
        "public aggregate",
    ),
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "probe_item_id",
    "probe_item_kind",
    "status",
    "probe_identity",
    "probe_kind",
    "source_policy",
    "input_refs",
    "target",
    "priority",
    "scheduling",
    "expected_outputs",
    "safety_requirements",
    "privacy",
    "retention_policy",
    "aggregation_policy",
    "no_execution_guarantees",
    "no_mutation_guarantees",
}
REQUIRED_POLICY_FALSE = {
    "runtime_probe_queue_implemented",
    "persistent_probe_queue_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "live_probe_execution_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "search_need_mutation_allowed",
    "result_cache_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "external_calls_allowed",
}
REQUIRED_REPORT_FALSE = {
    "runtime_probe_queue_implemented",
    "persistent_probe_queue_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "probe_executed",
    "live_probe_execution_allowed",
    "live_source_called",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "search_need_mutation_allowed",
    "result_cache_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "external_calls_performed",
}
FORBIDDEN_CLAIMS = (
    "hosted query intelligence is live",
    "probe queue runtime exists",
    "live probes are implemented",
    "source cache runtime exists",
    "evidence ledger runtime exists",
    "candidate index runtime exists",
    "master index was mutated",
    "external calls were performed",
)


def validate_probe_queue_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/probe_queue_item.v0.json")
    if contract:
        _validate_contract_schema(contract, errors)

    probe_kind = _read_json_object(PROBE_KIND_PATH, errors, "contracts/query/probe_kind.v0.json")
    if probe_kind:
        _validate_probe_kind_schema(probe_kind, errors)

    if not CONTRACT_README.is_file():
        errors.append("contracts/query/README.md: missing.")

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/probe_queue_policy.json")
    if policy:
        _validate_policy(policy, errors)

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("probe queue examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    folded = _scan_governed_text().casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime or deployment claim present: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "probe_queue_contract_validator_v0",
        "contract_file": "contracts/query/probe_queue_item.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract_schema(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("probe_queue_item.v0.json x-status must be contract_only.")
    for key in (
        "x-runtime_probe_queue_implemented",
        "x-persistent_probe_queue_implemented",
        "x-telemetry_implemented",
        "x-public_query_logging_enabled",
        "x-probe_execution_implemented",
        "x-live_source_calls_allowed",
        "x-source_cache_runtime_implemented",
        "x-evidence_ledger_runtime_implemented",
        "x-candidate_index_implemented",
        "x-master_index_mutation_allowed",
        "x-external_calls_allowed",
        "x-live_probes_allowed",
    ):
        if contract.get(key) is not False:
            errors.append(f"probe_queue_item.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"probe_queue_item.v0.json missing required fields: {', '.join(missing)}")
    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("probe_queue_item.v0.json properties must be an object.")
        return
    for field in sorted(REQUIRED_CONTRACT_FIELDS):
        if field not in properties:
            errors.append(f"probe_queue_item.v0.json properties missing {field}.")
    defs = contract.get("$defs", {})
    if not isinstance(defs, Mapping):
        errors.append("probe_queue_item.v0.json $defs must be an object.")
        return
    execution_required = set(defs.get("no_execution_guarantees", {}).get("required", []))
    mutation_required = set(defs.get("no_mutation_guarantees", {}).get("required", []))
    for field in ("probe_executed", "live_source_called", "external_calls_performed"):
        if field not in execution_required:
            errors.append(f"no_execution_guarantees must require {field}.")
    for field in (
        "source_cache_mutated",
        "evidence_ledger_mutated",
        "candidate_index_mutated",
        "master_index_mutated",
        "local_index_mutated",
        "result_cache_mutated",
        "miss_ledger_mutated",
        "search_need_mutated",
        "telemetry_exported",
    ):
        if field not in mutation_required:
            errors.append(f"no_mutation_guarantees must require {field}.")


def _validate_probe_kind_schema(probe_kind: Mapping[str, Any], errors: list[str]) -> None:
    if probe_kind.get("x-status") != "contract_only":
        errors.append("probe_kind.v0.json x-status must be contract_only.")
    for key in ("x-runtime_probe_queue_implemented", "x-probe_execution_implemented", "x-live_probes_allowed", "x-external_calls_allowed"):
        if probe_kind.get(key) is not False:
            errors.append(f"probe_kind.v0.json {key} must be false.")
    required = set(probe_kind.get("required", []))
    for field in ("kind", "execution_class", "live_network_required_future", "approval_required", "operator_required", "human_required"):
        if field not in required:
            errors.append(f"probe_kind.v0.json must require {field}.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("probe_queue_policy status must be contract_only.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("raw_query_retention_default must be none.")
    if policy.get("privacy_filter_required") is not True:
        errors.append("privacy_filter_required must be true.")
    if policy.get("approval_required_for_live_network_probe") is not True:
        errors.append("approval_required_for_live_network_probe must be true.")
    if policy.get("operator_required_for_worker_runtime") is not True:
        errors.append("operator_required_for_worker_runtime must be true.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"probe_queue_policy.{key} must be false.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list) or "candidate_index" not in next_contracts:
        errors.append("probe_queue_policy must list candidate_index as a next contract.")


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
        errors.append("control/audits/probe-queue-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P63 audit files: {', '.join(missing)}")
    report = _read_json_object(REPORT_PATH, errors, "probe_queue_report.json")
    if not report:
        return
    if report.get("report_id") != "probe_queue_v0":
        errors.append("report_id must be probe_queue_v0.")
    if report.get("contract_file") != "contracts/query/probe_queue_item.v0.json":
        errors.append("report contract_file must point to contracts/query/probe_queue_item.v0.json.")
    hard = report.get("no_execution_no_mutation_guarantees")
    if not isinstance(hard, Mapping):
        errors.append("report no_execution_no_mutation_guarantees must be present.")
    else:
        for key in sorted(REQUIRED_REPORT_FALSE):
            if hard.get(key) is not False:
                errors.append(f"report no_execution_no_mutation_guarantees.{key} must be false.")
    runtime = report.get("runtime_status")
    if not isinstance(runtime, Mapping):
        errors.append("report runtime_status must be present.")
    else:
        for key in ("runtime_probe_queue_implemented", "persistent_probe_queue_implemented", "telemetry_implemented", "public_query_logging_enabled"):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P64 Candidate Index v0":
        errors.append("next_recommended_branch must be P64 Candidate Index v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P63 is contract-only; probe queue runtime and probe execution remain deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        PROBE_KIND_PATH,
        POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_OBSERVATION_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_RESULT_CACHE_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_MISS_LEDGER_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_NEED_RECORD_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "PROBE_QUEUE_CONTRACT.md",
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
        "Probe Queue Contract validation",
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
    report = validate_probe_queue_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
