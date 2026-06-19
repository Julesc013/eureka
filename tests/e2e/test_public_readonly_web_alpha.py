from __future__ import annotations

import hashlib
import http.client
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import quote

from runtime.local.review_materialization import accept_candidate
from runtime.local.search_index import build_local_demo_index, write_index
from runtime.local.local_search import LocalSearchOptions, LocalSearchService
from runtime.local.public_alpha_service import PublicAlphaService
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for, main as run_local_main


QUERY = "manual for Sound Blaster CT1740"
FORBIDDEN_PUBLIC_MARKERS = (
    ".eureka",
    "local_review_ledger",
    "local_reviewed_records",
    "local_search_index",
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "C:\\",
    "D:\\",
    "/Users/",
    "\\Users\\",
)
UNSAFE_ACTION_MARKERS = (
    'href="/workbench',
    "Accept candidate",
    "rebuild index",
    "download",
    "install",
    "emulate",
)


class PublicReadonlyWebAlphaTests(unittest.TestCase):
    def test_public_alpha_startup_requires_valid_local_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.json"
            result = _run_local_main(
                "--smoke",
                "--public-alpha",
                "--index",
                "local",
                "--index-path",
                str(missing),
                "--metadata-fallback",
                "none",
            )

        self.assertEqual(result, 2)

    def test_public_alpha_startup_rejects_live_workbench_and_non_loopback(self) -> None:
        with _ReviewedIndexDemo() as demo:
            cases = [
                (
                    "--metadata-fallback",
                    "ia_live",
                ),
                (
                    "--allow-live-metadata",
                ),
                (
                    "--enable-workbench",
                    "--workbench-token",
                    "local-dev-token",
                ),
                (
                    "--host",
                    "0.0.0.0",
                ),
            ]
            results = [
                _run_local_main(
                    "--smoke",
                    "--public-alpha",
                    "--index",
                    "local",
                    "--index-path",
                    str(demo.reviewed_index_path),
                    "--metadata-fallback",
                    "none",
                    *case,
                )
                for case in cases
            ]

        self.assertEqual(results, [2, 2, 2, 2])

    def test_public_pages_status_about_method_and_health_work(self) -> None:
        with _ReviewedIndexDemo() as demo, _RunningPublicServer(demo.reviewed_index_path) as server:
            home = server.get("/")
            health = server.get("/health")
            status = server.get("/status")
            api_status = server.get("/api/status")
            about = server.get("/about")
            method = server.get("/method")

        self.assertEqual(home[0], 200)
        self.assertIn("Eureka Public Alpha", home[2])
        self.assertEqual(health[0], 200)
        self.assertFalse(json.loads(health[2])["public_mutation_enabled"])
        self.assertEqual(status[0], 200)
        self.assertIn("Read only:", status[2])
        self.assertEqual(api_status[0], 200)
        payload = json.loads(api_status[2])
        self.assertTrue(payload["public_alpha_mode"])
        self.assertTrue(payload["read_only"])
        self.assertTrue(payload["index_loaded"])
        self.assertFalse(payload["live_metadata_enabled"])
        self.assertFalse(payload["public_live_fanout"])
        self.assertFalse(payload["workbench_exposed"])
        self.assertFalse(payload["public_mutation_enabled"])
        self.assertNotIn("index_path", payload)
        self.assertEqual(about[0], 200)
        self.assertIn("evidence-first", about[2])
        self.assertEqual(method[0], 200)
        self.assertIn("Fallback and live metadata are disabled", method[2])
        self._assert_public_safe(home[2] + status[2] + api_status[2] + about[2] + method[2])

    def test_public_search_api_and_html_show_reviewed_result_first(self) -> None:
        with _ReviewedIndexDemo() as demo, _RunningPublicServer(demo.reviewed_index_path) as server:
            api_code, _api_headers, api_body = server.get(f"/api/search?q={quote(QUERY)}")
            html_code, html_headers, html_body = server.get(f"/search?q={quote(QUERY)}")

        payload = json.loads(api_body)
        first = payload["results"][0]
        self.assertEqual(api_code, 200)
        self.assertTrue(payload["public_alpha_mode"])
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["fallback_used"])
        self.assertEqual(payload["fallback_mode"], "none")
        self.assertEqual(first["review_state"], "accepted")
        self.assertFalse(first["artifact_verified"])
        self.assertTrue(first["record_url"].startswith("/record/"))
        self.assertEqual(first["read_actions"][0]["kind"], "read")
        self.assertEqual(html_code, 200)
        self.assertIn("text/html", html_headers.get("content-type", ""))
        self.assertIn("Review state:", html_body)
        self.assertIn("accepted", html_body)
        self.assertIn("Artifact verified:", html_body)
        self.assertIn("View record", html_body)
        self._assert_public_safe(api_body + html_body)
        self._assert_no_unsafe_action_affordances(html_body)

    def test_public_search_exposes_candidate_need_and_other_states(self) -> None:
        with _ReviewedIndexDemo() as demo, _RunningPublicServer(demo.reviewed_index_path) as server:
            windows = json.loads(server.get(f"/api/search?q={quote('Windows 7 apps')}")[2])
            driver = json.loads(server.get(f"/api/search?q={quote('driver for Win98')}")[2])
            ftp = json.loads(server.get(f"/api/search?q={quote('old blue FTP client for XP')}")[2])
            firefox = json.loads(server.get(f"/api/search?q={quote('latest Firefox before XP support ended')}")[2])
            article = json.loads(server.get(f"/api/search?q={quote('article about ray tracing in a 1994 magazine')}")[2])

        statuses = {
            windows["results"][0]["status"],
            driver["results"][0]["status"],
            ftp["results"][0]["status"],
            *[item["status"] for item in firefox["results"]],
            *[item["status"] for item in article["results"]],
        }
        self.assertIn("candidate", statuses)
        self.assertIn("need", statuses)
        self.assertIn("near_miss", statuses)
        self.assertIn("policy_blocked", statuses)
        self.assertIn("unavailable", statuses)

    def test_record_route_works_and_missing_record_is_public_safe_404(self) -> None:
        with _ReviewedIndexDemo() as demo, _RunningPublicServer(demo.reviewed_index_path) as server:
            search_payload = json.loads(server.get(f"/api/search?q={quote(QUERY)}")[2])
            record_url = search_payload["results"][0]["record_url"]
            record_code, record_headers, record_body = server.get(record_url)
            missing_code, _missing_headers, missing_body = server.get("/record/missing-public-record")

        self.assertEqual(record_code, 200)
        self.assertIn("text/html", record_headers.get("content-type", ""))
        self.assertIn("Provenance Summary", record_body)
        self.assertIn("local file paths redacted", record_body.lower())
        self.assertIn("Artifact verified:", record_body)
        self.assertIn("false", record_body)
        self.assertEqual(missing_code, 404)
        self.assertIn("No public record exists", missing_body)
        self._assert_public_safe(record_body + missing_body)

    def test_public_routes_do_not_mutate_local_artifacts(self) -> None:
        with _ReviewedIndexDemo() as demo, _RunningPublicServer(demo.reviewed_index_path) as server:
            before = demo.hashes()
            paths = [
                "/",
                "/health",
                "/status",
                "/api/status",
                "/about",
                "/method",
                f"/api/search?q={quote(QUERY)}",
                f"/search?q={quote(QUERY)}",
            ]
            for path in paths:
                status, _headers, body = server.get(path)
                self.assertEqual(status, 200, body)
            record_url = json.loads(server.get(f"/api/search?q={quote(QUERY)}")[2])["results"][0]["record_url"]
            self.assertEqual(server.get(record_url)[0], 200)
            after = demo.hashes()

        self.assertEqual(before, after)

    def test_workbench_routes_disabled_and_cannot_mutate_in_public_alpha(self) -> None:
        with _ReviewedIndexDemo() as demo, _RunningPublicServer(demo.reviewed_index_path) as server:
            before = demo.hashes()
            html_code, _headers, html_body = server.get("/workbench")
            api_code, _api_headers, api_body = server.get("/workbench/api/status")
            post_code, _post_headers, post_body = server.post_json(
                "/workbench/api/review/accept",
                {"query": QUERY, "reason": "should not mutate"},
            )
            after = demo.hashes()

        self.assertEqual(html_code, 404)
        self.assertIn("Workbench Disabled", html_body)
        self.assertEqual(api_code, 404)
        self.assertFalse(json.loads(api_body)["mutation_performed"])
        self.assertEqual(post_code, 404)
        self.assertFalse(json.loads(post_body)["mutation_performed"])
        self.assertEqual(before, after)

    def _assert_public_safe(self, body: str) -> None:
        for marker in FORBIDDEN_PUBLIC_MARKERS:
            self.assertNotIn(marker, body)

    def _assert_no_unsafe_action_affordances(self, body: str) -> None:
        for marker in UNSAFE_ACTION_MARKERS:
            self.assertNotIn(marker, body)


class _ReviewedIndexDemo:
    def __enter__(self) -> "_ReviewedIndexDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.index_path = root / "local_search_index.json"
        self.ledger_path = root / "local_review_ledger.jsonl"
        self.records_path = root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = root / "local_search_index.reviewed.json"
        write_index(self.index_path, build_local_demo_index())
        accept_candidate(
            index_path=self.index_path,
            query=QUERY,
            ledger_path=self.ledger_path,
            records_path=self.records_path,
            reviewer="local_demo",
            reason="Public alpha local reviewed seed",
            reviewed_at="2026-06-13T00:00:00+10:00",
        )
        write_index(self.reviewed_index_path, build_local_demo_index(reviewed_records_path=self.records_path))
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()

    def hashes(self) -> dict[str, str]:
        return {
            "index": _sha256(self.reviewed_index_path),
            "ledger": _sha256(self.ledger_path),
            "records": _sha256(self.records_path),
        }


class _RunningPublicServer:
    def __init__(self, index_path: Path) -> None:
        self._options = LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none")
        self._httpd: LocalSearchHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def __enter__(self) -> "_RunningPublicServer":
        service = LocalSearchService()
        public_alpha = PublicAlphaService(search_service=service, search_options=self._options)
        self._httpd = LocalSearchHTTPServer(
            ("127.0.0.1", 0),
            _handler_for(service, self._options, None, public_alpha),
        )
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        self.port = int(self._httpd.server_address[1])
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
        if self._thread is not None:
            self._thread.join(timeout=5)
        if self._httpd is not None:
            self._httpd.server_close()

    def get(self, path: str) -> tuple[int, dict[str, str], str]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return response.status, {key.lower(): value for key, value in response.getheaders()}, body
        finally:
            conn.close()

    def post_json(self, path: str, payload: dict[str, str]) -> tuple[int, dict[str, str], str]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("POST", path, body=json.dumps(payload), headers={"Content-Type": "application/json"})
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return response.status, {key.lower(): value for key, value in response.getheaders()}, body
        finally:
            conn.close()


def _run_local_main(*args: str) -> int:
    return run_local_main(list(args), stdout=io.StringIO(), stderr=io.StringIO())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
