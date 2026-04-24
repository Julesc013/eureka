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


class LocalIndexHttpApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            local_index_public_api=build_demo_local_index_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_index_build_status_and_query_routes_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            build_status, _, build_body = self._request("/api/index/build", {"index_path": index_path})
            status_status, _, status_body = self._request("/api/index/status", {"index_path": index_path})
            query_status, _, query_body = self._request(
                "/api/index/query",
                {"index_path": index_path, "q": "synthetic"},
            )

        self.assertEqual(build_status, "200 OK")
        self.assertEqual(status_status, "200 OK")
        self.assertEqual(query_status, "200 OK")
        self.assertEqual(json.loads(build_body)["status"], "built")
        self.assertEqual(json.loads(status_body)["status"], "available")
        self.assertGreater(json.loads(query_body)["result_count"], 0)

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
