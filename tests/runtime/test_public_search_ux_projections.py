from __future__ import annotations

import unittest

from runtime.public_alpha import build_public_search_ux_model_bundle


class PublicSearchUxProjectionTests(unittest.TestCase):
    def test_projection_profiles_are_read_only(self) -> None:
        projections = build_public_search_ux_model_bundle()["projections"]

        self.assertEqual({"public_web", "operator_workbench", "api_json", "classic_html", "text"}, set(projections))
        for projection in projections.values():
            self.assertTrue(projection["read_only"])
            self.assertFalse(projection["public_mutation_enabled"])
            self.assertFalse(projection["public_live_source_fanout_enabled"])
        self.assertFalse(projections["api_json"]["html_scrape_required_for_agents"])


if __name__ == "__main__":
    unittest.main()
