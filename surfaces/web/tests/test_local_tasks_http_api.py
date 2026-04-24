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


class LocalTasksHttpApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            local_index_public_api=build_demo_local_index_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_run_read_and_list_task_routes_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            run_status, _, run_body = self._request(
                "/api/task/run/build-local-index",
                {"task_store_root": temp_dir, "index_path": index_path},
            )
            task_id = json.loads(run_body)["tasks"][0]["task_id"]
            read_status, _, read_body = self._request(
                "/api/task",
                {"task_store_root": temp_dir, "id": task_id},
            )
            list_status, _, list_body = self._request(
                "/api/tasks",
                {"task_store_root": temp_dir},
            )

        self.assertEqual(run_status, "200 OK")
        self.assertEqual(read_status, "200 OK")
        self.assertEqual(list_status, "200 OK")
        self.assertEqual(json.loads(read_body)["selected_task_id"], task_id)
        self.assertEqual(json.loads(list_body)["task_count"], 1)

    def _request(
        self,
        path: str,
        query: dict[str, str],
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
                    "QUERY_STRING": urlencode(query),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )
        return str(captured["status"]), dict(captured["headers"]), body


if __name__ == "__main__":
    unittest.main()
