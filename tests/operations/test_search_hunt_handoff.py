import unittest
from pathlib import Path

from scripts.prepare_hunt_to_syn_f0_handoff import build_handoff


class SearchHuntHandoffTests(unittest.TestCase):
    def test_syn_f0_and_ghk_handoffs_exist(self):
        result = build_handoff(Path.cwd())
        self.assertIn("SYN-00", result["recommended_next_task"])
        self.assertTrue(result["syn_handoff"]["syn_should_generate_query_pressure"])
        self.assertTrue(result["f0_handoff"]["f0_can_resume"])
        self.assertFalse(result["f0_handoff"]["f0_recommended_now"])
        self.assertTrue(result["g_h_k_handoff"]["k_consumes_ai_escalation_gate_and_agent_research_task_contract"])

    def test_incomplete_hunt_recommends_remediation(self):
        result = build_handoff(Path.cwd(), "missing-capabilities.json", "missing-closeout.json")
        self.assertIn("HUNT-REMEDIATION", result["recommended_next_task"])


if __name__ == "__main__":
    unittest.main()
