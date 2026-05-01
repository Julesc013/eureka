#!/usr/bin/env python3
"""Validate Source Cache Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from _p70_contract_common import load_json_object, print_report  # noqa: E402
from validate_source_cache_record import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts/source_cache/source_cache_record.v0.json"
MANIFEST_PATH = REPO_ROOT / "contracts/source_cache/source_cache_manifest.v0.json"
POLICY_PATH = REPO_ROOT / "control/inventory/source_cache/source_cache_policy.json"
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "source_cache_record_id",
    "source_cache_record_kind",
    "status",
    "created_by_tool",
    "source_ref",
    "cache_identity",
    "cache_kind",
    "source_policy",
    "acquisition_context",
    "cached_payload_summary",
    "normalized_metadata",
    "freshness",
    "provenance",
    "fixity",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
CONTRACT_FALSE = {
    "x-source_cache_runtime_implemented",
    "x-cache_write_allowed",
    "x-live_source_calls_allowed_now",
    "x-arbitrary_url_cache_allowed",
    "x-raw_payload_storage_allowed_now",
    "x-private_data_storage_allowed_now",
    "x-executable_payload_storage_allowed_now",
    "x-evidence_ledger_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-master_index_mutation_allowed",
    "x-telemetry_implemented",
    "x-credentials_configured",
}
MANIFEST_FALSE = {
    "x-runtime_implemented",
    "x-live_sources_enabled_by_default",
    "x-public_query_fanout_allowed",
    "x-source_cache_mutation_allowed_now",
    "x-evidence_ledger_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-master_index_mutation_allowed_now",
}
POLICY_FALSE = {
    "runtime_source_cache_implemented",
    "persistent_source_cache_implemented",
    "live_sources_enabled_by_default",
    "public_query_fanout_allowed",
    "arbitrary_url_cache_allowed",
    "raw_payload_storage_allowed_now",
    "private_data_storage_allowed_now",
    "executable_payload_storage_allowed_now",
    "telemetry_implemented",
    "credentials_configured",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "master_index_mutation_allowed",
}
POLICY_TRUE = {
    "approval_required_for_live_network_cache",
    "source_policy_review_required",
    "rate_limit_required_future",
    "timeout_required_future",
    "circuit_breaker_required_future",
    "descriptive_user_agent_required_future",
    "cache_required_before_public_use",
    "evidence_attribution_required",
}
REQUIRED_DOCS = {
    "docs/reference/SOURCE_CACHE_CONTRACT.md": (
        "source cache contract v0",
        "not live connector runtime",
        "not arbitrary url cache",
        "not a raw payload store",
        "runtime source cache is contract-only",
        "not implemented",
        "public queries must not fan out",
        "provenance",
        "fixity",
        "freshness",
    ),
    "docs/architecture/SOURCE_INGESTION_PLANE.md": (
        "p70 source cache and evidence ledger",
        "not runtime",
        "not public-query fanout",
        "not arbitrary url cache",
        "not raw payload store",
    ),
}
FORBIDDEN = (
    "hosted source cache is live",
    "source cache runtime exists",
    "source cache has run",
    "source cache was mutated",
    "evidence ledger was mutated",
    "master index was mutated",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
)


def validate_source_cache_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    contract = load_json_object(CONTRACT_PATH, errors, "contracts/source_cache/source_cache_record.v0.json")
    if contract:
        _validate_contract(contract, errors)
    manifest = load_json_object(MANIFEST_PATH, errors, "contracts/source_cache/source_cache_manifest.v0.json")
    if manifest:
        _validate_manifest(manifest, errors)
    policy = load_json_object(POLICY_PATH, errors, "control/inventory/source_cache/source_cache_policy.json")
    if policy:
        _validate_policy(policy, errors)
    _validate_docs(errors)
    examples = validate_all_examples(strict=True)
    if examples.get("status") != "valid":
        errors.append("source cache examples failed validation.")
        errors.extend(examples.get("errors", []))
    _scan_forbidden(errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_cache_contract_validator_v0",
        "contract_file": "contracts/source_cache/source_cache_record.v0.json",
        "example_count": examples.get("example_count", 0),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("source cache contract x-status must be contract_only.")
    for key in CONTRACT_FALSE:
        if contract.get(key) is not False:
            errors.append(f"source cache contract {key} must be false.")
    missing = REQUIRED_CONTRACT_FIELDS - set(contract.get("required", []))
    if missing:
        errors.append(f"source cache contract missing required fields: {', '.join(sorted(missing))}")


def _validate_manifest(manifest: Mapping[str, Any], errors: list[str]) -> None:
    if manifest.get("x-status") != "contract_only":
        errors.append("source cache manifest x-status must be contract_only.")
    for key in MANIFEST_FALSE:
        if manifest.get(key) is not False:
            errors.append(f"source cache manifest {key} must be false.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("source cache policy status must be contract_only.")
    for key in POLICY_FALSE:
        if policy.get(key) is not False:
            errors.append(f"source cache policy {key} must be false.")
    for key in POLICY_TRUE:
        if policy.get(key) is not True:
            errors.append(f"source cache policy {key} must be true.")


def _validate_docs(errors: list[str]) -> None:
    for rel, phrases in REQUIRED_DOCS.items():
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"{rel} missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{rel} missing required phrase: {phrase}")


def _scan_forbidden(errors: list[str]) -> None:
    paths = [
        REPO_ROOT / "contracts/source_cache",
        REPO_ROOT / "control/inventory/source_cache",
        REPO_ROOT / "docs/reference/SOURCE_CACHE_CONTRACT.md",
        REPO_ROOT / "examples/source_cache",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for base in paths for path in ([base] if base.is_file() else base.rglob("*")) if path.is_file()).casefold()
    for phrase in FORBIDDEN:
        if phrase in text:
            errors.append(f"forbidden source cache claim present: {phrase}")
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", text, re.I):
        errors.append("source cache governed artifacts contain prohibited private path.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_source_cache_contract()
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
