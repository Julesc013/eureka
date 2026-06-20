from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.connectors.web import HTTPTransportResult, SafeHTTPFetcher
from runtime.connectors.web.dns_guard import DNSGuard
from runtime.connectors.web.robots import AllowAllRobotsClient
from runtime.index.preview import SQLitePreviewIndexStore
from runtime.search.foundry import FoundryRunStore, FoundryService, SurveyBudget, circuit_breakers_from_scorecards
from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchBudget, brave_capability_manifest


class FoundryServiceTests(unittest.TestCase):
    def test_plan_makes_no_network_calls_and_run_is_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            service = FoundryService(run_root=Path(temp) / "runs", provider_factory=_forbidden_provider_factory)

            plan = service.plan(["manual for Sound Blaster CT1740"], providers=("brave",), budget=SurveyBudget(maximum_seeds=1))
            result = service.run(plan, run_id="disabled-run").payload

        self.assertFalse(plan.network_enabled)
        self.assertFalse(plan.to_dict()["network_calls_performed"])
        self.assertEqual("disabled", result["status"])
        self.assertFalse(result["network_calls_performed"])
        self.assertFalse(result["reviewed_master_mutation"])
        self.assertFalse(result["public_index_mutation"])

    def test_bounded_run_indexes_observations_and_exports_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index = SQLitePreviewIndexStore(root / "preview.sqlite")
            fetcher = SafeHTTPFetcher(
                dns_guard=DNSGuard(resolver=lambda _host: ("93.184.216.34",)),
                robots_client=AllowAllRobotsClient(),
                transport=_transport,
                clock=lambda: "2026-06-21T00:00:00Z",
            )
            provider = _FoundryFakeProvider()
            service = FoundryService(run_root=root / "runs", index_store=index, provider_factory=lambda _provider: provider, fetcher=fetcher)
            plan = service.plan(
                ["manual for Sound Blaster CT1740"],
                providers=("brave",),
                budget=SurveyBudget(maximum_seeds=1, maximum_queries=1, maximum_provider_requests=1, maximum_fetches=1),
                network_enabled=True,
            )

            result = service.run(plan, run_id="foundry-test", enable_live=True).payload
            stats = index.stats()
            rollback = index.rollback(root / "runs" / "foundry-test" / "exports", result["generation"]["generation_id"])
            index.close()

        self.assertEqual("pass", result["status"])
        self.assertEqual(1, result["completed_seed_count"])
        self.assertEqual(1, result["provider_request_count"])
        self.assertGreaterEqual(result["fetch_attempt_count"], 1)
        self.assertGreaterEqual(result["observation_count"], 1)
        self.assertGreaterEqual(stats["document_count"], 1)
        self.assertTrue(result["scorecards"])
        self.assertGreaterEqual(result["scorecards"][0]["new_preview_document_yield"], 1)
        self.assertTrue(result["review_batch"]["review_items"])
        self.assertIsNone(result["review_batch"]["review_items"][0]["review_decision"])
        self.assertTrue(result["identity_clusters"])
        self.assertEqual("pass", result["generation"]["validation"]["status"])
        self.assertIn(rollback["status"], {"pass", "pass_with_warnings", "rolled_back"})
        self.assertFalse(result["reviewed_master_mutation"])
        self.assertFalse(result["public_index_mutation"])
        self.assertFalse(result["automatic_review_decision"])

    def test_run_store_controls_and_circuit_breaker(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = FoundryRunStore(Path(temp), "control-run")
            paused = store.pause()
            resumed = store.resume()
            cancelled = store.cancel()
            status = store.status()

        self.assertEqual("paused", paused["status"])
        self.assertEqual("running", resumed["status"])
        self.assertEqual("cancelled", cancelled["status"])
        self.assertEqual("cancelled", status["status"])
        breakers = circuit_breakers_from_scorecards([{"provider": "brave", "error_rate": 1.0}])
        self.assertEqual("cooldown", breakers[0]["state"])


def _forbidden_provider_factory(_provider: str) -> object:
    raise AssertionError("Foundry plan/default-disabled run must not call providers")


def _transport(_url: str, _headers: object, _timeout: int, _max_bytes: int) -> HTTPTransportResult:
    body = b"<html><head><title>Foundry Manual</title></head><body>Foundry indexed manual text</body></html>"
    return HTTPTransportResult(200, {"Content-Type": "text/html; charset=utf-8"}, body)


class _FoundryFakeProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def search(self, query: str, **kwargs: object) -> SearchResultPage:
        retention = self.capability_manifest.retention_policy()
        return SearchResultPage(
            provider="brave",
            query=query,
            query_variant=str(kwargs.get("query_variant") or query),
            page=0,
            count=1,
            retrieved_at="2026-06-21T00:00:00Z",
            results=(
                SearchLead(
                    lead_id="foundry-lead",
                    title="Foundry Manual",
                    url="https://example.test/foundry",
                    snippet="Provider snippet remains transient",
                    provider="brave",
                    provider_rank=1,
                    retrieved_at="2026-06-21T00:00:00Z",
                    query=query,
                    query_variant=str(kwargs.get("query_variant") or query),
                    page=0,
                    freshness="",
                    retention_policy=retention,
                ),
            ),
            more_results_available=False,
            rate_limit={},
            raw_response_stored=False,
        )


if __name__ == "__main__":
    unittest.main()
