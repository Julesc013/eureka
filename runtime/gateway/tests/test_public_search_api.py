from __future__ import annotations

from urllib.parse import parse_qs
import unittest

from runtime.gateway.public_api import build_demo_public_search_public_api


class PublicSearchPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_public_search_public_api()

    def test_search_returns_governed_result_cards(self) -> None:
        response = self.public_api.search(parse_qs("q=windows+7+apps&limit=3"))

        self.assertEqual(response.status_code, 200)
        payload = response.body
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "local_index_only")
        self.assertGreater(len(payload["results"]), 0)
        card = payload["results"][0]
        self.assertEqual(card["contract_id"], "eureka_public_search_result_card_v0")
        self.assertIn(card["result_lane"], {"inside_bundles", "best_direct_answer", "other"})
        self.assertIn("source_id", card["source"])
        self.assertIn("score", card["user_cost"])
        self.assertIn("summaries", card["evidence"])
        self.assertIn("status", card["compatibility"])
        blocked_actions = {entry["action_id"] for entry in card["actions"]["blocked"]}
        self.assertGreaterEqual(blocked_actions, {"download", "install_handoff", "execute", "upload"})
        self.assertIn("no_live_probe", card["limitations"])
        self.assertIn("no_rights_clearance", card["limitations"])

    def test_no_result_returns_absence_success_not_internal_error(self) -> None:
        response = self.public_api.search({"q": ["zzzz no such eureka fixture"]})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["results"], [])
        self.assertEqual(response.body["absence_summary"]["status"], "bounded_absence")
        self.assertEqual(response.body["gaps"][0]["gap_type"], "bounded_absence")

    def test_query_plan_status_and_sources_are_public_safe(self) -> None:
        plan = self.public_api.query_plan(parse_qs("q=windows+7+apps"))
        status = self.public_api.status()
        sources = self.public_api.list_sources({})
        source = self.public_api.get_source("local-bundle-fixtures")

        self.assertEqual(plan.status_code, 200)
        self.assertEqual(plan.body["mode"], "local_index_only")
        self.assertTrue(plan.body["no_live_probe"])
        self.assertEqual(status.body["public_search"]["implementation_scope"], "local_prototype_backend")
        self.assertFalse(status.body["public_search"]["live_probes_enabled"])
        self.assertFalse(status.body["public_search"]["downloads_enabled"])
        self.assertEqual(sources.status_code, 200)
        self.assertGreater(sources.body["source_count"], 0)
        self.assertEqual(source.status_code, 200)
        self.assertEqual(source.body["selected_source_id"], "local-bundle-fixtures")
        serialized = str(source.body)
        self.assertNotIn("D:/", serialized)
        self.assertNotIn("C:/", serialized)


if __name__ == "__main__":
    unittest.main()
