from __future__ import annotations

import json
from io import BytesIO
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_comparison_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class GitHubReleaseHttpApiSliceIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            comparison_public_api=build_demo_comparison_public_api(),
            subject_states_public_api=build_demo_subject_states_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_http_api_surfaces_recorded_github_release_through_public_boundary(self) -> None:
        search_status, _, search_body = self._request("/api/search", {"q": "archive"})
        self.assertEqual(search_status, "200 OK")
        search_payload = json.loads(search_body)
        self.assertGreaterEqual(search_payload["result_count"], 15)
        target_refs = [result["target_ref"] for result in search_payload["results"]]
        self.assertEqual(
            target_refs[:4],
            [
                "fixture:software/archive-viewer@0.9.0",
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
                "github-release:archivebox/archivebox@v0.8.5",
            ],
        )
        self.assertTrue(
            {
                "internet-archive-recorded:ia-win7-utility-pack-fixture",
                "internet-archive-recorded:ia-firefox-xp-support-fixture",
                "internet-archive-recorded:ia-thinkpad-t42-wireless-support-fixture",
                "internet-archive-recorded:ia-win98-registry-repair-fixture",
            }.issubset(set(target_refs)),
        )
        self.assertEqual(search_payload["results"][3]["source"]["label"], "GitHub Releases")
        self.assertEqual(search_payload["results"][3]["evidence"][1]["claim_kind"], "version")
        self.assertEqual(search_payload["results"][3]["evidence"][1]["claim_value"], "v0.8.5")
        self.assertEqual(search_payload["results"][3]["primary_lane"], "community")
        self.assertEqual(search_payload["results"][3]["user_cost_score"], 2)

        resolve_status, _, resolve_body = self._request(
            "/api/resolve",
            {"target_ref": "github-release:cli/cli@v2.65.0"},
        )
        self.assertEqual(resolve_status, "200 OK")
        resolve_payload = json.loads(resolve_body)
        self.assertEqual(resolve_payload["workbench_session"]["active_job"]["status"], "completed")
        self.assertEqual(resolve_payload["workbench_session"]["source"]["family"], "github_releases")
        self.assertEqual(resolve_payload["workbench_session"]["source"]["label"], "GitHub Releases")
        self.assertEqual(
            resolve_payload["workbench_session"]["source"]["locator"],
            "https://github.com/cli/cli/releases/tag/v2.65.0",
        )
        self.assertEqual(resolve_payload["workbench_session"]["evidence"][1]["claim_kind"], "version")
        self.assertEqual(resolve_payload["workbench_session"]["evidence"][1]["claim_value"], "v2.65.0")

    def _request(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> tuple[str, dict[str, str], bytes]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": path,
                    "QUERY_STRING": urlencode(query or {}),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )
        return str(captured["status"]), dict(captured["headers"]), body
