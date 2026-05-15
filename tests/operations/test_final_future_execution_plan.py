from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "control/inventory/final_future_execution_plan.json"
PROMOTION = ROOT / "control/inventory/final_main_promotion_result.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class FinalFutureExecutionPlanTests(unittest.TestCase):
    def test_future_plan_starts_with_hunt_when_local_is_green(self) -> None:
        payload = load_json(PLAN)
        self.assertEqual("final_future_execution_plan.v0", payload["schema_version"])
        self.assertEqual(
            "HUNT-00 \u2014 Search Hunt track planning over Local Appliance",
            payload["primary_next_task"],
        )
        self.assertIn("SYN-00 \u2014 Synthetic Query Foundry planning over Local Appliance", payload["sequence"])
        self.assertIn("F0-00 \u2014 Refresh F0 after Local Appliance/HUNT/SYN", payload["sequence"])

    def test_plan_keeps_boundary_constraints(self) -> None:
        payload = load_json(PLAN)
        constraints = " ".join(payload["constraints"])
        self.assertIn("No deployment", constraints)
        self.assertIn("No source probes", constraints)

    def test_promotion_result_rejects_force_push_and_history_rewrite(self) -> None:
        payload = load_json(PROMOTION)
        self.assertFalse(payload["force_push_performed"])
        self.assertFalse(payload["history_rewrite_performed"])


if __name__ == "__main__":
    unittest.main()
