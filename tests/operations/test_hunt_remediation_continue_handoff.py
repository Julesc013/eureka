import json
import unittest
from pathlib import Path


class HuntRemediationContinueHandoffTests(unittest.TestCase):
    def test_syn_handoff_ready_after_continuation(self):
        payload = json.loads(Path("control/inventory/hunt_remediation_continue_next_task_decision.json").read_text(encoding="utf-8"))
        self.assertIn("SYN-00", payload["recommended_next_task"])
        self.assertTrue(payload["syn_can_start"])

    def test_f0_resumable_but_not_recommended(self):
        payload = json.loads(Path("control/inventory/hunt_remediation_continue_next_task_decision.json").read_text(encoding="utf-8"))
        self.assertTrue(payload["f0_can_resume"])
        self.assertFalse(payload["f0_recommended_now"])

    def test_closeout_remains_green(self):
        payload = json.loads(Path("control/inventory/search_hunt_closeout_result.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["hard_blockers_remaining"], 0)
        self.assertEqual(payload["warnings_remaining"], 0)

    def test_public_and_production_claims_rejected(self):
        for rel in (
            "control/inventory/hunt_remediation_continue_result.json",
            "control/audits/hunt-remediation-continue-v0/hunt_remediation_continue_report.json",
            "control/inventory/search_hunt_closeout_result.json",
        ):
            payload = json.loads(Path(rel).read_text(encoding="utf-8"))
            self.assertFalse(payload["production_readiness_claimed"], rel)
            self.assertFalse(payload["public_launch_readiness_claimed"], rel)


if __name__ == "__main__":
    unittest.main()
