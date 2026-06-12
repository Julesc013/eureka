from __future__ import annotations

import http.client
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from urllib.parse import quote

from runtime.local.search_mvp import LocalSearchOptions, LocalSearchService
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for


REPO_ROOT = Path(__file__).resolve().parents[2]


class IAMetadataLiveOptInTests(unittest.TestCase):
    def test_cli_ia_live_without_opt_in_fails_closed(self) -> None:
        completed = _run_python(
            "scripts/eureka_search.py",
            "manual for Sound Blaster CT1740",
            "--format",
            "json",
            "--metadata-fallback",
            "ia_live",
        )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "policy_blocked")
        self.assertEqual(payload["provider_call_count"], 0)
        self.assertFalse(payload["network_used"])
        self.assertIn("--allow-live-metadata", completed.stderr)

    def test_server_smoke_ia_live_without_opt_in_fails_closed(self) -> None:
        completed = _run_python("scripts/run_eureka_local.py", "--smoke", "--metadata-fallback", "ia_live")

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status_summary"]["policy_blocked"], 6)
        self.assertFalse(payload["network_used"])
        self.assertIn("--allow-live-metadata", completed.stderr)

    def test_ia_live_with_opt_in_calls_provider_abstraction(self) -> None:
        provider = _FakeLiveProvider(_candidate_result())
        service = LocalSearchService(live_provider_factory=lambda _options: provider)

        response = service.search("manual for Sound Blaster CT1740", _live_options())

        self.assertEqual(provider.calls, [("manual for Sound Blaster CT1740", 5)])
        self.assertEqual(response["status"], "candidate")
        self.assertTrue(response["fallback_used"])
        self.assertEqual(response["fallback_mode"], "ia_live_metadata_fallback")
        self.assertTrue(response["live_metadata_enabled"])
        self.assertTrue(response["network_used"])
        self.assertEqual(response["budget_used"], 1)

    def test_mocked_live_provider_candidate_need_and_near_miss_are_not_verified(self) -> None:
        cases = [
            (_candidate_result(), "candidate"),
            (_need_result(), "need"),
            (_near_miss_result(), "near_miss"),
        ]
        for result, expected_status in cases:
            with self.subTest(status=expected_status):
                provider = _FakeLiveProvider(result)
                service = LocalSearchService(live_provider_factory=lambda _options, provider=provider: provider)

                response = service.search("obscure manual query", _live_options())

                self.assertEqual(response["status"], expected_status)
                self.assertFalse(response["fallback_created_verified_truth"])
                self.assertFalse(response["fallback_summary"]["verified"])
                self.assertTrue(all(not item["verified"] for item in response["results"]))

    def test_live_timeout_maps_to_unavailable_with_redacted_error(self) -> None:
        provider = _TimeoutLiveProvider()
        service = LocalSearchService(live_provider_factory=lambda _options: provider)

        response = service.search("manual for Sound Blaster CT1740", _live_options())

        self.assertEqual(response["status"], "unavailable")
        self.assertEqual(response["fallback_summary"]["failure_reason"], "source_timeout")
        self.assertFalse(response["network_used"])
        self.assertNotIn("Traceback", json.dumps(response))

    def test_metadata_budget_zero_blocks_provider_call(self) -> None:
        provider = _FakeLiveProvider(_candidate_result())
        service = LocalSearchService(live_provider_factory=lambda _options: provider)

        response = service.search(
            "manual for Sound Blaster CT1740",
            LocalSearchOptions(
                metadata_fallback="ia_live",
                allow_live_metadata=True,
                metadata_timeout_seconds=5,
                metadata_budget=0,
                limit=5,
            ),
        )

        self.assertEqual(provider.calls, [])
        self.assertEqual(response["status"], "unavailable")
        self.assertEqual(response["fallback_summary"]["failure_reason"], "fallback_budget_exceeded")
        self.assertEqual(response["budget_used"], 0)

    def test_no_download_urls_or_actions_are_exposed(self) -> None:
        provider = _FakeLiveProvider(_candidate_result())
        service = LocalSearchService(live_provider_factory=lambda _options: provider)

        response = service.search("manual for Sound Blaster CT1740", _live_options())
        encoded = json.dumps(response).casefold()

        self.assertNotIn("/download/", encoded)
        self.assertNotIn("download_action", encoded)
        self.assertFalse(response["downloads_performed"])
        self.assertFalse(response["source_observations"][0]["download_performed"])

    def test_local_server_refuses_live_metadata_on_non_loopback_host(self) -> None:
        completed = _run_python(
            "scripts/run_eureka_local.py",
            "--host",
            "0.0.0.0",
            "--port",
            "8765",
            "--metadata-fallback",
            "ia_live",
            "--allow-live-metadata",
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("loopback", completed.stderr)

    def test_api_status_reports_live_metadata_disabled_and_enabled(self) -> None:
        with _RunningServer(LocalSearchService(), LocalSearchOptions(metadata_fallback="none")) as server:
            _status, _headers, body = server.get("/api/status")
            disabled = json.loads(body)

        provider = _FakeLiveProvider(_candidate_result())
        service = LocalSearchService(live_provider_factory=lambda _options: provider)
        with _RunningServer(service, _live_options()) as server:
            _status, _headers, body = server.get("/api/status")
            enabled = json.loads(body)

        self.assertFalse(disabled["live_metadata_enabled"])
        self.assertEqual(disabled["provider_family"], "none")
        self.assertFalse(enabled["network_default"])
        self.assertTrue(enabled["live_metadata_enabled"])
        self.assertEqual(enabled["provider_family"], "ia_live")
        self.assertFalse(enabled["public_live_fanout"])

    def test_api_search_and_html_expose_non_verified_live_metadata_status(self) -> None:
        provider = _FakeLiveProvider(_candidate_result())
        service = LocalSearchService(live_provider_factory=lambda _options: provider)

        with _RunningServer(service, _live_options()) as server:
            status, _headers, body = server.get(f"/api/search?q={quote('manual for Sound Blaster CT1740')}")
            api_payload = json.loads(body)
            html_status, html_headers, html_body = server.get(f"/search?q={quote('manual for Sound Blaster CT1740')}")

        self.assertEqual(status, 200)
        self.assertEqual(api_payload["fallback_mode"], "ia_live_metadata_fallback")
        self.assertTrue(api_payload["live_metadata_enabled"])
        self.assertTrue(api_payload["network_used"])
        self.assertFalse(api_payload["results"][0]["verified"])
        self.assertEqual(html_status, 200)
        self.assertIn("text/html", html_headers.get("content-type", ""))
        self.assertIn("Live metadata enabled:", html_body)
        self.assertIn("Network used:", html_body)
        self.assertIn("Non-verified", html_body)

    def test_ia_fixture_behavior_still_passes(self) -> None:
        completed = _run_python(
            "scripts/eureka_search.py",
            "manual for Sound Blaster CT1740",
            "--format",
            "json",
            "--metadata-fallback",
            "ia_fixture",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "candidate")
        self.assertEqual(payload["provider_family"], "ia_fixture")
        self.assertFalse(payload["network_used"])


class _RunningServer:
    def __init__(self, service: LocalSearchService, options: LocalSearchOptions) -> None:
        self._service = service
        self._options = options
        self._httpd: LocalSearchHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def __enter__(self) -> "_RunningServer":
        self._httpd = LocalSearchHTTPServer(("127.0.0.1", 0), _handler_for(self._service, self._options))
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


class _FakeLiveProvider:
    source_id = "internet_archive_metadata"
    source_family = "internet_archive"

    def __init__(self, result: dict[str, object]) -> None:
        self.result = result
        self.calls: list[tuple[str, int]] = []

    def search_metadata_candidates(self, query: str, limit: int) -> dict[str, object]:
        self.calls.append((query, limit))
        result = json.loads(json.dumps(self.result))
        result["query"] = query
        return result


class _TimeoutLiveProvider:
    source_id = "internet_archive_metadata"
    source_family = "internet_archive"

    def search_metadata_candidates(self, query: str, limit: int) -> dict[str, object]:
        raise TimeoutError("network timeout with private detail")


def _candidate_result() -> dict[str, object]:
    return {
        "schema_version": "archive_org_metadata_candidate_search.v0",
        "status": "succeeded",
        "query": "manual for Sound Blaster CT1740",
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_label": "Internet Archive metadata search",
        "candidate_count": 1,
        "candidates": [
            {
                "candidate_id": "ia-live-candidate:test",
                "candidate_title": "Live IA metadata candidate",
                "candidate_summary": "Metadata-only live candidate; review required.",
                "source_id": "internet_archive_metadata",
                "source_family": "internet_archive",
                "source_locator": {
                    "locator_kind": "archive_org_details_page",
                    "url": "https://archive.org/details/example-live-candidate",
                },
                "limitations": ["archive_org_metadata_only", "candidate_not_reviewed_truth", "no_download"],
                "warnings": ["Archive.org metadata candidates require review before promotion."],
            }
        ],
        "total_http_requests": 1,
        "live_call_performed": True,
        "metadata_request_performed": True,
        "source_probe_executed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "accepted_truth": False,
        "review_required": True,
        "limitations": ["archive_org_metadata_only", "candidate_not_reviewed_truth", "no_download"],
        "warnings": ["Metadata search does not grant download permission."],
    }


def _need_result() -> dict[str, object]:
    result = _candidate_result()
    result["candidates"] = []
    result["candidate_count"] = 0
    return result


def _near_miss_result() -> dict[str, object]:
    result = _need_result()
    result["status"] = "near_miss"
    result["failure_reason"] = "metadata_near_miss"
    return result


def _live_options() -> LocalSearchOptions:
    return LocalSearchOptions(
        metadata_fallback="ia_live",
        allow_live_metadata=True,
        metadata_timeout_seconds=5,
        metadata_budget=3,
        limit=5,
        show_evidence=True,
    )


def _run_python(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


if __name__ == "__main__":
    unittest.main()
