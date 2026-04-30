from __future__ import annotations

import json
from pathlib import Path
import unittest

from surfaces.web.server.public_alpha_config import load_public_alpha_wrapper_config


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "site/dist"


class LiveProbeGatewayContractTest(unittest.TestCase):
    def test_gateway_inventory_is_disabled_by_default(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_probe_gateway.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["gateway_id"], "eureka-live-probe-gateway")
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["stability"], "experimental")
        self.assertTrue(payload["no_live_probes_implemented"])
        self.assertTrue(payload["no_network_calls_performed"])
        self.assertFalse(payload["enabled_by_default"])
        self.assertFalse(payload["public_alpha_default_enabled"])
        self.assertTrue(payload["requires_operator_signoff"])
        self.assertTrue(payload["requires_abuse_controls"])

    def test_global_limits_disable_fetch_download_and_credentials(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_probe_gateway.json").read_text(encoding="utf-8"))
        limits = payload["global_limits"]

        self.assertLessEqual(limits["max_query_length"], 160)
        self.assertLessEqual(limits["max_total_results"], 20)
        self.assertLessEqual(limits["max_results_per_source"], 10)
        self.assertLessEqual(limits["max_sources_per_request"], 2)
        self.assertFalse(limits["allow_arbitrary_url_fetch"])
        self.assertFalse(limits["allow_downloads"])
        self.assertFalse(limits["allow_write_actions"])
        self.assertFalse(limits["allow_auth_user_credentials"])

    def test_candidate_sources_are_future_disabled(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_probe_gateway.json").read_text(encoding="utf-8"))
        candidates = {item["id"]: item for item in payload["future_candidate_sources"]}

        for source_id in (
            "internet_archive_metadata",
            "internet_archive_item_metadata",
            "wayback_availability",
            "wayback_cdx_metadata",
            "github_releases_metadata",
            "software_heritage_metadata",
            "pypi_package_metadata",
            "npm_package_metadata",
            "wikidata_metadata",
        ):
            with self.subTest(source_id=source_id):
                candidate = candidates[source_id]
                self.assertEqual(candidate["status"], "future_disabled")
                self.assertFalse(candidate["live_supported_now"])
                self.assertTrue(candidate["requires_operator_enable"])
                self.assertTrue(candidate["cache_required"])
                self.assertTrue(candidate["evidence_required"])
                self.assertIn("downloads", candidate["forbidden_modes"])
                self.assertIn("scraping", candidate["forbidden_modes"])
                self.assertIn("arbitrary URL fetching", candidate["forbidden_modes"])

    def test_google_is_manual_baseline_only(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_probe_gateway.json").read_text(encoding="utf-8"))
        candidates = {item["id"] for item in payload["future_candidate_sources"]}
        manual = {item["id"]: item for item in payload["manual_only_sources"]}

        self.assertNotIn("google_web_search", candidates)
        self.assertEqual(manual["google_web_search"]["status"], "manual_external_baseline")
        self.assertFalse(manual["google_web_search"]["live_probe_candidate"])

    def test_policies_require_cache_and_evidence(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_probe_gateway.json").read_text(encoding="utf-8"))

        self.assertTrue(payload["cache_policy"]["cache_required"])
        self.assertTrue(payload["cache_policy"]["cache_first"])
        self.assertTrue(payload["evidence_policy"]["evidence_required"])
        self.assertFalse(payload["download_policy"]["allow_downloads"])
        self.assertFalse(payload["download_policy"]["allow_executable_downloads"])
        self.assertFalse(payload["privacy_policy"]["allow_auth_user_credentials"])
        self.assertFalse(payload["privacy_policy"]["allow_private_account_data"])
        self.assertTrue(payload["circuit_breaker_policy"]["per_source_disable_switch_required"])

    def test_public_alpha_wrapper_reports_live_probes_disabled(self) -> None:
        summary = load_public_alpha_wrapper_config(environ={}).to_summary_dict()

        self.assertFalse(summary["live_probes_enabled"])
        self.assertFalse(summary["live_internet_archive_enabled"])
        self.assertEqual(summary["route_policy"]["live_probes"], "disabled")

    def test_live_backend_handoff_keeps_live_probe_route_blocked(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_backend_routes.json").read_text(encoding="utf-8"))
        routes = {route["path_template"]: route for route in payload["routes"]}
        live_probe = routes["/api/v1/live-probe"]

        self.assertEqual(live_probe["status"], "blocked")
        self.assertFalse(live_probe["static_handoff_allowed"])
        self.assertFalse(live_probe["public_alpha_allowed"])

    def test_static_pages_do_not_claim_live_probes_available(self) -> None:
        prohibited = (
            "live probes are available",
            "live probes are enabled",
            "internet archive live probe is enabled",
        )
        for path in PUBLIC_SITE.rglob("*"):
            if path.suffix.lower() not in {".html", ".txt", ".json"}:
                continue
            text = path.read_text(encoding="utf-8").casefold()
            for phrase in prohibited:
                with self.subTest(path=path, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_docs_say_no_live_probe_implementation(self) -> None:
        contract = (REPO_ROOT / "docs" / "reference" / "LIVE_PROBE_GATEWAY_CONTRACT.md").read_text(
            encoding="utf-8"
        )
        architecture = (REPO_ROOT / "docs" / "architecture" / "LIVE_PROBE_GATEWAY.md").read_text(
            encoding="utf-8"
        )
        policy = (REPO_ROOT / "docs" / "operations" / "LIVE_PROBE_POLICY.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("does not call Internet Archive", contract)
        self.assertIn("Google is not a live probe candidate", contract)
        self.assertIn("does not exist as runtime behavior yet", architecture)
        self.assertIn("No live probe is implemented", policy)


if __name__ == "__main__":
    unittest.main()
