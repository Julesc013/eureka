from __future__ import annotations

import unittest

from runtime.search.discovery_broker import (
    DiscoveryBroker,
    DiscoveryIntentId,
    ProviderBudgetLedger,
    canonical_url_key,
    classify_query_intent,
)
from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchBudget, brave_capability_manifest


class DiscoveryBrokerTests(unittest.TestCase):
    def test_classifies_common_query_intents(self) -> None:
        self.assertEqual(DiscoveryIntentId.GENERAL_WEB, classify_query_intent("latest matrix release notes"))
        self.assertEqual(DiscoveryIntentId.MANUAL_OR_DOCUMENT, classify_query_intent("manual for Sound Blaster CT1740"))
        self.assertEqual(DiscoveryIntentId.SOURCE_CODE, classify_query_intent("github release archive utility"))
        self.assertEqual(DiscoveryIntentId.URL_DIRECT, classify_query_intent("https://example.test/windows-95-manual"))
        self.assertEqual(DiscoveryIntentId.PACKAGE, classify_query_intent("pypi package release history"))
        self.assertEqual(DiscoveryIntentId.ACADEMIC, classify_query_intent("doi:10.1234/example paper"))

    def test_archive_plan_prefers_local_then_ia_then_broad_web(self) -> None:
        plan = DiscoveryBroker(env={}).plan("manual for Sound Blaster CT1740")

        payload = plan.to_dict()
        stages = payload["stages"]
        self.assertEqual(DiscoveryIntentId.MANUAL_OR_DOCUMENT, payload["intent_id"])
        self.assertEqual("local", stages[0]["provider"]["provider_id"])
        self.assertEqual("internet_archive_metadata", stages[1]["provider"]["provider_id"])
        self.assertEqual("brave", stages[2]["provider"]["provider_id"])
        self.assertEqual("eligible", stages[1]["provider"]["run_policy"])
        self.assertEqual("needs_configuration", stages[2]["provider"]["run_policy"])
        self.assertFalse(plan.public_live_fanout)
        self.assertFalse(plan.reviewed_truth_mutation)
        self.assertFalse(plan.network_calls_performed)
        self.assertEqual(("internet_archive_metadata",), plan.provider_ids())

    def test_general_web_plan_uses_configured_broad_web_provider_after_local(self) -> None:
        plan = DiscoveryBroker(env={"BRAVE_SEARCH_API_KEY": "real-looking-token"}).plan("current web search topic")

        by_provider = {stage.provider_id: stage for stage in plan.stages}
        self.assertEqual(DiscoveryIntentId.GENERAL_WEB, plan.intent.intent_id)
        self.assertEqual("eligible", by_provider["brave"].provider_selection.run_policy)
        self.assertIn("brave", plan.provider_ids())

    def test_local_results_stop_auto_plan_before_provider_stages(self) -> None:
        plan = DiscoveryBroker(env={"BRAVE_SEARCH_API_KEY": "real-looking-token"}).plan(
            "current web search topic",
            local_result_count=2,
        )

        self.assertEqual(1, len(plan.stages))
        self.assertEqual("local", plan.stages[0].provider_id)
        self.assertEqual((), plan.provider_ids())

    def test_url_keys_normalize_tracking_parameters_and_trailing_slashes(self) -> None:
        self.assertEqual(
            "https://example.test/manual?a=1",
            canonical_url_key("HTTPS://Example.Test/manual/?utm_source=x&a=1"),
        )

    def test_execute_fuses_duplicate_leads_and_tracks_cost_yield(self) -> None:
        registry = _FakeRegistry({
            "brave": _LeadProvider("brave", ("https://example.test/page?utm_source=x", "https://example.test/page/")),
        })
        broker = DiscoveryBroker(registry=registry, env={"BRAVE_SEARCH_API_KEY": "real-looking-token"})

        plan = broker.plan("current web search topic")
        result = broker.execute(plan, ProviderBudgetLedger(max_provider_requests=1, count=5))

        payload = result.to_dict()
        self.assertEqual("pass", payload["status"])
        self.assertEqual(("brave",), tuple(registry.calls))
        self.assertEqual(2, payload["fusion"]["lead_count"])
        self.assertEqual(1, payload["fusion"]["unique_lead_count"])
        self.assertEqual(1, payload["fusion"]["duplicate_count"])
        self.assertEqual(1, payload["provider_outcomes"][0]["cost"]["request_count"])
        self.assertGreaterEqual(payload["provider_outcomes"][0]["cost"]["estimated_monetary_cost"], 0)
        self.assertEqual(1, payload["provider_outcomes"][0]["yield"]["unique_lead_count"])
        self.assertFalse(payload["provider_result_payload_persisted"])
        self.assertFalse(payload["reviewed_master_mutation"])
        self.assertFalse(payload["public_index_mutation"])

    def test_progressive_escalation_stops_after_vertical_yield(self) -> None:
        registry = _FakeRegistry({
            "internet_archive_metadata": _LeadProvider("internet_archive_metadata", ("https://archive.org/details/item",)),
            "brave": _LeadProvider("brave", ("https://example.test/broad",)),
        })
        broker = DiscoveryBroker(registry=registry, env={"BRAVE_SEARCH_API_KEY": "real-looking-token"})

        plan = broker.plan("manual for Sound Blaster CT1740")
        result = broker.execute(plan, ProviderBudgetLedger(max_provider_requests=3, count=5, minimum_unique_yield=1))

        self.assertEqual(("internet_archive_metadata",), tuple(registry.calls))
        self.assertEqual("minimum_unique_yield_met", result.stopped_reason)
        self.assertEqual(1, result.fusion.to_dict()["unique_lead_count"])


class _FakeRegistry:
    def __init__(self, providers: dict[str, object]) -> None:
        self.providers = providers
        self.calls: list[str] = []

    def provider(self, provider_id: str) -> object | None:
        self.calls.append(provider_id)
        return self.providers.get(provider_id)


class _LeadProvider:
    capability_manifest = brave_capability_manifest()

    def __init__(self, provider_id: str, urls: tuple[str, ...]) -> None:
        self.provider_id = provider_id
        self.urls = urls

    def search(self, query: str, **kwargs: object) -> SearchResultPage:
        retention = self.capability_manifest.retention_policy()
        return SearchResultPage(
            provider=self.provider_id,
            query=query,
            query_variant=str(kwargs.get("query_variant") or query),
            page=int(kwargs.get("page") or 0),
            count=int(kwargs.get("count") or len(self.urls)),
            retrieved_at="2026-06-21T00:00:00Z",
            results=tuple(
                SearchLead(
                    lead_id=f"lead:{self.provider_id}:{index}",
                    title=f"{self.provider_id} title {index}",
                    url=url,
                    snippet="transient snippet",
                    provider=self.provider_id,
                    provider_rank=index,
                    retrieved_at="2026-06-21T00:00:00Z",
                    query=query,
                    query_variant=str(kwargs.get("query_variant") or query),
                    page=int(kwargs.get("page") or 0),
                    freshness="",
                    retention_policy=retention,
                )
                for index, url in enumerate(self.urls, start=1)
            ),
            more_results_available=False,
            rate_limit={},
            raw_response_stored=False,
        )


if __name__ == "__main__":
    unittest.main()
