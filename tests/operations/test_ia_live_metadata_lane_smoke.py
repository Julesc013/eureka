from __future__ import annotations

import unittest

from runtime.local_service.request_context import build_request_context
from runtime.local_service.routes import route_request


class IALiveMetadataLaneSmokeTests(unittest.TestCase):
    def test_local_service_command_route_blocks_public_and_allows_operator_mock(self) -> None:
        created = route_request(
            object(),
            build_request_context("GET", "/api/v1/resolution-runs", {"q": "sampleproject", "projection": "operator_workbench"}, "127.0.0.1"),
        )
        self.assertEqual(200, created.status_code)
        run_id = created.payload["run_id"]
        operator = route_request(
            object(),
            build_request_context(
                "GET",
                f"/api/v1/resolution-runs/{run_id}/commands",
                "command=run_live_ia_metadata_mock&projection=operator_workbench&mock-live=true",
                "127.0.0.1",
            ),
        )
        self.assertEqual(200, operator.status_code)
        self.assertTrue(operator.payload["allowed"])
        public = route_request(
            object(),
            build_request_context(
                "GET",
                f"/api/v1/resolution-runs/{run_id}/commands",
                "command=run_live_ia_metadata_mock&projection=public_web&mock-live=true",
                "127.0.0.1",
            ),
        )
        self.assertEqual(403, public.status_code)
        self.assertFalse(public.payload["allowed"])


if __name__ == "__main__":
    unittest.main()
