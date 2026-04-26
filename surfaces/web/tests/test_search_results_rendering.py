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
                        "evidence": [
                            {
                                "claim_kind": "label",
                                "claim_value": "Archive Viewer",
                                "asserted_by_family": "synthetic_fixture",
                                "asserted_by_label": "Synthetic Fixture",
                                "evidence_kind": "recorded_fixture",
                                "evidence_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                            }
                        ],
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
                        "evidence": [
                            {
                                "claim_kind": "label",
                                "claim_value": "ArchiveBox v0.8.5",
                                "asserted_by_family": "github_releases",
                                "asserted_by_label": "GitHub Releases",
                                "evidence_kind": "recorded_source_payload",
                                "evidence_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                            }
                        ],
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
        self.assertIn("[evidence: label via GitHub Releases]", html)

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
        self.assertIn("/absence/search?q=missing", html)

    def test_member_results_render_parent_and_member_context(self) -> None:
        html = render_search_results_html(
            {
                "query": "driver.inf",
                "result_count": 1,
                "results": [
                    {
                        "target_ref": "member:sha256:abc",
                        "resolved_resource_id": "resolved:sha256:abc",
                        "primary_lane": "inside_bundles",
                        "user_cost_score": 1,
                        "usefulness_summary": "inside bundles; user cost 1; why: member_has_path",
                        "compatibility_summary": "Windows 2000: driver_for_hardware via file_path (medium)",
                        "compatibility_evidence": [
                            {
                                "evidence_id": "compat-evidence:sha256:abc",
                                "subject_target_ref": "member:sha256:abc",
                                "source_family": "local_bundle_fixtures",
                                "evidence_kind": "file_path",
                                "claim_type": "driver_for_hardware",
                                "platform": {"family": "windows", "name": "Windows 2000"},
                                "architecture": "x86",
                                "confidence": "medium",
                                "locator": "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
                                "created_by_slice": "compatibility_evidence_pack_v0",
                            }
                        ],
                        "object": {
                            "id": "obj.synthetic-member.abc",
                            "kind": "synthetic_member",
                            "label": "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
                            "record_kind": "synthetic_member",
                            "member_path": "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
                            "member_kind": "driver",
                            "parent_target_ref": "local-bundle-fixture:driver-support-cd@1.0",
                        },
                        "source": {
                            "family": "local_bundle_fixtures",
                            "source_id": "local-bundle-fixtures",
                            "label": "Local Bundle Fixtures",
                        },
                        "evidence": [],
                    }
                ],
            }
        )

        self.assertIn("drivers/wifi/thinkpad_t42/windows2000/driver.inf", html)
        self.assertIn("[member: drivers/wifi/thinkpad_t42/windows2000/driver.inf]", html)
        self.assertIn("[kind: driver]", html)
        self.assertIn("[parent: local-bundle-fixture:driver-support-cd@1.0]", html)
        self.assertIn("[lane: inside_bundles]", html)
        self.assertIn("[user cost: 1]", html)
        self.assertIn("[compatibility: Windows 2000: driver_for_hardware via file_path (medium)]", html)
        self.assertIn("[compat evidence: Windows 2000 driver_for_hardware via file_path]", html)
