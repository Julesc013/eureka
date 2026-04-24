from __future__ import annotations

import json
from io import BytesIO
import tempfile
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


class ResolutionRunsHttpApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            source_registry_public_api=build_demo_source_registry_public_api(),
            default_target_ref=KNOWN_TARGET_REF,
        )

    def test_run_endpoints_start_read_and_list_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resolve_status, _, resolve_body = self._request(
                "/api/run/resolve",
                {"target_ref": KNOWN_TARGET_REF, "run_store_root": temp_dir},
            )
            read_status, _, read_body = self._request(
                "/api/run",
                {"id": "run-exact-resolution-0001", "run_store_root": temp_dir},
            )
            list_status, _, list_body = self._request(
                "/api/runs",
                {"run_store_root": temp_dir},
            )

        resolve_payload = json.loads(resolve_body)
        read_payload = json.loads(read_body)
        list_payload = json.loads(list_body)

        self.assertEqual(resolve_status, "200 OK")
        self.assertEqual(read_status, "200 OK")
        self.assertEqual(list_status, "200 OK")
        self.assertEqual(resolve_payload["selected_run_id"], "run-exact-resolution-0001")
        self.assertEqual(read_payload["runs"][0]["run_kind"], "exact_resolution")
        self.assertEqual(list_payload["run_count"], 1)

    def test_run_search_endpoint_returns_result_summary_and_not_found_is_structured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            search_status, _, search_body = self._request(
                "/api/run/search",
                {"q": "synthetic", "run_store_root": temp_dir},
            )
            missing_status, _, missing_body = self._request(
                "/api/run",
                {"id": "missing-run", "run_store_root": temp_dir},
            )

        search_payload = json.loads(search_body)
        missing_payload = json.loads(missing_body)

        self.assertEqual(search_status, "200 OK")
        self.assertEqual(search_payload["runs"][0]["result_summary"]["result_count"], 2)
        self.assertEqual(missing_status, "404 Not Found")
        self.assertEqual(missing_payload["notices"][0]["code"], "resolution_run_not_found")

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
