from __future__ import annotations

import unittest

from runtime.public_search import build_public_search_home_page_view_model, render_public_page_html


class PublicSearchHomePageTests(unittest.TestCase):
    def test_home_page_is_search_first_no_js(self) -> None:
        page = build_public_search_home_page_view_model()
        html = render_public_page_html(page)

        self.assertEqual("home", page["page_kind"])
        self.assertTrue(page["search_first"])
        self.assertIn('method="get"', html)
        self.assertIn('<label for="q">', html)
        self.assertNotIn("<script", html.lower())
        self.assertFalse(page["deployment_performed"])


if __name__ == "__main__":
    unittest.main()
