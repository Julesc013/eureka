from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "public-search-ranking-local-dry-run-runtime-v0"
DEFAULT_REPORT = AUDIT_ROOT / "public_search_ranking_local_dry_run_runtime_report.json"

REQUIRED_AUDIT_FIELDS = [
    "report_id",
    "created_by_slice",
    "repo_head",
    "branch",
    "worktree_status",
    "runtime_scope",
    "eval_gate_status",
    "input_model",
    "output_model",
    "runtime_modules",
    "cli_script",
    "validator_script",
    "examples",
    "dry_run_results",
    "factor_summary",
    "evidence_weighted_factor_summary",
    "compatibility_aware_factor_summary",
    "grouping_identity_boundary",
    "explanation_user_reason_model",
    "current_order_fallback_model",
    "privacy_no_telemetry_hidden_score_review",
    "public_search_boundary",
    "source_cache_evidence_candidate_boundary",
    "mutation_promotion_boundary",
    "command_results",
    "remaining_blockers",
    "next_recommended_branch",
    "notes",
]

REQUIRED_DRY_RUN_FIELDS = [
    "report_id",
    "mode",
    "input_roots",
    "result_sets_seen",
    "result_sets_valid",
    "result_sets_invalid",
    "result_summaries",
    "current_order",
    "proposed_dry_run_order",
    "fallback_order",
    "ranking_factors",
    "factor_summary",
    "explanation_summaries",
    "conflict_gap_visibility_summary",
    "privacy_status_counts",
    "public_safety_status_counts",
    "eval_gate_summary",
    "warnings",
    "errors",
    "hard_booleans",
]

FALSE_KEYS = [
    "public_search_ranking_runtime_enabled",
    "public_search_response_changed",
    "public_search_order_changed",
    "public_search_routes_changed",
    "hosted_runtime_enabled",
    "hidden_scores_enabled",
    "hidden_suppression_performed",
    "result_suppression_enabled",
    "model_call_performed",
    "AI_reranking_performed",
    "telemetry_signal_used",
    "popularity_signal_used",
    "user_profile_signal_used",
    "ad_signal_used",
    "source_cache_read",
    "evidence_ledger_read",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "credentials_used",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
]

REQUIRED_AUDIT_FILES = [
    "README.md",
    "IMPLEMENTATION_SUMMARY.md",
    "RUNTIME_SCOPE.md",
    "EVAL_GATE_STATUS.md",
    "DRY_RUN_INPUT_MODEL.md",
    "DRY_RUN_OUTPUT_MODEL.md",
    "RANKING_FACTOR_MODEL.md",
    "EVIDENCE_WEIGHTED_FACTOR_IMPLEMENTATION.md",
    "COMPATIBILITY_AWARE_FACTOR_IMPLEMENTATION.md",
    "GROUPING_AND_IDENTITY_FACTOR_BOUNDARY.md",
    "EXPLANATION_AND_USER_VISIBLE_REASON_MODEL.md",
    "CURRENT_ORDER_FALLBACK_MODEL.md",
    "PRIVACY_NO_TELEMETRY_AND_NO_HIDDEN_SCORE_REVIEW.md",
    "PUBLIC_SEARCH_BOUNDARY.md",
    "SOURCE_CACHE_EVIDENCE_CANDIDATE_BOUNDARY.md",
    "MUTATION_AND_PROMOTION_BOUNDARY.md",
    "FAILURE_AND_ERROR_MODEL.md",
    "ACCEPTANCE_RESULTS.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "public_search_ranking_local_dry_run_runtime_report.json",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _bool_source(data: dict[str, Any]) -> dict[str, Any]:
    hard = data.get("hard_booleans")
    return hard if isinstance(hard, dict) else data


def validate(path: Path, audit_report: bool = False) -> list[str]:
    errors: list[str] = []
    if audit_report:
        if not AUDIT_ROOT.exists():
            errors.append(f"missing audit pack: {AUDIT_ROOT.relative_to(ROOT)}")
        for name in REQUIRED_AUDIT_FILES:
            if not (AUDIT_ROOT / name).exists():
                errors.append(f"missing file: {(AUDIT_ROOT / name).relative_to(ROOT)}")
    if not path.exists():
        return errors + [f"missing report: {path}"]
    try:
        data = _load(path)
    except Exception as exc:  # noqa: BLE001
        return errors + [f"report JSON parse failed: {exc}"]
    required = REQUIRED_AUDIT_FIELDS if audit_report else REQUIRED_DRY_RUN_FIELDS
    for field in required:
        if field not in data:
            errors.append(f"report missing field: {field}")
    if not audit_report and data.get("mode") != "local_dry_run":
        errors.append("report.mode must be local_dry_run")
    bools = _bool_source(data)
    if bools.get("local_dry_run" if not audit_report else "local_dry_run_runtime_implemented") is not True:
        errors.append("local dry-run true flag missing")
    for key in FALSE_KEYS:
        if bools.get(key) is not False:
            errors.append(f"{key} must be false")
    if not audit_report:
        seen = data.get("result_sets_seen")
        valid = data.get("result_sets_valid")
        invalid = data.get("result_sets_invalid")
        if isinstance(seen, int) and isinstance(valid, int) and isinstance(invalid, int):
            if valid + invalid != seen:
                errors.append("result set counts are inconsistent")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate P107 ranking dry-run report.")
    parser.add_argument("--report", help="Dry-run report JSON path.")
    parser.add_argument("--audit-report", action="store_true", help="Validate the default P107 audit report.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args(argv)

    path = Path(args.report) if args.report else DEFAULT_REPORT
    audit_report = args.audit_report or args.report is None
    errors = validate(path, audit_report=audit_report)
    payload = {"status": "invalid" if errors else "valid", "errors": errors, "report": str(path)}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        for error in errors:
            print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

