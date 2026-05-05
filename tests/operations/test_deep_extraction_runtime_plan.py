from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "deep-extraction-runtime-planning-v0"
REPORT = AUDIT_ROOT / "deep_extraction_runtime_planning_report.json"
INVENTORY = REPO_ROOT / "control" / "inventory" / "extraction" / "deep_extraction_runtime_plan.json"
DOC = REPO_ROOT / "docs" / "operations" / "DEEP_EXTRACTION_RUNTIME_PLAN.md"
COMMAND_MATRIX = REPO_ROOT / "control" / "inventory" / "tests" / "command_matrix.json"

REQUIRED_FILES = [
    "README.md",
    "PLANNING_SUMMARY.md",
    "READINESS_DECISION.md",
    "EXTRACTION_CONTRACT_GATE_REVIEW.md",
    "SANDBOX_AND_RESOURCE_LIMIT_GATE_REVIEW.md",
    "PRIVACY_PATH_SECRET_GATE_REVIEW.md",
    "EXECUTABLE_PAYLOAD_AND_CONTENT_SAFETY_GATE_REVIEW.md",
    "OCR_TRANSCRIPTION_AND_TEXT_BOUNDARY_REVIEW.md",
    "PACK_IMPORT_AND_STAGING_BOUNDARY_REVIEW.md",
    "SOURCE_CACHE_EVIDENCE_CANDIDATE_BOUNDARY_REVIEW.md",
    "PUBLIC_SEARCH_AND_PAGE_BOUNDARY_REVIEW.md",
    "RUNTIME_BOUNDARY.md",
    "DEEP_EXTRACTION_RUNTIME_ARCHITECTURE_PLAN.md",
    "APPROVED_INPUT_MODEL.md",
    "EXTRACTION_PIPELINE_PLAN.md",
    "CONTAINER_TYPE_HANDLING_PLAN.md",
    "SANDBOX_RESOURCE_AND_TIMEOUT_PLAN.md",
    "OUTPUT_REPORT_AND_CANDIDATE_EFFECT_MODEL.md",
    "FAILURE_ROLLBACK_AND_AUDIT_MODEL.md",
    "SECURITY_AND_ABUSE_REVIEW.md",
    "IMPLEMENTATION_PHASES.md",
    "ACCEPTANCE_CRITERIA.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "deep_extraction_runtime_planning_report.json",
]

READINESS_VALUES = {
    "ready_for_local_dry_run_runtime_after_operator_approval",
    "ready_for_sandboxed_fixture_runtime_after_operator_approval",
    "ready_for_planning_only",
    "blocked_deep_extraction_contract_missing",
    "blocked_extraction_examples_missing",
    "blocked_sandbox_policy_missing",
    "blocked_resource_limit_policy_missing",
    "blocked_privacy_path_secret_policy_missing",
    "blocked_executable_payload_policy_missing",
    "blocked_OCR_transcription_boundary_missing",
    "blocked_pack_import_boundary_incomplete",
    "blocked_source_cache_evidence_boundary_incomplete",
    "blocked_candidate_index_boundary_incomplete",
    "blocked_public_search_page_boundary_incomplete",
    "blocked_other",
}


class DeepExtractionRuntimePlanOperationsTest(unittest.TestCase):
    def test_audit_pack_exists(self) -> None:
        self.assertTrue(AUDIT_ROOT.exists())

    def test_required_files_exist(self) -> None:
        missing = [name for name in REQUIRED_FILES if not (AUDIT_ROOT / name).exists()]
        self.assertEqual(missing, [])

    def test_report_json_parses_and_readiness_valid(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertIn(payload["readiness_decision"], READINESS_VALUES)
        self.assertTrue(payload["planning_only"])
        self.assertFalse(payload["runtime_extraction_implemented"])

    def test_inventory_json_parses(self) -> None:
        payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "planning_only")
        self.assertFalse(payload["runtime_extraction_implemented"])
        self.assertFalse(payload["arbitrary_local_path_enabled"])

    def test_gate_reviews_exist(self) -> None:
        for name in [
            "SANDBOX_AND_RESOURCE_LIMIT_GATE_REVIEW.md",
            "PRIVACY_PATH_SECRET_GATE_REVIEW.md",
            "EXECUTABLE_PAYLOAD_AND_CONTENT_SAFETY_GATE_REVIEW.md",
            "OCR_TRANSCRIPTION_AND_TEXT_BOUNDARY_REVIEW.md",
            "PUBLIC_SEARCH_AND_PAGE_BOUNDARY_REVIEW.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ]:
            self.assertTrue((AUDIT_ROOT / name).exists(), name)

    def test_command_matrix_includes_validator(self) -> None:
        payload = json.loads(COMMAND_MATRIX.read_text(encoding="utf-8"))
        commands = {command for lane in payload["lanes"] for command in lane["commands"]}
        self.assertIn("deep_extraction_runtime_plan_validator", commands)
        self.assertIn("deep_extraction_runtime_plan_validator_json", commands)

    def test_docs_exist(self) -> None:
        self.assertTrue(DOC.exists())
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("blocked_resource_limit_policy_missing", text)
        self.assertIn("Runtime extraction", text)


if __name__ == "__main__":
    unittest.main()

