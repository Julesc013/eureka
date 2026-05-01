#!/usr/bin/env python3
"""Validate Query Observation Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_query_observation import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "query_observation.v0.json"
CONTRACT_README = REPO_ROOT / "contracts" / "query" / "README.md"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "query_observation_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "query-observation-contract-v0"
REPORT_PATH = AUDIT_DIR / "query_observation_contract_report.json"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "QUERY_OBSERVATION_SCHEMA.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "FINGERPRINT_AND_NORMALIZATION_MODEL.md",
    "INTENT_ENTITY_DESTINATION_MODEL.md",
    "RESULT_SUMMARY_MODEL.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_OBSERVATION_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "query_observation_contract_report.json",
}
REQUIRED_DOCS = {
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "query observation",
        "contract-only",
        "fast learning, slow truth",
        "master-index mutation",
    ),
    "docs/reference/QUERY_OBSERVATION_CONTRACT.md": (
        "raw query retention default",
        "query fingerprint",
        "no telemetry runtime",
        "no runtime persistence",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "email",
        "api key",
        "private path",
        "ip address",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "no persistent query logging",
        "public aggregate",
        "operator-gated",
    ),
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "observation_id",
    "observation_kind",
    "status",
    "raw_query_policy",
    "normalized_query",
    "query_fingerprint",
    "query_intent",
    "destination",
    "detected_entities",
    "result_summary",
    "checked_scope",
    "index_refs",
    "privacy",
    "retention_policy",
    "probe_policy",
    "no_mutation_guarantees",
}
REQUIRED_POLICY_FALSE = {
    "runtime_persistence_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
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
    "runtime_persistence_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "result_cache_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "probe_enqueue_allowed",
    "external_calls_performed",
    "live_probes_enabled",
}
FORBIDDEN_CLAIMS = (
    "telemetry runtime implemented",
    "persistent query logging implemented",
    "public query logging enabled",
    "master index mutation enabled",
    "probe queue implemented",
    "hosted query intelligence is live",
)


def validate_query_observation_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/query_observation.v0.json")
    if contract:
        _validate_contract_schema(contract, errors)

    if not CONTRACT_README.is_file():
        errors.append("contracts/query/README.md: missing.")

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/query_observation_policy.json")
    if policy:
        _validate_policy(policy, errors)

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("query observation examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    scanned_text = _scan_governed_text()
    folded = scanned_text.casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime claim present: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "query_observation_contract_validator_v0",
        "contract_file": "contracts/query/query_observation.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract_schema(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("query_observation.v0.json x-status must be contract_only.")
    if contract.get("x-runtime_persistence_implemented") is not False:
        errors.append("query_observation.v0.json must record runtime persistence false.")
    if contract.get("x-telemetry_implemented") is not False:
        errors.append("query_observation.v0.json must record telemetry implemented false.")
    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"query_observation.v0.json missing required fields: {', '.join(missing)}")
    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("query_observation.v0.json properties must be an object.")
        return
    for field in sorted(REQUIRED_CONTRACT_FIELDS):
        if field not in properties:
            errors.append(f"query_observation.v0.json properties missing {field}.")
    mutation = properties.get("no_mutation_guarantees")
    if isinstance(mutation, Mapping):
        mutation_required = set(mutation.get("required", []))
        for field in (
            "master_index_mutated",
            "local_index_mutated",
            "candidate_index_mutated",
            "probe_enqueued",
            "result_cache_mutated",
            "miss_ledger_mutated",
            "telemetry_exported",
            "external_calls_performed",
        ):
            if field not in mutation_required:
                errors.append(f"no_mutation_guarantees must require {field}.")
    else:
        errors.append("no_mutation_guarantees schema missing.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("query_observation_policy status must be contract_only.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("raw_query_retention_default must be none.")
    if policy.get("privacy_filter_required") is not True:
        errors.append("privacy_filter_required must be true.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"query_observation_policy.{key} must be false.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list) or "shared_query_result_cache" not in next_contracts:
        errors.append("query_observation_policy must list shared_query_result_cache as a next contract.")


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
        errors.append("control/audits/query-observation-contract-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P59 audit files: {', '.join(missing)}")
    report = _read_json_object(REPORT_PATH, errors, "query_observation_contract_report.json")
    if not report:
        return
    if report.get("report_id") != "query_observation_contract_v0":
        errors.append("report_id must be query_observation_contract_v0.")
    if report.get("contract_file") != "contracts/query/query_observation.v0.json":
        errors.append("report contract_file must point to contracts/query/query_observation.v0.json.")
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
        for key in ("runtime_persistence_implemented", "telemetry_implemented", "public_query_logging_enabled"):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P60 Shared Query/Result Cache v0":
        errors.append("next_recommended_branch must be P60 Shared Query/Result Cache v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P59 is contract-only; runtime query observation collection remains deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_OBSERVATION_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
        REPO_ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
    ]
    pieces: list[str] = []
    for path in paths:
        if path.is_file():
            pieces.append(path.read_text(encoding="utf-8"))
    return "\n".join(pieces)


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
        "Query Observation Contract validation",
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
    report = validate_query_observation_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
