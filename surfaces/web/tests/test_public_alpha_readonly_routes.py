from __future__ import annotations

from io import BytesIO
import json
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_public_alpha_readonly_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WebServerConfig, WorkbenchWsgiApp


class PublicAlphaReadOnlyRoutesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            public_alpha_readonly_api=build_demo_public_alpha_readonly_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
            server_config=WebServerConfig.public_alpha(),
        )

    def test_alpha_api_search_uses_reviewed_snapshot_mode(self) -> None:
        status, headers, body = self._request("/api/v1/alpha/search", {"q": "sampleproject"})
        payload = json.loads(body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(payload["mode"], "reviewed_snapshot_read_only")
        self.assertTrue(payload["snapshot_backed"])
        self.assertTrue(payload["reviewed_index_only"])
        self.assertEqual(payload["result_count"], 1)

    def test_alpha_api_detail_routes_return_packets(self) -> None:
        object_status, _, object_body = self._request("/api/v1/alpha/object/sampleproject")
        source_status, _, source_body = self._request("/api/v1/alpha/source/source-summary-sampleproject-001")
        evidence_status, _, evidence_body = self._request("/api/v1/alpha/evidence/evidence-summary-sampleproject-001")
        needs_status, _, needs_body = self._request("/api/v1/alpha/needs")

        self.assertEqual(object_status, "200 OK")
        self.assertEqual(json.loads(object_body)["record"]["object_id"], "sampleproject")
        self.assertEqual(source_status, "200 OK")
        self.assertIn("source_summary", json.loads(source_body))
        self.assertEqual(evidence_status, "200 OK")
        self.assertIn("evidence_summary", json.loads(evidence_body))
        self.assertEqual(needs_status, "200 OK")
        self.assertGreater(json.loads(needs_body)["need_count"], 0)

    def test_alpha_web_page_renders_search_and_object(self) -> None:
        search_status, _, search_body = self._request("/alpha", {"q": "sampleproject"})
        object_status, _, object_body = self._request("/alpha/object", {"id": "sampleproject"})

        self.assertEqual(search_status, "200 OK")
        self.assertIn("Reviewed snapshot search", search_body)
        self.assertIn("SampleProject 1.0 reviewed local record", search_body)
        self.assertEqual(object_status, "200 OK")
        self.assertIn("Object ID", object_body)
        self.assertIn("sampleproject", object_body)

    def test_alpha_routes_reject_unsafe_controls(self) -> None:
        status, _headers, body = self._request(
            "/api/v1/alpha/search",
            {"q": "sampleproject", "download": "1"},
        )
        payload = json.loads(body)

        self.assertEqual(status, "400 Bad Request")
        self.assertEqual(payload["error"]["code"], "downloads_disabled")

    def _request(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> tuple[str, dict[str, str], str]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": path,
                    "QUERY_STRING": urlencode(query or {}),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )
        return str(captured["status"]), dict(captured["headers"]), body.decode("utf-8")


if __name__ == "__main__":
    unittest.main()
