import json
import unittest
from pathlib import Path


class HuntRemediationHandoffTests(unittest.TestCase):
    def test_syn_handoff_ready(self):
        payload = json.loads(Path("control/inventory/search_hunt_handoff_to_syn.json").read_text(encoding="utf-8"))
        self.assertIn("SYN-00", payload["next_task"])
        self.assertTrue(payload["syn_should_generate_query_pressure"])
        self.assertTrue(payload["syn_must_use_hunt_absence_exhaustion_structures"])

    def test_f0_can_resume_but_is_not_recommended_by_default(self):
        payload = json.loads(Path("control/inventory/hunt_remediation_next_task_decision.json").read_text(encoding="utf-8"))
        self.assertTrue(payload["f0_can_resume"])
        self.assertFalse(payload["f0_recommended_now"])
        self.assertIn("SYN-00", payload["recommended_next_task"])

    def test_public_and_production_claims_rejected(self):
        for rel in (
            "control/inventory/hunt_remediation_result.json",
            "control/audits/hunt-remediation-v0/hunt_remediation_report.json",
            "control/inventory/search_hunt_closeout_result.json",
        ):
            payload = json.loads(Path(rel).read_text(encoding="utf-8"))
            self.assertFalse(payload["production_readiness_claimed"], rel)
            self.assertFalse(payload["public_launch_readiness_claimed"], rel)


if __name__ == "__main__":
    unittest.main()
