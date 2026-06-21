from __future__ import annotations

import copy
import json
import unittest

from runtime.search.live_web import WebSearchConfigurationError
from runtime.search.provider_policy import DEFAULT_PROVIDER_POLICY_PATH, ProviderPolicyError, load_provider_policy_registry
from runtime.search.providers import ProviderBudget, ProviderRegistry, provider_status


class ProviderPolicyRegistryTests(unittest.TestCase):
    def test_default_registry_contains_brave_mojeek_ia_and_disabled_searxng_policy(self) -> None:
        registry = load_provider_policy_registry()

        self.assertEqual("eureka.discovery_provider_registry.v0", registry.schema_version)
        self.assertFalse(registry.public_live_fanout_enabled)
        self.assertFalse(registry.reviewed_truth_mutation_enabled)
        brave = registry.provider("brave")
        mojeek = registry.provider("mojeek")
        ia = registry.provider("ia")
        searxng = registry.provider("searxng")
        self.assertFalse(brave.retention["persist_urls"])
        self.assertFalse(brave.retention["persist_snippets"])
        self.assertFalse(brave.retention["persist_rank"])
        self.assertFalse(brave.retention["persist_raw_response"])
        self.assertTrue(brave.fetch_handoff_policy["persist_only_independent_source_observation"])
        self.assertFalse(mojeek.retention["persist_urls"])
        self.assertFalse(mojeek.retention["persist_snippets"])
        self.assertFalse(mojeek.retention["persist_rank"])
        self.assertEqual("enabled_when_configured", mojeek.enabled_state)
        self.assertTrue(searxng.enabled_state.startswith("disabled"))
        self.assertTrue(ia.retention["persist_urls"])
        self.assertFalse(ia.retention["persist_rank"])
        self.assertFalse(ia.fetch_handoff_policy["provider_downloads_allowed"])

    def test_provider_status_includes_sanitized_policy_without_secret_values(self) -> None:
        status = provider_status("brave", env={"BRAVE_SEARCH_API_KEY": "super-secret-token"})

        self.assertTrue(status["configured"])
        self.assertFalse(status["credential_value_exposed"])
        self.assertIn("provider_policy_registry", status)
        self.assertNotIn("super-secret-token", repr(status))
        policy = status["provider_policy_registry"]["providers"]["brave"]
        self.assertEqual(["BRAVE_SEARCH_API_KEY", "BRAVE_API_KEY"], policy["credential_env_keys"])
        self.assertFalse(policy["retention"]["persist_raw_response"])

    def test_registry_rejects_missing_retention_and_unsupported_schema(self) -> None:
        payload = _default_policy_payload()
        payload["providers"][0].pop("retention")
        with self.assertRaises(ProviderPolicyError):
            load_provider_policy_registry(payload=payload)

        payload = _default_policy_payload()
        payload["schema_version"] = "future.registry.v99"
        with self.assertRaises(ProviderPolicyError):
            load_provider_policy_registry(payload=payload)

    def test_runtime_activation_rejects_disallowed_mode_and_budget(self) -> None:
        registry = load_provider_policy_registry()

        with self.assertRaises(ProviderPolicyError):
            registry.validate_activation("brave", mode="public_fanout")
        with self.assertRaises(ProviderPolicyError):
            registry.validate_activation("brave", requested_budget={"max_provider_requests": 10_000})
        with self.assertRaises(WebSearchConfigurationError):
            ProviderRegistry(env={}, policy_registry=registry).execution_plan(
                "manual for Sound Blaster CT1740",
                "internet_archive_metadata",
                ProviderBudget(max_provider_requests=5),
            )

    def test_provider_selection_consumes_registry_policy(self) -> None:
        payload = _default_policy_payload()
        for provider in payload["providers"]:
            if provider["provider_id"] == "internet_archive_metadata":
                provider["enabled_state"] = "disabled_by_policy"
        policy_registry = load_provider_policy_registry(payload=payload)

        selection = ProviderRegistry(env={}, policy_registry=policy_registry).select("manual for Sound Blaster CT1740", "auto")

        self.assertEqual(("brave", "mojeek"), selection.provider_ids)
        with self.assertRaises(WebSearchConfigurationError):
            ProviderRegistry(env={}, policy_registry=policy_registry).select("manual", "internet_archive_metadata")


def _default_policy_payload() -> dict[str, object]:
    return copy.deepcopy(json.loads(DEFAULT_PROVIDER_POLICY_PATH.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
