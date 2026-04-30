from __future__ import annotations

from urllib.parse import parse_qs
import unittest

from runtime.gateway.public_api import build_demo_public_search_public_api


class PublicSearchSourceExpansionV2TestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_public_search_public_api()

    def test_public_search_returns_safe_recorded_fixture_cards(self) -> None:
        response = self.public_api.search(
            parse_qs("q=archived+Firefox+XP+release+notes&limit=5")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["mode"], "local_index_only")
        self.assertTrue(response.body["results"])
        card = response.body["results"][0]
        self.assertEqual(card["source"]["source_id"], "wayback-memento-recorded-fixtures")
        self.assertIn("fixture_backed", card["limitations"])
        self.assertIn("no_download", card["limitations"])
        self.assertIn("no_install", card["limitations"])
        blocked_actions = {item["action_id"] for item in card["actions"]["blocked"]}
        self.assertGreaterEqual(blocked_actions, {"download", "install_handoff", "execute", "upload"})

    def test_public_source_endpoint_exposes_new_source_without_private_paths(self) -> None:
        response = self.public_api.get_source("software-heritage-recorded-fixtures")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["selected_source_id"], "software-heritage-recorded-fixtures")
        source = response.body["sources"][0]
        self.assertEqual(source["source_status"], "active_recorded_fixture")
        self.assertIn("recorded_fixture_backed", source["capabilities_summary"])
        self.assertIn("no_live_probe", source["limitations"])
        serialized = str(response.body)
        self.assertNotIn("C:/", serialized)
        self.assertNotIn("D:/", serialized)


if __name__ == "__main__":
    unittest.main()
