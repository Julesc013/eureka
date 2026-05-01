#!/usr/bin/env python3
"""Validate Evidence Ledger Contract v0 governance artifacts."""

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
from validate_evidence_ledger_record import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts/evidence_ledger/evidence_ledger_record.v0.json"
MANIFEST_PATH = REPO_ROOT / "contracts/evidence_ledger/evidence_ledger_manifest.v0.json"
POLICY_PATH = REPO_ROOT / "control/inventory/evidence_ledger/evidence_ledger_policy.json"
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "evidence_ledger_record_id",
    "evidence_ledger_record_kind",
    "status",
    "created_by_tool",
    "evidence_identity",
    "evidence_kind",
    "subject_ref",
    "claim",
    "source_cache_refs",
    "provenance",
    "observation",
    "confidence",
    "review",
    "conflicts",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_truth_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
CONTRACT_FALSE = {
    "x-evidence_ledger_runtime_implemented",
    "x-ledger_write_allowed",
    "x-accepted_as_truth_by_default",
    "x-source_cache_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-public_index_mutation_allowed_now",
    "x-local_index_mutation_allowed_now",
    "x-master_index_mutation_allowed",
    "x-live_source_calls_allowed_now",
    "x-telemetry_implemented",
    "x-credentials_configured",
}
MANIFEST_FALSE = {
    "x-runtime_implemented",
    "x-accepted_as_truth_by_default",
    "x-master_index_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-public_index_mutation_allowed_now",
}
POLICY_FALSE = {
    "runtime_evidence_ledger_implemented",
    "persistent_evidence_ledger_implemented",
    "accepted_as_truth_by_default",
    "automatic_promotion_allowed",
    "telemetry_implemented",
    "credentials_configured",
    "ledger_mutation_allowed_now",
    "source_cache_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "public_index_mutation_allowed_now",
    "local_index_mutation_allowed_now",
    "master_index_mutation_allowed",
    "destructive_merge_allowed",
}
POLICY_TRUE = {
    "promotion_policy_required",
    "master_index_review_required",
    "evidence_review_required",
    "rights_risk_review_required",
    "conflict_review_required",
}
REQUIRED_DOCS = {
    "docs/reference/EVIDENCE_LEDGER_CONTRACT.md": (
        "evidence ledger contract v0",
        "not truth by default",
        "not production evidence authority",
        "not master-index mutation",
        "accepted_as_truth is false",
        "confidence is not truth",
        "promotion policy",
        "master-index review",
        "conflicts",
    ),
    "docs/architecture/SOURCE_INGESTION_PLANE.md": (
        "p70 source cache and evidence ledger",
        "not runtime",
        "not source/evidence/candidate/public/local/master index mutation",
    ),
}
FORBIDDEN = (
    "evidence ledger runtime exists",
    "evidence ledger has run",
    "accepted as truth by default",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
    "master index was mutated",
)


def validate_evidence_ledger_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    contract = load_json_object(CONTRACT_PATH, errors, "contracts/evidence_ledger/evidence_ledger_record.v0.json")
    if contract:
        _validate_contract(contract, errors)
    manifest = load_json_object(MANIFEST_PATH, errors, "contracts/evidence_ledger/evidence_ledger_manifest.v0.json")
    if manifest:
        _validate_manifest(manifest, errors)
    policy = load_json_object(POLICY_PATH, errors, "control/inventory/evidence_ledger/evidence_ledger_policy.json")
    if policy:
        _validate_policy(policy, errors)
    _validate_docs(errors)
    examples = validate_all_examples(strict=True)
    if examples.get("status") != "valid":
        errors.append("evidence ledger examples failed validation.")
        errors.extend(examples.get("errors", []))
    _scan_forbidden(errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "evidence_ledger_contract_validator_v0",
        "contract_file": "contracts/evidence_ledger/evidence_ledger_record.v0.json",
        "example_count": examples.get("example_count", 0),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("evidence ledger contract x-status must be contract_only.")
    for key in CONTRACT_FALSE:
        if contract.get(key) is not False:
            errors.append(f"evidence ledger contract {key} must be false.")
    missing = REQUIRED_CONTRACT_FIELDS - set(contract.get("required", []))
    if missing:
        errors.append(f"evidence ledger contract missing required fields: {', '.join(sorted(missing))}")


def _validate_manifest(manifest: Mapping[str, Any], errors: list[str]) -> None:
    if manifest.get("x-status") != "contract_only":
        errors.append("evidence ledger manifest x-status must be contract_only.")
    for key in MANIFEST_FALSE:
        if manifest.get(key) is not False:
            errors.append(f"evidence ledger manifest {key} must be false.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("evidence ledger policy status must be contract_only.")
    for key in POLICY_FALSE:
        if policy.get(key) is not False:
            errors.append(f"evidence ledger policy {key} must be false.")
    for key in POLICY_TRUE:
        if policy.get(key) is not True:
            errors.append(f"evidence ledger policy {key} must be true.")


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
        REPO_ROOT / "contracts/evidence_ledger",
        REPO_ROOT / "control/inventory/evidence_ledger",
        REPO_ROOT / "docs/reference/EVIDENCE_LEDGER_CONTRACT.md",
        REPO_ROOT / "examples/evidence_ledger",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for base in paths for path in ([base] if base.is_file() else base.rglob("*")) if path.is_file()).casefold()
    for phrase in FORBIDDEN:
        if phrase in text:
            errors.append(f"forbidden evidence ledger claim present: {phrase}")
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", text, re.I):
        errors.append("evidence ledger governed artifacts contain prohibited private path.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_evidence_ledger_contract()
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
