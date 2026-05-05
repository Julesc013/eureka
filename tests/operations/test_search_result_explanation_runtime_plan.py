from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "search-result-explanation-runtime-planning-v0"
REPORT = AUDIT_ROOT / "search_result_explanation_runtime_planning_report.json"
INVENTORY = REPO_ROOT / "control" / "inventory" / "search" / "search_result_explanation_runtime_plan.json"
DOC = REPO_ROOT / "docs" / "operations" / "SEARCH_RESULT_EXPLANATION_RUNTIME_PLAN.md"
COMMAND_MATRIX = REPO_ROOT / "control" / "inventory" / "tests" / "command_matrix.json"

REQUIRED_FILES = [
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


class SearchResultExplanationRuntimePlanOperationsTest(unittest.TestCase):
    def test_audit_pack_exists(self) -> None:
        self.assertTrue(AUDIT_ROOT.exists())

    def test_required_files_exist(self) -> None:
        missing = [name for name in REQUIRED_FILES if not (AUDIT_ROOT / name).exists()]
        self.assertEqual(missing, [])

    def test_report_json_parses_and_readiness_valid(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertIn(payload["readiness_decision"], READINESS_VALUES)
        self.assertTrue(payload["planning_only"])
        self.assertFalse(payload["runtime_explanation_implemented"])

    def test_inventory_json_parses(self) -> None:
        payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "planning_only")
        self.assertFalse(payload["runtime_explanation_implemented"])
        self.assertFalse(payload["public_search_response_changed"])

    def test_gate_reviews_exist(self) -> None:
        for name in [
            "EXPLANATION_CONTRACT_GATE_REVIEW.md",
            "PUBLIC_SEARCH_AND_RESULT_CARD_GATE_REVIEW.md",
            "PUBLIC_INDEX_AND_RESULT_ENVELOPE_GATE_REVIEW.md",
            "DEPENDENCY_GATE_REVIEW.md",
            "PRIVACY_REDACTION_AND_COPY_POLICY_REVIEW.md",
            "MODEL_AI_AND_HIDDEN_SCORE_BOUNDARY_REVIEW.md",
            "RUNTIME_BOUNDARY.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ]:
            self.assertTrue((AUDIT_ROOT / name).exists(), name)

    def test_command_matrix_includes_validator(self) -> None:
        payload = json.loads(COMMAND_MATRIX.read_text(encoding="utf-8"))
        commands = {command for lane in payload["lanes"] for command in lane["commands"]}
        self.assertIn("search_result_explanation_runtime_plan_validator", commands)
        self.assertIn("search_result_explanation_runtime_plan_validator_json", commands)

    def test_docs_exist(self) -> None:
        self.assertTrue(DOC.exists())
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("ready_for_local_dry_run_runtime_after_operator_approval", text)
        self.assertIn("no model calls", text)


if __name__ == "__main__":
    unittest.main()

