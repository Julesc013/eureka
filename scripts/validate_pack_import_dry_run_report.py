#!/usr/bin/env python3
"""Validate P104 pack import dry-run reports and audit report projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.packs.policy import HARD_FALSE_FIELDS, HARD_TRUE_FIELDS  # noqa: E402


AUDIT_DIR = REPO_ROOT / "control" / "audits" / "pack-import-local-dry-run-runtime-v0"
AUDIT_REPORT = AUDIT_DIR / "pack_import_local_dry_run_runtime_report.json"
REQUIRED_AUDIT_FILES = {
    "README.md",
    "IMPLEMENTATION_SUMMARY.md",
    "RUNTIME_SCOPE.md",
    "DRY_RUN_INPUT_MODEL.md",
    "DRY_RUN_OUTPUT_MODEL.md",
    "PACK_DISCOVERY_AND_CLASSIFICATION.md",
    "VALIDATION_PIPELINE_IMPLEMENTATION.md",
    "IMPORT_REPORT_AND_DIFF_MODEL.md",
    "SOURCE_EVIDENCE_INDEX_CONTRIBUTION_PACK_HANDLING.md",
    "QUARANTINE_STAGING_BOUNDARY.md",
    "PRIVACY_PATH_SECRET_POLICY.md",
    "EXECUTABLE_PAYLOAD_AND_URL_POLICY.md",
    "RIGHTS_RISK_AND_PROVENANCE_REVIEW.md",
    "MUTATION_AND_PROMOTION_BOUNDARY.md",
    "PUBLIC_CONTRIBUTION_BOUNDARY.md",
    "FAILURE_AND_ERROR_MODEL.md",
    "ACCEPTANCE_RESULTS.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "pack_import_local_dry_run_runtime_report.json",
}
REQUIRED_DRY_RUN_FIELDS = {
    "report_id",
    "mode",
    "input_roots",
    "packs_seen",
    "packs_valid",
    "packs_invalid",
    "pack_summaries",
    "pack_kinds",
    "schema_versions",
    "validation_status_counts",
    "privacy_status_counts",
    "public_safety_status_counts",
    "risk_status_counts",
    "mutation_impact_counts",
    "promotion_readiness_counts",
    "dry_run_effects",
    "mutation_summary",
    "warnings",
    "errors",
    "hard_booleans",
}
AUDIT_TRUE = {"local_dry_run_runtime_implemented"}
AUDIT_FALSE = {
    "admin_endpoint_enabled",
    "accepted_record_created",
    "authoritative_pack_import_runtime_implemented",
    "candidate_index_mutated",
    "credentials_used",
    "downloads_enabled",
    "evidence_ledger_mutated",
    "execution_enabled",
    "external_calls_performed",
    "hosted_runtime_enabled",
    "installs_enabled",
    "live_source_called",
    "local_index_mutated",
    "master_index_mutated",
    "pack_content_executed",
    "pack_urls_followed",
    "promotion_decision_created",
    "promotion_runtime_enabled",
    "public_contribution_intake_enabled",
    "public_index_mutated",
    "quarantine_store_written",
    "real_pack_staging_performed",
    "source_cache_mutated",
    "staging_store_written",
    "telemetry_exported",
    "upload_endpoint_enabled",
}


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.is_file():
        return None, [f"{path} missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{path} does not parse as JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, [f"{path} must contain a JSON object"]
    return payload, []


def validate_dry_run_report(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_DRY_RUN_FIELDS - set(report)
    if missing:
        errors.append(f"dry-run report missing fields: {', '.join(sorted(missing))}")
    if report.get("mode") != "local_dry_run":
        errors.append("mode must be local_dry_run")
    for key in ("packs_seen", "packs_valid", "packs_invalid"):
        if not isinstance(report.get(key), int) or report.get(key) < 0:
            errors.append(f"{key} must be a non-negative integer")
    summaries = report.get("pack_summaries", [])
    if not isinstance(summaries, list):
        errors.append("pack_summaries must be a list")
        summaries = []
    if report.get("packs_seen") != len(summaries):
        errors.append("packs_seen must equal len(pack_summaries)")
    if report.get("packs_seen") != report.get("packs_valid") + report.get("packs_invalid"):
        errors.append("pack counts are inconsistent")
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
    if not isinstance(mutation, Mapping):
        errors.append("mutation_summary must be an object")
    else:
        for key, value in mutation.items():
            if value is not False:
                errors.append(f"mutation_summary.{key} must be false")
    effects = report.get("dry_run_effects", {})
    if isinstance(effects, Mapping):
        for key in ("accepted_records_created", "promotion_decisions_created", "authoritative_import_performed"):
            if effects.get(key) is not False:
                errors.append(f"dry_run_effects.{key} must be false")
    else:
        errors.append("dry_run_effects must be an object")
    return errors


def validate_audit_report(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not AUDIT_DIR.is_dir():
        errors.append(f"{AUDIT_DIR} missing")
    else:
        missing_files = sorted(name for name in REQUIRED_AUDIT_FILES if not (AUDIT_DIR / name).is_file())
        if missing_files:
            errors.append(f"audit pack missing files: {', '.join(missing_files)}")
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
    report_id = None
    if payload is not None:
        report_id = payload.get("report_id")
        if payload.get("mode") == "local_dry_run":
            errors.extend(validate_dry_run_report(payload))
        else:
            errors.extend(validate_audit_report(payload))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "pack_import_dry_run_report_validator_v0",
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
