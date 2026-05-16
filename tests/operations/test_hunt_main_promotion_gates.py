import copy
import unittest
from pathlib import Path

from scripts.audit_hunt_main_promotion import build_promotion_records
from scripts.validate_hunt_main_promotion import validate_branch_plan, validate_gates, validate_result


ROOT = Path(__file__).resolve().parents[2]


class HuntMainPromotionGateTests(unittest.TestCase):
    def test_all_current_blocking_gates_pass(self):
        records = build_promotion_records(ROOT)
        errors = []
        validate_gates(records["gate_matrix"], errors)
        self.assertEqual([], errors)

    def test_gate_matrix_fails_if_full_discovery_or_generated_cleanliness_fails(self):
        for gate_id in ("full_unittest_discovery_pass", "generated_artifact_cleanliness_pass"):
            records = build_promotion_records(ROOT)
            gate = next(row for row in records["gate_matrix"]["gates"] if row["gate_id"] == gate_id)
            gate["actual"] = False
            gate["status"] = "fail"
            errors = []
            validate_gates(records["gate_matrix"], errors)
            self.assertIn(f"promotion gate failed: {gate_id}", errors)

    def test_branch_plan_rejects_force_push_or_history_rewrite(self):
        for field in ("force_push_allowed", "history_rewrite_allowed", "rebase_allowed", "squash_allowed"):
            records = build_promotion_records(ROOT)
            plan = copy.deepcopy(records["branch_plan"])
            plan[field] = True
            errors = []
            validate_branch_plan(plan, errors)
            self.assertTrue(any(field in error for error in errors), field)

    def test_result_rejects_force_push_and_history_rewrite_performed(self):
        for field in ("force_push_performed", "history_rewrite_performed"):
            records = build_promotion_records(ROOT)
            payload = copy.deepcopy(records["result"])
            payload[field] = True
            errors = []
            validate_result(payload, errors)
            self.assertIn(f"result {field} must be false", errors)


if __name__ == "__main__":
    unittest.main()
