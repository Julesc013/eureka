from __future__ import annotations

import hashlib
import http.client
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import quote, urlencode

from runtime.local.search_index import build_local_demo_index, write_index
from runtime.local.local_search import LocalSearchOptions, LocalSearchService
from runtime.local.workbench_service import WorkbenchOptions, WorkbenchService
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for, main as run_local_main


QUERY = "manual for Sound Blaster CT1740"
TOKEN = "local-dev-token"


class WorkbenchOperatorRoutesTests(unittest.TestCase):
    def test_workbench_routes_disabled_by_default(self) -> None:
        with _WorkbenchDemo(enable_workbench=False) as demo:
            status, _headers, body = demo.server.get("/workbench")
            api_status, _api_headers, api_body = demo.server.get("/workbench/api/status")

        self.assertEqual(status, 404)
        self.assertIn("Workbench Disabled", body)
        self.assertEqual(api_status, 404)
        self.assertEqual(json.loads(api_body)["status"], "disabled")

    def test_workbench_refuses_non_loopback_host_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"
            write_index(index_path, build_local_demo_index())
            completed = run_local_main(
                [
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8765",
                    "--index",
                    "local",
                    "--index-path",
                    str(index_path),
                    "--metadata-fallback",
                    "none",
                    "--enable-workbench",
                    "--workbench-token",
                    TOKEN,
                    "--smoke",
                ],
                stdout=io.StringIO(),
                stderr=io.StringIO(),
            )

        self.assertEqual(completed, 2)

    def test_workbench_token_required_and_unauthorized_requests_do_not_mutate(self) -> None:
        with _WorkbenchDemo() as demo:
            before = demo.hashes()
            missing_status, _missing_headers, missing_body = demo.server.get(f"/workbench/api/candidates?q={quote(QUERY)}")
            bad_status, _bad_headers, bad_body = demo.server.post_json(
                "/workbench/api/review/accept",
                {"token": "wrong", "query": QUERY, "reason": "bad token"},
            )
            after = demo.hashes()

        self.assertEqual(missing_status, 403)
        self.assertEqual(json.loads(missing_body)["status"], "unauthorized")
        self.assertEqual(bad_status, 403)
        self.assertEqual(json.loads(bad_body)["mutation_performed"], False)
        self.assertEqual(before, after)

    def test_status_candidates_and_review_page_are_visible_with_token(self) -> None:
        with _WorkbenchDemo() as demo:
            status_code, _status_headers, status_body = demo.server.get(f"/workbench/api/status?token={TOKEN}")
            candidates_code, _candidate_headers, candidates_body = demo.server.get(
                f"/workbench/api/candidates?q={quote(QUERY)}&token={TOKEN}"
            )
            review_code, review_headers, review_body = demo.server.get(
                f"/workbench/review?q={quote(QUERY)}&token={TOKEN}"
            )

        status_payload = json.loads(status_body)
        candidates_payload = json.loads(candidates_body)
        self.assertEqual(status_code, 200)
        self.assertTrue(status_payload["enabled"])
        self.assertTrue(status_payload["token_required"])
        self.assertTrue(status_payload["local_private"])
        self.assertFalse(status_payload["public_workbench"])
        self.assertEqual(candidates_code, 200)
        self.assertGreaterEqual(candidates_payload["candidate_count"], 1)
        self.assertEqual(candidates_payload["candidates"][0]["status"], "candidate")
        self.assertEqual(review_code, 200)
        self.assertIn("text/html", review_headers.get("content-type", ""))
        self.assertIn("Accept candidate", review_body)
        self.assertIn("artifact verified", review_body.lower())

    def test_accept_writes_local_review_artifacts_rebuilds_index_and_updates_search(self) -> None:
        with _WorkbenchDemo() as demo:
            before_index_hash = _sha256(demo.index_path)
            status, _headers, body = demo.server.post_json(
                "/workbench/api/review/accept",
                {"query": QUERY, "reason": "Workbench P0 local accept demo"},
                token=TOKEN,
            )
            after_index_hash = _sha256(demo.index_path)
            ledger_rows = _jsonl(demo.ledger_path)
            record_rows = _jsonl(demo.records_path)
            api_code, _api_headers, api_body = demo.server.get(f"/api/search?q={quote(QUERY)}")
            html_code, html_headers, html_body = demo.server.get(f"/search?q={quote(QUERY)}")

        payload = json.loads(body)
        api_payload = json.loads(api_body)
        first = api_payload["results"][0]
        self.assertEqual(status, 200)
        self.assertNotEqual(before_index_hash, after_index_hash)
        self.assertTrue(payload["index_rebuilt"])
        self.assertTrue(payload["review_event_id"])
        self.assertTrue(payload["reviewed_record_id"])
        self.assertFalse(payload["artifact_verified"])
        self.assertFalse(payload["accepted_truth_created"])
        self.assertFalse(payload["public_index_mutated"])
        self.assertFalse(payload["master_index_mutated"])
        self.assertEqual(len(ledger_rows), 1)
        self.assertEqual(len(record_rows), 1)
        self.assertFalse(record_rows[0]["artifact_verified"])
        self.assertEqual(api_code, 200)
        self.assertEqual(first["review_state"], "accepted")
        self.assertFalse(first["artifact_verified"])
        self.assertEqual(first["reviewed_record_id"], payload["reviewed_record_id"])
        self.assertEqual(html_code, 200)
        self.assertIn("text/html", html_headers.get("content-type", ""))
        self.assertIn("Review state:", html_body)
        self.assertIn("accepted", html_body)
        self.assertIn("Artifact verified:", html_body)
        self.assertIn("false", html_body)

    def test_search_routes_do_not_mutate_review_or_index_artifacts_after_accept(self) -> None:
        with _WorkbenchDemo() as demo:
            accept_status, _headers, _body = demo.server.post_json(
                "/workbench/api/review/accept",
                {"query": QUERY, "reason": "Workbench P0 local accept demo"},
                token=TOKEN,
            )
            before = demo.hashes()
            api_code, _api_headers, _api_body = demo.server.get(f"/api/search?q={quote(QUERY)}")
            html_code, _html_headers, _html_body = demo.server.get(f"/search?q={quote(QUERY)}")
            after = demo.hashes()

        self.assertEqual(accept_status, 200)
        self.assertEqual(api_code, 200)
        self.assertEqual(html_code, 200)
        self.assertEqual(before, after)

    def test_accept_without_candidate_fails_without_artifacts(self) -> None:
        with _WorkbenchDemo() as demo:
            status, _headers, body = demo.server.post_json(
                "/workbench/api/review/accept",
                {"query": "unmatched local workbench query", "reason": "no candidate"},
                token=TOKEN,
            )

        self.assertEqual(status, 400)
        self.assertIn("no reviewable candidate", json.loads(body)["error"])
        self.assertFalse(demo.ledger_path.exists())
        self.assertFalse(demo.records_path.exists())

    def test_workbench_accept_does_not_report_official_or_public_mutation(self) -> None:
        with _WorkbenchDemo() as demo:
            status, _headers, body = demo.server.post_json(
                "/workbench/api/review/accept",
                {"query": QUERY, "reason": "Workbench P0 local accept demo"},
                token=TOKEN,
            )

        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertFalse(payload["public_index_mutated"])
        self.assertFalse(payload["master_index_mutated"])
        self.assertFalse(payload["official_reviewed_records_mutated"])
        self.assertFalse(payload["gate_counts_mutated"])
        self.assertFalse(payload["canon_mutated"])
        self.assertFalse(payload["release_mutated"])
        self.assertFalse(payload["queue_current_mutated"])
        self.assertFalse(payload["source_fixtures_mutated"])


class _WorkbenchDemo:
    def __init__(self, *, enable_workbench: bool = True) -> None:
        self._enable_workbench = enable_workbench
        self._temp_dir: tempfile.TemporaryDirectory[str] | None = None
        self.server: _RunningServer
        self.index_path: Path
        self.ledger_path: Path
        self.records_path: Path

    def __enter__(self) -> "_WorkbenchDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.index_path = root / "local_search_index.json"
        self.ledger_path = root / "local_review_ledger.jsonl"
        self.records_path = root / "local_reviewed_records.jsonl"
        write_index(self.index_path, build_local_demo_index())
        search_options = LocalSearchOptions(index="local", index_path=str(self.index_path), metadata_fallback="none")
        workbench = (
            WorkbenchService(
                search_service=LocalSearchService(),
                search_options=search_options,
                workbench_options=WorkbenchOptions(
                    enabled=True,
                    token=TOKEN,
                    ledger_path=str(self.ledger_path),
                    records_path=str(self.records_path),
                    reviewer="local_workbench",
                ),
            )
            if self._enable_workbench
            else None
        )
        self.server = _RunningServer(search_options, workbench)
        self.server.__enter__()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.server.__exit__(exc_type, exc, traceback)
        if self._temp_dir is not None:
            self._temp_dir.cleanup()

    def hashes(self) -> dict[str, str]:
        return {
            "index": _sha256(self.index_path),
            "ledger": _sha256_optional(self.ledger_path),
            "records": _sha256_optional(self.records_path),
        }


class _RunningServer:
    def __init__(self, options: LocalSearchOptions, workbench: WorkbenchService | None) -> None:
        self._options = options
        self._workbench = workbench
        self._httpd: LocalSearchHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def __enter__(self) -> "_RunningServer":
        self._httpd = LocalSearchHTTPServer(
            ("127.0.0.1", 0),
            _handler_for(LocalSearchService(), self._options, self._workbench),
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

    def post_json(self, path: str, payload: dict[str, str], *, token: str = "") -> tuple[int, dict[str, str], str]:
        body = json.dumps(payload)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-Eureka-Workbench-Token"] = token
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("POST", path, body=body, headers=headers)
            response = conn.getresponse()
            response_body = response.read().decode("utf-8")
            return response.status, {key.lower(): value for key, value in response.getheaders()}, response_body
        finally:
            conn.close()

    def post_form(self, path: str, payload: dict[str, str], *, token: str = "") -> tuple[int, dict[str, str], str]:
        body = urlencode(payload)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if token:
            headers["X-Eureka-Workbench-Token"] = token
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("POST", path, body=body, headers=headers)
            response = conn.getresponse()
            response_body = response.read().decode("utf-8")
            return response.status, {key.lower(): value for key, value in response.getheaders()}, response_body
        finally:
            conn.close()


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_optional(path: Path) -> str:
    if not path.exists():
        return "missing"
    return _sha256(path)


if __name__ == "__main__":
    unittest.main()
