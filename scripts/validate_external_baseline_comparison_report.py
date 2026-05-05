#!/usr/bin/env python3
"""Validate External Baseline Comparison Report v0 audit files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "external-baseline-comparison-report-v0"
REPORT_PATH = AUDIT_DIR / "external_baseline_comparison_report.json"
DOC_PATH = REPO_ROOT / "docs" / "operations" / "EXTERNAL_BASELINE_COMPARISON.md"
RUNNER_PATH = REPO_ROOT / "scripts" / "run_external_baseline_comparison.py"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "COMPARISON_SUMMARY.md",
    "BASELINE_OBSERVATION_STATUS.md",
    "ELIGIBILITY_DECISION.md",
    "BASELINE_SCHEMA_REVIEW.md",
    "BASELINE_BATCH_REVIEW.md",
    "EUREKA_SEARCH_RUN_RESULTS.md",
    "COMPARISON_METHOD.md",
    "QUERY_BY_QUERY_COMPARISON.md",
    "SOURCE_AND_CAPABILITY_GAP_ANALYSIS.md",
    "WHERE_EUREKA_HELPED.md",
    "WHERE_EUREKA_FAILED.md",
    "NOT_COMPARABLE_CASES.md",
    "LIMITATIONS.md",
    "CLAIMS_AND_NON_CLAIMS.md",
    "MANUAL_WORK_REMAINING.md",
    "NEXT_PRODUCT_PRIORITIES.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "external_baseline_comparison_report.json",
}
VALID_ELIGIBILITY = {
    "no_observations",
    "partial_observations",
    "complete_batch",
    "invalid_observations",
    "local_search_unavailable",
    "eligible",
    "comparison_completed",
}
COMPARISON_COUNT_FIELDS = (
    "eureka_better_count",
    "baseline_better_count",
    "both_good_count",
    "both_partial_count",
    "eureka_only_count",
    "baseline_only_count",
    "neither_count",
    "not_comparable_count",
    "insufficient_data_count",
)
REQUIRED_FALSE_BOOLEANS = (
    "external_calls_performed",
    "live_source_calls_performed",
    "model_calls_performed",
    "fabricated_observations",
    "fabricated_comparisons",
    "production_claimed",
    "master_index_mutated",
    "public_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
)


def validate_external_baseline_comparison_report() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not RUNNER_PATH.is_file():
        errors.append("scripts/run_external_baseline_comparison.py is missing.")

    if not AUDIT_DIR.is_dir():
        errors.append("control/audits/external-baseline-comparison-report-v0 is missing.")
    else:
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_AUDIT_FILES - existing)
        if missing:
            errors.append(f"missing audit files: {', '.join(missing)}")

    report = _load_report(errors)
    if report:
        _validate_report(report, errors, warnings)

    if not DOC_PATH.is_file():
        errors.append("docs/operations/EXTERNAL_BASELINE_COMPARISON.md is missing.")
    else:
        doc = DOC_PATH.read_text(encoding="utf-8").casefold()
        for phrase in (
            "manual observation",
            "no web calls",
            "no-fabrication",
            "eligibility",
            "local_index_only",
        ):
            if phrase not in doc:
                errors.append(f"EXTERNAL_BASELINE_COMPARISON.md missing phrase: {phrase}")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "external_baseline_comparison_report_validator_v0",
        "report_id": report.get("report_id") if report else None,
        "eligibility": report.get("eligibility") if report else None,
        "observed_count": report.get("observed_count") if report else None,
        "pending_count": report.get("pending_count") if report else None,
        "compared_count": report.get("compared_count") if report else None,
        "errors": errors,
        "warnings": warnings,
    }


def _load_report(errors: list[str]) -> dict[str, Any]:
    if not REPORT_PATH.is_file():
        errors.append("external_baseline_comparison_report.json is missing.")
        return {}
    try:
        payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"external_baseline_comparison_report.json invalid JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append("external_baseline_comparison_report.json must be an object.")
        return {}
    return payload


def _validate_report(report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if report.get("report_id") != "external_baseline_comparison_report_v0":
        errors.append("report_id must be external_baseline_comparison_report_v0.")
    if report.get("eligibility") not in VALID_ELIGIBILITY:
        errors.append(f"eligibility has invalid value: {report.get('eligibility')!r}.")

    observed_count = _int(report.get("observed_count"))
    pending_count = _int(report.get("pending_count"))
    invalid_count = _int(report.get("invalid_count"))
    compared_count = _int(report.get("compared_count"))

    if observed_count < 0 or pending_count < 0 or invalid_count < 0 or compared_count < 0:
        errors.append("counts must be non-negative integers.")
    if observed_count == 0 and compared_count != 0:
        errors.append("observed_count 0 requires compared_count 0.")
    if report.get("eligibility") == "no_observations" and observed_count != 0:
        errors.append("eligibility no_observations requires observed_count 0.")
    if observed_count > 0 and report.get("eligibility") == "no_observations":
        errors.append("no_observations is invalid when observed_count > 0.")

    aggregate = report.get("aggregate_comparison")
    if not isinstance(aggregate, Mapping):
        errors.append("aggregate_comparison must be present.")
    else:
        aggregate_compared = _int(aggregate.get("compared_count"))
        label_sum = sum(_int(aggregate.get(field)) for field in COMPARISON_COUNT_FIELDS)
        if aggregate_compared != compared_count:
            errors.append("aggregate_comparison.compared_count must match compared_count.")
        if label_sum != compared_count:
            errors.append("comparison label counts must sum to compared_count.")
        if compared_count == 0:
            for field in COMPARISON_COUNT_FIELDS:
                if _int(aggregate.get(field)) != 0:
                    errors.append(f"{field} must be 0 when compared_count is 0.")

    for key in REQUIRED_FALSE_BOOLEANS:
        if report.get(key) is not False:
            errors.append(f"{key} must be false.")
    if compared_count == 0 and report.get("superiority_claimed") is not False:
        errors.append("superiority_claimed must be false when compared_count is 0.")
    if report.get("fabricated_observations") is not False:
        errors.append("fabricated_observations must be false.")
    if report.get("fabricated_comparisons") is not False:
        errors.append("fabricated_comparisons must be false.")

    manual = report.get("manual_work_remaining")
    if pending_count > 0 and (not isinstance(manual, list) or not manual):
        errors.append("manual_work_remaining must be non-empty when observations are pending.")
    command_results = report.get("command_results")
    if not isinstance(command_results, list) or not command_results:
        errors.append("command_results must be a non-empty list.")
    remaining = report.get("remaining_blockers")
    if not isinstance(remaining, list) or not remaining:
        errors.append("remaining_blockers must be a non-empty list.")
    claims = report.get("claims_and_non_claims")
    if not isinstance(claims, Mapping):
        errors.append("claims_and_non_claims must be present.")
    else:
        for key in (
            "no_external_calls_performed",
            "no_observations_fabricated",
            "no_comparisons_fabricated",
            "no_production_readiness_claim",
        ):
            if claims.get(key) is not True:
                errors.append(f"claims_and_non_claims.{key} must be true.")

    if observed_count == 0:
        warnings.append("No manual baseline observations are present; comparison is intentionally not eligible.")


def _int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _format_plain(result: Mapping[str, Any]) -> str:
    lines = [
        "External Baseline Comparison Report validation",
        f"status: {result['status']}",
        f"report_id: {result.get('report_id')}",
        f"eligibility: {result.get('eligibility')}",
        f"observed_count: {result.get('observed_count')}",
        f"pending_count: {result.get('pending_count')}",
        f"compared_count: {result.get('compared_count')}",
    ]
    if result.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in result["errors"])
    if result.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in result["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON validation output.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = validate_external_baseline_comparison_report()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(result))
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
