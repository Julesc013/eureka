from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime.local.portable_instance import bootstrap_command, canary_command
from runtime.search.canary import sanitize_canary_evidence, validate_canary_evidence


class LiveCanaryCloseoutTests(unittest.TestCase):
    def test_canary_preflight_reports_readiness_without_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp, patch.dict("os.environ", {"BRAVE_SEARCH_API_KEY": "", "BRAVE_API_KEY": ""}):
            instance = Path(temp) / "instance"
            bootstrap_command(instance=instance, no_demo=True)

            preflight = canary_command("preflight", instance=instance, provider="brave", max_queries=99, max_fetches=99)

            self.assertEqual("pass_with_warnings", preflight["status"])
            self.assertFalse(preflight["provider_configured"])
            self.assertTrue(preflight["instance_ready"])
            self.assertTrue(preflight["database_ready"])
            self.assertFalse(preflight["credential_value_exposed"])
            self.assertFalse(preflight["public_exposure"])
            self.assertFalse(preflight["public_live_fanout"])
            self.assertEqual(3, preflight["budgets"]["max_queries"])
            self.assertEqual(5, preflight["budgets"]["max_fetches"])
            self.assertNotIn("secret", repr(preflight).casefold())

    def test_canary_preflight_classifies_placeholder_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp, patch.dict("os.environ", {"BRAVE_SEARCH_API_KEY": "PASTE_REAL_BRAVE_KEY_HERE"}):
            instance = Path(temp) / "instance"
            bootstrap_command(instance=instance, no_demo=True)

            preflight = canary_command("preflight", instance=instance, provider="brave", live_check=True)

            self.assertEqual("pass_with_warnings", preflight["status"])
            self.assertFalse(preflight["provider_configured"])
            self.assertFalse(preflight["provider_auth_verified"])
            self.assertEqual("invalid_key_placeholder", preflight["provider_health_category"])
            self.assertFalse(preflight["provider_health"]["live_check_performed"])
            self.assertFalse(preflight["network_provider_calls"])
            self.assertNotIn("PASTE_REAL_BRAVE_KEY_HERE", repr(preflight))

    def test_canary_evidence_is_aggregate_and_url_free(self) -> None:
        payload = {
            "status": "pass_with_warnings",
            "live_canary": {
                "status": "waiting",
                "reason": "BRAVE_SEARCH_API_KEY/BRAVE_API_KEY is not configured",
                "provider": "brave",
                "live_provider_configured": False,
                "live_result_count": 0,
                "queries_attempted": 0,
                "transient_lead_count": 0,
                "fetch_attempt_count": 0,
                "pages_fetched": 0,
                "observations_created": 0,
                "documents_indexed": 0,
                "restart_local_search_hits": 0,
                "provider_result_payload_persisted": False,
                "reviewed_master_mutation": False,
                "public_index_mutation": False,
            },
        }

        evidence = sanitize_canary_evidence(payload, query="operator private unseen query", query_label="operator-query-1")

        self.assertEqual("eureka.operator_live_canary_evidence.v0", evidence["schema_version"])
        self.assertEqual("pass", evidence["validation_status"])
        self.assertEqual([], validate_canary_evidence(evidence))
        self.assertEqual("operator-query-1", evidence["query_label"])
        self.assertNotIn("operator private unseen query", repr(evidence))
        self.assertNotIn("http://", repr(evidence))
        self.assertNotIn("https://", repr(evidence))
        self.assertFalse(evidence["provider_result_payload_persisted"])
        self.assertFalse(evidence["credential_value_exposed"])


if __name__ == "__main__":
    unittest.main()
