import copy
import unittest
from pathlib import Path

from scripts.audit_hunt_main_promotion import build_promotion_records
from scripts.validate_hunt_main_promotion import validate_result


ROOT = Path(__file__).resolve().parents[2]


class HuntMainPromotionTests(unittest.TestCase):
    def test_current_records_recommend_syn_after_pass(self):
        records = build_promotion_records(ROOT)
        result = records["result"]
        self.assertEqual("pass", result["status"])
        self.assertTrue(result["promotion_gates_passed"])
        self.assertIn("SYN-00", result["recommended_next_task"])

    def test_promotion_gate_fails_with_hard_blockers(self):
        records = build_promotion_records(ROOT)
        payload = copy.deepcopy(records["result"])
        payload["hard_blockers_remaining"] = 1
        errors = []
        validate_result(payload, errors)
        self.assertIn("result hard blockers must be zero", errors)

    def test_promotion_gate_fails_if_forbidden_side_effects_occurred(self):
        for field in (
            "source_probe_executed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
        ):
            records = build_promotion_records(ROOT)
            payload = copy.deepcopy(records["result"])
            payload[field] = True
            errors = []
            validate_result(payload, errors)
            self.assertIn(f"result {field} must be false", errors)

    def test_next_task_decision_points_to_syn_after_pass(self):
        records = build_promotion_records(ROOT)
        decision = records["next_decision"]
        self.assertIn("SYN-00", decision["recommended_next_task"])
        self.assertTrue(decision["syn_can_start"])
        self.assertTrue(decision["f0_can_resume"])
        self.assertFalse(decision["f0_recommended_now"])


if __name__ == "__main__":
    unittest.main()
