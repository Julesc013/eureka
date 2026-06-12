from __future__ import annotations

import http.client
import json
import threading
import unittest
from urllib.parse import quote

from runtime.local.search_mvp import LocalSearchOptions, LocalSearchService
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for


class LocalSearchServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LocalSearchService()
        self.options = LocalSearchOptions(metadata_fallback="ia_fixture")
        self.httpd = LocalSearchHTTPServer(("127.0.0.1", 0), _handler_for(self.service, self.options))
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.port = int(self.httpd.server_address[1])

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=5)
        self.httpd.server_close()

    def test_health_route(self) -> None:
        status, headers, body = self._get("/health")

        self.assertEqual(status, 200)
        self.assertIn("application/json", headers.get("content-type", ""))
        payload = json.loads(body)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["live_network_enabled"])

    def test_api_status_route(self) -> None:
        status, _headers, body = self._get("/api/status")

        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertEqual(payload["schema_version"], "eureka.local_search_status.v0")
        self.assertIn("/api/search?q=", payload["routes"])
        self.assertFalse(payload["reviewed_index_mutated"])

    def test_api_search_route(self) -> None:
        query = quote("manual for Sound Blaster CT1740")
        status, _headers, body = self._get(f"/api/search?q={query}")

        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertEqual(payload["status"], "candidate")
        self.assertEqual(payload["results"][0]["status"], "candidate")
        self.assertFalse(payload["results"][0]["verified"])

    def test_search_html_route(self) -> None:
        query = quote("old blue FTP client for XP")
        status, headers, body = self._get(f"/search?q={query}")

        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("content-type", ""))
        self.assertIn("old blue FTP client for XP", body)
        self.assertIn('data-status="near_miss"', body)

    def _get(self, path: str) -> tuple[int, dict[str, str], str]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return response.status, {key.lower(): value for key, value in response.getheaders()}, body
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
