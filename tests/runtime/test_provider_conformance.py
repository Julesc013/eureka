from __future__ import annotations

import unittest

from runtime.search.hunt_engine import HuntBudget, HuntEngine
from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchBudget, WebSearchProviderError, brave_capability_manifest
from runtime.search.providers import (
    InternetArchiveMetadataAdapter,
    MultiProviderSearchProvider,
    ProviderBudget,
    ProviderRegistry,
    ProviderSearchRequest,
    provider_status,
)


class ProviderConformanceTests(unittest.TestCase):
    def test_internet_archive_metadata_adapter_returns_review_only_leads(self) -> None:
        adapter = InternetArchiveMetadataAdapter(_FakeIACandidateProvider())

        page = adapter.search(ProviderSearchRequest("sound blaster manual", count=2), ProviderBudget()).page

        self.assertEqual("internet_archive_metadata", page.provider)
        self.assertEqual(1, len(page.results))
        lead = page.results[0]
        self.assertEqual("https://archive.org/details/sb-manual", lead.url)
        self.assertEqual("internet_archive_metadata", lead.provider)
        self.assertTrue(lead.retention_policy.persist_urls)
        self.assertFalse(lead.retention_policy.persist_rank)
        self.assertFalse(page.raw_response_stored)

    def test_registry_routes_archive_queries_to_ia_then_broad_web(self) -> None:
        selection = ProviderRegistry(env={}).select("manual for Sound Blaster CT1740", "auto")

        self.assertEqual(("internet_archive_metadata", "brave", "mojeek"), selection.provider_ids)

    def test_multi_provider_partial_failure_and_dedupe(self) -> None:
        provider = MultiProviderSearchProvider((_FailingProvider(), _LeadProvider("internet_archive_metadata", "https://archive.org/details/item")))

        page = provider.search(
            "manual",
            page=0,
            count=5,
            freshness="",
            country="",
            language="",
            safe_search="moderate",
            budget_context=WebSearchBudget(max_provider_requests=1),
        )

        self.assertEqual(1, len(page.results))
        self.assertEqual("1", page.rate_limit["partial_failure_count"])

        both_fail = MultiProviderSearchProvider((_FailingProvider(), _FailingProvider(provider_id="internet_archive_metadata")))
        with self.assertRaises(WebSearchProviderError):
            both_fail.search(
                "manual",
                page=0,
                count=5,
                freshness="",
                country="",
                language="",
                safe_search="moderate",
                budget_context=WebSearchBudget(max_provider_requests=1),
            )

        duplicate = MultiProviderSearchProvider((
            _LeadProvider("brave", "https://example.test/manual/"),
            _LeadProvider("internet_archive_metadata", "https://example.test/manual"),
        ))
        deduped = duplicate.search(
            "manual",
            page=0,
            count=5,
            freshness="",
            country="",
            language="",
            safe_search="moderate",
            budget_context=WebSearchBudget(max_provider_requests=1),
        )
        self.assertEqual(1, len(deduped.results))

    def test_status_does_not_expose_secret_values(self) -> None:
        status = provider_status("brave", env={"BRAVE_SEARCH_API_KEY": "super-secret-token"})

        self.assertTrue(status["configured"])
        self.assertFalse(status["credential_value_exposed"])
        self.assertNotIn("super-secret-token", repr(status))

    def test_hunt_engine_can_use_multi_provider_wrapper(self) -> None:
        provider = MultiProviderSearchProvider((
            _LeadProvider("brave", "https://example.test/manual"),
            _LeadProvider("internet_archive_metadata", "https://archive.org/details/item"),
        ))
        engine = HuntEngine(provider_name="brave,internet_archive_metadata", provider_factory=lambda _provider: provider, fetcher=_NoopFetcher())

        result = engine.run("manual", run_id="multi-provider-hunt", budget=HuntBudget(max_queries=1, max_provider_requests=1, max_pages=1, max_fetches=0))

        self.assertEqual(2, result.persisted_summary["transient_lead_count"])
        self.assertEqual(2, result.persisted_summary["unique_transient_lead_count"])
        self.assertFalse(result.persisted_summary["reviewed_master_mutation"])
        self.assertFalse(result.persisted_summary["public_index_mutation"])


class _FakeIACandidateProvider:
    def search_metadata_candidates(self, query: str, limit: int = 5) -> dict[str, object]:
        return {
            "status": "succeeded",
            "candidate_count": 1,
            "total_http_requests": 1,
            "candidates": [
                {
                    "candidate_id": "ia-meta-candidate:test",
                    "candidate_title": "Sound Blaster manual",
                    "candidate_summary": "Metadata candidate only.",
                    "identifier": "sb-manual",
                    "rank": 1,
                    "source_locator": {"url": "https://archive.org/details/sb-manual"},
                    "download_performed": False,
                    "accepted_truth": False,
                }
            ],
        }


class _LeadProvider:
    def __init__(self, provider_id: str, url: str) -> None:
        self.provider_id = provider_id
        self.url = url
        self.capability_manifest = brave_capability_manifest()

    def search(self, query: str, **kwargs: object) -> SearchResultPage:
        retention = self.capability_manifest.retention_policy()
        return SearchResultPage(
            provider=self.provider_id,
            query=query,
            query_variant=str(kwargs.get("query_variant") or query),
            page=int(kwargs.get("page") or 0),
            count=int(kwargs.get("count") or 1),
            retrieved_at="2026-06-21T00:00:00Z",
            results=(
                SearchLead(
                    lead_id=f"lead:{self.provider_id}",
                    title=f"{self.provider_id} title",
                    url=self.url,
                    snippet="transient snippet",
                    provider=self.provider_id,
                    provider_rank=1,
                    retrieved_at="2026-06-21T00:00:00Z",
                    query=query,
                    query_variant=str(kwargs.get("query_variant") or query),
                    page=int(kwargs.get("page") or 0),
                    freshness="",
                    retention_policy=retention,
                ),
            ),
            more_results_available=False,
            rate_limit={},
            raw_response_stored=False,
        )


class _FailingProvider:
    capability_manifest = brave_capability_manifest()

    def __init__(self, provider_id: str = "brave") -> None:
        self.provider_id = provider_id

    def search(self, query: str, **_kwargs: object) -> SearchResultPage:
        raise WebSearchProviderError("provider failed", provider=self.provider_id, status_code=503)


class _NoopFetcher:
    pass


if __name__ == "__main__":
    unittest.main()
