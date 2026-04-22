from __future__ import annotations

import unittest

from surfaces.web.workbench import render_search_results_html


class SearchResultsRenderingTestCase(unittest.TestCase):
    def test_non_empty_results_render_query_result_list_and_links(self) -> None:
        html = render_search_results_html(
            {
                "query": "archive",
                "result_count": 2,
                "results": [
                    {
                        "target_ref": "fixture:software/archive-viewer@0.9.0",
                        "resolved_resource_id": "resolved:sha256:b38c82f9ca3af117ce8b3984ad311fb4102261c3c1573cd18a8a7db0c760fc81",
                        "object": {
                            "id": "obj.archive-viewer",
                            "kind": "software",
                            "label": "Archive Viewer",
                        },
                        "source": {
                            "family": "synthetic_fixture",
                            "label": "Synthetic Fixture",
                        },
                    },
                    {
                        "target_ref": "github-release:archivebox/archivebox@v0.8.5",
                        "resolved_resource_id": "resolved:sha256:4e3bbaf3175192349b3f9d9c978d8a6a25cc306ab8d0f9fe3acab9eeca3b107f",
                        "object": {
                            "id": "obj.github-release.archivebox.archivebox",
                            "kind": "software",
                            "label": "ArchiveBox v0.8.5",
                        },
                        "source": {
                            "family": "github_releases",
                            "label": "GitHub Releases",
                        },
                    },
                ],
            }
        )

        self.assertIn("archive", html)
        self.assertIn("Result count", html)
        self.assertIn("Archive Viewer", html)
        self.assertIn("ArchiveBox v0.8.5", html)
        self.assertIn("/?target_ref=github-release%3Aarchivebox%2Farchivebox%40v0.8.5", html)
        self.assertIn("[source: GitHub Releases]", html)
        self.assertIn("[source: Synthetic Fixture]", html)

    def test_empty_results_render_query_and_absence_report(self) -> None:
        html = render_search_results_html(
            {
                "query": "missing",
                "result_count": 0,
                "results": [],
                "absence": {
                    "code": "search_no_matches",
                    "message": "No bounded records matched query 'missing'.",
                },
            }
        )

        self.assertIn("missing", html)
        self.assertIn("No Results", html)
        self.assertIn("search_no_matches", html)
        self.assertIn("No bounded records matched query", html)
