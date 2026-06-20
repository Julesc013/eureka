from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.web import FetchRequest, HTTPTransportResult, SafeHTTPFetcher
from runtime.connectors.web.dns_guard import DNSGuard
from runtime.connectors.web.robots import AllowAllRobotsClient
from runtime.index.preview import SQLitePreviewIndexStore
from runtime.search.hunt_engine import HuntBudget, HuntEngine, HuntRunStore
from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchBudget, brave_capability_manifest


class HuntEngineTests(unittest.TestCase):
    def test_hunt_paginates_fetches_follows_links_indexes_and_persists_safe_events(self) -> None:
        provider = _FakeProvider()
        pages = {
            "https://example.test/one": b"<html><head><title>Alpha manual</title></head><body>Alpha CT1740 jumper detail <a href='/linked'>linked detail</a></body></html>",
            "https://example.test/two": b"<html><head><title>Beta manual</title></head><body>Beta CT1740 driver note</body></html>",
            "https://example.test/linked": b"<html><head><title>Linked detail</title></head><body>Linked CT1740 reference</body></html>",
        }
        fetcher = SafeHTTPFetcher(
            dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
            robots_client=AllowAllRobotsClient(),
            transport=lambda url, _headers, _timeout, _max_bytes: HTTPTransportResult(200, {"Content-Type": "text/html; charset=utf-8"}, pages[url]),
            clock=lambda: "2026-06-21T00:00:00Z",
        )
        with tempfile.TemporaryDirectory() as temp:
            store = SQLitePreviewIndexStore(Path(temp) / "preview.sqlite")
            engine = HuntEngine(provider_factory=lambda _name: provider, fetcher=fetcher, index_store=store)
            result = engine.run(
                "CT1740 manual",
                run_id="hunt-test",
                budget=HuntBudget(max_queries=1, max_provider_requests=2, max_pages=2, max_fetches=3, max_links_followed=1, count=2),
            )
            search = store.search("reference", limit=5)
            run_store = HuntRunStore(Path(temp) / "run")
            run_store.write(result.persisted_summary, list(result.events))
            pause = run_store.pause()
            resume = run_store.resume()
            cancel = run_store.cancel()
            replayed_events = run_store.events()
            store.close()

        summary = result.persisted_summary
        self.assertEqual(2, summary["provider_request_count"])
        self.assertEqual(3, summary["transient_lead_count"])
        self.assertEqual(2, summary["unique_transient_lead_count"])
        self.assertEqual(1, summary["duplicates_removed"])
        self.assertEqual(3, summary["fetch_attempt_count"])
        self.assertEqual(3, summary["pages_fetched"])
        self.assertEqual(3, summary["documents_indexed"])
        self.assertEqual(1, summary["links_followed"])
        self.assertFalse(summary["provider_results_persisted"])
        self.assertNotIn("Snippet", repr(summary))
        self.assertNotIn("provider_rank", repr(summary))
        self.assertEqual(1, search["result_count"])
        self.assertEqual("paused", pause["state"])
        self.assertEqual("running", resume["state"])
        self.assertEqual("cancelled", cancel["state"])
        self.assertTrue(any(item["event_type"] == "provider_results_received" for item in replayed_events))
        self.assertTrue(any(item["event_type"] == "document_indexed" for item in replayed_events))


class _FakeProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def search(
        self,
        query: str,
        *,
        page: int,
        count: int,
        freshness: str,
        country: str,
        language: str,
        safe_search: str,
        budget_context: WebSearchBudget,
        query_variant: str | None = None,
    ) -> SearchResultPage:
        retention = self.capability_manifest.retention_policy()
        if page == 0:
            leads = (
                _lead(query, page, "one", "https://example.test/one", 1, retention),
                _lead(query, page, "one-duplicate", "https://example.test/one", 2, retention),
            )
            more = True
        else:
            leads = (_lead(query, page, "two", "https://example.test/two", 1, retention),)
            more = False
        return SearchResultPage(
            provider="brave",
            query=query,
            query_variant=query_variant or query,
            page=page,
            count=count,
            retrieved_at="2026-06-21T00:00:00Z",
            results=leads,
            more_results_available=more,
            rate_limit={},
            raw_response_stored=False,
        )


def _lead(query: str, page: int, suffix: str, url: str, rank: int, retention: dict[str, object]) -> SearchLead:
    return SearchLead(
        lead_id=f"lead-{suffix}",
        title=f"Title {suffix}",
        url=url,
        snippet=f"Snippet {suffix}",
        provider="brave",
        provider_rank=rank,
        retrieved_at="2026-06-21T00:00:00Z",
        query=query,
        query_variant=query,
        page=page,
        freshness="",
        retention_policy=retention,
    )


if __name__ == "__main__":
    unittest.main()
