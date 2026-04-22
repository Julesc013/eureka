from __future__ import annotations

from io import BytesIO
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp, render_subject_states_page
from surfaces.web.workbench import render_subject_states_html


class SubjectStatesRenderingTestCase(unittest.TestCase):
    def test_subject_states_html_renders_subject_and_ordered_states(self) -> None:
        html = render_subject_states_html(
            {
                "status": "listed",
                "requested_subject_key": "archivebox",
                "subject": {
                    "subject_key": "archivebox",
                    "subject_label": "ArchiveBox",
                    "state_count": 3,
                    "source_family_hint": "mixed",
                },
                "states": [
                    {
                        "target_ref": "fixture:software/archivebox@0.8.5",
                        "resolved_resource_id": "resolved:sha256:left",
                        "version_or_state": "0.8.5",
                        "normalized_version_or_state": "0.8.5",
                        "object": {
                            "id": "obj.archivebox.synthetic",
                            "kind": "software",
                            "label": "ArchiveBox 0.8.5",
                        },
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
                    },
                    {
                        "target_ref": "github-release:archivebox/archivebox@v0.8.4",
                        "resolved_resource_id": "resolved:sha256:right",
                        "version_or_state": "v0.8.4",
                        "normalized_version_or_state": "0.8.4",
                        "object": {
                            "id": "obj.github-release.archivebox.archivebox",
                            "kind": "software",
                            "label": "ArchiveBox v0.8.4",
                        },
                        "source": {
                            "family": "github_releases",
                            "label": "GitHub Releases",
                            "locator": "https://github.com/archivebox/archivebox/releases/tag/v0.8.4",
                        },
                        "evidence": [
                            {
                                "claim_kind": "version",
                                "claim_value": "v0.8.4",
                                "asserted_by_family": "github_releases",
                                "asserted_by_label": "GitHub Releases",
                                "evidence_kind": "recorded_source_payload",
                                "evidence_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                            }
                        ],
                    },
                ],
                "notices": [],
            },
            subject_key="archivebox",
        )

        self.assertIn("ArchiveBox", html)
        self.assertIn("Ordered States", html)
        self.assertIn("ArchiveBox 0.8.5", html)
        self.assertIn("ArchiveBox v0.8.4", html)
        self.assertIn("Normalized version/state", html)
        self.assertIn("/?target_ref=fixture%3Asoftware%2Farchivebox%400.8.5", html)

    def test_subject_states_page_renders_message_for_missing_input(self) -> None:
        html = render_subject_states_page(build_demo_subject_states_public_api(), "")

        self.assertIn("Provide a bounded subject key", html)

    def test_wsgi_app_serves_subject_states_page(self) -> None:
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            subject_states_public_api=build_demo_subject_states_public_api(),
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
                    "PATH_INFO": "/subject",
                    "QUERY_STRING": urlencode({"key": "archivebox"}),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertIn("State Listing", body)
        self.assertIn("ArchiveBox", body)
        self.assertIn("ArchiveBox v0.8.4", body)
        self.assertIn("Resolved resource ID", body)


if __name__ == "__main__":
    unittest.main()
