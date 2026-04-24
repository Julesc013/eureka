from __future__ import annotations

from io import BytesIO
import json
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_archive_resolution_evals_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class ArchiveResolutionEvalsHttpApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            archive_resolution_evals_public_api=build_demo_archive_resolution_evals_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_eval_endpoint_returns_json(self) -> None:
        status, _headers, body = self._request(
            "/api/evals/archive-resolution",
            {"task_id": "windows_7_apps"},
        )
        payload = json.loads(body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(payload["status"], "evaluated")
        self.assertEqual(payload["eval_suite"]["total_task_count"], 1)
        self.assertEqual(payload["eval_suite"]["tasks"][0]["task_id"], "windows_7_apps")

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
