from __future__ import annotations

import unittest

from runtime.search.live_service import LiveSearchService, TransientLeadBuffer
from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchBudget, brave_capability_manifest


class _FakeProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def __init__(self) -> None:
        self.queries: list[str] = []

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
        self.queries.append(query_variant or query)
        retention = self.capability_manifest.retention_policy()
        return SearchResultPage(
            provider="brave",
            query=query,
            query_variant=query_variant or query,
            page=page,
            count=count,
            retrieved_at="2026-06-21T00:00:00Z",
            results=(
                SearchLead(
                    lead_id=f"{query}-1",
                    title="Provider title",
                    url="https://provider.example/one",
                    snippet="Provider snippet one",
                    provider="brave",
                    provider_rank=1,
                    retrieved_at="2026-06-21T00:00:00Z",
                    query=query,
                    query_variant=query_variant or query,
                    page=page,
                    freshness=freshness,
                    retention_policy=retention,
                ),
                SearchLead(
                    lead_id=f"{query}-2",
                    title="Provider duplicate",
                    url="https://provider.example/one",
                    snippet="Provider snippet duplicate",
                    provider="brave",
                    provider_rank=2,
                    retrieved_at="2026-06-21T00:00:00Z",
                    query=query,
                    query_variant=query_variant or query,
                    page=page,
                    freshness=freshness,
                    retention_policy=retention,
                ),
            ),
            more_results_available=False,
            rate_limit={},
            raw_response_stored=False,
        )


class LiveSearchServiceTests(unittest.TestCase):
    def test_search_without_provider_fails_honestly(self) -> None:
        service = LiveSearchService(provider_factory=lambda _provider: None)

        payload = service.search("manual", mode="live")

        self.assertEqual("fail", payload["status"])
        self.assertEqual("live_provider_not_configured", payload["error"]["code"])
        self.assertFalse(payload["network_provider_calls"])
        self.assertFalse(payload["provider_results_persisted"])

    def test_hunt_summary_excludes_provider_result_payloads(self) -> None:
        provider = _FakeProvider()
        service = LiveSearchService(provider_factory=lambda _provider: provider, lead_buffer=TransientLeadBuffer(ttl_seconds=60))

        hunt = service.start_hunt(
            "manual for Sound Blaster CT1740",
            run_id="live-hunt-test",
            max_queries=1,
            max_fetches=10,
            count=10,
            timeout_seconds=5,
        )

        self.assertEqual(1, hunt.response["result_count"])
        self.assertEqual("https://provider.example/one", hunt.response["results"][0]["url"])
        self.assertEqual(2, hunt.persisted_summary["transient_lead_count"])
        self.assertEqual(1, hunt.persisted_summary["duplicates_removed"])
        self.assertEqual(
            hunt.persisted_summary["transient_lead_count"] - hunt.persisted_summary["unique_transient_lead_count"],
            hunt.persisted_summary["duplicates_removed"],
        )
        self.assertFalse(hunt.persisted_summary["provider_results_persisted"])
        self.assertFalse(hunt.persisted_summary["provider_raw_response_persisted"])
        self.assertNotIn("results", hunt.persisted_summary)
        self.assertNotIn("unresolved_leads", hunt.persisted_summary)
        persisted = repr(hunt.persisted_summary)
        self.assertNotIn("https://provider.example/one", persisted)
        self.assertNotIn("Provider snippet", persisted)
        self.assertNotIn("provider_rank", persisted)

    def test_transient_lead_buffer_expires_without_disk_state(self) -> None:
        now = [100.0]

        def clock() -> float:
            return now[0]

        buffer = TransientLeadBuffer(ttl_seconds=10, max_leads=2, clock=clock)

        stored = buffer.store_page(
            {
                "results": [
                    {
                        "lead_id": "lead-one",
                        "url": "https://provider.example/one",
                        "snippet": "Provider snippet",
                        "provider_rank": 1,
                    }
                ]
            }
        )

        self.assertEqual(["lead-one"], stored)
        self.assertEqual(1, buffer.active_count())
        self.assertEqual("https://provider.example/one", buffer.get("lead-one")["url"])

        now[0] = 111.0

        self.assertEqual(0, buffer.active_count())
        self.assertIsNone(buffer.get("lead-one"))


if __name__ == "__main__":
    unittest.main()
