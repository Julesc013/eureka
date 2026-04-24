from __future__ import annotations

import json
from io import BytesIO
import tempfile
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


class ResolutionMemoryHttpApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref=KNOWN_TARGET_REF,
        )

    def test_memory_create_read_and_list_routes_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_status, _, run_body = self._request(
                "/api/run/search",
                {"q": "archive", "run_store_root": temp_dir},
            )
            run_payload = json.loads(run_body)
            run_id = run_payload["selected_run_id"]

            create_status, _, create_body = self._request(
                "/api/memory/create",
                {
                    "run_store_root": temp_dir,
                    "memory_store_root": temp_dir,
                    "run_id": run_id,
                },
            )
            create_payload = json.loads(create_body)
            memory_id = create_payload["selected_memory_id"]

            read_status, _, read_body = self._request(
                "/api/memory",
                {"id": memory_id, "memory_store_root": temp_dir},
            )
            list_status, _, list_body = self._request(
                "/api/memories",
                {"memory_store_root": temp_dir},
            )

        self.assertEqual(run_status, "200 OK")
        self.assertEqual(create_status, "200 OK")
        self.assertEqual(read_status, "200 OK")
        self.assertEqual(list_status, "200 OK")
        self.assertEqual(create_payload["requested_run_id"], run_id)
        self.assertEqual(json.loads(read_body)["selected_memory_id"], memory_id)
        self.assertEqual(json.loads(list_body)["memory_count"], 1)

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
