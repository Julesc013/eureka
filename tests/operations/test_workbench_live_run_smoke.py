from __future__ import annotations

import unittest

from runtime.local.service.request_context import build_request_context
from runtime.local.service.routes import route_request


class WorkbenchLiveRunSmokeTests(unittest.TestCase):
    def test_local_service_routes_project_run(self) -> None:
        response = route_request(
            object(),
            build_request_context("GET", "/api/v1/resolution-runs", {"q": "sampleproject"}, "127.0.0.1"),
        )
        self.assertEqual(200, response.status_code)
        run_id = response.payload["run_id"]
        self.assertTrue(run_id)
        for suffix in ("", "/events", "/lanes", "/workunits"):
            route = f"/api/v1/resolution-runs/{run_id}{suffix}"
            detail = route_request(object(), build_request_context("GET", route, "", "127.0.0.1"))
            self.assertEqual(200, detail.status_code, route)
        blocked = route_request(
            object(),
            build_request_context("GET", f"/api/v1/resolution-runs/{run_id}/commands", "command=run_live_source", "127.0.0.1"),
        )
        self.assertEqual(403, blocked.status_code)
        self.assertFalse(blocked.payload["allowed"])

    def test_html_run_page_renders(self) -> None:
        response = route_request(
            object(),
            build_request_context("GET", "/runs", {"q": "sampleproject"}, "127.0.0.1"),
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("Resolution Run", response.body)
        self.assertIn("Lane snapshot", response.body)


if __name__ == "__main__":
    unittest.main()
