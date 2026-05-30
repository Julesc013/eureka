from __future__ import annotations

import unittest

from runtime.search.query_plan import plan_query_to_source_actions


class QueryPlanExplanationTests(unittest.TestCase):
    def test_explanation_packet_names_intent_domain_and_rewrite(self) -> None:
        plan = plan_query_to_source_actions("New York 1993 D-Theater HD demo tape original source")
        explanation = plan["explanation"]
        factors = {item["factor"]: item["value"] for item in explanation["factors"]}

        self.assertEqual(plan["intent"], factors["intent"])
        self.assertEqual(plan["domain_pack"], factors["domain_pack"])
        self.assertEqual(
            plan["source_query_rewrites"]["archive_org_metadata"],
            factors["archive_org_metadata_query"],
        )
        self.assertIn("automatic_promotion", explanation["blocked"])

    def test_explanation_does_not_claim_truth(self) -> None:
        plan = plan_query_to_source_actions("StyleWriter 2500 Mac OS 8 driver")
        uncertainty = " ".join(plan["explanation"]["uncertainty"]).casefold()

        self.assertIn("candidates only", uncertainty)
        self.assertIn("does not establish", uncertainty)


if __name__ == "__main__":
    unittest.main()
