from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "control/audits/final-state-promotion-plan-01-v0/final_state_report.json"
NOT_DONE = ROOT / "control/inventory/final_not_done_matrix.json"
VALIDATION = ROOT / "control/inventory/final_validation_matrix.json"
PROMOTION = ROOT / "control/inventory/final_main_promotion_result.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class FinalStatePromotionPlanTests(unittest.TestCase):
    def test_final_report_rejects_public_or_production_claims(self) -> None:
        payload = load_json(REPORT)
        self.assertEqual("final_state_report.v0", payload["schema_version"])
        self.assertFalse(payload["deployment_performed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])
        self.assertFalse(payload["force_push_performed"])
        self.assertFalse(payload["history_rewrite_performed"])

    def test_final_report_requires_core_state_packets(self) -> None:
        payload = load_json(REPORT)
        self.assertTrue(payload["r0_state_reviewed"])
        self.assertTrue(payload["local_state_reviewed"])
        self.assertTrue(payload["not_done_matrix_created"])
        self.assertTrue(NOT_DONE.is_file())
        self.assertTrue(VALIDATION.is_file())

    def test_promotion_status_is_explicit_and_safe(self) -> None:
        promotion = load_json(PROMOTION)
        self.assertEqual("final_main_promotion_result.v0", promotion["schema_version"])
        self.assertIn("dev_pushed", promotion)
        self.assertIn("main_promoted", promotion)
        self.assertFalse(promotion["force_push_performed"])
        self.assertFalse(promotion["history_rewrite_performed"])

    def test_hard_blockers_control_future_track_start(self) -> None:
        payload = load_json(REPORT)
        if payload["hard_blockers_remaining"] > 0:
            self.assertNotIn("HUNT-00", payload["recommended_next_task"])
            self.assertNotIn("SYN-00", payload["recommended_next_task"])
            self.assertNotIn("F0-00", payload["recommended_next_task"])


if __name__ == "__main__":
    unittest.main()
