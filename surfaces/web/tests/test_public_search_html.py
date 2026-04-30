from __future__ import annotations

from io import BytesIO
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_public_search_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class PublicSearchHtmlTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            public_search_public_api=build_demo_public_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_missing_query_renders_search_form(self) -> None:
        status, headers, html = self._request("/search")

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("Eureka Public Search", html)
        self.assertIn("type=\"search\"", html)
        self.assertIn("local-index-only", html)

    def test_search_route_renders_result_cards_without_javascript(self) -> None:
        status, _, html = self._request("/search", {"q": "driver.inf"})

        self.assertEqual(status, "200 OK")
        self.assertIn("Search State", html)
        self.assertIn("Results", html)
        self.assertIn("Blocked actions", html)
        self.assertIn("download", html)
        self.assertIn("No live probes", html)
        self.assertNotIn("<script", html.casefold())

    def test_forbidden_parameter_renders_safe_error_page(self) -> None:
        status, _, html = self._request(
            "/search",
            {"q": "archive", "url": "https://example.invalid/"},
        )

        self.assertEqual(status, "400 Bad Request")
        self.assertIn("Request Blocked", html)
        self.assertIn("forbidden_parameter", html)
        self.assertNotIn("example.invalid", html)

    def _request(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> tuple[str, dict[str, str], str]:
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
        return str(captured["status"]), dict(captured["headers"]), body.decode("utf-8")


if __name__ == "__main__":
    unittest.main()
