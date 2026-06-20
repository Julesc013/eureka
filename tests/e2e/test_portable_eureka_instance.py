from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.local import portable_instance
from runtime.local.portable_instance import (
    PortableInstanceError,
    bootstrap_command,
    build_portable_paths,
    hunt_command,
    replay_command,
    serve_command,
    status_command,
    test_command,
)
from runtime.search.live_service import LiveHuntResult


class PortableEurekaInstanceE2ETests(unittest.TestCase):
    def test_hunt_replay_status_and_serve_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable eureka"
            bootstrap = bootstrap_command(instance=root, with_demo=True)
            self.assertEqual(bootstrap["status"], "pass")

            hunt = hunt_command("old blue FTP client for XP", instance=root)
            self.assertEqual(hunt["status"], "pass")
            self.assertEqual(hunt["mode"], "synthetic")
            self.assertFalse(hunt["provider_network_calls"])
            self.assertTrue((build_portable_paths(root).run_bundles / hunt["run_id"]).is_dir())

            replay = replay_command(instance=root, run_id=hunt["run_id"], strict=True)
            self.assertEqual(replay["status"], "pass")
            self.assertFalse(replay["review_or_index_mutation"])

            status = status_command(instance=root)
            self.assertEqual(status["status"], "pass")
            self.assertGreaterEqual(status["run_bundles"]["valid"], 1)

            smoke = serve_command(instance=root, port=0, smoke=True, json_output=True)
            self.assertEqual(smoke["status"], "pass")
            self.assertTrue(all(item["ok"] for item in smoke["smoke"]["endpoints"]))
            endpoints = {item["endpoint"]: item for item in smoke["smoke"]["endpoints"]}
            self.assertEqual(302, endpoints["/"]["status_code"])
            self.assertEqual(200, endpoints["/explore"]["status_code"])
            self.assertEqual(200, endpoints["/explore?q=old%20blue%20FTP%20client%20for%20XP"]["status_code"])
            self.assertEqual(200, endpoints["/explore?q=zzzxqvblorp"]["status_code"])
            self.assertFalse(build_portable_paths(root).server_lock.exists())

    def test_bootstrap_defaults_to_no_demo_and_live_serve_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap = bootstrap_command(instance=root)
            self.assertEqual(bootstrap["status"], "pass")
            self.assertFalse(bootstrap["demo_run"]["created"])
            self.assertFalse(bootstrap["preview_index"]["created"])

            smoke = serve_command(instance=root, port=0, smoke=True, json_output=True, live=True)
            self.assertEqual(smoke["status"], "pass")
            endpoints = {item["endpoint"]: item for item in smoke["smoke"]["endpoints"]}
            self.assertEqual(200, endpoints["/"]["status_code"])
            self.assertEqual(200, endpoints["/api/search"]["status_code"])
            self.assertFalse(build_portable_paths(root).server_lock.exists())

    def test_live_hunt_summary_does_not_persist_transient_provider_results(self) -> None:
        class FakeLiveSearchService:
            def start_hunt(
                self,
                query: str,
                *,
                run_id: str,
                max_queries: int,
                max_fetches: int,
                count: int,
                timeout_seconds: int,
            ) -> LiveHuntResult:
                summary = {
                    "schema_version": "eureka.live_hunt_run.v1",
                    "run_id": run_id,
                    "query": query,
                    "mode": "live",
                    "queries_planned": [query],
                    "queries_attempted": [query],
                    "provider": "brave",
                    "providers_checked": ["brave"],
                    "request_count": 1,
                    "transient_lead_count": 1,
                    "unique_transient_lead_count": 1,
                    "new_unique_results": 1,
                    "duplicates_removed": 0,
                    "fetch_attempt_count": 0,
                    "observation_refs": [],
                    "pages_fetched": 0,
                    "max_fetches": max_fetches,
                    "blocked_fetches": 0,
                    "errors": [],
                    "near_miss_count": 0,
                    "unresolved_lead_count": 1,
                    "provider_results_persisted": False,
                    "provider_result_payload_fields_persisted": [],
                    "provider_raw_response_persisted": False,
                    "provider_results_are_transient": True,
                    "fetch_milestone_complete": False,
                    "persistent_preview_index_update_complete": False,
                }
                response = {
                    **summary,
                    "status": "pass",
                    "results": [
                        {
                            "state": "LIVE - UNREVIEWED",
                            "title": "Provider title",
                            "url": "https://provider.example/result",
                            "snippet": "Provider snippet",
                            "provider": "brave",
                            "provider_rank": 1,
                        }
                    ],
                    "unresolved_leads": [
                        {
                            "title": "Provider title",
                            "url": "https://provider.example/result",
                            "snippet": "Provider snippet",
                            "provider_rank": 1,
                        }
                    ],
                    "result_count": 1,
                    "network_provider_calls": True,
                }
                return LiveHuntResult(response=response, persisted_summary=summary)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap_command(instance=root)
            original = portable_instance.LiveSearchService
            portable_instance.LiveSearchService = FakeLiveSearchService  # type: ignore[assignment]
            try:
                result = hunt_command("manual", instance=root, live=True, max_queries=1, max_fetches=1)
            finally:
                portable_instance.LiveSearchService = original  # type: ignore[assignment]

            self.assertEqual("pass", result["status"])
            self.assertEqual("https://provider.example/result", result["results"][0]["url"])
            summary_path = build_portable_paths(root).run_bundles / result["run_id"] / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary_text = json.dumps(summary, sort_keys=True)
            self.assertFalse(summary["provider_results_persisted"])
            self.assertNotIn("results", summary)
            self.assertNotIn("unresolved_leads", summary)
            self.assertNotIn("https://provider.example/result", summary_text)
            self.assertNotIn("Provider snippet", summary_text)
            self.assertNotIn("provider_rank", summary_text)

    def test_live_shadow_and_path_traversal_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap_command(instance=root, no_demo=True)
            with self.assertRaises(PortableInstanceError):
                hunt_command("query", instance=root, mode="live-shadow")
            with self.assertRaises(PortableInstanceError):
                replay_command(instance=root, run_id="../escape")

    def test_oracle_case_writes_under_instance_eval_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap_command(instance=root, no_demo=True)
            result = test_command(instance=root, case="boundary_privacy_canaries")
            self.assertEqual(result["status"], "pass")
            self.assertTrue(str(result["result_path"]).startswith("run/e2e-reference/eval/"))
            self.assertFalse(result["full_unittest_discovery"])
            self.assertFalse(result["oracle"]["network_provider_calls"])


if __name__ == "__main__":
    unittest.main()
