from __future__ import annotations

import unittest

from surfaces.web.workbench import render_search_results_html


class SearchResultsRenderingTestCase(unittest.TestCase):
    def test_non_empty_results_render_query_result_list_and_links(self) -> None:
        html = render_search_results_html(
            {
                "query": "synthetic",
                "result_count": 2,
                "results": [
                    {
                        "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                        "object": {
                            "id": "obj.synthetic-demo-app",
                            "kind": "software",
                            "label": "Synthetic Demo App",
                        },
                    },
                    {
                        "target_ref": "fixture:software/synthetic-demo-suite@2.0.0",
                        "object": {
                            "id": "obj.synthetic-demo-suite",
                            "kind": "software",
                            "label": "Synthetic Demo Suite",
                        },
                    },
                ],
            }
        )

        self.assertIn("synthetic", html)
        self.assertIn("Result count", html)
        self.assertIn("Synthetic Demo App", html)
        self.assertIn("Synthetic Demo Suite", html)
        self.assertIn("/?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)

    def test_empty_results_render_query_and_absence_report(self) -> None:
        html = render_search_results_html(
            {
                "query": "missing",
                "result_count": 0,
                "results": [],
                "absence": {
                    "code": "search_no_matches",
                    "message": "No governed synthetic records matched query 'missing'.",
                },
            }
        )

        self.assertIn("missing", html)
        self.assertIn("No Results", html)
        self.assertIn("search_no_matches", html)
        self.assertIn("No governed synthetic records matched query", html)
