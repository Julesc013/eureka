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

from runtime.local.local_search import LocalSearchOptions, LocalSearchService
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for


REPO_ROOT = Path(__file__).resolve().parents[2]
QUERY = "manual for Sound Blaster CT1740"
REVIEWED_AT = "2026-06-13T00:00:00+10:00"


class ReviewedRecordMaterializationTests(unittest.TestCase):
    def test_candidates_command_lists_deterministic_candidate(self) -> None:
        with _ReviewDemo() as demo:
            completed = _run_python(
                "scripts/eureka_review.py",
                "candidates",
                "--index",
                str(demo.index_path),
                "--query",
                QUERY,
                "--json",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["candidate_count"], 1)
        self.assertIn("ct1740", payload["candidates"][0]["candidate_id"])
        self.assertFalse(payload["candidates"][0]["artifact_verified"])

    def test_accept_creates_idempotent_review_event_and_reviewed_record(self) -> None:
        with _ReviewDemo() as demo:
            first = demo.accept()
            second = demo.accept()
            ledger_rows = _jsonl(demo.ledger_path)
            record_rows = _jsonl(demo.records_path)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        first_payload = json.loads(first.stdout)
        second_payload = json.loads(second.stdout)
        self.assertTrue(first_payload["event_written"])
        self.assertTrue(first_payload["record_written"])
        self.assertTrue(second_payload["idempotent_existing_event"])
        self.assertTrue(second_payload["idempotent_existing_record"])
        self.assertEqual(len(ledger_rows), 1)
        self.assertEqual(len(record_rows), 1)
        self.assertEqual(ledger_rows[0]["review_event_id"], first_payload["review_event_id"])
        self.assertEqual(record_rows[0]["reviewed_record_id"], first_payload["reviewed_record_id"])

    def test_reviewed_record_preserves_evidence_and_is_not_artifact_verified(self) -> None:
        with _ReviewDemo() as demo:
            demo.accept()
            record = _jsonl(demo.records_path)[0]

        self.assertEqual(record["review_state"], "accepted")
        self.assertEqual(record["record_state"], "reviewed")
        self.assertFalse(record["artifact_verified"])
        self.assertFalse(record["accepted_truth"])
        self.assertIn("reason: manual_candidate_available", record["evidence_hints"])
        self.assertIn("synthetic_hard_query_fixture", record["source_hints"])

    def test_index_build_with_reviewed_records_includes_reviewed_metadata(self) -> None:
        with _ReviewDemo() as demo:
            demo.accept()
            reviewed_index = demo.build_reviewed_index()
            stats = _run_python("scripts/eureka_index.py", "stats", "--index", str(reviewed_index), "--json")

        self.assertEqual(stats.returncode, 0, stats.stderr)
        payload = json.loads(stats.stdout)
        self.assertEqual(payload["reviewed_record_count"], 1)
        self.assertEqual(payload["review_state_counts"], {"accepted": 1})
        self.assertEqual(payload["artifact_verified_count"], 0)

    def test_reviewed_record_ranks_above_unreviewed_candidate(self) -> None:
        with _ReviewDemo() as demo:
            demo.accept()
            reviewed_index = demo.build_reviewed_index()
            response = LocalSearchService().search(
                QUERY,
                LocalSearchOptions(index="local", index_path=str(reviewed_index), metadata_fallback="none"),
            )

        self.assertTrue(response["index_results_used"])
        self.assertEqual(response["reviewed_record_count"], 1)
        self.assertEqual(response["artifact_verified_count"], 0)
        self.assertEqual(response["results"][0]["review_state"], "accepted")
        self.assertTrue(response["results"][0]["reviewed_record_id"].startswith("local-reviewed-record:"))
        self.assertFalse(response["results"][0]["artifact_verified"])

    def test_cli_json_shows_review_state_and_no_fallback(self) -> None:
        with _ReviewDemo() as demo:
            demo.accept()
            reviewed_index = demo.build_reviewed_index()
            completed = _run_python(
                "scripts/eureka_search.py",
                QUERY,
                "--format",
                "json",
                "--index",
                "local",
                "--index-path",
                str(reviewed_index),
                "--metadata-fallback",
                "none",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["fallback_used"])
        self.assertEqual(payload["results"][0]["review_state"], "accepted")
        self.assertFalse(payload["results"][0]["artifact_verified"])
        self.assertIn("review_event_id", payload["results"][0])

    def test_cli_text_shows_reviewed_local_accepted_state(self) -> None:
        with _ReviewDemo() as demo:
            demo.accept()
            reviewed_index = demo.build_reviewed_index()
            completed = _run_python(
                "scripts/eureka_search.py",
                QUERY,
                "--format",
                "text",
                "--index",
                "local",
                "--index-path",
                str(reviewed_index),
                "--metadata-fallback",
                "none",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("review state: accepted", completed.stdout)
        self.assertIn("artifact verified: false", completed.stdout)
        self.assertIn("Fallback used: false", completed.stdout)

    def test_api_status_search_and_html_show_reviewed_state(self) -> None:
        with _ReviewDemo() as demo:
            demo.accept()
            reviewed_index = demo.build_reviewed_index()
            with _RunningServer(LocalSearchOptions(index="local", index_path=str(reviewed_index), metadata_fallback="none")) as server:
                status_code, _headers, status_body = server.get("/api/status")
                api_code, _api_headers, api_body = server.get(f"/api/search?q={quote(QUERY)}")
                html_code, html_headers, html_body = server.get(f"/search?q={quote(QUERY)}")

        status_payload = json.loads(status_body)
        api_payload = json.loads(api_body)
        self.assertEqual(status_code, 200)
        self.assertEqual(status_payload["reviewed_record_count"], 1)
        self.assertEqual(status_payload["artifact_verified_count"], 0)
        self.assertEqual(api_code, 200)
        self.assertEqual(api_payload["results"][0]["review_state"], "accepted")
        self.assertFalse(api_payload["results"][0]["artifact_verified"])
        self.assertEqual(html_code, 200)
        self.assertIn("text/html", html_headers.get("content-type", ""))
        self.assertIn("Review state:", html_body)
        self.assertIn("accepted", html_body)
        self.assertIn("Artifact verified:", html_body)
        self.assertIn("false", html_body)

    def test_review_command_does_not_mutate_source_index(self) -> None:
        with _ReviewDemo() as demo:
            before = _sha256(demo.index_path)
            result = demo.accept()
            after = _sha256(demo.index_path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, after)

    def test_search_does_not_mutate_review_or_index_artifacts(self) -> None:
        with _ReviewDemo() as demo:
            demo.accept()
            reviewed_index = demo.build_reviewed_index()
            before = {
                "ledger": _sha256(demo.ledger_path),
                "records": _sha256(demo.records_path),
                "index": _sha256(reviewed_index),
            }
            response = LocalSearchService().search(
                QUERY,
                LocalSearchOptions(index="local", index_path=str(reviewed_index), metadata_fallback="none"),
            )
            after = {
                "ledger": _sha256(demo.ledger_path),
                "records": _sha256(demo.records_path),
                "index": _sha256(reviewed_index),
            }

        self.assertEqual(before, after)
        self.assertFalse(response["reviewed_index_mutated"])
        self.assertFalse(response["public_index_mutated"])
        self.assertFalse(response["master_index_mutated"])
        self.assertFalse(response["accepted_truth_created"])

    def test_invalid_accept_no_candidate_fails_without_records(self) -> None:
        with _ReviewDemo() as demo:
            completed = _run_python(
                "scripts/eureka_review.py",
                "accept",
                "--index",
                str(demo.index_path),
                "--query",
                "unmatched local review query",
                "--ledger",
                str(demo.ledger_path),
                "--records",
                str(demo.records_path),
                "--reviewer",
                "local_demo",
                "--reason",
                "no candidate",
                "--json",
            )
            ledger_exists = demo.ledger_path.exists()
            records_exists = demo.records_path.exists()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("no reviewable candidate", completed.stdout)
        self.assertFalse(ledger_exists)
        self.assertFalse(records_exists)

    def test_invalid_reviewed_records_file_fails_index_build(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid = Path(temp_dir) / "invalid.jsonl"
            output = Path(temp_dir) / "reviewed-index.json"
            invalid.write_text(json.dumps({"review_state": "accepted"}) + "\n", encoding="utf-8")
            completed = _run_python(
                "scripts/eureka_index.py",
                "build",
                "--source",
                "local_demo",
                "--reviewed-records",
                str(invalid),
                "--out",
                str(output),
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("reviewed_record_id is required", completed.stderr)

    def test_fallback_and_live_opt_in_blocking_still_work(self) -> None:
        fixture = _run_python(
            "scripts/eureka_search.py",
            QUERY,
            "--format",
            "json",
            "--metadata-fallback",
            "ia_fixture",
        )
        live_blocked = _run_python(
            "scripts/eureka_search.py",
            QUERY,
            "--format",
            "json",
            "--metadata-fallback",
            "ia_live",
        )

        self.assertEqual(fixture.returncode, 0, fixture.stderr)
        self.assertEqual(json.loads(fixture.stdout)["fallback_mode"], "ia_fixture_metadata_fallback")
        self.assertNotEqual(live_blocked.returncode, 0)
        self.assertEqual(json.loads(live_blocked.stdout)["status"], "policy_blocked")


class _ReviewDemo:
    def __enter__(self) -> "_ReviewDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.index_path = root / "local_search_index.json"
        self.ledger_path = root / "local_review_ledger.jsonl"
        self.records_path = root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = root / "local_search_index.reviewed.json"
        build = _run_python("scripts/eureka_index.py", "build", "--source", "local_demo", "--out", str(self.index_path))
        if build.returncode != 0:
            raise AssertionError(build.stderr)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()

    def accept(self) -> subprocess.CompletedProcess[str]:
        return _run_python(
            "scripts/eureka_review.py",
            "accept",
            "--index",
            str(self.index_path),
            "--query",
            QUERY,
            "--ledger",
            str(self.ledger_path),
            "--records",
            str(self.records_path),
            "--reviewer",
            "local_demo",
            "--reason",
            "P0 local review materialization demo",
            "--reviewed-at",
            REVIEWED_AT,
            "--json",
        )

    def build_reviewed_index(self) -> Path:
        completed = _run_python(
            "scripts/eureka_index.py",
            "build",
            "--source",
            "local_demo",
            "--reviewed-records",
            str(self.records_path),
            "--out",
            str(self.reviewed_index_path),
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)
        return self.reviewed_index_path


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


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
