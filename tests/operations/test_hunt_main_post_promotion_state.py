import copy
import unittest
from pathlib import Path

from scripts.audit_hunt_main_promotion import build_promotion_records
from scripts.validate_hunt_main_promotion import validate_next_decision, validate_post_state, validate_result


ROOT = Path(__file__).resolve().parents[2]


class HuntMainPostPromotionStateTests(unittest.TestCase):
    def test_post_promotion_state_records_branch_equality_expectation(self):
        records = build_promotion_records(ROOT)
        post_state = records["post_state"]
        self.assertTrue(post_state["expected_origin_main_equals_origin_dev"])
        self.assertTrue(post_state["expected_fast_forward_only"])
        self.assertEqual("dev", post_state["expected_current_branch_after"])

    def test_promotion_result_records_branch_equality(self):
        records = build_promotion_records(ROOT)
        result = records["result"]
        self.assertTrue(result["origin_main_equals_origin_dev"])
        self.assertTrue(result["fast_forward_only"])

    def test_post_state_validator_rejects_missing_equality(self):
        records = build_promotion_records(ROOT)
        payload = copy.deepcopy(records["post_state"])
        payload["expected_origin_main_equals_origin_dev"] = False
        errors = []
        validate_post_state(payload, errors)
        self.assertIn("post promotion state must expect origin/main == origin/dev", errors)

    def test_next_decision_requires_syn_and_main_promoted(self):
        records = build_promotion_records(ROOT)
        decision = copy.deepcopy(records["next_decision"])
        errors = []
        validate_next_decision(decision, errors)
        self.assertEqual([], errors)
        decision["main_promoted"] = False
        validate_next_decision(decision, errors)
        self.assertIn("next decision must record main_promoted true", errors)

    def test_result_rejects_public_claims(self):
        records = build_promotion_records(ROOT)
        for field in ("production_readiness_claimed", "public_launch_readiness_claimed"):
            payload = copy.deepcopy(records["result"])
            payload[field] = True
            errors = []
            validate_result(payload, errors)
            self.assertIn(f"result {field} must be false", errors)


if __name__ == "__main__":
    unittest.main()
