from __future__ import annotations

import unittest

from runtime.public_search import build_public_search_ux_mvp_bundle


class PublicSearchUxMvpTests(unittest.TestCase):
    def test_bundle_builds_read_only_no_js_mvp(self) -> None:
        bundle = build_public_search_ux_mvp_bundle()

        self.assertEqual("pass", bundle["status"])
        self.assertTrue(bundle["home_page_added"])
        self.assertTrue(bundle["search_results_page_added"])
        self.assertTrue(bundle["public_projection_read_only"])
        self.assertFalse(bundle["deployment_performed"])
        self.assertFalse(bundle["public_launch_performed"])
        self.assertFalse(bundle["site_dist_written"])

    def test_required_result_states_are_visible(self) -> None:
        statuses = {card["status"] for card in build_public_search_ux_mvp_bundle()["result_cards"]}

        self.assertTrue(
            {
                "verified",
                "reviewed_metadata_record",
                "reviewed_source_lead",
                "candidate",
                "near_miss",
                "known_need",
                "absence",
            }.issubset(statuses)
        )


if __name__ == "__main__":
    unittest.main()
