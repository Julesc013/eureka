from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DATA = REPO_ROOT / "site/dist" / "data"
PUBLIC_SITE = REPO_ROOT / "site/dist"
SITE_DIST = REPO_ROOT / "site" / "dist"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"
SOURCE_DIR = REPO_ROOT / "control" / "inventory" / "sources"
PUBLIC_ALPHA_ROUTES = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
REQUIRED_DATA_FILES = {
    "site_manifest.json",
    "page_registry.json",
    "source_summary.json",
    "eval_summary.json",
    "route_summary.json",
    "search_handoff.json",
    "search_config.json",
    "public_index_summary.json",
    "build_manifest.json",
}


class GeneratedPublicDataSummariesTest(unittest.TestCase):
    def test_public_data_directory_contains_required_static_json(self) -> None:
        self.assertTrue(PUBLIC_DATA.is_dir())
        for name in REQUIRED_DATA_FILES:
            with self.subTest(name=name):
                path = PUBLIC_DATA / name
                self.assertTrue(path.exists())
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema_version"], "0.1.0")

    def test_site_manifest_preserves_static_only_posture(self) -> None:
        manifest = json.loads((PUBLIC_DATA / "site_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["artifact"], "site/dist/data")
        self.assertEqual(manifest["current_static_artifact"], "site/dist")
        self.assertFalse(manifest["contains_live_backend"])
        self.assertFalse(manifest["contains_live_probes"])
        self.assertFalse(manifest["contains_external_observations"])
        self.assertTrue(manifest["no_deployment_claim"])
        self.assertIn("/eureka/", manifest["base_path_targets"])
        self.assertIn("/", manifest["base_path_targets"])

    def test_page_registry_keeps_reserved_routes_honest(self) -> None:
        registry = json.loads((PUBLIC_DATA / "page_registry.json").read_text(encoding="utf-8"))
        by_path = {page["path"]: page for page in registry["pages"]}

        for implemented in ("/", "/status.html", "/sources.html", "/evals.html"):
            with self.subTest(implemented=implemented):
                self.assertEqual(by_path[implemented]["status"], "implemented")
                self.assertTrue(by_path[implemented]["safe_for_static_hosting"])

        for seeded in ("/lite/", "/text/", "/files/", "/demo/"):
            with self.subTest(seeded=seeded):
                self.assertEqual(by_path[seeded]["status"], "static_demo")
                self.assertTrue(by_path[seeded]["safe_for_static_hosting"])

        for reserved in ("/data/", "/api/", "/snapshots/"):
            with self.subTest(reserved=reserved):
                self.assertNotIn(by_path[reserved]["status"], {"implemented", "static_demo"})

    def test_source_summary_marks_placeholders_and_fixtures_honestly(self) -> None:
        summary = json.loads((PUBLIC_DATA / "source_summary.json").read_text(encoding="utf-8"))
        sources = {source["source_id"]: source for source in summary["sources"]}
        expected_ids = {
            json.loads(path.read_text(encoding="utf-8"))["source_id"]
            for path in SOURCE_DIR.glob("*.source.json")
        }

        self.assertEqual(set(sources), expected_ids)
        self.assertTrue(sources["internet-archive-placeholder"]["placeholder"])
        self.assertFalse(sources["internet-archive-placeholder"]["live_supported"])
        self.assertTrue(sources["internet-archive-placeholder"]["live_deferred"])
        self.assertTrue(sources["synthetic-fixtures"]["fixture_backed"])
        self.assertFalse(sources["synthetic-fixtures"]["placeholder"])

    def test_eval_summary_counts_match_current_manual_pending_state(self) -> None:
        summary = json.loads((PUBLIC_DATA / "eval_summary.json").read_text(encoding="utf-8"))

        self.assertEqual(summary["archive_resolution"]["task_count"], 6)
        self.assertEqual(summary["archive_resolution"]["status_counts"]["satisfied"], 6)
        self.assertEqual(summary["search_usefulness"]["query_count"], 64)
        self.assertEqual(summary["search_usefulness"]["status_counts"]["covered"], 5)
        self.assertEqual(summary["search_usefulness"]["status_counts"]["partial"], 40)
        self.assertEqual(summary["search_usefulness"]["source_gap_count"], 10)
        self.assertEqual(summary["search_usefulness"]["capability_gap_count"], 7)
        self.assertEqual(summary["manual_external_baselines"]["global_pending_count"], 192)
        self.assertEqual(summary["manual_external_baselines"]["global_observed_count"], 0)
        self.assertEqual(summary["manual_external_baselines"]["batch_0_pending_count"], 39)
        self.assertEqual(summary["manual_external_baselines"]["batch_0_observed_count"], 0)
        self.assertFalse(summary["contains_external_observations"])

    def test_route_summary_includes_public_alpha_posture_counts(self) -> None:
        summary = json.loads((PUBLIC_DATA / "route_summary.json").read_text(encoding="utf-8"))
        inventory = json.loads(PUBLIC_ALPHA_ROUTES.read_text(encoding="utf-8"))
        route_counts = Counter(route["classification"] for route in inventory["routes"])

        self.assertEqual(summary["route_counts"]["total"], len(inventory["routes"]))
        self.assertEqual(
            summary["route_counts"]["safe_public_alpha"],
            route_counts["safe_public_alpha"],
        )
        self.assertEqual(
            summary["route_counts"]["blocked_public_alpha"],
            route_counts["blocked_public_alpha"],
        )
        self.assertEqual(
            summary["route_counts"]["local_dev_only"],
            route_counts["local_dev_only"],
        )
        self.assertEqual(
            summary["route_counts"]["review_required"],
            route_counts["review_required"],
        )
        self.assertEqual(len(summary["review_required_routes"]), route_counts["review_required"])
        self.assertEqual(len(summary["blocked_routes"]), route_counts["blocked_public_alpha"])
        self.assertTrue(summary["public_alpha_not_production"])

    def test_build_manifest_does_not_claim_deployment_or_ci_provenance(self) -> None:
        manifest = json.loads((PUBLIC_DATA / "build_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["repo"], "Julesc013/eureka")
        self.assertEqual(manifest["commit"], "UNKNOWN_UNTIL_CI")
        self.assertEqual(manifest["built_at"], "UNKNOWN_UNTIL_CI")
        self.assertFalse(manifest["contains_live_backend"])
        self.assertFalse(manifest["contains_live_probes"])
        self.assertFalse(manifest["contains_external_observations"])
        self.assertFalse(manifest["deployment_performed"])
        self.assertEqual(manifest["artifact_root"], "site/dist")

    def test_search_handoff_summary_preserves_static_handoff_posture(self) -> None:
        summary = json.loads((PUBLIC_DATA / "search_handoff.json").read_text(encoding="utf-8"))

        self.assertEqual(summary["search_handoff_status"], "implemented_static_handoff")
        self.assertEqual(summary["hosted_backend_status"], "unavailable")
        self.assertEqual(summary["first_mode"], "local_index_only")
        self.assertIsNone(summary["backend_url"])
        self.assertTrue(summary["local_runtime_available"])
        self.assertTrue(summary["no_hosted_search_claim"])
        self.assertFalse(summary["contains_live_backend"])
        self.assertFalse(summary["contains_live_probes"])
        for key in (
            "live_probes_enabled",
            "downloads_enabled",
            "installs_enabled",
            "uploads_enabled",
            "local_path_search_enabled",
            "arbitrary_url_fetch_enabled",
        ):
            with self.subTest(key=key):
                self.assertFalse(summary["disabled_behaviors"][key])

    def test_site_dist_contains_generated_public_data_and_pages_deploy_site_dist(self) -> None:
        for name in REQUIRED_DATA_FILES:
            with self.subTest(name=name):
                self.assertTrue((SITE_DIST / "data" / name).exists())

        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: site/dist", workflow)
        self.assertTrue(PUBLIC_SITE.exists())

    def test_public_static_pages_link_to_selected_machine_readable_summaries(self) -> None:
        expected_links = {
            "status.html": ["data/site_manifest.json", "data/page_registry.json"],
            "sources.html": ["data/source_summary.json"],
            "evals.html": ["data/eval_summary.json"],
            "search.html": [
                "data/search_handoff.json",
                "data/search_config.json",
                "data/public_index_summary.json",
            ],
            "roadmap.html": ["data/build_manifest.json", "data/route_summary.json"],
        }
        for page, links in expected_links.items():
            text = (PUBLIC_SITE / page).read_text(encoding="utf-8")
            for link in links:
                with self.subTest(page=page, link=link):
                    self.assertIn(link, text)


if __name__ == "__main__":
    unittest.main()
