from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.web import FetchBudget, FetchPolicy, FetchRequest, HTTPTransportResult, JsonlSourceObservationStore, SafeHTTPFetcher
from runtime.connectors.web.dns_guard import DNSGuard
from runtime.connectors.web.robots import AllowAllRobotsClient, RobotsTxtClient


class SafeWebFetcherTests(unittest.TestCase):
    def test_blocks_private_ip_literal_before_transport(self) -> None:
        calls: list[str] = []
        fetcher = SafeHTTPFetcher(transport=lambda url, _h, _t, _m: calls.append(url) or HTTPTransportResult(200, {}, b""))

        outcome = fetcher.fetch(FetchRequest("http://127.0.0.1/secret"))

        self.assertEqual("blocked", outcome.status)
        self.assertEqual("non_public_network_target", outcome.error.code if outcome.error else "")
        self.assertEqual([], calls)

    def test_blocks_private_dns_resolution_before_transport(self) -> None:
        dns = DNSGuard(resolver=lambda _host: ("10.0.0.10",))
        fetcher = SafeHTTPFetcher(dns_guard=dns, robots_client=AllowAllRobotsClient())

        outcome = fetcher.fetch(FetchRequest("https://example.test/manual"))

        self.assertEqual("blocked", outcome.status)
        self.assertEqual("non_public_network_target", outcome.error.code if outcome.error else "")
        self.assertIn("non_public_ip", outcome.error.message if outcome.error else "")

    def test_revalidates_redirect_target_and_blocks_private_redirect(self) -> None:
        calls: list[str] = []

        def transport(url: str, _headers: object, _timeout: int, _max_bytes: int) -> HTTPTransportResult:
            calls.append(url)
            return HTTPTransportResult(302, {"Location": "http://127.0.0.1/admin"}, b"")

        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=transport,
        )

        outcome = fetcher.fetch(FetchRequest("https://example.test/start"))

        self.assertEqual("blocked", outcome.status)
        self.assertEqual("non_public_network_target", outcome.error.code if outcome.error else "")
        self.assertEqual(["https://example.test/start"], calls)

    def test_honors_and_caches_robots_txt(self) -> None:
        fetch_count = 0

        def robots_fetcher(_robots_url: str) -> tuple[int, str]:
            nonlocal fetch_count
            fetch_count += 1
            return 200, "User-agent: EurekaBot\nDisallow: /private\nAllow: /private/public\n"

        robots = RobotsTxtClient(robots_fetcher)
        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=robots,
            transport=lambda _url, _headers, _timeout, _max_bytes: HTTPTransportResult(200, {"Content-Type": "text/plain"}, b"ok"),
        )

        blocked = fetcher.fetch(FetchRequest("https://example.test/private/file"))
        allowed = fetcher.fetch(FetchRequest("https://example.test/private/public/file"))

        self.assertEqual("blocked", blocked.status)
        self.assertEqual("robots_blocked", blocked.error.code if blocked.error else "")
        self.assertEqual("fetched", allowed.status)
        self.assertEqual(1, fetch_count)

    def test_extracts_html_observation_without_truth_mutation(self) -> None:
        body = b"""<!doctype html>
        <html><head><title>Manual</title><link rel="canonical" href="/canonical"></head>
        <body><h1>Sound Blaster</h1><a href="/driver">Driver</a><script>ignore()</script></body></html>"""

        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda _url, _headers, _timeout, _max_bytes: HTTPTransportResult(
                200,
                {"Content-Type": "text/html; charset=utf-8", "ETag": '"abc"'},
                body,
            ),
            clock=lambda: "2026-06-21T00:00:00Z",
        )

        outcome = fetcher.fetch(FetchRequest("https://example.test/manual", query="manual", run_id="run-1"))
        payload = outcome.to_dict()

        self.assertEqual("fetched", outcome.status)
        self.assertIsNotNone(outcome.observation)
        observation = outcome.observation
        self.assertEqual("https://example.test/canonical", observation.canonical_url)
        self.assertEqual("Manual", observation.extracted_title)
        self.assertIn("Sound Blaster", observation.extracted_text)
        self.assertNotIn("ignore", observation.extracted_text)
        self.assertEqual("https://example.test/driver", observation.outbound_links[0]["target_url"])
        self.assertFalse(payload["reviewed_master_mutation"])
        self.assertFalse(payload["public_index_mutation"])
        self.assertFalse(payload["provider_result_payload_persisted"])

    def test_blocks_unsupported_mime_type(self) -> None:
        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda _url, _headers, _timeout, _max_bytes: HTTPTransportResult(200, {"Content-Type": "application/zip"}, b"PK"),
        )

        outcome = fetcher.fetch(FetchRequest("https://example.test/file.zip"))

        self.assertEqual("blocked", outcome.status)
        self.assertEqual("unsupported_mime_type", outcome.error.code if outcome.error else "")

    def test_blocks_oversized_body(self) -> None:
        policy = FetchPolicy(max_body_bytes=10, max_decompressed_bytes=10)
        fetcher = SafeHTTPFetcher(
            policy=policy,
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda _url, _headers, _timeout, _max_bytes: HTTPTransportResult(200, {"Content-Type": "text/plain"}, b"x" * 11),
        )

        outcome = fetcher.fetch(FetchRequest("https://example.test/large.txt"))

        self.assertEqual("blocked", outcome.status)
        self.assertEqual("body_too_large", outcome.error.code if outcome.error else "")

    def test_rejects_unsupported_scheme_and_port(self) -> None:
        fetcher = SafeHTTPFetcher(robots_client=AllowAllRobotsClient())

        ftp = fetcher.fetch(FetchRequest("ftp://example.test/file"))
        port = fetcher.fetch(FetchRequest("https://example.test:444/path"))

        self.assertEqual("unsupported_scheme", ftp.error.code if ftp.error else "")
        self.assertEqual("unsupported_port", port.error.code if port.error else "")

    def test_rejects_url_credentials_before_transport(self) -> None:
        calls: list[str] = []
        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda url, _headers, _timeout, _max_bytes: calls.append(url) or HTTPTransportResult(200, {"Content-Type": "text/plain"}, b"ok"),
        )

        outcome = fetcher.fetch(FetchRequest("https://user:secret@example.test/manual"))

        self.assertEqual("blocked", outcome.status)
        self.assertEqual("url_credentials_not_allowed", outcome.error.code if outcome.error else "")
        self.assertEqual([], calls)

    def test_records_http_error_without_observation(self) -> None:
        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda _url, _headers, _timeout, _max_bytes: HTTPTransportResult(404, {"Content-Type": "text/plain"}, b"missing"),
        )

        outcome = fetcher.fetch(FetchRequest("https://example.test/missing"))

        self.assertEqual("error", outcome.status)
        self.assertEqual("http_error", outcome.error.code if outcome.error else "")
        self.assertIsNone(outcome.observation)

    def test_enforces_per_host_request_budget(self) -> None:
        fetcher = SafeHTTPFetcher(
            budget=FetchBudget(per_host_request_limit=1),
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda _url, _headers, _timeout, _max_bytes: HTTPTransportResult(200, {"Content-Type": "text/plain"}, b"ok"),
        )

        first = fetcher.fetch(FetchRequest("https://example.test/one"))
        second = fetcher.fetch(FetchRequest("https://example.test/two"))

        self.assertEqual("fetched", first.status)
        self.assertEqual("blocked", second.status)
        self.assertEqual("per_host_budget_exhausted", second.error.code if second.error else "")

    def test_persists_source_observation_without_provider_payload(self) -> None:
        body = b"<html><head><title>Saved</title></head><body>Durable observation</body></html>"
        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda _url, _headers, _timeout, _max_bytes: HTTPTransportResult(200, {"Content-Type": "text/html; charset=utf-8"}, body),
            clock=lambda: "2026-06-21T00:00:00Z",
        )
        outcome = fetcher.fetch(FetchRequest("https://example.test/saved", query="saved manual", run_id="run-fetch"))
        self.assertIsNotNone(outcome.observation)

        with tempfile.TemporaryDirectory() as temp:
            store = JsonlSourceObservationStore(Path(temp) / "observations")
            observation_id = store.put(outcome.observation)
            loaded = store.get(observation_id)
            records = store.list()

        self.assertIsNotNone(loaded)
        self.assertEqual(1, len(records))
        self.assertEqual("https://example.test/saved", loaded["final_url"])
        self.assertEqual("saved manual", loaded["query"])
        self.assertFalse(loaded["provider_result_payload_persisted"])
        self.assertFalse(loaded["retention_policy"]["provider_result_payload_persisted"])
        self.assertNotIn("provider_rank", repr(loaded))


if __name__ == "__main__":
    unittest.main()
