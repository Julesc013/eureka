from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONTRACTS = [
    "contracts/search/search_result_explanation.v0.json",
    "contracts/search/search_result_explanation_component.v0.json",
    "contracts/search/search_result_explanation_policy.v0.json",
]
AUDIT_REQUIRED = [
    "README.md",
    "CONTRACT_SUMMARY.md",
    "SEARCH_RESULT_EXPLANATION_SCHEMA.md",
    "EXPLANATION_COMPONENT_TAXONOMY.md",
    "QUERY_INTERPRETATION_EXPLANATION_MODEL.md",
    "MATCH_AND_RECALL_EXPLANATION_MODEL.md",
    "SOURCE_COVERAGE_EXPLANATION_MODEL.md",
    "EVIDENCE_AND_PROVENANCE_EXPLANATION_MODEL.md",
    "IDENTITY_GROUPING_AND_DEDUPLICATION_EXPLANATION_MODEL.md",
    "RANKING_EXPLANATION_RELATIONSHIP.md",
    "COMPATIBILITY_EXPLANATION_MODEL.md",
    "ABSENCE_NEAR_MISS_AND_GAP_EXPLANATION_MODEL.md",
    "ACTION_SAFETY_EXPLANATION_MODEL.md",
    "RIGHTS_RISK_CAUTION_MODEL.md",
    "USER_FACING_COPY_POLICY.md",
    "API_STATIC_LITE_TEXT_PROJECTION.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_HIDDEN_SCORE_NO_TRUTH_NO_RUNTIME_NO_MUTATION_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_SEARCH_RESULT_EXPLANATION_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "search_result_explanation_contract_report.json",
]
EXAMPLES = [
    "minimal_match_explanation_v0",
    "minimal_source_evidence_explanation_v0",
    "minimal_grouped_result_explanation_v0",
    "minimal_compatibility_explanation_v0",
    "minimal_absence_gap_explanation_v0",
    "minimal_conflict_explanation_v0",
    "minimal_action_safety_explanation_v0",
]
REPORT_FALSE = [
    "runtime_explanation_implemented",
    "persistent_explanation_store_implemented",
    "explanation_generated_by_runtime",
    "explanation_applied_to_live_search",
    "public_search_response_changed",
    "public_search_order_changed",
    "hidden_score_used",
    "hidden_suppression_performed",
    "result_suppressed",
    "model_call_performed",
    "AI_generated_answer",
    "candidate_promotion_performed",
    "ranking_applied_to_live_search",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "installability_claimed",
]
INVENTORY_FALSE = [
    "runtime_explanation_implemented",
    "persistent_explanation_store_implemented",
    "explanation_applied_to_live_search",
    "public_search_response_changed",
    "public_search_order_changed",
    "hidden_scores_allowed",
    "hidden_suppression_allowed",
    "result_suppression_without_explanation_allowed",
    "model_calls_allowed",
    "AI_answer_generation_allowed",
    "telemetry_enabled",
    "candidate_promotion_allowed",
    "source_cache_mutation_allowed",
    "evidence_ledger_mutation_allowed",
    "candidate_index_mutation_allowed",
    "public_index_mutation_allowed",
    "local_index_mutation_allowed",
    "master_index_mutation_allowed",
    "raw_query_in_explanation_allowed",
    "private_data_in_public_explanation_allowed",
    "rights_clearance_claim_allowed",
    "malware_safety_claim_allowed",
    "installability_claim_allowed_without_evidence",
    "live_source_call_allowed",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_validator(args: list[str]) -> None:
    result = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise AssertionError(f"{' '.join(args)} failed: {result.stdout} {result.stderr}")


def validate() -> list[str]:
    checked: list[str] = []
    for rel in CONTRACTS:
        path = ROOT / rel
        if not path.exists():
            raise AssertionError(f"missing contract {rel}")
        load(path)
        checked.append(rel)
    inventory = ROOT / "control/inventory/search/search_result_explanation_policy.json"
    if not inventory.exists():
        raise AssertionError("missing search result explanation inventory")
    inventory_data = load(inventory)
    if inventory_data.get("status") != "contract_only":
        raise AssertionError("inventory status must be contract_only")
    for key in INVENTORY_FALSE:
        if inventory_data.get(key) is not False:
            raise AssertionError(f"inventory {key} must be false")
    if not inventory_data.get("required_components"):
        raise AssertionError("inventory required_components must be present")
    checked.append(str(inventory.relative_to(ROOT)))

    audit = ROOT / "control/audits/search-result-explanation-contract-v0"
    for name in AUDIT_REQUIRED:
        path = audit / name
        if not path.exists():
            raise AssertionError(f"missing audit file {name}")
        checked.append(str(path.relative_to(ROOT)))
    report = load(audit / "search_result_explanation_contract_report.json")
    for key in REPORT_FALSE:
        if report.get(key) is not False:
            raise AssertionError(f"report {key} must be false")

    for root_name in EXAMPLES:
        root = ROOT / "examples/search_result_explanations" / root_name
        for name in ("SEARCH_RESULT_EXPLANATION.json", "SEARCH_RESULT_EXPLANATION_POLICY.json", "README.md", "CHECKSUMS.SHA256"):
            path = root / name
            if not path.exists():
                raise AssertionError(f"missing example file {path}")
        checked.append(str(root.relative_to(ROOT)))
    run_validator(["scripts/validate_search_result_explanation.py", "--all-examples"])

    docs = [
        ROOT / "docs/reference/SEARCH_RESULT_EXPLANATION_CONTRACT.md",
        audit / "EXPLANATION_COMPONENT_TAXONOMY.md",
        audit / "QUERY_INTERPRETATION_EXPLANATION_MODEL.md",
        audit / "MATCH_AND_RECALL_EXPLANATION_MODEL.md",
        audit / "SOURCE_COVERAGE_EXPLANATION_MODEL.md",
        audit / "EVIDENCE_AND_PROVENANCE_EXPLANATION_MODEL.md",
        audit / "IDENTITY_GROUPING_AND_DEDUPLICATION_EXPLANATION_MODEL.md",
        audit / "RANKING_EXPLANATION_RELATIONSHIP.md",
        audit / "COMPATIBILITY_EXPLANATION_MODEL.md",
        audit / "ABSENCE_NEAR_MISS_AND_GAP_EXPLANATION_MODEL.md",
        audit / "ACTION_SAFETY_EXPLANATION_MODEL.md",
        audit / "RIGHTS_RISK_CAUTION_MODEL.md",
        audit / "USER_FACING_COPY_POLICY.md",
        audit / "API_STATIC_LITE_TEXT_PROJECTION.md",
        audit / "PRIVACY_AND_REDACTION_POLICY.md",
        audit / "NO_HIDDEN_SCORE_NO_TRUTH_NO_RUNTIME_NO_MUTATION_POLICY.md",
        audit / "INTEGRATION_BOUNDARIES.md",
    ]
    required_phrases = [
        "contract-only",
        "no runtime",
        "no hidden score",
        "no suppression",
        "no AI answer",
        "no mutation",
        "query interpretation",
        "source coverage",
        "evidence",
        "ranking",
        "compatibility",
        "privacy",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in docs)
    for phrase in required_phrases:
        if phrase.lower() not in combined:
            raise AssertionError(f"search result explanation docs missing phrase {phrase}")
    for path in docs:
        checked.append(str(path.relative_to(ROOT)))
    return checked


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Search Result Explanation Contract v0.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    checked: list[str] = []
    errors: list[str] = []
    try:
        checked = validate()
    except Exception as exc:
        errors.append(str(exc))
    if args.json:
        print(json.dumps({"ok": not errors, "checked": checked, "error_count": len(errors), "errors": errors}, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print(f"search result explanation contract validation passed: {len(checked)} item(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
