from __future__ import annotations

import http.client
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from urllib.parse import quote

from runtime.local.local_search import LocalSearchOptions, LocalSearchService
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalMetadataFallbackDemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LocalSearchService()

    def test_cli_json_includes_fallback_summary(self) -> None:
        payload = self._run_cli_json("manual for Sound Blaster CT1740")

        self.assertEqual(payload["status"], "candidate")
        self.assertTrue(payload["fallback_used"])
        self.assertEqual(payload["fallback_mode"], "ia_fixture_metadata_fallback")
        self.assertEqual(payload["provider_family"], "ia_fixture")
        self.assertIsInstance(payload["fallback_summary"], dict)
        self.assertFalse(payload["fallback_summary"]["verified"])
        self.assertIn("non_verified_reason", payload["results"][0])

    def test_cli_text_states_fixture_fallback_is_non_verified(self) -> None:
        completed = self._run_cli(
            "driver for Win98",
            "--format",
            "text",
            "--metadata-fallback",
            "ia_fixture",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Fallback mode:", completed.stdout)
        self.assertIn("Fallback used:", completed.stdout)
        self.assertIn("Non-verified reason:", completed.stdout)
        self.assertIn("not verified truth", completed.stdout)

    def test_api_search_includes_fallback_summary(self) -> None:
        with _RunningServer(self.service) as server:
            status, _headers, body = server.get(f"/api/search?q={quote('manual for Sound Blaster CT1740')}")

        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertEqual(payload["fallback_mode"], "ia_fixture_metadata_fallback")
        self.assertTrue(payload["fallback_used"])
        self.assertIn("fallback_summary", payload)
        self.assertFalse(payload["results"][0]["verified"])

    def test_search_html_shows_fallback_and_non_verified_status(self) -> None:
        with _RunningServer(self.service) as server:
            status, headers, body = server.get(f"/search?q={quote('manual for Sound Blaster CT1740')}")

        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("content-type", ""))
        self.assertIn("Fallback mode:", body)
        self.assertIn("Fallback used:", body)
        self.assertIn("Non-verified", body)
        self.assertIn("Source hints:", body)
        self.assertIn("Evidence hints:", body)

    def test_manual_query_is_candidate_or_need_and_not_verified(self) -> None:
        response = self.service.search(
            "manual for Sound Blaster CT1740",
            LocalSearchOptions(metadata_fallback="ia_fixture", show_evidence=True),
        )

        self.assertIn(response["status"], {"candidate", "need"})
        self.assertTrue(response["fallback_used"])
        self.assertFalse(response["fallback_created_verified_truth"])
        self.assertFalse(response["fallback_summary"]["verified"])
        self.assertTrue(all(not result["verified"] for result in response["results"]))

    def test_driver_query_remains_need_or_policy_blocked_without_hardware_details(self) -> None:
        response = self.service.search(
            "driver for Win98",
            LocalSearchOptions(metadata_fallback="ia_fixture", show_evidence=True),
        )

        self.assertIn(response["status"], {"need", "policy_blocked"})
        self.assertIn("hardware vendor", response["missing"])
        self.assertFalse(response["fallback_created_verified_truth"])

    def test_fixture_fallback_does_not_mutate_review_or_indexes(self) -> None:
        response = self.service.search(
            "latest Firefox before XP support ended",
            LocalSearchOptions(metadata_fallback="ia_fixture", show_evidence=True),
        )

        self.assertFalse(response["accepted_truth_created"])
        self.assertFalse(response["reviewed_record_created"])
        self.assertFalse(response["fallback_created_verified_truth"])
        self.assertFalse(response["reviewed_index_mutated"])
        self.assertFalse(response["public_index_mutated"])
        self.assertFalse(response["master_index_mutated"])
        self.assertFalse(response["no_mutation"]["review_ledgers_mutated"])
        self.assertFalse(response["no_mutation"]["truth_promotion_performed"])

    def test_fallback_disabled_path_does_not_call_ia_fixture(self) -> None:
        response = self.service.search(
            "unmatched local metadata fallback demo query",
            LocalSearchOptions(metadata_fallback="none", show_evidence=True),
        )

        self.assertFalse(response["fallback_used"])
        self.assertFalse(response["metadata_fallback_used"])
        self.assertEqual(response["fallback_mode"], "none")
        self.assertEqual(response["provider_call_count"], 0)
        self.assertIsNone(response["fallback_summary"])
        self.assertNotEqual(response["source_path"], "ia_fixture_metadata_fallback")

    def test_p0_smoke_commands_still_pass(self) -> None:
        commands = [
            ["scripts/eureka_search.py", "--all", "--format", "text", "--metadata-fallback", "ia_fixture"],
            [
                "scripts/eureka_search.py",
                "old blue FTP client for XP",
                "--format",
                "text",
                "--metadata-fallback",
                "ia_fixture",
            ],
            ["scripts/run_eureka_local.py", "--smoke", "--metadata-fallback", "ia_fixture"],
        ]
        for command in commands:
            with self.subTest(command=command):
                completed = subprocess.run(
                    [sys.executable, *command],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)

    def _run_cli_json(self, query: str) -> dict[str, object]:
        completed = self._run_cli(query, "--format", "json", "--metadata-fallback", "ia_fixture")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def _run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/eureka_search.py", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )


class _RunningServer:
    def __init__(self, service: LocalSearchService) -> None:
        self._service = service
        self._httpd: LocalSearchHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def __enter__(self) -> "_RunningServer":
        options = LocalSearchOptions(metadata_fallback="ia_fixture")
        self._httpd = LocalSearchHTTPServer(("127.0.0.1", 0), _handler_for(self._service, options))
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


if __name__ == "__main__":
    unittest.main()
