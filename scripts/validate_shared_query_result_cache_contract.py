#!/usr/bin/env python3
"""Validate Shared Query/Result Cache Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_search_result_cache_entry import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "search_result_cache_entry.v0.json"
CACHE_KEY_PATH = REPO_ROOT / "contracts" / "query" / "cache_key.v0.json"
CONTRACT_README = REPO_ROOT / "contracts" / "query" / "README.md"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_result_cache_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "shared-query-result-cache-v0"
REPORT_PATH = AUDIT_DIR / "shared_query_result_cache_report.json"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "CACHE_ENTRY_SCHEMA.md",
    "CACHE_KEY_AND_FINGERPRINT_MODEL.md",
    "CACHED_RESULT_SUMMARY_MODEL.md",
    "ABSENCE_AND_GAP_CACHE_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "FRESHNESS_AND_INVALIDATION_POLICY.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_CACHE_ENTRY_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "shared_query_result_cache_report.json",
}
REQUIRED_DOCS = {
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "shared query/result cache",
        "contract-only",
        "fast learning, slow truth",
        "not master-index truth",
    ),
    "docs/reference/SEARCH_RESULT_CACHE_CONTRACT.md": (
        "raw query retention default",
        "cache key",
        "scoped absence",
        "no runtime cache writes",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "prohibited data",
        "ip address",
        "account id",
        "private path",
        "shared query/result cache",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "not telemetry",
        "no persistent query logging",
        "no runtime cache writes",
        "public aggregate",
    ),
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "cache_entry_id",
    "cache_entry_kind",
    "status",
    "query_ref",
    "cache_key",
    "request_summary",
    "response_summary",
    "result_summaries",
    "absence_summary",
    "checked_scope",
    "index_refs",
    "source_status_summary",
    "freshness",
    "invalidation",
    "privacy",
    "retention_policy",
    "no_mutation_guarantees",
}
REQUIRED_POLICY_FALSE = {
    "runtime_cache_implemented",
    "persistent_cache_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "search_need_mutation_allowed",
    "probe_enqueue_allowed",
    "external_calls_allowed",
    "live_probes_allowed",
}
REQUIRED_REPORT_FALSE = {
    "runtime_cache_implemented",
    "persistent_cache_implemented",
    "telemetry_implemented",
    "public_query_logging_enabled",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "candidate_index_mutation_allowed",
    "miss_ledger_mutation_allowed",
    "search_need_mutation_allowed",
    "probe_enqueue_allowed",
    "external_calls_performed",
    "live_probes_enabled",
}
FORBIDDEN_CLAIMS = (
    "result cache runtime exists",
    "runtime cache implemented",
    "persistent cache implemented",
    "telemetry runtime implemented",
    "public query logging enabled",
    "master index mutation enabled",
    "hosted query intelligence is live",
)


def validate_shared_query_result_cache_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/search_result_cache_entry.v0.json")
    if contract:
        _validate_contract_schema(contract, errors)

    cache_key = _read_json_object(CACHE_KEY_PATH, errors, "contracts/query/cache_key.v0.json")
    if cache_key:
        _validate_cache_key_schema(cache_key, errors)

    if not CONTRACT_README.is_file():
        errors.append("contracts/query/README.md: missing.")

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/search_result_cache_policy.json")
    if policy:
        _validate_policy(policy, errors)

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("search result cache examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    scanned_text = _scan_governed_text()
    folded = scanned_text.casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime claim present: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "shared_query_result_cache_contract_validator_v0",
        "contract_file": "contracts/query/search_result_cache_entry.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract_schema(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("search_result_cache_entry.v0.json x-status must be contract_only.")
    for key in ("x-runtime_cache_implemented", "x-persistent_cache_implemented", "x-telemetry_implemented", "x-public_query_logging_enabled"):
        if contract.get(key) is not False:
            errors.append(f"search_result_cache_entry.v0.json {key} must be false.")
    required = set(contract.get("required", []))
    missing = sorted(REQUIRED_CONTRACT_FIELDS - required)
    if missing:
        errors.append(f"search_result_cache_entry.v0.json missing required fields: {', '.join(missing)}")
    properties = contract.get("properties")
    if not isinstance(properties, Mapping):
        errors.append("search_result_cache_entry.v0.json properties must be an object.")
        return
    for field in sorted(REQUIRED_CONTRACT_FIELDS):
        if field not in properties:
            errors.append(f"search_result_cache_entry.v0.json properties missing {field}.")
    mutation = properties.get("no_mutation_guarantees")
    if isinstance(mutation, Mapping):
        mutation_required = set(mutation.get("required", []))
        for field in (
            "master_index_mutated",
            "local_index_mutated",
            "candidate_index_mutated",
            "query_observation_mutated",
            "miss_ledger_mutated",
            "search_need_mutated",
            "probe_enqueued",
            "telemetry_exported",
            "external_calls_performed",
        ):
            if field not in mutation_required:
                errors.append(f"no_mutation_guarantees must require {field}.")
    else:
        errors.append("no_mutation_guarantees schema missing.")


def _validate_cache_key_schema(cache_key: Mapping[str, Any], errors: list[str]) -> None:
    if cache_key.get("x-status") != "contract_only":
        errors.append("cache_key.v0.json x-status must be contract_only.")
    for key in ("x-runtime_cache_implemented", "x-persistent_cache_implemented", "x-telemetry_implemented"):
        if cache_key.get(key) is not False:
            errors.append(f"cache_key.v0.json {key} must be false.")
    required = set(cache_key.get("required", []))
    for field in ("key_algorithm", "key_basis", "normalized_query_hash", "mode", "index_snapshot_ref", "reversible", "salt_policy", "value"):
        if field not in required:
            errors.append(f"cache_key.v0.json must require {field}.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("search_result_cache_policy status must be contract_only.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("raw_query_retention_default must be none.")
    if policy.get("privacy_filter_required") is not True:
        errors.append("privacy_filter_required must be true.")
    for key in sorted(REQUIRED_POLICY_FALSE):
        if policy.get(key) is not False:
            errors.append(f"search_result_cache_policy.{key} must be false.")
    next_contracts = policy.get("next_contracts")
    if not isinstance(next_contracts, list) or "search_miss_ledger" not in next_contracts:
        errors.append("search_result_cache_policy must list search_miss_ledger as a next contract.")


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
        errors.append("control/audits/shared-query-result-cache-v0: missing audit directory.")
        return
    existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - existing)
    if missing:
        errors.append(f"missing P60 audit files: {', '.join(missing)}")
    report = _read_json_object(REPORT_PATH, errors, "shared_query_result_cache_report.json")
    if not report:
        return
    if report.get("report_id") != "shared_query_result_cache_v0":
        errors.append("report_id must be shared_query_result_cache_v0.")
    if report.get("contract_file") != "contracts/query/search_result_cache_entry.v0.json":
        errors.append("report contract_file must point to contracts/query/search_result_cache_entry.v0.json.")
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
        for key in ("runtime_cache_implemented", "persistent_cache_implemented", "telemetry_implemented", "public_query_logging_enabled"):
            if runtime.get(key) is not False:
                errors.append(f"report runtime_status.{key} must be false.")
    if report.get("next_recommended_branch") != "P61 Search Miss Ledger v0":
        errors.append("next_recommended_branch must be P61 Search Miss Ledger v0.")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("remaining_blockers must be recorded.")
    warnings.append("P60 is contract-only; runtime cache reads/writes remain deferred.")


def _scan_governed_text() -> str:
    paths = [
        CONTRACT_PATH,
        CACHE_KEY_PATH,
        POLICY_PATH,
        REPORT_PATH,
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "QUERY_OBSERVATION_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SEARCH_RESULT_CACHE_CONTRACT.md",
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
        "Shared Query/Result Cache Contract validation",
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
    report = validate_shared_query_result_cache_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
