from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
import tempfile
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_local_index_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class LocalTasksIntegrationTestCase(unittest.TestCase):
    def test_run_build_and_query_tasks_then_render_selected_task(self) -> None:
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            local_index_public_api=build_demo_local_index_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            build_status, _, build_body = self._request(
                app,
                "/api/task/run/build-local-index",
                {"task_store_root": temp_dir, "index_path": index_path},
            )
            query_status, _, query_body = self._request(
                app,
                "/api/task/run/query-local-index",
                {"task_store_root": temp_dir, "index_path": index_path, "q": "archive"},
            )
            query_task_id = json.loads(query_body)["tasks"][0]["task_id"]
            page_status, _, page_body = self._request(
                app,
                "/task",
                {"task_store_root": temp_dir, "id": query_task_id},
            )

        self.assertEqual(build_status, "200 OK")
        self.assertEqual(query_status, "200 OK")
        self.assertEqual(page_status, "200 OK")
        self.assertEqual(json.loads(build_body)["status"], "completed")
        html = page_body.decode("utf-8")
        self.assertIn("Eureka Local Tasks", html)
        self.assertIn(query_task_id, html)
        self.assertIn("archive", html.casefold())

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
