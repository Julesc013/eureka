from __future__ import annotations

import unittest

from runtime.public_search import build_public_search_results_page_view_model, render_public_page_html


class PublicSearchResultsPageTests(unittest.TestCase):
    def test_results_page_returns_matching_cards(self) -> None:
        page = build_public_search_results_page_view_model("D-Theater New York")
        html = render_public_page_html(page)

        self.assertEqual("search", page["page_kind"])
        self.assertGreater(len(page["result_cards"]), 0)
        self.assertIn("D-Theater", html)
        self.assertIn("review required", html)
        self.assertFalse(page["public_mutation_enabled"])

    def test_no_results_routes_to_need_view_model(self) -> None:
        page = build_public_search_results_page_view_model("nonexistent artefact")
        html = render_public_page_html(page)

        self.assertEqual("no_results", page["page_kind"])
        self.assertEqual([], page["result_cards"])
        self.assertIn("No reviewed result yet", html)
        self.assertIn("future disabled", html)


if __name__ == "__main__":
    unittest.main()
