from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs" / "operations" / "HUMAN_LIVE_SEARCH_ACCEPTANCE_REHEARSAL.md"
DECISION_TEMPLATE = ROOT / "control" / "inventory" / "product" / "human_live_search_acceptance_decision_template.json"


class HumanAcceptanceRehearsalTests(unittest.TestCase):
    def test_runbook_is_product_facing_and_not_internal_audit(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("Search with three unseen queries", text)
        self.assertIn("use Hunt deeper", text)
        self.assertIn("restart Eureka", text)
        self.assertNotIn("task packet", text.casefold())
        self.assertNotIn("AIDE", text)
        self.assertNotIn("architecture", text.casefold())

    def test_decision_template_is_blank_and_human_only(self) -> None:
        payload = json.loads(DECISION_TEMPLATE.read_text(encoding="utf-8"))

        self.assertEqual("eureka.human_live_search_acceptance_decision.v0", payload["schema_version"])
        self.assertEqual("blank_operator_required", payload["status"])
        self.assertEqual("", payload["decision"])
        self.assertEqual(["accepted", "accepted_with_changes", "rejected"], payload["allowed_decisions"])
        self.assertFalse(payload["ai_generated_decision"])
        self.assertFalse(payload["preconditions"]["operator_live_canary_passed"])
        self.assertIsNone(payload["would_use_for_real_unknowns"])
        self.assertEqual(3, len(payload["queries"]))


if __name__ == "__main__":
    unittest.main()
