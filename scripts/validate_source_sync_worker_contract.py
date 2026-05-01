#!/usr/bin/env python3
"""Validate Source Sync Worker Contract v0 governance artifacts."""

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

from scripts.validate_source_sync_worker_job import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "source_sync" / "source_sync_worker_job.v0.json"
MANIFEST_PATH = REPO_ROOT / "contracts" / "source_sync" / "source_sync_worker_manifest.v0.json"
KIND_PATH = REPO_ROOT / "contracts" / "source_sync" / "source_sync_job_kind.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "source_sync" / "source_sync_worker_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "source-sync-worker-contract-v0"
REPORT_PATH = AUDIT_DIR / "source_sync_worker_contract_report.json"
QUERY_POLICY_DIR = REPO_ROOT / "control" / "inventory" / "query_intelligence"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "SOURCE_SYNC_WORKER_JOB_SCHEMA.md",
    "SOURCE_SYNC_WORKER_MANIFEST_SCHEMA.md",
    "WORKER_LIFECYCLE_MODEL.md",
    "SYNC_JOB_TAXONOMY.md",
    "SOURCE_POLICY_AND_APPROVAL_GATES.md",
    "SCHEDULING_RETRY_TIMEOUT_MODEL.md",
    "RATE_LIMIT_AND_CIRCUIT_BREAKER_MODEL.md",
    "USER_AGENT_AND_SOURCE_TERMS_POLICY.md",
    "INPUT_REFERENCE_MODEL.md",
    "EXPECTED_OUTPUT_MODEL.md",
    "CACHE_AND_EVIDENCE_LEDGER_RELATIONSHIP.md",
    "QUERY_INTELLIGENCE_RELATIONSHIP.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_EXECUTION_AND_NO_MUTATION_POLICY.md",
    "EXAMPLE_SOURCE_SYNC_JOB_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "source_sync_worker_contract_report.json",
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "source_sync_job_id",
    "source_sync_job_kind",
    "status",
    "created_by_tool",
    "job_identity",
    "job_kind",
    "source_target",
    "source_policy",
    "approval_gates",
    "scheduling",
    "retry_timeout_rate_limit",
    "user_agent_and_terms",
    "input_refs",
    "expected_outputs",
    "safety_requirements",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_execution_guarantees",
    "no_mutation_guarantees",
    "notes",
}
CONTRACT_FALSE_KEYS = {
    "x-runtime_source_sync_implemented",
    "x-worker_runtime_implemented",
    "x-job_execution_allowed",
    "x-live_source_calls_allowed_now",
    "x-public_query_fanout_allowed",
    "x-source_cache_mutation_allowed_now",
    "x-evidence_ledger_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-master_index_mutation_allowed",
    "x-telemetry_implemented",
    "x-credentials_configured",
}
MANIFEST_FALSE_KEYS = {
    "x-runtime_implemented",
    "x-live_sources_enabled_by_default",
    "x-public_query_fanout_allowed",
    "x-source_cache_mutation_allowed_now",
    "x-evidence_ledger_mutation_allowed_now",
    "x-candidate_index_mutation_allowed_now",
    "x-master_index_mutation_allowed_now",
}
REQUIRED_POLICY_FALSE = {
    "runtime_source_sync_implemented",
    "persistent_worker_queue_implemented",
    "telemetry_implemented",
    "credentials_configured",
    "public_query_fanout_allowed",
    "live_source_calls_allowed_now",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "public_index_mutation_allowed",
}
REQUIRED_POLICY_TRUE = {
    "approval_required_for_live_network_sync",
    "operator_required_for_worker_runtime",
    "source_policy_review_required",
    "rate_limit_required_future",
    "timeout_required_future",
    "circuit_breaker_required_future",
    "descriptive_user_agent_required_future",
    "cache_required_before_public_use",
    "evidence_attribution_required",
}
REQUIRED_REPORT_FALSE = {
    "runtime_source_sync_implemented",
    "persistent_worker_queue_implemented",
    "telemetry_implemented",
    "credentials_configured",
    "public_query_fanout_allowed",
    "worker_runtime_implemented",
    "job_executed",
    "live_source_calls_allowed_now",
    "live_source_called",
    "external_calls_performed",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "master_index_mutation_allowed",
    "local_index_mutation_allowed",
    "public_index_mutation_allowed",
}
REQUIRED_DOCS = {
    "docs/architecture/SOURCE_INGESTION_PLANE.md": (
        "source ingestion plane",
        "not connector runtime yet",
        "not public-query fanout",
        "rate limits",
        "circuit breakers",
        "user-agent policy",
    ),
    "docs/reference/SOURCE_SYNC_WORKER_CONTRACT.md": (
        "not connector runtime yet",
        "not a crawler/scraper",
        "not public-query fanout",
        "not source cache/evidence ledger mutation in v0",
        "live source sync requires approval",
        "cache-first",
        "evidence attribution",
        "probe queue",
        "demand dashboard",
    ),
    "docs/reference/SOURCE_SYNC_SOURCE_POLICY.md": (
        "no public-query fanout",
        "no arbitrary url fetch",
        "descriptive user-agent policy",
        "rate limits",
        "timeouts",
        "circuit breakers",
        "source terms review",
    ),
    "docs/reference/PROBE_QUEUE_CONTRACT.md": (
        "source sync worker contract v0",
        "contract-only",
    ),
    "docs/reference/DEMAND_DASHBOARD_CONTRACT.md": (
        "source sync worker contract v0",
        "contract-only",
    ),
    "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md": (
        "source sync worker contract v0",
        "contract-only",
    ),
}
FORBIDDEN_CLAIMS = (
    "hosted source sync is live",
    "worker runtime exists",
    "source sync has run",
    "source sync ran",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
    "telemetry enabled",
    "credentials configured",
    "master index was mutated",
    "source cache was mutated",
    "evidence ledger was mutated",
)
PRIVATE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path_backslash", re.compile(r"\b[A-Za-z]:\\+(?:Users|Documents|Temp|Windows|Projects|Private|Local)\\+", re.IGNORECASE)),
    ("windows_absolute_path_slash", re.compile(r"\b[A-Za-z]:/+(?:Users|Documents|Temp|Windows|Projects|Private|Local)/+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
)


def validate_source_sync_worker_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/source_sync/source_sync_worker_job.v0.json")
    if contract:
        _validate_job_contract(contract, errors)
    manifest = _read_json_object(MANIFEST_PATH, errors, "contracts/source_sync/source_sync_worker_manifest.v0.json")
    if manifest:
        _validate_manifest_contract(manifest, errors)
    kind = _read_json_object(KIND_PATH, errors, "contracts/source_sync/source_sync_job_kind.v0.json")
    if kind and kind.get("x-status") != "contract_only":
        errors.append("contracts/source_sync/source_sync_job_kind.v0.json must be contract_only.")
    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/source_sync/source_sync_worker_policy.json")
    if policy:
        _validate_policy(policy, errors)
    _validate_query_policy_refs(errors)
    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("source sync worker examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    governed_text = _scan_governed_text()
    folded = governed_text.casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime, live source, mutation, credential, production, or safety claim present: {phrase}")
    for label, pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(governed_text):
            errors.append(f"governed P69 artifacts contain prohibited private path pattern: {label}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_sync_worker_contract_validator_v0",
        "contract_file": "contracts/source_sync/source_sync_worker_job.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_job_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("source sync worker job contract x-status must be contract_only.")
    for key in CONTRACT_FALSE_KEYS:
        if contract.get(key) is not False:
            errors.append(f"source sync worker job contract {key} must be false.")
    required = set(contract.get("required", []))
    missing = REQUIRED_CONTRACT_FIELDS - required
    if missing:
        errors.append(f"source sync worker job contract missing required fields: {', '.join(sorted(missing))}")


def _validate_manifest_contract(manifest: Mapping[str, Any], errors: list[str]) -> None:
    if manifest.get("x-status") != "contract_only":
        errors.append("source sync worker manifest x-status must be contract_only.")
    for key in MANIFEST_FALSE_KEYS:
        if manifest.get(key) is not False:
            errors.append(f"source sync worker manifest {key} must be false.")
    required = set(manifest.get("required", []))
    for field in ("schema_version", "manifest_id", "manifest_kind", "status", "worker_family", "supported_job_kinds", "allowed_source_families", "default_policy", "required_approvals", "safety_defaults", "output_policy", "no_runtime_guarantees", "notes"):
        if field not in required:
            errors.append(f"source sync worker manifest missing required field {field}.")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("source sync worker policy status must be contract_only.")
    for key in REQUIRED_POLICY_FALSE:
        if policy.get(key) is not False:
            errors.append(f"source sync worker policy {key} must be false.")
    for key in REQUIRED_POLICY_TRUE:
        if policy.get(key) is not True:
            errors.append(f"source sync worker policy {key} must be true.")
    next_contracts = policy.get("next_contracts", [])
    for expected in ("source_cache_evidence_ledger", "internet_archive_metadata_connector_approval", "wayback_connector_approval", "github_releases_connector_approval"):
        if expected not in next_contracts:
            errors.append(f"source sync worker policy next_contracts must include {expected}.")


def _validate_query_policy_refs(errors: list[str]) -> None:
    if not QUERY_POLICY_DIR.is_dir():
        errors.append("control/inventory/query_intelligence missing.")
        return
    for path in sorted(QUERY_POLICY_DIR.glob("*.json")):
        payload = _read_json_object(path, errors, _repo_relative(path))
        if payload and payload.get("source_sync_worker_status") != "contract_only_p69":
            errors.append(f"{_repo_relative(path)} must reference P69 source sync worker as contract-only.")


def _validate_docs(errors: list[str]) -> None:
    for rel, phrases in REQUIRED_DOCS.items():
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"{rel} missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in phrases:
            if phrase.casefold() not in text:
                errors.append(f"{rel} must mention {phrase!r}.")


def _validate_audit_pack(errors: list[str], warnings: list[str]) -> None:
    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/source-sync-worker-contract-v0 missing.")
        return
    present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = REQUIRED_AUDIT_FILES - present
    if missing:
        errors.append(f"source sync worker audit pack missing files: {', '.join(sorted(missing))}")
    report = _read_json_object(REPORT_PATH, errors, "control/audits/source-sync-worker-contract-v0/source_sync_worker_contract_report.json")
    if not report:
        return
    if report.get("report_id") != "source_sync_worker_contract_v0":
        errors.append("source sync worker report_id must be source_sync_worker_contract_v0.")
    for key in REQUIRED_REPORT_FALSE:
        if report.get(key) is not False:
            errors.append(f"source sync worker report {key} must be false.")
    runtime = report.get("runtime_status")
    if isinstance(runtime, Mapping):
        for key in ("public_search_runtime_wired", "source_sync_runtime_implemented", "persistent_worker_queue_implemented", "connector_runtime_implemented", "telemetry_implemented", "credentials_configured"):
            if runtime.get(key) is not False:
                errors.append(f"source sync worker report runtime_status.{key} must be false.")
    else:
        errors.append("source sync worker report runtime_status must be an object.")
    if report.get("next_recommended_branch") != "P70 Source Cache and Evidence Ledger v0":
        warnings.append("source sync worker report should recommend P70 Source Cache and Evidence Ledger v0 next.")


def _read_json_object(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{label}: missing.")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: JSON parse error: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}: top-level JSON value must be an object.")
        return {}
    return value


def _scan_governed_text() -> str:
    paths: list[Path] = [CONTRACT_PATH, MANIFEST_PATH, KIND_PATH, POLICY_PATH]
    paths.extend([
        REPO_ROOT / "docs" / "architecture" / "SOURCE_INGESTION_PLANE.md",
        REPO_ROOT / "docs" / "reference" / "SOURCE_SYNC_WORKER_CONTRACT.md",
        REPO_ROOT / "docs" / "reference" / "SOURCE_SYNC_SOURCE_POLICY.md",
        REPO_ROOT / "scripts" / "README.md",
    ])
    paths.extend(sorted(AUDIT_DIR.glob("*.md")))
    paths.extend(sorted(AUDIT_DIR.glob("*.json")))
    paths.extend(sorted((REPO_ROOT / "examples" / "source_sync").glob("*/*.json")))
    paths.extend(sorted((REPO_ROOT / "examples" / "source_sync").glob("*/*.md")))
    chunks = []
    for path in paths:
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _report_id() -> str | None:
    if not REPORT_PATH.is_file():
        return None
    try:
        return json.loads(REPORT_PATH.read_text(encoding="utf-8")).get("report_id")
    except json.JSONDecodeError:
        return None


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _print_text(report: Mapping[str, Any], out: TextIO) -> None:
    print(f"status: {report['status']}", file=out)
    print(f"contract_file: {report['contract_file']}", file=out)
    print(f"example_count: {report['example_count']}", file=out)
    if report.get("errors"):
        print("errors:", file=out)
        for error in report["errors"]:
            print(f"  - {error}", file=out)
    if report.get("warnings"):
        print("warnings:", file=out)
        for warning in report["warnings"]:
            print(f"  - {warning}", file=out)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Source Sync Worker Contract v0 governance artifacts.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)
    report = validate_source_sync_worker_contract()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        _print_text(report, sys.stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
