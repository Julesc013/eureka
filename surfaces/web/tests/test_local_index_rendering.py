from __future__ import annotations

import unittest

from surfaces.web.workbench import render_local_index_html


class LocalIndexRenderingTestCase(unittest.TestCase):
    def test_local_index_rendering_shows_metadata_and_results(self) -> None:
        html = render_local_index_html(
            {
                "status": "queried",
                "query": "archive",
                "result_count": 1,
                "results": [
                    {
                        "index_record_id": "resolved_object:github-release:archivebox/archivebox@v0.8.5",
                        "record_kind": "resolved_object",
                        "label": "ArchiveBox v0.8.5",
                        "summary": "software_release from GitHub Releases",
                        "target_ref": "github-release:archivebox/archivebox@v0.8.5",
                        "resolved_resource_id": "github-release.archivebox.archivebox.v0.8.5",
                        "source_id": "github-releases-recorded-fixtures",
                        "source_family": "github_releases",
                        "representation_id": "rep.github-release.archivebox.archivebox.v0.8.5.release-page",
                        "member_path": None,
                        "version_or_state": "v0.8.5",
                        "evidence": ["version v0.8.5"],
                        "route_hints": {"surface_route": "/", "target_ref": "github-release:archivebox/archivebox@v0.8.5"},
                    }
                ],
                "index": {
                    "index_path_kind": "bootstrap_local_path",
                    "index_path": "D:/tmp/local-index.sqlite3",
                    "fts_mode": "fts5",
                    "record_count": 18,
                    "record_kind_counts": {"resolved_object": 2, "source_record": 6},
                },
            },
            requested_index_path="D:/tmp/local-index.sqlite3",
            requested_query="archive",
        )

        self.assertIn("Eureka Local Index", html)
        self.assertIn("ArchiveBox v0.8.5", html)
        self.assertIn("github-releases-recorded-fixtures", html)
        self.assertIn("fts5", html)


if __name__ == "__main__":
    unittest.main()
