from __future__ import annotations

from io import BytesIO
import unittest
from urllib.parse import quote

from runtime.gateway import build_demo_resolution_jobs_public_api, build_demo_search_public_api
from runtime.gateway.public_api import build_demo_public_search_public_api
from surfaces.web.server import WorkbenchWsgiApp


class WebSearchSliceIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            public_search_public_api=build_demo_public_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_search_surface_renders_multiple_single_and_absent_results_from_full_runtime_flow(self) -> None:
        with self.subTest(query="synthetic"):
            status, body = self._fetch("synthetic")
            self.assertEqual(status, "200 OK")
            self.assertIn("synthetic", body)
            self.assertIn("Results", body)
            self.assertIn("local-index-only", body)
            self.assertIn("Blocked actions", body)

        with self.subTest(query="compatibility"):
            status, body = self._fetch("compatibility")
            self.assertEqual(status, "200 OK")
            self.assertIn("Compatibility Lab", body)
            self.assertIn("Results", body)

        with self.subTest(query="missing"):
            status, body = self._fetch("missing")
            self.assertEqual(status, "200 OK")
            self.assertIn("No controlled local-index records matched this query", body)
            self.assertIn("Gaps", body)

    def _fetch(self, query: str) -> tuple[str, str]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": "/search",
                    "QUERY_STRING": f"q={quote(query)}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")
        return str(captured["status"]), body
