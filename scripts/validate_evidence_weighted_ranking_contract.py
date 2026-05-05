#!/usr/bin/env python3
"""Validate Evidence-Weighted Ranking Contract v0 governance artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_evidence_weighted_ranking_assessment import validate_all_examples as validate_all_assessments  # noqa: E402
from scripts.validate_ranking_explanation import validate_all_examples as validate_all_explanations  # noqa: E402


ASSESSMENT_SCHEMA = REPO_ROOT / "contracts" / "search" / "evidence_weighted_ranking_assessment.v0.json"
EXPLANATION_SCHEMA = REPO_ROOT / "contracts" / "search" / "ranking_explanation.v0.json"
FACTOR_SCHEMA = REPO_ROOT / "contracts" / "search" / "ranking_factor.v0.json"
POLICY_PATH = REPO_ROOT / "control" / "inventory" / "search" / "evidence_weighted_ranking_policy.json"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "evidence-weighted-ranking-contract-v0"
REPORT_PATH = AUDIT_DIR / "evidence_weighted_ranking_report.json"
DOC_PATH = REPO_ROOT / "docs" / "reference" / "EVIDENCE_WEIGHTED_RANKING_CONTRACT.md"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "RANKING_ASSESSMENT_SCHEMA.md",
    "RANKING_EXPLANATION_SCHEMA.md",
    "RANKING_FACTOR_TAXONOMY.md",
    "EVIDENCE_STRENGTH_MODEL.md",
    "PROVENANCE_STRENGTH_MODEL.md",
    "SOURCE_POSTURE_MODEL.md",
    "FRESHNESS_AND_STALENESS_MODEL.md",
    "CONFLICT_AND_UNCERTAINTY_PENALTY_MODEL.md",
    "CANDIDATE_AND_PROVISIONAL_STATUS_MODEL.md",
    "ABSENCE_AND_GAP_TRANSPARENCY_MODEL.md",
    "ACTION_SAFETY_MODEL.md",
    "RIGHTS_RISK_CAUTION_MODEL.md",
    "TIE_BREAK_POLICY.md",
    "ANTI_POPULARITY_AND_ANTI_TELEMETRY_POLICY.md",
    "NO_HIDDEN_SUPPRESSION_POLICY.md",
    "RESULT_CARD_OBJECT_SOURCE_COMPARISON_PROJECTION.md",
    "API_PROJECTION.md",
    "STATIC_DEMO_PROJECTION.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_RUNTIME_NO_RANKING_CHANGE_NO_MUTATION_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_RANKING_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "evidence_weighted_ranking_report.json",
}
ASSESSMENT_REQUIRED = {
    "schema_version",
    "ranking_assessment_id",
    "ranking_assessment_kind",
    "status",
    "created_by_tool",
    "ranking_scope",
    "ranked_items",
    "ranking_factors",
    "evidence_strength",
    "provenance_strength",
    "source_posture",
    "freshness",
    "conflicts_and_uncertainty",
    "candidate_status",
    "absence_and_gaps",
    "action_safety",
    "rights_risk",
    "tie_breaks",
    "ranking_explanation_ref",
    "public_projection",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_ranking_change_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ASSESSMENT_FALSE_FIELDS = {
    "runtime_ranking_implemented",
    "persistent_ranking_store_implemented",
    "ranking_applied_to_live_search",
    "public_search_order_changed",
    "result_suppressed",
    "hidden_suppression_performed",
    "candidate_promotion_performed",
    "records_merged",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "telemetry_exported",
    "popularity_signal_used",
    "user_profile_signal_used",
    "ad_signal_used",
    "model_call_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
}
EXPLANATION_REQUIRED = {
    "schema_version",
    "ranking_explanation_id",
    "ranking_explanation_kind",
    "status",
    "created_by_tool",
    "explanation_scope",
    "item_explanations",
    "factor_explanations",
    "uncertainty_explanations",
    "conflict_explanations",
    "gap_explanations",
    "tie_break_explanations",
    "public_user_text",
    "limitations",
    "no_hidden_suppression_guarantees",
    "no_runtime_guarantees",
    "notes",
}
EXPLANATION_FALSE_FIELDS = {
    "explanation_generated_by_runtime",
    "explanation_applied_to_live_search",
    "result_suppressed",
    "hidden_suppression_performed",
    "ranking_applied_to_live_search",
}
POLICY_FALSE_FIELDS = {
    "runtime_ranking_implemented",
    "persistent_ranking_store_implemented",
    "public_search_order_changed",
    "ranking_applied_to_live_search",
    "hidden_suppression_allowed",
    "result_suppression_allowed_without_explanation",
    "candidate_promotion_allowed",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "popularity_signal_allowed",
    "user_profile_signal_allowed",
    "ad_signal_allowed",
    "telemetry_signal_allowed",
    "random_tie_break_allowed",
}
POLICY_TRUE_FIELDS = {
    "evidence_strength_required",
    "provenance_strength_required",
    "conflict_explanation_required",
    "gap_transparency_required",
}
REPORT_FALSE_FIELDS = {
    "runtime_ranking_implemented",
    "persistent_ranking_store_implemented",
    "ranking_applied_to_live_search",
    "public_search_order_changed",
    "result_suppressed",
    "hidden_suppression_performed",
    "candidate_promotion_performed",
    "records_merged",
    "master_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "live_source_called",
    "external_calls_performed",
    "telemetry_implemented",
    "popularity_signal_allowed",
    "user_profile_signal_allowed",
    "ad_signal_allowed",
    "random_tie_break_allowed",
}
REQUIRED_DOC_PHRASES = {
    "contract-only",
    "ranking is not runtime yet",
    "ranking is not truth",
    "ranking is not candidate promotion",
    "ranking is not source trust",
    "ranking is not popularity/telemetry/ad/user-profile ranking",
    "evidence strength",
    "provenance",
    "source posture",
    "freshness",
    "conflicts must not be hidden",
    "candidate confidence is not truth",
    "global_absence_claimed is false",
    "random tie breaks are forbidden",
    "no hidden suppression",
    "public search",
    "public index",
    "source cache",
    "evidence ledger",
    "candidate index",
    "future compatibility-aware ranking",
    "no mutation",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_schema(path: Path, required_fields: set[str], false_fields: set[str], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing schema: {path.relative_to(REPO_ROOT)}")
        return
    try:
        schema = load_json(path)
    except Exception as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)} failed to parse: {exc}")
        return
    required = set(schema.get("required", []))
    missing = sorted((required_fields | false_fields) - required)
    if missing:
        errors.append(f"{path.relative_to(REPO_ROOT)} required list missing: {', '.join(missing)}")
    properties = schema.get("properties", {})
    if not isinstance(properties, Mapping):
        errors.append(f"{path.relative_to(REPO_ROOT)} properties must be an object")
        return
    for key in sorted(false_fields):
        prop = properties.get(key)
        if not isinstance(prop, Mapping):
            errors.append(f"{path.relative_to(REPO_ROOT)} missing false property {key}")
        elif prop.get("const") is not False:
            errors.append(f"{path.relative_to(REPO_ROOT)} property {key} must const false")


def check_false_map(data: Mapping[str, Any], fields: set[str], label: str, errors: list[str]) -> None:
    for field in sorted(fields):
        if data.get(field) is not False:
            errors.append(f"{label}.{field} must be false")


def validate_contract() -> list[str]:
    errors: list[str] = []
    check_schema(ASSESSMENT_SCHEMA, ASSESSMENT_REQUIRED, ASSESSMENT_FALSE_FIELDS, errors)
    check_schema(EXPLANATION_SCHEMA, EXPLANATION_REQUIRED, EXPLANATION_FALSE_FIELDS, errors)
    if not FACTOR_SCHEMA.exists():
        errors.append(f"missing schema: {FACTOR_SCHEMA.relative_to(REPO_ROOT)}")
    else:
        try:
            load_json(FACTOR_SCHEMA)
        except Exception as exc:
            errors.append(f"{FACTOR_SCHEMA.relative_to(REPO_ROOT)} failed to parse: {exc}")

    for path in (POLICY_PATH, DOC_PATH, REPORT_PATH):
        if not path.exists():
            errors.append(f"missing required artifact: {path.relative_to(REPO_ROOT)}")

    if AUDIT_DIR.exists():
        missing = sorted(name for name in REQUIRED_AUDIT_FILES if not (AUDIT_DIR / name).exists())
        if missing:
            errors.append(f"audit pack missing files: {', '.join(missing)}")
    else:
        errors.append(f"missing audit directory: {AUDIT_DIR.relative_to(REPO_ROOT)}")

    if POLICY_PATH.exists():
        policy = load_json(POLICY_PATH)
        if isinstance(policy, Mapping):
            check_false_map(policy, POLICY_FALSE_FIELDS, "policy", errors)
            for field in sorted(POLICY_TRUE_FIELDS):
                if policy.get(field) is not True:
                    errors.append(f"policy.{field} must be true")
        else:
            errors.append("ranking policy must be an object")

    if REPORT_PATH.exists():
        report = load_json(REPORT_PATH)
        if isinstance(report, Mapping):
            check_false_map(report, REPORT_FALSE_FIELDS, "report", errors)
            if report.get("runtime_status") != "contract_only_not_implemented":
                errors.append("report.runtime_status must be contract_only_not_implemented")
        else:
            errors.append("report must be an object")

    if DOC_PATH.exists():
        text = DOC_PATH.read_text(encoding="utf-8").lower()
        for phrase in sorted(REQUIRED_DOC_PHRASES):
            if phrase not in text:
                errors.append(f"doc missing phrase: {phrase}")

    assessment_paths, assessment_errors = validate_all_assessments()
    explanation_paths, explanation_errors = validate_all_explanations()
    if len(assessment_paths) < 5:
        errors.append("expected at least five ranking assessment examples")
    if len(explanation_paths) < 5:
        errors.append("expected at least five ranking explanation examples")
    errors.extend(assessment_errors)
    errors.extend(explanation_errors)
    return errors


def emit(errors: Sequence[str], *, as_json: bool, stream: TextIO) -> None:
    status = "valid" if not errors else "invalid"
    if as_json:
        print(
            json.dumps(
                {
                    "status": status,
                    "report_id": "evidence_weighted_ranking_contract_v0",
                    "assessment_example_count": len(validate_all_assessments()[0]),
                    "explanation_example_count": len(validate_all_explanations()[0]),
                    "contract_files": [
                        str(ASSESSMENT_SCHEMA.relative_to(REPO_ROOT)),
                        str(EXPLANATION_SCHEMA.relative_to(REPO_ROOT)),
                        str(FACTOR_SCHEMA.relative_to(REPO_ROOT)),
                    ],
                    "audit_dir": str(AUDIT_DIR.relative_to(REPO_ROOT)),
                    "errors": list(errors),
                },
                indent=2,
            ),
            file=stream,
        )
    else:
        print(f"status: {status}", file=stream)
        for error in errors:
            print(f"error: {error}", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors = validate_contract()
    emit(errors, as_json=args.json, stream=sys.stdout)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
