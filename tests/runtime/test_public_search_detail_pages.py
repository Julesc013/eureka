from __future__ import annotations

import unittest

from runtime.public_search import (
    build_public_candidate_page_view_model,
    build_public_evidence_page_view_model,
    build_public_need_page_view_model,
    build_public_object_page_view_model,
    build_public_search_ux_mvp_bundle,
    build_public_source_page_view_model,
    render_public_page_html,
)


class PublicSearchDetailPageTests(unittest.TestCase):
    def test_detail_pages_render_primary_card(self) -> None:
        bundle = build_public_search_ux_mvp_bundle()
        cards = bundle["result_cards"]
        ids = {
            card["status"]: card["href"].rstrip("/").split("/")[-1]
            for card in cards
            if card["status"] in {"verified", "candidate", "known_need", "reviewed_source_lead", "absence"}
        }

        pages = [
            build_public_object_page_view_model(ids["verified"]),
            build_public_candidate_page_view_model(ids["candidate"]),
            build_public_need_page_view_model(ids["known_need"]),
            build_public_source_page_view_model(ids["reviewed_source_lead"]),
            build_public_evidence_page_view_model(ids["absence"]),
        ]

        for page in pages:
            html = render_public_page_html(page)
            self.assertIn("result-card", html)
            self.assertTrue(page["read_only"])
            self.assertFalse(page["public_mutation_enabled"])


if __name__ == "__main__":
    unittest.main()
