from __future__ import annotations

from io import BytesIO
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_comparison_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp, render_comparison_page
from surfaces.web.workbench import render_comparison_html


class ComparisonRenderingTestCase(unittest.TestCase):
    def test_comparison_html_renders_both_sides_agreements_disagreements_and_evidence(self) -> None:
        html = render_comparison_html(
            {
                "status": "compared",
                "left": {
                    "target_ref": "fixture:software/archivebox@0.8.5",
                    "status": "completed",
                    "object": {
                        "id": "obj.archivebox.synthetic",
                        "kind": "software",
                        "label": "ArchiveBox 0.8.5",
                    },
                    "version_or_state": "0.8.5",
                    "source": {
                        "family": "synthetic_fixture",
                        "label": "Synthetic Fixture",
                        "locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    },
                    "evidence": [
                        {
                            "claim_kind": "label",
                            "claim_value": "ArchiveBox 0.8.5",
                            "asserted_by_family": "synthetic_fixture",
                            "asserted_by_label": "Synthetic Fixture",
                            "evidence_kind": "recorded_fixture",
                            "evidence_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        }
                    ],
                    "notices": [],
                },
                "right": {
                    "target_ref": "github-release:archivebox/archivebox@v0.8.5",
                    "status": "completed",
                    "object": {
                        "id": "obj.github-release.archivebox.archivebox",
                        "kind": "software",
                        "label": "ArchiveBox v0.8.5",
                    },
                    "version_or_state": "v0.8.5",
                    "source": {
                        "family": "github_releases",
                        "label": "GitHub Releases",
                        "locator": "https://github.com/archivebox/archivebox/releases/tag/v0.8.5",
                    },
                    "evidence": [
                        {
                            "claim_kind": "version",
                            "claim_value": "v0.8.5",
                            "asserted_by_family": "github_releases",
                            "asserted_by_label": "GitHub Releases",
                            "evidence_kind": "recorded_source_payload",
                            "evidence_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                        }
                    ],
                    "notices": [],
                },
                "agreements": [
                    {"category": "subject_key", "value": "archivebox"},
                    {"category": "object_kind", "value": "software"},
                ],
                "disagreements": [
                    {
                        "category": "object_label",
                        "left_value": "ArchiveBox 0.8.5",
                        "right_value": "ArchiveBox v0.8.5",
                    }
                ],
                "notices": [],
            },
            left_target_ref="fixture:software/archivebox@0.8.5",
            right_target_ref="github-release:archivebox/archivebox@v0.8.5",
        )

        self.assertIn("Compare Two Targets", html)
        self.assertIn("ArchiveBox 0.8.5", html)
        self.assertIn("ArchiveBox v0.8.5", html)
        self.assertIn("subject_key", html)
        self.assertIn("object_label", html)
        self.assertIn("version", html)

    def test_comparison_page_renders_blocked_message_for_missing_input(self) -> None:
        html = render_comparison_page(
            build_demo_comparison_public_api(),
            "",
            "",
        )

        self.assertIn("Provide both left and right target references", html)

    def test_comparison_page_renders_blocked_result_for_unresolved_side(self) -> None:
        html = render_comparison_page(
            build_demo_comparison_public_api(),
            "fixture:software/archivebox@0.8.5",
            "fixture:software/missing-demo-app@0.0.1",
        )

        self.assertIn("comparison_right_unresolved", html)
        self.assertIn("target_ref_not_found", html)
        self.assertIn("fixture:software/missing-demo-app@0.0.1", html)

    def test_wsgi_app_serves_comparison_page(self) -> None:
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            comparison_public_api=build_demo_comparison_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": "/compare",
                    "QUERY_STRING": urlencode(
                        {
                            "left": "fixture:software/archivebox@0.8.5",
                            "right": "github-release:archivebox/archivebox@v0.8.5",
                        }
                    ),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertIn("Comparison State", body)
        self.assertIn("Agreements", body)
        self.assertIn("Disagreements", body)
        self.assertIn("Evidence", body)


if __name__ == "__main__":
    unittest.main()
