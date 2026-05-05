from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "search-result-explanation-runtime-planning-v0"
DEFAULT_REPORT = AUDIT_ROOT / "search_result_explanation_runtime_planning_report.json"
DEFAULT_INVENTORY = ROOT / "control" / "inventory" / "search" / "search_result_explanation_runtime_plan.json"

READINESS_VALUES = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_hosted_staging_after_operator_approval",
    "ready_for_planning_only",
    "blocked_search_result_explanation_contract_missing",
    "blocked_explanation_examples_missing",
    "blocked_public_search_contract_missing",
    "blocked_public_result_card_contract_missing",
    "blocked_public_index_contract_missing",
    "blocked_public_search_safety_failed",
    "blocked_result_envelope_incomplete",
    "blocked_dependency_contracts_missing",
    "blocked_privacy_redaction_policy_incomplete",
    "blocked_model_ai_boundary_incomplete",
    "blocked_source_cache_evidence_boundary_incomplete",
    "blocked_hosted_deployment_unverified",
    "blocked_other",
}

REQUIRED_AUDIT_FILES = [
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "EXPLANATION_CONTRACT_GATE_REVIEW.md",
    "PUBLIC_SEARCH_AND_RESULT_CARD_GATE_REVIEW.md",
    "PUBLIC_INDEX_AND_RESULT_ENVELOPE_GATE_REVIEW.md",
    "HOSTED_DEPLOYMENT_GATE_REVIEW.md",
    "DEPENDENCY_GATE_REVIEW.md",
    "PRIVACY_REDACTION_AND_COPY_POLICY_REVIEW.md",
    "MODEL_AI_AND_HIDDEN_SCORE_BOUNDARY_REVIEW.md",
    "SOURCE_CACHE_EVIDENCE_CANDIDATE_BOUNDARY_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "EXPLANATION_RUNTIME_ARCHITECTURE_PLAN.md",
    "APPROVED_INPUT_MODEL.md",
    "EXPLANATION_PIPELINE_PLAN.md",
    "COMPONENT_ASSEMBLY_PLAN.md",
    "API_STATIC_LITE_TEXT_OUTPUT_PLAN.md",
    "FAILURE_FALLBACK_AND_ROLLBACK_MODEL.md",
    "SECURITY_AND_ABUSE_REVIEW.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "search_result_explanation_runtime_planning_report.json",
]

REQUIRED_REPORT_FIELDS = [
    "report_id",
    "created_by_slice",
    "repo_head",
    "branch",
    "worktree_status",
    "readiness_decision",
    "explanation_contract_gate_review",
    "public_search_result_card_gate_review",
    "public_index_result_envelope_gate_review",
    "hosted_deployment_gate_review",
    "dependency_gate_review",
    "privacy_redaction_copy_policy_review",
    "model_ai_hidden_score_boundary_review",
    "source_cache_evidence_candidate_boundary_review",
    "runtime_boundary",
    "runtime_architecture_plan",
    "approved_input_model",
    "explanation_pipeline_plan",
    "component_assembly_plan",
    "api_static_lite_text_output_plan",
    "failure_fallback_rollback_model",
    "security_abuse_review",
    "implementation_phases",
    "acceptance_criteria",
    "command_results",
    "remaining_blockers",
    "next_recommended_branch",
    "notes",
]

REPORT_TRUE = ["planning_only"]
REPORT_FALSE = [
    "runtime_explanation_implemented",
    "explanation_generated_by_runtime",
    "explanation_applied_to_live_search",
    "public_search_response_changed",
    "public_search_routes_changed",
    "public_search_order_changed",
    "explanation_api_routes_enabled",
    "persistent_explanation_store_implemented",
    "model_call_performed",
    "model_calls_enabled",
    "AI_generated_answer",
    "ai_answer_generation_enabled",
    "hidden_score_used",
    "hidden_scores_enabled",
    "hidden_suppression_performed",
    "result_suppression_enabled",
    "result_suppressed",
    "telemetry_enabled",
    "accounts_enabled",
    "source_cache_read",
    "source_cache_mutated",
    "evidence_ledger_read",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
]

INVENTORY_TRUE = [
    "public_search_contract_required",
    "result_card_contract_required",
    "explanation_contract_required",
    "privacy_redaction_policy_required",
    "no_model_boundary_required",
    "no_hidden_score_policy_required",
    "hosted_deployment_required_for_hosted_runtime",
    "operator_approval_required",
]

INVENTORY_FALSE = [
    "runtime_explanation_implemented",
    "explanation_runtime_enabled",
    "public_search_response_changed",
    "public_search_routes_changed",
    "explanation_api_routes_enabled",
    "persistent_explanation_store_implemented",
    "model_calls_enabled",
    "ai_answer_generation_enabled",
    "hidden_scores_enabled",
    "result_suppression_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "source_cache_reads_enabled",
    "evidence_ledger_reads_enabled",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "live_source_calls_enabled",
]

ACCEPTANCE_PHRASES = [
    "explanation contract",
    "public search",
    "result-card",
    "public index/result envelope",
    "privacy/redaction",
    "no-model",
    "no-hidden-score",
    "source/evidence/candidate boundary",
    "fallback",
    "hosted deployment",
    "operator approval",
]

DO_NOT_IMPLEMENT_PHRASES = [
    "no explanation runtime",
    "no public search response changes",
    "no public route changes",
    "no API explanation route",
    "no model calls",
    "no hidden scores",
    "no source cache reads/writes",
    "no evidence ledger reads/writes",
    "no public/local/master index mutation",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require_file(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(ROOT)}")


def _validate_bool(data: dict[str, Any], key: str, expected: bool, errors: list[str], prefix: str) -> None:
    if data.get(key) is not expected:
        errors.append(f"{prefix}.{key} must be {str(expected).lower()}")


def _combined_text(paths: list[Path]) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists()).lower()


def validate(report_path: Path, inventory_path: Path) -> list[str]:
    errors: list[str] = []

    if not AUDIT_ROOT.exists():
        errors.append(f"missing audit pack: {AUDIT_ROOT.relative_to(ROOT)}")
    for name in REQUIRED_AUDIT_FILES:
        _require_file(AUDIT_ROOT / name, errors)

    doc = ROOT / "docs" / "operations" / "SEARCH_RESULT_EXPLANATION_RUNTIME_PLAN.md"
    _require_file(doc, errors)
    _require_file(inventory_path, errors)
    _require_file(report_path, errors)

    report: dict[str, Any] = {}
    inventory: dict[str, Any] = {}
    if report_path.exists():
        try:
            report = _load_json(report_path)
        except Exception as exc:  # noqa: BLE001 - bounded validator output
            errors.append(f"report JSON parse failed: {exc}")
    if inventory_path.exists():
        try:
            inventory = _load_json(inventory_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"inventory JSON parse failed: {exc}")

    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"report missing field: {field}")

    decision = report.get("readiness_decision")
    if decision not in READINESS_VALUES:
        errors.append(f"invalid readiness_decision: {decision}")

    for key in REPORT_TRUE:
        _validate_bool(report, key, True, errors, "report")
    for key in REPORT_FALSE:
        _validate_bool(report, key, False, errors, "report")

    if inventory.get("status") != "planning_only":
        errors.append("inventory.status must be planning_only")
    for key in INVENTORY_TRUE:
        _validate_bool(inventory, key, True, errors, "inventory")
    for key in INVENTORY_FALSE:
        _validate_bool(inventory, key, False, errors, "inventory")

    acceptance = _combined_text([AUDIT_ROOT / "ACCEPTANCE_CRITERIA.md"])
    for phrase in ACCEPTANCE_PHRASES:
        if phrase.lower() not in acceptance:
            errors.append(f"acceptance criteria missing phrase: {phrase}")

    do_not = _combined_text([AUDIT_ROOT / "DO_NOT_IMPLEMENT_YET.md"])
    for phrase in DO_NOT_IMPLEMENT_PHRASES:
        if phrase.lower() not in do_not:
            errors.append(f"DO_NOT_IMPLEMENT_YET missing phrase: {phrase}")

    for name in [
        "EXPLANATION_CONTRACT_GATE_REVIEW.md",
        "PUBLIC_SEARCH_AND_RESULT_CARD_GATE_REVIEW.md",
        "PUBLIC_INDEX_AND_RESULT_ENVELOPE_GATE_REVIEW.md",
        "DEPENDENCY_GATE_REVIEW.md",
        "PRIVACY_REDACTION_AND_COPY_POLICY_REVIEW.md",
        "MODEL_AI_AND_HIDDEN_SCORE_BOUNDARY_REVIEW.md",
    ]:
        _require_file(AUDIT_ROOT / name, errors)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate P106 search result explanation runtime planning audit.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Report JSON path to validate.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY), help="Inventory JSON path to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON validation result.")
    args = parser.parse_args(argv)

    errors = validate(Path(args.report), Path(args.inventory))
    payload = {
        "status": "invalid" if errors else "valid",
        "errors": errors,
        "report": str(Path(args.report)),
        "inventory": str(Path(args.inventory)),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        for error in errors:
            print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

