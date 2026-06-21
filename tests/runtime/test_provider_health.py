from __future__ import annotations

import unittest
from unittest.mock import patch

from runtime.search.live_web import SearchLead, SearchResultPage, WebSearchProviderError, brave_capability_manifest
from runtime.search.provider_health import ProviderHealthState, provider_health_check


class ProviderHealthTests(unittest.TestCase):
    def test_placeholder_key_is_not_configured_and_does_not_call_provider(self) -> None:
        health = provider_health_check("brave", env={"BRAVE_SEARCH_API_KEY": "PASTE_REAL_BRAVE_KEY_HERE"}, live_check=True)

        self.assertFalse(health["configured"])
        self.assertEqual("invalid_key_placeholder", health["category"])
        self.assertEqual(ProviderHealthState.NOT_CONFIGURED, health["state"])
        self.assertFalse(health["live_check_performed"])
        self.assertFalse(health["credential_value_exposed"])

    def test_missing_key_is_classified_without_network(self) -> None:
        health = provider_health_check("brave", env={}, live_check=True)

        self.assertFalse(health["configured"])
        self.assertEqual("missing_key", health["category"])
        self.assertEqual(ProviderHealthState.NOT_CONFIGURED, health["state"])
        self.assertFalse(health["live_check_performed"])

    def test_live_check_reports_results_without_payload(self) -> None:
        with patch("runtime.search.provider_health.provider_from_environment", return_value=_HealthProvider(result_count=1)):
            health = provider_health_check("brave", env={"BRAVE_SEARCH_API_KEY": "real-looking-token"}, live_check=True)

        self.assertTrue(health["configured"])
        self.assertTrue(health["auth_verified"])
        self.assertTrue(health["live_check_performed"])
        self.assertEqual("provider_ok_results_available", health["category"])
        self.assertEqual(ProviderHealthState.HEALTHY, health["state"])
        self.assertEqual(1, health["result_count"])
        self.assertFalse(health["provider_payload_included"])
        self.assertFalse(health["provider_result_payload_persisted"])
        self.assertNotIn("https://example.test", repr(health))

    def test_live_check_maps_auth_errors(self) -> None:
        with patch("runtime.search.provider_health.provider_from_environment", return_value=_AuthErrorProvider()):
            health = provider_health_check("brave", env={"BRAVE_SEARCH_API_KEY": "real-looking-token"}, live_check=True)

        self.assertEqual("provider_auth", health["category"])
        self.assertEqual(ProviderHealthState.AUTHENTICATION_FAILED, health["state"])
        self.assertEqual(401, health["http_status"])
        self.assertFalse(health["auth_verified"])

    def test_live_check_maps_rate_limit_and_permission_states(self) -> None:
        with patch("runtime.search.provider_health.provider_from_environment", return_value=_StatusErrorProvider(403)):
            permission = provider_health_check("brave", env={"BRAVE_SEARCH_API_KEY": "real-looking-token"}, live_check=True)
        with patch("runtime.search.provider_health.provider_from_environment", return_value=_StatusErrorProvider(429)):
            limited = provider_health_check("brave", env={"BRAVE_SEARCH_API_KEY": "real-looking-token"}, live_check=True)

        self.assertEqual(ProviderHealthState.PERMISSION_FAILED, permission["state"])
        self.assertEqual(ProviderHealthState.RATE_LIMITED, limited["state"])


class _HealthProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def __init__(self, *, result_count: int) -> None:
        self.result_count = result_count

    def search(self, query: str, **_kwargs: object) -> SearchResultPage:
        leads = [
            SearchLead(
                lead_id="lead:health:1",
                title="Health result",
                url="https://example.test/health",
                snippet="provider payload",
                provider="brave",
                provider_rank=1,
                retrieved_at="2026-06-21T00:00:00Z",
                query=query,
                query_variant=query,
                page=0,
                freshness="",
                retention_policy=self.capability_manifest.retention_policy(),
            )
        ][: self.result_count]
        return SearchResultPage(
            provider="brave",
            query=query,
            query_variant=query,
            page=0,
            count=1,
            retrieved_at="2026-06-21T00:00:00Z",
            results=tuple(leads),
            more_results_available=False,
            rate_limit={},
            raw_response_stored=False,
        )


class _AuthErrorProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def search(self, _query: str, **_kwargs: object) -> SearchResultPage:
        raise WebSearchProviderError("provider rejected credentials", provider="brave", status_code=401)


class _StatusErrorProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code

    def search(self, _query: str, **_kwargs: object) -> SearchResultPage:
        raise WebSearchProviderError("provider status", provider="brave", status_code=self.status_code)


if __name__ == "__main__":
    unittest.main()
