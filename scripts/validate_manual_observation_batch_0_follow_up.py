#!/usr/bin/env python3
"""Validate Manual Observation Batch 0 Follow-up Plan v0 artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "manual-observation-batch-0-follow-up-plan-v0"
REPORT_PATH = AUDIT_DIR / "manual_observation_batch_0_follow_up_report.json"
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "external_baselines" / "manual_observation_batch_0_follow_up.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "MANUAL_OBSERVATION_BATCH_0_FOLLOW_UP.md"

STATUS_VALUES = {
    "complete",
    "partial",
    "pending",
    "invalid",
    "missing",
    "not_applicable",
    "blocked",
    "ready_for_human_operation",
    "ready_for_comparison",
    "comparison_not_eligible",
}

REQUIRED_FILES = {
    "README.md",
    "FOLLOW_UP_SUMMARY.md",
    "CURRENT_BATCH_STATUS.md",
    "OBSERVATION_SCHEMA_STATUS.md",
    "OBSERVATION_VALIDATOR_STATUS.md",
    "BATCH_0_TASK_REVIEW.md",
    "HUMAN_WORK_INSTRUCTIONS.md",
    "OBSERVATION_WORKSHEET.md",
    "OBSERVATION_RECORD_TEMPLATE.md",
    "SOURCE_SPECIFIC_OBSERVATION_GUIDANCE.md",
    "PRIVACY_COPYRIGHT_AND_QUOTE_POLICY.md",
    "SCREENSHOT_AND_EVIDENCE_ATTACHMENT_POLICY.md",
    "VALIDATION_AND_REPAIR_GUIDE.md",
    "COMPARISON_READINESS_DECISION.md",
    "CODEX_BOUNDARY.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "manual_observation_batch_0_follow_up_report.json",
}

TRUE_FIELDS = {"follow_up_plan_only"}

FALSE_FIELDS = {
    "manual_observations_performed_by_codex",
    "external_calls_performed",
    "web_browsing_performed",
    "fabricated_observations",
    "fabricated_external_results",
    "comparison_claimed_complete",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "telemetry_enabled",
    "accounts_enabled",
    "uploads_enabled",
    "downloads_enabled",
}

INVENTORY_FALSE_FIELDS = {
    "codex_external_observation_allowed",
    "external_calls_performed",
    "fabricated_observations",
    "fabricated_results",
    "public_index_mutated",
    "master_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
}


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing required JSON: {display_path(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{display_path(path)} invalid JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{display_path(path)} must contain a JSON object")
        return {}
    return payload


def check_true(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not True:
            errors.append(f"{prefix}.{field} must be true")


def check_false(data: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not False:
            errors.append(f"{prefix}.{field} must be false")


def require_phrases(path: Path, phrases: Sequence[str], errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required artifact: {display_path(path)}")
        return ""
    text = path.read_text(encoding="utf-8")
    folded = text.casefold()
    for phrase in phrases:
        if phrase.casefold() not in folded:
            errors.append(f"{display_path(path)} missing required phrase: {phrase}")
    return text


def scan_sensitive_text(text: str, label: str, errors: list[str]) -> None:
    if re.search(r"\b[A-Za-z]:\\+(?:users|documents|downloads|desktop|projects|private|temp|windows)\\+", text, re.I):
        errors.append(f"{label} contains a prohibited private absolute path")
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
        errors.append(f"{label} contains an email-like private identifier")
    if re.search(r"\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{8,}", text, re.I):
        errors.append(f"{label} contains a secret-like value")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("report_id") != "manual_observation_batch_0_follow_up_plan_v0":
        errors.append("report.report_id must be manual_observation_batch_0_follow_up_plan_v0")
    for key in (
        "batch_0_status",
        "observation_schema_status",
        "observation_validator_status",
        "observation_record_status",
        "comparison_readiness_status",
        "human_work_status",
    ):
        if report.get(key) not in STATUS_VALUES:
            errors.append(f"report.{key} has invalid status {report.get(key)!r}")
    check_true(report, TRUE_FIELDS, "report", errors)
    check_false(report, FALSE_FIELDS, "report", errors)
    for count_key in ("observed_count", "pending_count", "invalid_count", "valid_count"):
        value = report.get(count_key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"report.{count_key} must be a non-negative integer")
    if report.get("observed_count") == 0 and report.get("comparison_readiness_status") != "comparison_not_eligible":
        errors.append("report.comparison_readiness_status must be comparison_not_eligible when observed_count is 0")
    if report.get("valid_count") != report.get("observed_count"):
        errors.append("report.valid_count must match observed_count for Batch 0 follow-up")
    if report.get("pending_count", 0) > 0 and report.get("human_work_required") is not True:
        errors.append("report.human_work_required must be true while pending observations remain")
    if not isinstance(report.get("task_review_summary"), Mapping):
        errors.append("report.task_review_summary must be an object")
    if not isinstance(report.get("command_results"), list) or not report.get("command_results"):
        errors.append("report.command_results must be a non-empty list")
    if not isinstance(report.get("remaining_blockers"), list) or not report.get("remaining_blockers"):
        errors.append("report.remaining_blockers must be a non-empty list")


def validate_inventory(inventory: Mapping[str, Any], errors: list[str]) -> None:
    if inventory.get("inventory_id") != "manual_observation_batch_0_follow_up_v0":
        errors.append("inventory.inventory_id must be manual_observation_batch_0_follow_up_v0")
    if inventory.get("status") not in STATUS_VALUES:
        errors.append("inventory.status has invalid status")
    if inventory.get("batch_id") != "batch_0":
        errors.append("inventory.batch_id must be batch_0")
    check_false(inventory, INVENTORY_FALSE_FIELDS, "inventory", errors)
    if inventory.get("manual_work_required") is not True:
        errors.append("inventory.manual_work_required must be true")
    if inventory.get("comparison_readiness_status") not in STATUS_VALUES:
        errors.append("inventory.comparison_readiness_status has invalid status")


def validate_artifacts(
    *,
    audit_dir: Path,
    report_path: Path,
    inventory_path: Path,
    doc_path: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not audit_dir.is_dir():
        errors.append(f"missing audit directory: {display_path(audit_dir)}")
    else:
        existing = {path.name for path in audit_dir.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_FILES - existing)
        if missing:
            errors.append(f"missing audit files: {', '.join(missing)}")
        for path in sorted(audit_dir.iterdir()):
            if path.is_file() and path.suffix in {".md", ".json"}:
                scan_sensitive_text(path.read_text(encoding="utf-8"), display_path(path), errors)

    report = load_json(report_path, errors)
    inventory = load_json(inventory_path, errors)
    if report:
        validate_report(report, errors)
    if inventory:
        validate_inventory(inventory, errors)

    require_phrases(
        audit_dir / "HUMAN_WORK_INSTRUCTIONS.md",
        ("perform the external search manually", "run the validator", "avoid long copyrighted quotes"),
        errors,
    )
    require_phrases(
        audit_dir / "OBSERVATION_WORKSHEET.md",
        ("task_id", "external_source", "validation_status"),
        errors,
    )
    require_phrases(
        audit_dir / "OBSERVATION_RECORD_TEMPLATE.md",
        ("placeholders are invalid", "observed_result_quality", "observed_results"),
        errors,
    )
    require_phrases(
        audit_dir / "VALIDATION_AND_REPAIR_GUIDE.md",
        ("validator commands", "placeholder", "rerun comparison"),
        errors,
    )
    require_phrases(
        audit_dir / "CODEX_BOUNDARY.md",
        ("must not perform manual observations", "must not browse external sites", "must not fabricate external results"),
        errors,
    )
    require_phrases(
        audit_dir / "COMPARISON_READINESS_DECISION.md",
        ("comparison_not_eligible", "valid observed records: 0"),
        errors,
    )
    doc_text = require_phrases(
        doc_path,
        (
            "human-operated",
            "codex must not browse",
            "comparison_not_eligible",
            "validate_external_baseline_observations.py",
        ),
        errors,
    )
    if doc_text:
        scan_sensitive_text(doc_text, display_path(doc_path), errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "manual_observation_batch_0_follow_up_validator_v0",
        "report_id": report.get("report_id") if report else None,
        "inventory_id": inventory.get("inventory_id") if inventory else None,
        "batch_0_status": report.get("batch_0_status") if report else None,
        "comparison_readiness_status": report.get("comparison_readiness_status") if report else None,
        "observed_count": report.get("observed_count") if report else None,
        "pending_count": report.get("pending_count") if report else None,
        "errors": errors,
        "warnings": warnings,
    }


def _format_plain(result: Mapping[str, Any]) -> str:
    lines = [
        "Manual Observation Batch 0 Follow-up validation",
        f"status: {result['status']}",
        f"report_id: {result.get('report_id')}",
        f"batch_0_status: {result.get('batch_0_status')}",
        f"comparison_readiness_status: {result.get('comparison_readiness_status')}",
        f"observed_count: {result.get('observed_count')}",
        f"pending_count: {result.get('pending_count')}",
    ]
    if result.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in result["errors"])
    if result.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", default=str(AUDIT_DIR))
    parser.add_argument("--report", default=str(REPORT_PATH))
    parser.add_argument("--inventory", default=str(INVENTORY_PATH))
    parser.add_argument("--doc", default=str(DOC_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_artifacts(
        audit_dir=Path(args.audit_dir),
        report_path=Path(args.report),
        inventory_path=Path(args.inventory),
        doc_path=Path(args.doc),
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_plain(result), end="")
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())

