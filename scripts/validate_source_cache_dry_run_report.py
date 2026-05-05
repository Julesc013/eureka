#!/usr/bin/env python3
"""Validate P98 source cache dry-run reports and the audit report projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source_cache.policy import HARD_FALSE_FIELDS, HARD_TRUE_FIELDS  # noqa: E402


AUDIT_REPORT = REPO_ROOT / "control" / "audits" / "source-cache-local-dry-run-runtime-v0" / "source_cache_local_dry_run_runtime_report.json"
REQUIRED_DRY_RUN_FIELDS = {
    "report_id",
    "mode",
    "input_roots",
    "candidates_seen",
    "candidates_valid",
    "candidates_invalid",
    "candidate_summaries",
    "source_families",
    "record_kinds",
    "privacy_status_counts",
    "public_safety_status_counts",
    "evidence_readiness_counts",
    "policy_status_counts",
    "mutation_summary",
    "warnings",
    "errors",
    "hard_booleans",
}
AUDIT_TRUE = {"local_dry_run_runtime_implemented"}
AUDIT_FALSE = {
    "authoritative_source_cache_runtime_implemented",
    "live_source_called",
    "external_calls_performed",
    "connector_runtime_executed",
    "source_sync_worker_executed",
    "authoritative_source_cache_written",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "public_search_runtime_mutated",
    "hosted_runtime_enabled",
    "telemetry_exported",
    "credentials_used",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
}


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not path.is_file():
        return None, [f"{path} missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{path} does not parse as JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, [f"{path} must contain a JSON object"]
    return payload, errors


def validate_dry_run_report(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_DRY_RUN_FIELDS - set(report)
    if missing:
        errors.append(f"dry-run report missing fields: {', '.join(sorted(missing))}")
    if report.get("mode") != "local_dry_run":
        errors.append("mode must be local_dry_run")
    for key in ("candidates_seen", "candidates_valid", "candidates_invalid"):
        if not isinstance(report.get(key), int) or report.get(key) < 0:
            errors.append(f"{key} must be a non-negative integer")
    summaries = report.get("candidate_summaries", [])
    if not isinstance(summaries, list):
        errors.append("candidate_summaries must be a list")
        summaries = []
    if report.get("candidates_seen") != len(summaries):
        errors.append("candidates_seen must equal len(candidate_summaries)")
    if report.get("candidates_seen") != report.get("candidates_valid") + report.get("candidates_invalid"):
        errors.append("candidate counts are inconsistent")
    hard = report.get("hard_booleans", {})
    if not isinstance(hard, Mapping):
        errors.append("hard_booleans must be an object")
    else:
        for key in HARD_TRUE_FIELDS:
            if hard.get(key) is not True:
                errors.append(f"hard_booleans.{key} must be true")
        for key in HARD_FALSE_FIELDS:
            if hard.get(key) is not False:
                errors.append(f"hard_booleans.{key} must be false")
    mutation = report.get("mutation_summary", {})
    if isinstance(mutation, Mapping):
        for key, value in mutation.items():
            if value is not False:
                errors.append(f"mutation_summary.{key} must be false")
    else:
        errors.append("mutation_summary must be an object")
    return errors


def validate_audit_report(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in AUDIT_TRUE:
        if report.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in AUDIT_FALSE:
        if report.get(key) is not False:
            errors.append(f"{key} must be false")
    dry_run = report.get("dry_run_results")
    if not isinstance(dry_run, Mapping):
        errors.append("audit report dry_run_results must be an object")
    else:
        errors.extend(validate_dry_run_report(dry_run))
    return errors


def validate_report_path(path: Path) -> dict[str, Any]:
    payload, errors = load_json(path)
    if payload is not None:
        if payload.get("mode") == "local_dry_run":
            errors.extend(validate_dry_run_report(payload))
            report_id = payload.get("report_id")
        else:
            errors.extend(validate_audit_report(payload))
            report_id = payload.get("report_id")
    else:
        report_id = None
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_cache_dry_run_report_validator_v0",
        "report": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
        "report_id": report_id,
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report")
    parser.add_argument("--audit-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    path = Path(args.report) if args.report else AUDIT_REPORT
    result = validate_report_path(path)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        print(f"report: {result['report']}")
        if result["errors"]:
            print("errors:")
            for error in result["errors"]:
                print(f"  - {error}")
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
