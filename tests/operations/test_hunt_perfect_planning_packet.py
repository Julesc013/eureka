import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "control/inventory/hunt_perfect_planning_packet.json"
PACKET_DOC = ROOT / "docs/operations/HUNT_PERFECT_CLOSEOUT_PACKET.md"
SYN_DOC = ROOT / "docs/operations/POST_HUNT_SYN_ENTRY_PLAN.md"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class HuntPerfectPlanningPacketTests(unittest.TestCase):
    def test_packet_includes_capabilities_disabled_state_and_non_claims(self):
        payload = load_json(PACKET)
        self.assertEqual("hunt_perfect_planning_packet.v0", payload["schema_version"])
        self.assertIn("hunt_01_search_hunt_session_runtime", payload["implemented_hunt_capabilities"])
        self.assertIn("hunt_11_ai_escalation_gate_disabled_by_default", payload["implemented_hunt_capabilities"])
        self.assertIn("source probes", payload["what_remains_disabled"])
        self.assertIn("extraction", payload["what_remains_disabled"])
        self.assertIn("AI/model/provider execution", payload["what_remains_disabled"])
        self.assertIn("not production readiness", payload["explicit_non_claims"])
        self.assertIn("not public launch readiness", payload["explicit_non_claims"])

    def test_packet_records_syn_f0_and_promotion_plan(self):
        payload = load_json(PACKET)
        self.assertIn("SYN", payload["why_syn_is_next"])
        self.assertIn("F0", payload["why_f0_is_deferred_but_resumable"])
        self.assertEqual("HUNT-TO-MAIN-PROMOTION-REVIEW", payload["recommended_next_task"])
        self.assertIn("SYN-00", payload["alternative_next_task"])

    def test_docs_state_non_claims_and_boundaries(self):
        packet_doc = PACKET_DOC.read_text(encoding="utf-8")
        syn_doc = SYN_DOC.read_text(encoding="utf-8")
        self.assertIn("not a production readiness claim", packet_doc)
        self.assertIn("not a public launch readiness claim", packet_doc)
        self.assertIn("source probes", packet_doc)
        self.assertIn("HUNT-TO-MAIN-PROMOTION-REVIEW", packet_doc)
        self.assertIn("SYN-00 may start", syn_doc)
        self.assertIn("must not create fake evidence", syn_doc)


if __name__ == "__main__":
    unittest.main()
