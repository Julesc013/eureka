from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LocalApplianceHandoffTests(unittest.TestCase):
    def test_hunt_syn_f0_handoffs_exist(self) -> None:
        hunt = json.loads((ROOT / "control/inventory/local_appliance_handoff_to_hunt.json").read_text())
        syn = json.loads((ROOT / "control/inventory/local_appliance_handoff_to_syn.json").read_text())
        f0 = json.loads((ROOT / "control/inventory/local_appliance_handoff_to_f0.json").read_text())
        self.assertEqual("local_appliance_handoff_to_hunt.v0", hunt["schema_version"])
        self.assertEqual("local_appliance_handoff_to_syn.v0", syn["schema_version"])
        self.assertEqual("local_appliance_handoff_to_f0.v0", f0["schema_version"])
        self.assertTrue(f0["f0_can_resume_only_through_local_appliance"])

    def test_next_decision_prefers_hunt_and_allows_syn_f0(self) -> None:
        decision = json.loads((ROOT / "control/inventory/local_14_next_task_decision.json").read_text())
        self.assertIn("HUNT-00", decision["recommended_next_task"])
        self.assertIn("SYN-00", decision["alternative_next_task"])
        self.assertTrue(decision["f0_can_resume"])
        self.assertFalse(decision["f0_recommended_now"])


if __name__ == "__main__":
    unittest.main()
