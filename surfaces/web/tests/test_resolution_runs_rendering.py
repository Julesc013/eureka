from __future__ import annotations

import tempfile
import unittest

from surfaces.web.server import (
    WorkbenchWsgiApp,
    render_deterministic_search_run_page,
    render_exact_resolution_run_page,
    render_resolution_runs_page,
)
from runtime.gateway.public_api import (
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
)
from io import BytesIO
from urllib.parse import urlencode


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


class ResolutionRunsRenderingTestCase(unittest.TestCase):
    def test_render_functions_show_status_and_checked_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resolve_html = render_exact_resolution_run_page(temp_dir, KNOWN_TARGET_REF)
            search_html = render_deterministic_search_run_page(temp_dir, "archive")
            list_html = render_resolution_runs_page(temp_dir, run_id="run-exact-resolution-0001")

        self.assertIn("Eureka Resolution Runs", resolve_html)
        self.assertIn("Selected Run", resolve_html)
        self.assertIn("github-releases-recorded-fixtures", resolve_html)
        self.assertIn("Result Summary", search_html)
        self.assertIn("run-exact-resolution-0001", list_html)

    def test_wsgi_routes_render_run_pages(self) -> None:
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            source_registry_public_api=build_demo_source_registry_public_api(),
            default_target_ref=KNOWN_TARGET_REF,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            resolve_status, resolve_body = self._request(
                app,
                "/run/resolve",
                {"target_ref": KNOWN_TARGET_REF, "run_store_root": temp_dir},
            )
            runs_status, runs_body = self._request(
                app,
                "/runs",
                {"run_store_root": temp_dir},
            )

        self.assertEqual(resolve_status, "200 OK")
        self.assertIn("Selected Run", resolve_body)
        self.assertEqual(runs_status, "200 OK")
        self.assertIn("run-exact-resolution-0001", runs_body)

    def _request(
        self,
        app: WorkbenchWsgiApp,
        path: str,
        query: dict[str, str],
    ) -> tuple[str, str]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": path,
                    "QUERY_STRING": urlencode(query),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")
        return str(captured["status"]), body


if __name__ == "__main__":
    unittest.main()
