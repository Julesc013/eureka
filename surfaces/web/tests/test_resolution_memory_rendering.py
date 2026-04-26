from __future__ import annotations

from io import BytesIO
import tempfile
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import (
    WorkbenchWsgiApp,
    render_create_resolution_memory_page,
    render_resolution_memory_page,
)


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


class ResolutionMemoryRenderingTestCase(unittest.TestCase):
    def test_render_functions_show_memory_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app = WorkbenchWsgiApp(
                build_demo_resolution_jobs_public_api(),
                search_public_api=build_demo_search_public_api(),
                default_target_ref=KNOWN_TARGET_REF,
            )
            self._request(
                app,
                "/api/run/planned-search",
                {"q": "latest Firefox before XP support ended", "run_store_root": temp_dir},
            )
            create_html = render_create_resolution_memory_page(
                temp_dir,
                run_store_root=temp_dir,
                run_id="run-planned-search-0001",
            )
            list_html = render_resolution_memory_page(
                temp_dir,
                memory_id="memory-successful-search-0001",
                run_store_root=temp_dir,
            )

        self.assertIn("Eureka Resolution Memory", create_html)
        self.assertIn("memory-successful-search-0001", create_html)
        self.assertIn("Result Summaries", list_html)
        self.assertIn("latest Firefox before XP support ended", list_html)

    def test_wsgi_routes_render_memory_pages(self) -> None:
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref=KNOWN_TARGET_REF,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            self._request(
                app,
                "/api/run/resolve",
                {"target_ref": KNOWN_TARGET_REF, "run_store_root": temp_dir},
            )
            create_status, create_body = self._request(
                app,
                "/memory/create",
                {
                    "run_store_root": temp_dir,
                    "memory_store_root": temp_dir,
                    "run_id": "run-exact-resolution-0001",
                },
            )
            list_status, list_body = self._request(
                app,
                "/memories",
                {"memory_store_root": temp_dir},
            )

        self.assertEqual(create_status, "200 OK")
        self.assertIn("Selected Memory", create_body)
        self.assertEqual(list_status, "200 OK")
        self.assertIn("memory-successful-resolution-0001", list_body)

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
