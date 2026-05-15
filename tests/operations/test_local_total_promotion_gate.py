from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOLUTION = ROOT / "control/inventory/local_total_solution_result.json"
PROMOTION = ROOT / "control/inventory/local_total_promotion_plan.json"
NEXT_TASK = ROOT / "control/inventory/local_total_next_task_decision.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class LocalTotalPromotionGateTests(unittest.TestCase):
    def test_promotion_forbids_force_push_and_history_rewrite(self):
        payload = load_json(PROMOTION)
        self.assertEqual("local_total_promotion_plan.v0", payload["schema_version"])
        self.assertFalse(payload["force_push_performed"])
        self.assertFalse(payload["history_rewrite_performed"])
        self.assertFalse(payload["deployment_performed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])

    def test_promotion_requires_all_green_gates(self):
        promotion = load_json(PROMOTION)
        solution = load_json(SOLUTION)
        required_flags = [
            "runtime_leakage_gate_pass",
            "full_unittest_discovery_pass",
            "generated_artifact_cleanliness_pass",
            "architecture_boundaries_pass",
            "local_service_smoke_pass",
            "local_workbench_smoke_pass",
            "auto_test_auto_search_pass",
            "clean_machine_bootstrap_pass",
        ]
        if promotion.get("promotion_allowed_after_full_sweep"):
            self.assertEqual(0, solution["hard_blockers_remaining"])
            for flag in required_flags:
                self.assertTrue(solution[flag], flag)
        if not solution.get("full_unittest_discovery_pass"):
            self.assertFalse(promotion["main_promoted"])

    def test_promotion_requires_fast_forward_branch_state(self):
        promotion = load_json(PROMOTION)
        if promotion.get("main_promoted"):
            self.assertTrue(promotion["origin_main_equals_origin_dev"])
            self.assertTrue(promotion["dev_pushed"])
            self.assertTrue(promotion["branch_mutation_performed"])

    def test_next_task_decision_is_explicit(self):
        decision = load_json(NEXT_TASK)
        self.assertEqual("local_total_next_task_decision.v0", decision["schema_version"])
        self.assertIn(
            decision["recommended_next_task"],
            {
                "HUNT-00 \u2014 Search Hunt track planning over Local Appliance",
                "LOCAL-REMEDIATION \u2014 Complete remaining Local Appliance blockers",
                "LOCAL-TO-MAIN-PROMOTION-REVIEW \u2014 Promote if green but not promoted",
            },
        )
        self.assertFalse(decision["deployment_performed"])
        self.assertFalse(decision["production_readiness_claimed"])
        self.assertFalse(decision["public_launch_readiness_claimed"])


if __name__ == "__main__":
    unittest.main()
