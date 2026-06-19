from __future__ import annotations

import hashlib
import http.client
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.parse import quote

from runtime.local.search_index import (
    build_local_demo_index,
    render_index_json,
    validate_index,
    write_index,
)
from runtime.local.local_search import LocalSearchOptions, LocalSearchService
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalSearchIndexBuilderTests(unittest.TestCase):
    def test_eureka_index_build_stats_and_validate_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "local_search_index.json"

            build = _run_python("scripts/eureka_index.py", "build", "--source", "local_demo", "--out", str(index_path))
            stats = _run_python("scripts/eureka_index.py", "stats", "--index", str(index_path), "--json")
            validate = _run_python("scripts/eureka_index.py", "validate", "--index", str(index_path), "--json")

        self.assertEqual(build.returncode, 0, build.stderr)
        self.assertIn("Built Eureka local search index", build.stdout)
        self.assertEqual(stats.returncode, 0, stats.stderr)
        stats_payload = json.loads(stats.stdout)
        self.assertGreaterEqual(stats_payload["document_count"], 6)
        self.assertIn("candidate", stats_payload["status_counts"])
        self.assertIn("internet_archive", stats_payload["source_family_counts"])
        self.assertEqual(validate.returncode, 0, validate.stderr)
        self.assertEqual(json.loads(validate.stdout)["status"], "pass")

    def test_build_output_is_deterministic_for_same_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.json"
            second = Path(temp_dir) / "second.json"

            self.assertEqual(_run_python("scripts/eureka_index.py", "build", "--source", "local_demo", "--out", str(first)).returncode, 0)
            self.assertEqual(_run_python("scripts/eureka_index.py", "build", "--source", "local_demo", "--out", str(second)).returncode, 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))

    def test_index_search_returns_non_verified_result_without_fallback(self) -> None:
        with _TempIndex() as index_path:
            response = LocalSearchService().search(
                "manual for Sound Blaster CT1740",
                LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="ia_fixture"),
            )

        self.assertEqual(response["status"], "candidate")
        self.assertTrue(response["index_results_used"])
        self.assertFalse(response["fallback_used"])
        self.assertEqual(response["provider_call_count"], 0)
        self.assertFalse(response["results"][0]["verified"])
        self.assertFalse(response["fallback_created_verified_truth"])

    def test_index_miss_can_fall_back_to_ia_fixture_when_enabled(self) -> None:
        with _EmptyTempIndex() as index_path:
            response = LocalSearchService().search(
                "manual for Sound Blaster CT1740",
                LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="ia_fixture"),
            )

        self.assertTrue(response["index_loaded"])
        self.assertFalse(response["index_results_used"])
        self.assertEqual(response["index_result_count"], 0)
        self.assertTrue(response["fallback_used"])
        self.assertEqual(response["fallback_mode"], "ia_fixture_metadata_fallback")
        self.assertFalse(response["results"][0]["verified"])

    def test_index_miss_with_fallback_disabled_returns_honest_need_or_unavailable(self) -> None:
        with _EmptyTempIndex() as index_path:
            response = LocalSearchService().search(
                "unmatched local index query",
                LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none"),
            )

        self.assertIn(response["status"], {"need", "unavailable"})
        self.assertFalse(response["fallback_used"])
        self.assertFalse(response["index_results_used"])
        self.assertIn("indexed result or enabled metadata fallback", response["missing"])

    def test_driver_query_remains_need_or_policy_blocked_from_index(self) -> None:
        with _TempIndex() as index_path:
            response = LocalSearchService().search(
                "driver for Win98",
                LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none"),
            )

        self.assertIn(response["status"], {"need", "policy_blocked"})
        self.assertFalse(response["results"][0]["verified"])
        self.assertIn("hardware vendor", response["missing"])

    def test_index_build_does_not_invent_verified_truth(self) -> None:
        index = build_local_demo_index()
        self.assertEqual(validate_index(index), [])
        self.assertFalse(any(document.get("verified") is True for document in index["documents"]))
        self.assertFalse(any(document.get("accepted_truth") is True for document in index["documents"]))

    def test_search_does_not_mutate_index_file(self) -> None:
        with _TempIndex() as index_path:
            before = _sha256(index_path)
            response = LocalSearchService().search(
                "manual for Sound Blaster CT1740",
                LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none"),
            )
            after = _sha256(index_path)

        self.assertTrue(response["index_results_used"])
        self.assertEqual(before, after)
        self.assertFalse(response["reviewed_index_mutated"])
        self.assertFalse(response["public_index_mutated"])
        self.assertFalse(response["master_index_mutated"])
        self.assertFalse(response["no_mutation"]["review_ledgers_mutated"])

    def test_api_status_reports_index_state(self) -> None:
        with _TempIndex() as index_path:
            with _RunningServer(LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none")) as server:
                status, _headers, body = server.get("/api/status")

        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(payload["index_mode"], "local")
        self.assertTrue(payload["index_loaded"])
        self.assertGreaterEqual(payload["index_document_count"], 6)
        self.assertEqual(payload["metadata_fallback"], "none")

    def test_api_search_returns_indexed_results(self) -> None:
        with _TempIndex() as index_path:
            with _RunningServer(LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none")) as server:
                status, _headers, body = server.get(f"/api/search?q={quote('manual for Sound Blaster CT1740')}")

        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(payload["source_path"], "local_search_index")
        self.assertTrue(payload["index_results_used"])
        self.assertFalse(payload["fallback_used"])
        self.assertFalse(payload["results"][0]["verified"])

    def test_search_html_shows_indexed_result_state(self) -> None:
        with _TempIndex() as index_path:
            with _RunningServer(LocalSearchOptions(index="local", index_path=str(index_path), metadata_fallback="none")) as server:
                status, headers, body = server.get(f"/search?q={quote('manual for Sound Blaster CT1740')}")

        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("content-type", ""))
        self.assertIn("Index mode:", body)
        self.assertIn("Index results used:", body)
        self.assertIn("local_search_index", body)
        self.assertIn("Non-verified", body)


class _TempIndex:
    def __enter__(self) -> Path:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self._temp_dir.name) / "local_search_index.json"
        write_index(self.path, build_local_demo_index())
        return self.path

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()


class _EmptyTempIndex:
    def __enter__(self) -> Path:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self._temp_dir.name) / "empty_search_index.json"
        index = build_local_demo_index()
        index["documents"] = []
        index["document_count"] = 0
        index["status_counts"] = {}
        index["source_family_counts"] = {}
        self.path.write_text(render_index_json(index), encoding="utf-8")
        return self.path

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()


class _RunningServer:
    def __init__(self, options: LocalSearchOptions) -> None:
        self._options = options
        self._httpd: LocalSearchHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def __enter__(self) -> "_RunningServer":
        self._httpd = LocalSearchHTTPServer(("127.0.0.1", 0), _handler_for(LocalSearchService(), self._options))
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


def _run_python(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
