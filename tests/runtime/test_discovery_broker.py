from __future__ import annotations

import unittest

from runtime.search.discovery_broker import DiscoveryBroker, classify_query_intent


class DiscoveryBrokerTests(unittest.TestCase):
    def test_classifies_common_query_intents(self) -> None:
        self.assertEqual("current_web", classify_query_intent("latest matrix release notes"))
        self.assertEqual("historical_artifact", classify_query_intent("manual for Sound Blaster CT1740"))
        self.assertEqual("code_or_package", classify_query_intent("github release archive utility"))
        self.assertEqual("site_specific", classify_query_intent("site:archive.org windows 95 manual"))

    def test_archive_plan_prefers_local_then_ia_then_broad_web(self) -> None:
        plan = DiscoveryBroker(env={}).plan("manual for Sound Blaster CT1740")

        steps = plan.to_dict()["steps"]
        self.assertEqual("historical_artifact", plan.intent)
        self.assertEqual("local_preview_reviewed_index", steps[0]["source"])
        self.assertEqual("internet_archive_metadata", steps[1]["provider_id"])
        self.assertEqual("brave", steps[2]["provider_id"])
        self.assertEqual("mojeek", steps[3]["provider_id"])
        self.assertEqual("eligible", steps[1]["run_policy"])
        self.assertEqual("needs_configuration", steps[2]["run_policy"])
        self.assertEqual("needs_configuration", steps[3]["run_policy"])
        self.assertFalse(plan.public_live_fanout)
        self.assertFalse(plan.reviewed_truth_mutation)
        self.assertFalse(plan.network_calls_performed)
        self.assertEqual(("internet_archive_metadata",), plan.provider_ids())

    def test_current_web_plan_uses_configured_broad_web_providers(self) -> None:
        plan = DiscoveryBroker(env={"MOJEEK_SEARCH_API_KEY": "real-looking-mojeek-token"}).plan("current web search topic")

        by_provider = {step.provider_id: step for step in plan.steps}
        self.assertEqual("current_web", plan.intent)
        self.assertEqual("needs_configuration", by_provider["brave"].run_policy)
        self.assertEqual("eligible", by_provider["mojeek"].run_policy)
        self.assertIn("mojeek", plan.provider_ids())
        self.assertNotIn("brave", plan.provider_ids())

    def test_searxng_is_declared_but_disabled_until_self_hosted(self) -> None:
        plan = DiscoveryBroker(env={}).plan("current web search topic")

        searxng = [step for step in plan.steps if step.provider_id == "searxng"][0]
        self.assertEqual("disabled_until_self_hosted_configured", searxng.run_policy)
        self.assertFalse(searxng.configured)
        self.assertNotIn("searxng", plan.provider_ids())


if __name__ == "__main__":
    unittest.main()
