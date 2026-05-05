import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "manual-observation-batch-0-follow-up-plan-v0"
REPORT = AUDIT / "manual_observation_batch_0_follow_up_report.json"
INVENTORY = ROOT / "control" / "inventory" / "external_baselines" / "manual_observation_batch_0_follow_up.json"
DOC = ROOT / "docs" / "operations" / "MANUAL_OBSERVATION_BATCH_0_FOLLOW_UP.md"

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


class ManualObservationBatch0FollowUpOperationTests(unittest.TestCase):
    def test_audit_pack_inventory_and_docs_exist(self):
        self.assertTrue(AUDIT.exists())
        for name in REQUIRED_FILES:
            self.assertTrue((AUDIT / name).is_file(), name)
        self.assertTrue(INVENTORY.is_file())
        self.assertTrue(DOC.is_file())

    def test_report_and_inventory_parse(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "manual_observation_batch_0_follow_up_plan_v0")
        self.assertEqual(inventory["inventory_id"], "manual_observation_batch_0_follow_up_v0")
        self.assertEqual(report["batch_id"], "batch_0")
        self.assertEqual(report["comparison_readiness_status"], "comparison_not_eligible")

    def test_required_operator_guidance_exists(self):
        for name in (
            "HUMAN_WORK_INSTRUCTIONS.md",
            "OBSERVATION_WORKSHEET.md",
            "OBSERVATION_RECORD_TEMPLATE.md",
            "CODEX_BOUNDARY.md",
            "COMPARISON_READINESS_DECISION.md",
        ):
            text = (AUDIT / name).read_text(encoding="utf-8").lower()
            self.assertTrue(text.strip(), name)
        self.assertIn("codex must not", (AUDIT / "CODEX_BOUNDARY.md").read_text(encoding="utf-8").lower())

    def test_hard_booleans_and_counts(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["follow_up_plan_only"])
        self.assertEqual(report["observed_count"], 0)
        self.assertEqual(report["valid_count"], 0)
        self.assertEqual(report["pending_count"], 39)
        self.assertEqual(report["invalid_count"], 0)
        for key in (
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
        ):
            self.assertFalse(report[key], key)

    def test_command_matrix_and_docs_reference_validator(self):
        matrix_text = (ROOT / "control" / "inventory" / "tests" / "command_matrix.json").read_text(encoding="utf-8")
        registry_text = (ROOT / "control" / "inventory" / "tests" / "test_registry.json").read_text(encoding="utf-8")
        scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        for text in (matrix_text, registry_text, scripts_readme):
            self.assertIn("validate_manual_observation_batch_0_follow_up.py", text)
            self.assertIn("report_manual_observation_batch_0_status.py --json", text)
        doc_text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "human-operated",
            "codex must not browse",
            "comparison_not_eligible",
        ):
            self.assertIn(phrase, doc_text)


if __name__ == "__main__":
    unittest.main()

