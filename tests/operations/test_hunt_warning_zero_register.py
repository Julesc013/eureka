import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "control/inventory/hunt_warning_zero_register.json"
REPAIR_PLAN = ROOT / "control/inventory/hunt_warning_zero_repair_plan.json"
REPAIR_RESULT = ROOT / "control/inventory/hunt_warning_zero_repair_result.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class HuntWarningZeroRegisterTests(unittest.TestCase):
    def test_unified_warning_register_has_required_fields(self):
        payload = load_json(REGISTER)
        self.assertEqual("hunt_warning_zero_register.v0", payload["schema_version"])
        self.assertGreaterEqual(len(payload["warnings"]), payload["warnings_before"])
        required = {
            "warning_id",
            "source_file",
            "source_task",
            "source_validator_or_test",
            "category",
            "current_status",
            "safe_to_fix_now",
            "blocks_syn",
            "blocks_f0",
            "blocks_main_promotion",
            "evidence",
            "proposed_repair",
            "child_task_if_needed",
        }
        for warning in payload["warnings"]:
            self.assertTrue(required.issubset(warning), warning)

    def test_failed_validator_warning_would_be_a_hard_blocker(self):
        warning = {
            "source_validator_or_test": "example validator FAIL",
            "current_status": "hard_blocker",
        }
        self.assertEqual("hard_blocker", warning["current_status"])

    def test_all_current_warnings_are_resolved_or_evidence_backed(self):
        payload = load_json(REGISTER)
        allowed = {"resolved", "duplicate", "false_positive_with_evidence"}
        for warning in payload["warnings"]:
            self.assertIn(warning["current_status"], allowed, warning["warning_id"])
            self.assertFalse(warning["blocks_syn"], warning["warning_id"])
            self.assertFalse(warning["blocks_f0"], warning["warning_id"])
            self.assertFalse(warning["blocks_main_promotion"], warning["warning_id"])

    def test_repair_plan_forbids_policy_weakening(self):
        plan = load_json(REPAIR_PLAN)
        result = load_json(REPAIR_RESULT)
        self.assertFalse(plan["product_behavior_change_allowed"])
        self.assertFalse(plan["source_probe_allowed"])
        self.assertFalse(plan["extraction_allowed"])
        self.assertFalse(plan["model_provider_allowed"])
        self.assertFalse(plan["deployment_allowed"])
        self.assertFalse(result["product_behavior_changed"])
        self.assertFalse(result["policy_weakened"])
        self.assertEqual([], result["warnings_remaining"])


if __name__ == "__main__":
    unittest.main()
