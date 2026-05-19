import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from scripts.validate_ia_pilot_closeout import (  # noqa: E402
    validate_capability_matrix,
    validate_next_task_decision,
    validate_reuse_matrix,
)


class IAPilotSynHandoffTests(unittest.TestCase):
    def test_next_task_decision_points_to_syn_and_promotion_review(self):
        decision = json.loads((ROOT / "control/inventory/ia_pilot_next_task_decision.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_next_task_decision(decision))
        self.assertIn("SYN-00", decision["recommended_next_task"])
        self.assertTrue(decision["ia_to_main_promotion_review_recommended"])

    def test_capability_matrix_records_syn_handoff(self):
        matrix = json.loads((ROOT / "control/inventory/ia_pilot_capability_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_capability_matrix(matrix))
        ids = {row["capability_id"] for row in matrix["rows"]}
        self.assertIn("syn_handoff_readiness", ids)

    def test_reuse_matrix_covers_future_source_packs(self):
        matrix = json.loads((ROOT / "control/inventory/ia_pilot_reuse_matrix.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_reuse_matrix(matrix))
        for row in matrix["rows"]:
            self.assertIn("future source packs", row["reusable_for"])


if __name__ == "__main__":
    unittest.main()
