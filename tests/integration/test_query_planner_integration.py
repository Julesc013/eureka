from __future__ import annotations

import json
from io import BytesIO
import tempfile
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_query_planner_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class QueryPlannerIntegrationTestCase(unittest.TestCase):
    def test_planned_search_run_persists_and_renders_plan_summary(self) -> None:
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            query_planner_public_api=build_demo_query_planner_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            start_status, _, start_body = self._request(
                app,
                "/api/run/planned-search",
                {"q": "latest Firefox before XP support ended", "run_store_root": temp_dir},
            )
            start_payload = json.loads(start_body)
            run_id = start_payload["selected_run_id"]

            read_status, _, page_body = self._request(
                app,
                "/run",
                {"id": run_id, "run_store_root": temp_dir},
            )

        self.assertEqual(start_status, "200 OK")
        self.assertEqual(read_status, "200 OK")
        html = page_body.decode("utf-8")
        self.assertIn("Resolution Task", html)
        self.assertIn("find_software_release", html)
        self.assertIn("Firefox", html)

    def _request(
        self,
        app,
        path: str,
        query: dict[str, str],
    ) -> tuple[str, dict[str, str], bytes]:
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
        )
        return str(captured["status"]), dict(captured["headers"]), body


if __name__ == "__main__":
    unittest.main()
