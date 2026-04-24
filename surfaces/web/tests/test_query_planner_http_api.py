from __future__ import annotations

import json
from io import BytesIO
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_query_planner_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class QueryPlannerHttpApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            query_planner_public_api=build_demo_query_planner_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_query_plan_endpoint_returns_machine_readable_plan(self) -> None:
        status, headers, body = self._request(
            "/api/query-plan",
            {"q": "driver for ThinkPad T42 Wi-Fi Windows 2000"},
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["query_plan"]["task_kind"], "find_driver")
        self.assertEqual(
            payload["query_plan"]["constraints"]["platform"]["marketing_alias"],
            "Windows 2000",
        )

    def test_planned_search_run_endpoint_records_resolution_task(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            status, _, body = self._request(
                "/api/run/planned-search",
                {"q": "latest Firefox before XP support ended", "run_store_root": temp_dir},
            )

        payload = json.loads(body)
        self.assertEqual(status, "200 OK")
        self.assertEqual(payload["runs"][0]["run_kind"], "planned_search")
        self.assertEqual(payload["runs"][0]["resolution_task"]["constraints"]["product_hint"], "Firefox")

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
