#!/usr/bin/env python3
"""Validate Demand Dashboard v0 governance artifacts."""

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

from scripts.validate_demand_dashboard_snapshot import validate_all_examples  # noqa: E402


CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "demand_dashboard_snapshot.v0.json"
SIGNAL_CONTRACT_PATH = REPO_ROOT / "contracts" / "query" / "demand_signal.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "query_intelligence" / "demand_dashboard_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "demand-dashboard-v0"
REPORT_PATH = AUDIT_DIR / "demand_dashboard_report.json"
PRIOR_POLICY_PATHS = [
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "query_observation_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_result_cache_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_miss_ledger_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "search_need_record_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "probe_queue_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_index_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "candidate_promotion_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "known_absence_page_policy.json",
    REPO_ROOT / "control" / "inventory" / "query_intelligence" / "query_privacy_poisoning_guard_policy.json",
]
REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "DEMAND_DASHBOARD_SNAPSHOT_SCHEMA.md",
    "DEMAND_SIGNAL_TAXONOMY.md",
    "AGGREGATE_BUCKET_MODEL.md",
    "PRIORITY_AND_RANKING_MODEL.md",
    "SOURCE_GAP_DEMAND_MODEL.md",
    "CAPABILITY_GAP_DEMAND_MODEL.md",
    "MANUAL_OBSERVATION_DEMAND_MODEL.md",
    "CONNECTOR_PRIORITY_MODEL.md",
    "DEEP_EXTRACTION_PRIORITY_MODEL.md",
    "CANDIDATE_REVIEW_PRIORITY_MODEL.md",
    "KNOWN_ABSENCE_PATTERN_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "POISONING_AND_FAKE_DEMAND_EXCLUSION_POLICY.md",
    "PUBLIC_VISIBILITY_POLICY.md",
    "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
    "STATIC_EXAMPLE_DASHBOARD_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "demand_dashboard_report.json",
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "dashboard_snapshot_id",
    "dashboard_snapshot_kind",
    "status",
    "created_by_tool",
    "input_summary",
    "privacy_guard_summary",
    "poisoning_guard_summary",
    "dashboard_scope",
    "aggregate_buckets",
    "demand_signals",
    "source_gap_demand",
    "capability_gap_demand",
    "manual_observation_demand",
    "connector_priorities",
    "deep_extraction_priorities",
    "candidate_review_priorities",
    "known_absence_patterns",
    "priority_summary",
    "public_visibility",
    "freshness_and_invalidation",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
CONTRACT_FALSE_KEYS = {
    "x-runtime_dashboard_implemented",
    "x-persistent_dashboard_store_implemented",
    "x-telemetry_implemented",
    "x-account_tracking_implemented",
    "x-ip_tracking_implemented",
    "x-public_query_logging_enabled",
    "x-real_user_demand_claimed",
    "x-query_intelligence_mutation_allowed",
    "x-public_search_mutation_allowed",
    "x-master_index_mutation_allowed",
    "x-external_calls_allowed",
}
REQUIRED_POLICY_FALSE = {
    "runtime_dashboard_implemented",
    "persistent_dashboard_store_implemented",
    "telemetry_implemented",
    "account_tracking_implemented",
    "ip_tracking_implemented",
    "public_query_logging_enabled",
    "high_privacy_risk_public_aggregate_allowed",
    "high_poisoning_risk_public_aggregate_allowed",
    "real_user_demand_claimed",
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
}
REQUIRED_POLICY_TRUE = {
    "privacy_filter_required",
    "poisoning_guard_required_before_aggregation",
}
REQUIRED_REPORT_FALSE = {
    "runtime_dashboard_implemented",
    "persistent_dashboard_store_implemented",
    "telemetry_implemented",
    "account_tracking_implemented",
    "ip_tracking_implemented",
    "public_query_logging_enabled",
    "real_user_demand_claimed",
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
    "dashboard_runtime_implemented",
    "persistent_store_implemented",
    "telemetry_implemented",
    "account_tracking_implemented",
    "ip_tracking_implemented",
    "real_user_demand_claimed",
}
REQUIRED_DOCS = {
    "docs/reference/DEMAND_DASHBOARD_CONTRACT.md": (
        "dashboard is not runtime yet",
        "dashboard is not telemetry",
        "dashboard is not user tracking",
        "not source trust",
        "not candidate promotion",
        "does not claim real demand",
        "raw query retention default none",
        "privacy filtering before aggregation",
        "poisoning/fake-demand filtering before aggregation",
        "aggregate buckets",
        "priority signals",
        "public visibility caveats",
    ),
    "docs/architecture/QUERY_INTELLIGENCE_PLANE.md": (
        "demand dashboard v0",
        "privacy-filtered aggregate demand",
        "first query intelligence plane contract sequence",
    ),
    "docs/reference/QUERY_PRIVACY_POISONING_GUARD_CONTRACT.md": (
        "demand dashboard",
        "fake demand",
        "contract-only",
    ),
    "docs/reference/QUERY_PRIVACY_AND_REDACTION_POLICY.md": (
        "demand dashboard",
        "prohibited data",
        "private path",
    ),
    "docs/operations/QUERY_INTELLIGENCE_PRIVACY.md": (
        "demand dashboard",
        "contract-only",
        "no telemetry",
    ),
    "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md": (
        "demand dashboard",
        "contract-only",
    ),
}
FORBIDDEN_CLAIMS = (
    "hosted query intelligence is live",
    "demand dashboard runtime exists",
    "production analytics exists",
    "waf/rate limiting exists",
    "rights clearance is complete",
    "malware safety is confirmed",
    "production ready",
    "telemetry enabled",
    "account tracking enabled",
    "ip tracking enabled",
    "master index was mutated",
    "real public demand counts are available",
)
PRIVATE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path_backslash", re.compile(r"\b[A-Za-z]:\\+(?:Users|Documents|Temp|Windows|Projects|Private|Local)\\+", re.IGNORECASE)),
    ("windows_absolute_path_slash", re.compile(r"\b[A-Za-z]:/+(?:Users|Documents|Temp|Windows|Projects|Private|Local)/+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
)


def validate_demand_dashboard_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contract = _read_json_object(CONTRACT_PATH, errors, "contracts/query/demand_dashboard_snapshot.v0.json")
    if contract:
        _validate_contract(contract, errors)

    signal_contract = _read_json_object(SIGNAL_CONTRACT_PATH, errors, "contracts/query/demand_signal.v0.json")
    if signal_contract and signal_contract.get("x-status") != "contract_only":
        errors.append("contracts/query/demand_signal.v0.json must remain contract_only.")

    policy = _read_json_object(POLICY_PATH, errors, "control/inventory/query_intelligence/demand_dashboard_policy.json")
    if policy:
        _validate_policy(policy, errors)

    for path in PRIOR_POLICY_PATHS:
        if path.is_file():
            prior = _read_json_object(path, errors, _repo_relative(path))
            if prior and prior.get("demand_dashboard_status") != "contract_only_p68":
                errors.append(f"{_repo_relative(path)} must reference P68 demand dashboard as contract-only.")

    _validate_docs(errors)
    _validate_audit_pack(errors, warnings)

    examples_report = validate_all_examples(strict=True)
    if examples_report.get("status") != "valid":
        errors.append("demand dashboard examples failed validation.")
        errors.extend(examples_report.get("errors", []))

    governed_text = _scan_governed_text()
    folded = governed_text.casefold()
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in folded:
            errors.append(f"forbidden runtime, telemetry, tracking, mutation, production, or demand-count claim present: {phrase}")
    for label, pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(governed_text):
            errors.append(f"governed P68 artifacts contain prohibited private path pattern: {label}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "demand_dashboard_contract_validator_v0",
        "contract_file": "contracts/query/demand_dashboard_snapshot.v0.json",
        "example_count": examples_report.get("example_count", 0),
        "report_id": _report_id(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(contract: Mapping[str, Any], errors: list[str]) -> None:
    if contract.get("x-status") != "contract_only":
        errors.append("demand dashboard contract x-status must be contract_only.")
    for key in CONTRACT_FALSE_KEYS:
        if contract.get(key) is not False:
            errors.append(f"demand dashboard contract {key} must be false.")
    if contract.get("x-raw_query_retention_default") != "none":
        errors.append("demand dashboard contract raw query retention default must be none.")
    required = set(contract.get("required", []))
    missing = REQUIRED_CONTRACT_FIELDS - required
    if missing:
        errors.append(f"demand dashboard contract missing required fields: {', '.join(sorted(missing))}")


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "contract_only":
        errors.append("demand dashboard policy status must be contract_only.")
    for key in REQUIRED_POLICY_FALSE:
        if policy.get(key) is not False:
            errors.append(f"demand dashboard policy {key} must be false.")
    for key in REQUIRED_POLICY_TRUE:
        if policy.get(key) is not True:
            errors.append(f"demand dashboard policy {key} must be true.")
    if policy.get("raw_query_retention_default") != "none":
        errors.append("demand dashboard policy raw_query_retention_default must be none.")
    next_contracts = policy.get("next_contracts", [])
    for expected in ("source_sync_worker", "source_cache_evidence_ledger", "internet_archive_metadata_connector_approval"):
        if expected not in next_contracts:
            errors.append(f"demand dashboard policy next_contracts must include {expected}.")


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
        errors.append("control/audits/demand-dashboard-v0 missing.")
        return
    present = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
    missing = REQUIRED_AUDIT_FILES - present
    if missing:
        errors.append(f"demand dashboard audit pack missing files: {', '.join(sorted(missing))}")
    report = _read_json_object(REPORT_PATH, errors, "control/audits/demand-dashboard-v0/demand_dashboard_report.json")
    if not report:
        return
    if report.get("report_id") != "demand_dashboard_v0":
        errors.append("demand dashboard report_id must be demand_dashboard_v0.")
    if report.get("contract_file") != "contracts/query/demand_dashboard_snapshot.v0.json":
        errors.append("demand dashboard report must reference the snapshot contract file.")
    for key in REQUIRED_REPORT_FALSE:
        if report.get(key) is not False:
            errors.append(f"demand dashboard report {key} must be false.")
    if report.get("raw_query_retention_default_none") is not True:
        errors.append("demand dashboard report raw_query_retention_default_none must be true.")
    runtime = report.get("runtime_status")
    if isinstance(runtime, Mapping):
        for key in REQUIRED_RUNTIME_FALSE:
            if runtime.get(key) is not False:
                errors.append(f"demand dashboard report runtime_status.{key} must be false.")
    else:
        errors.append("demand dashboard report runtime_status must be an object.")
    if report.get("next_recommended_branch") != "P69 Source Sync Worker Contract v0":
        warnings.append("demand dashboard report should recommend P69 Source Sync Worker Contract v0 next.")


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
    paths: list[Path] = [
        CONTRACT_PATH,
        SIGNAL_CONTRACT_PATH,
        POLICY_PATH,
        REPO_ROOT / "docs" / "reference" / "DEMAND_DASHBOARD_CONTRACT.md",
        REPO_ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
        REPO_ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
        REPO_ROOT / "scripts" / "README.md",
    ]
    paths.extend(sorted(AUDIT_DIR.glob("*.md")))
    paths.extend(sorted(AUDIT_DIR.glob("*.json")))
    paths.extend(sorted((REPO_ROOT / "examples" / "demand_dashboard").glob("*/*.json")))
    paths.extend(sorted((REPO_ROOT / "examples" / "demand_dashboard").glob("*/*.md")))
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
    parser = argparse.ArgumentParser(description="Validate Demand Dashboard v0 governance artifacts.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)
    report = validate_demand_dashboard_contract()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        _print_text(report, sys.stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
