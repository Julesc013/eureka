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

    def test_local_index_rendering_shows_synthetic_member_context(self) -> None:
        html = render_local_index_html(
            {
                "status": "queried",
                "query": "driver.inf",
                "result_count": 1,
                "results": [
                    {
                        "index_record_id": "synthetic_member:member:sha256:abc",
                        "record_kind": "synthetic_member",
                        "label": "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
                        "summary": "driver member of ThinkPad T42 wireless support bundle",
                        "target_ref": "member:sha256:abc",
                        "resolved_resource_id": "obj.synthetic-member.abc",
                        "source_id": "local-bundle-fixtures",
                        "source_family": "local_bundle_fixtures",
                        "representation_id": "rep.synthetic-member.abc",
                        "member_path": "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
                        "parent_target_ref": "local-bundle-fixture:driver-support-cd@1.0",
                        "parent_representation_id": "rep.local-bundle.driver-support-cd.zip",
                        "member_kind": "driver",
                        "media_type": "text/plain",
                        "size_bytes": 128,
                        "content_hash": "sha256:abcd",
                        "action_hints": ["inspect_parent_bundle", "read_member", "preview_member"],
                        "result_lanes": ["inside_bundles", "best_direct_answer"],
                        "primary_lane": "inside_bundles",
                        "user_cost_score": 1,
                        "user_cost_reasons": ["member_has_path", "source_evidence_present"],
                        "usefulness_summary": "inside bundles; user cost 1; why: member_has_path",
                        "evidence": ["member_path drivers/wifi/thinkpad_t42/windows2000/driver.inf"],
                        "route_hints": {"surface_route": "/", "target_ref": "member:sha256:abc"},
                    }
                ],
                "index": {
                    "index_path_kind": "bootstrap_local_path",
                    "index_path": "D:/tmp/local-index.sqlite3",
                    "fts_mode": "fts5",
                    "record_count": 1,
                    "record_kind_counts": {"synthetic_member": 1},
                },
            },
            requested_index_path="D:/tmp/local-index.sqlite3",
            requested_query="driver.inf",
        )

        self.assertIn("synthetic_member", html)
        self.assertIn("drivers/wifi/thinkpad_t42/windows2000/driver.inf", html)
        self.assertIn("local-bundle-fixture:driver-support-cd@1.0", html)
        self.assertIn("preview_member", html)
        self.assertIn("primary_lane: inside_bundles", html)
        self.assertIn("user_cost_score: 1", html)


if __name__ == "__main__":
    unittest.main()
