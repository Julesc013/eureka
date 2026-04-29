from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "public_site"
REQUIRED_JSON_FILES = {
    "action_policy.json",
    "local_cache_privacy_policy.json",
    "publication_contract.json",
    "page_registry.json",
    "client_profiles.json",
    "deployment_targets.json",
    "public_data_contract.json",
    "redirects.json",
    "relay_surface.json",
    "snapshot_contract.json",
}
REQUIRED_STATUS_VALUES = {
    "implemented",
    "recorded_fixture",
    "static_demo",
    "placeholder",
    "planned",
    "deferred",
    "blocked",
    "unsafe_for_public_alpha",
    "removed",
}
REQUIRED_STABILITY_VALUES = {
    "experimental",
    "stable_draft",
    "stable",
    "deprecated",
    "removed",
}
REQUIRED_RESERVED_ROUTES = {
    "/data/",
    "/api/",
    "/snapshots/",
}
REQUIRED_SEEDED_COMPATIBILITY_ROUTES = {
    "/lite/",
    "/text/",
    "/files/",
}
REQUIRED_CLIENT_PROFILES = {
    "modern_web",
    "standard_web",
    "lite_html",
    "text",
    "file_tree",
    "snapshot",
    "native_client",
    "relay",
    "api_client",
}
REQUIRED_PUBLIC_DATA_PATHS = {
    "/data/site_manifest.json",
    "/data/page_registry.json",
    "/data/source_summary.json",
    "/data/eval_summary.json",
    "/data/route_summary.json",
    "/data/build_manifest.json",
    "/files/manifest.json",
    "/files/index.txt",
    "/files/SHA256SUMS",
    "/demo/data/demo_snapshots.json",
}
REQUIRED_GENERATED_PUBLIC_DATA_PATHS = {
    "/data/site_manifest.json",
    "/data/page_registry.json",
    "/data/source_summary.json",
    "/data/eval_summary.json",
    "/data/route_summary.json",
    "/data/build_manifest.json",
}
REQUIRED_FILE_SURFACE_PATHS = {
    "/files/manifest.json",
    "/files/index.txt",
    "/files/SHA256SUMS",
}
REQUIRED_DEMO_ROUTES = {
    "/demo/",
    "/demo/query-plan-windows-7-apps.html",
    "/demo/result-member-driver-inside-support-cd.html",
    "/demo/result-firefox-xp.html",
    "/demo/result-article-scan.html",
    "/demo/absence-example.html",
    "/demo/comparison-example.html",
    "/demo/source-example.html",
    "/demo/eval-summary.html",
}


def load_json(name: str) -> dict:
    return json.loads((PUBLICATION_DIR / name).read_text(encoding="utf-8"))


def ids(values: list) -> set[str]:
    result: set[str] = set()
    for value in values:
        if isinstance(value, str):
            result.add(value)
        elif isinstance(value, dict) and isinstance(value.get("id"), str):
            result.add(value["id"])
    return result


class PublicationInventoryTest(unittest.TestCase):
    def test_publication_inventory_directory_and_json_files_exist(self) -> None:
        self.assertTrue(PUBLICATION_DIR.is_dir())
        self.assertTrue((PUBLICATION_DIR / "README.md").exists())
        for name in REQUIRED_JSON_FILES:
            with self.subTest(name=name):
                self.assertIsInstance(load_json(name), dict)

    def test_publication_contract_records_v0_boundary(self) -> None:
        contract = load_json("publication_contract.json")

        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(contract["contract_id"], "eureka-publication-plane")
        self.assertEqual(contract["status"], "draft")
        self.assertEqual(contract["stability"], "pre_alpha")
        self.assertEqual(contract["current_static_artifact"], "public_site")
        self.assertEqual(contract["future_generator_root"], "site")
        self.assertEqual(contract["future_generated_artifact"], "site/dist")
        self.assertEqual(contract["generator_status"], "implemented")
        self.assertFalse(contract["generated_artifact_deployed"])
        self.assertEqual(contract["snapshot_format_contract_status"], "implemented")
        self.assertEqual(contract["snapshot_contract"], "control/inventory/publication/snapshot_contract.json")
        self.assertEqual(contract["snapshot_seed_example_root"], "snapshots/examples/static_snapshot_v0")
        self.assertIsNone(contract["snapshot_seed_example_public_route"])
        self.assertEqual(contract["action_policy_status"], "implemented_policy_only")
        self.assertEqual(contract["action_policy"], "control/inventory/publication/action_policy.json")
        self.assertEqual(
            contract["local_cache_privacy_policy_status"], "implemented_policy_only"
        )
        self.assertEqual(
            contract["local_cache_privacy_policy"],
            "control/inventory/publication/local_cache_privacy_policy.json",
        )
        self.assertEqual(contract["deploy_artifact_current"], "public_site")
        self.assertEqual(contract["base_path_policy"], "deployment_target_defined")
        self.assertTrue(contract["no_live_backend"])
        self.assertTrue(contract["no_deployment_performed"])
        self.assertTrue(contract["no_external_observations"])
        self.assertEqual(
            contract["public_claim_source_policy"]["rule"],
            "No public claim without a repo source.",
        )

    def test_status_taxonomy_and_route_stability_values_exist(self) -> None:
        contract = load_json("publication_contract.json")

        self.assertTrue(REQUIRED_STATUS_VALUES.issubset(ids(contract["public_status_taxonomy"])))
        self.assertTrue(
            REQUIRED_STABILITY_VALUES.issubset(ids(contract["route_stability_levels"]))
        )

    def test_page_registry_covers_current_public_site_html_pages(self) -> None:
        registry = load_json("page_registry.json")
        routes = registry["routes"]
        source_files = {
            route["source_file"]
            for route in routes
            if isinstance(route.get("source_file"), str)
        }
        current_pages = {
            str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            for path in PUBLIC_SITE.glob("*.html")
        }

        self.assertEqual(current_pages - source_files, set())
        for source_file in source_files:
            with self.subTest(source_file=source_file):
                self.assertTrue((REPO_ROOT / source_file).exists())

    def test_future_reserved_routes_are_registered_but_not_implemented(self) -> None:
        registry = load_json("page_registry.json")
        routes = {route["path"]: route for route in registry["routes"]}

        self.assertTrue(REQUIRED_RESERVED_ROUTES.issubset(routes))
        for route_path in REQUIRED_RESERVED_ROUTES:
            with self.subTest(route_path=route_path):
                route = routes[route_path]
                self.assertNotEqual(route["status"], "implemented")
                self.assertIsNone(route["source_file"])

        self.assertTrue(REQUIRED_SEEDED_COMPATIBILITY_ROUTES.issubset(routes))
        for route_path in REQUIRED_SEEDED_COMPATIBILITY_ROUTES:
            with self.subTest(route_path=route_path):
                route = routes[route_path]
                self.assertEqual(route["status"], "static_demo")
                self.assertEqual(route["stability"], "stable_draft")
                self.assertIsInstance(route["source_file"], str)
                self.assertTrue((REPO_ROOT / route["source_file"]).exists())

        self.assertTrue(REQUIRED_DEMO_ROUTES.issubset(routes))
        for route_path in REQUIRED_DEMO_ROUTES:
            with self.subTest(route_path=route_path):
                route = routes[route_path]
                self.assertEqual(route["status"], "static_demo")
                self.assertEqual(route["stability"], "stable_draft")
                self.assertFalse(route["requires_javascript"])
                self.assertFalse(route["live_backend_required"])
                self.assertFalse(route["external_observation_required"])
                self.assertIsInstance(route["source_file"], str)
                self.assertTrue((REPO_ROOT / route["source_file"]).exists())

    def test_client_profiles_include_required_profiles(self) -> None:
        payload = load_json("client_profiles.json")
        profiles = {profile["id"]: profile for profile in payload["profiles"]}

        self.assertTrue(REQUIRED_CLIENT_PROFILES.issubset(profiles))
        self.assertEqual(
            profiles["standard_web"]["current_support_level"],
            "current public_site static pages",
        )
        self.assertIn("/data/", profiles["api_client"]["intended_path_prefixes"])
        self.assertEqual(profiles["lite_html"]["status"], "static_demo")
        self.assertEqual(profiles["text"]["status"], "static_demo")
        self.assertEqual(profiles["file_tree"]["status"], "static_demo")
        self.assertNotEqual(profiles["native_client"]["status"], "implemented")

    def test_deployment_targets_record_project_pages_and_custom_domain_contracts(self) -> None:
        payload = load_json("deployment_targets.json")
        targets = {target["id"]: target for target in payload["targets"]}

        project = targets["github_pages_project"]
        self.assertEqual(project["kind"], "static")
        self.assertEqual(project["status"], "implemented")
        self.assertEqual(project["artifact_root"], "public_site")
        self.assertEqual(project["generated_artifact_root"], "site/dist")
        self.assertFalse(project["generated_artifact_deployed"])
        self.assertEqual(project["base_path"], "/eureka/")
        self.assertEqual(project["canonical_base_url"], "https://julesc013.github.io/eureka/")
        self.assertTrue(project["requires_base_path_safe_links"])
        self.assertTrue(project["no_backend"])
        self.assertTrue(project["no_live_probes"])
        self.assertTrue(project["no_secrets"])
        self.assertEqual(project["deployment_workflow_path"], ".github/workflows/pages.yml")
        self.assertTrue(project["workflow_configured"])
        self.assertFalse(project["deployment_success_claimed"])
        self.assertEqual(
            project["deployment_status"],
            "workflow_configured_deployment_unverified",
        )

        custom = targets["custom_domain_static"]
        self.assertEqual(custom["status"], "future")
        self.assertEqual(custom["base_path"], "/")
        self.assertTrue(custom["requires_domain_verification"])
        self.assertTrue(custom["no_backend"])

        backend = targets["hosted_public_alpha_backend"]
        self.assertEqual(backend["status"], "future")
        self.assertTrue(backend["no_live_probes_by_default"])

    def test_snapshot_contract_records_seed_only_posture(self) -> None:
        payload = load_json("snapshot_contract.json")

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["snapshot_format_version"], "0.1.0")
        self.assertEqual(payload["status"], "planned")
        self.assertFalse(payload["production_signed_release"])
        self.assertFalse(payload["real_signing_keys_present"])
        self.assertFalse(payload["contains_real_binaries"])
        self.assertFalse(payload["contains_live_backend"])
        self.assertFalse(payload["contains_live_probes"])
        self.assertFalse(payload["contains_external_observations"])
        for required in (
            "SNAPSHOT_MANIFEST.json",
            "BUILD_MANIFEST.json",
            "CHECKSUMS.SHA256",
            "SIGNATURES.README.txt",
            "README_FIRST.txt",
            "index.html",
            "index.txt",
        ):
            self.assertIn(required, payload["required_files"])
        self.assertEqual(payload["signature_policy"]["status"], "placeholder_only")
        self.assertFalse(payload["signature_policy"]["real_private_keys_allowed_in_repo"])

    def test_relay_surface_records_design_only_posture(self) -> None:
        payload = load_json("relay_surface.json")

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["status"], "design_only")
        self.assertTrue(payload["no_relay_implemented"])
        self.assertTrue(payload["no_network_services_implemented"])
        self.assertTrue(payload["no_protocol_servers_implemented"])
        self.assertTrue(payload["public_data_only_by_default"])
        self.assertTrue(payload["private_data_disabled_by_default"])
        self.assertTrue(payload["write_actions_disabled_by_default"])
        self.assertTrue(payload["live_probes_disabled_by_default"])
        self.assertTrue(payload["admin_routes_disabled_for_old_clients"])

        candidates = {item["id"]: item for item in payload["future_protocol_candidates"]}
        for candidate_id in (
            "local_static_http",
            "read_only_ftp_mirror",
            "webdav_read_only",
            "smb_read_only",
            "gopher_experimental",
            "snapshot_mount",
        ):
            with self.subTest(candidate_id=candidate_id):
                self.assertEqual(candidates[candidate_id]["status"], "future_deferred")
                self.assertFalse(candidates[candidate_id]["implemented"])

    def test_public_data_contract_includes_required_files(self) -> None:
        payload = load_json("public_data_contract.json")
        entries = {entry["path"]: entry for entry in payload["entries"]}

        self.assertTrue(REQUIRED_PUBLIC_DATA_PATHS.issubset(entries))
        for path in REQUIRED_GENERATED_PUBLIC_DATA_PATHS:
            with self.subTest(path=path):
                entry = entries[path]
                self.assertEqual(entry["status"], "implemented")
                self.assertEqual(entry["stability"], "stable_draft")
                self.assertEqual(entry["generated_by"], "scripts/generate_public_data_summaries.py")
                self.assertTrue((PUBLIC_SITE / path.removeprefix("/")).exists())
                self.assertIsInstance(entry["source_inputs"], list)
                self.assertTrue(entry["source_inputs"])
                self.assertFalse(entry["contains_live_data"])
                self.assertFalse(entry["contains_external_observations"])
                self.assertTrue(entry["safe_for_static_hosting"])

        for path in REQUIRED_FILE_SURFACE_PATHS:
            with self.subTest(path=path):
                entry = entries[path]
                self.assertEqual(entry["status"], "static_demo")
                self.assertEqual(entry["stability"], "stable_draft")
                self.assertEqual(entry["generated_by"], "scripts/generate_compatibility_surfaces.py")
                self.assertTrue((PUBLIC_SITE / path.removeprefix("/")).exists())
                self.assertFalse(entry["contains_live_data"])
                self.assertFalse(entry["contains_external_observations"])
                self.assertTrue(entry["safe_for_static_hosting"])

        demo_entry = entries["/demo/data/demo_snapshots.json"]
        self.assertEqual(demo_entry["status"], "static_demo")
        self.assertEqual(demo_entry["stability"], "stable_draft")
        self.assertEqual(demo_entry["generated_by"], "scripts/generate_static_resolver_demos.py")
        self.assertTrue((PUBLIC_SITE / "demo" / "data" / "demo_snapshots.json").exists())
        self.assertFalse(demo_entry["contains_live_data"])
        self.assertFalse(demo_entry["contains_external_observations"])
        self.assertTrue(demo_entry["safe_for_static_hosting"])

    def test_redirects_start_empty(self) -> None:
        payload = load_json("redirects.json")

        self.assertEqual(payload["redirects"], [])
        self.assertFalse(payload["supports_server_side_redirects"])

    def test_publication_docs_record_claim_traceability_rule(self) -> None:
        text = (REPO_ROOT / "docs" / "architecture" / "PUBLICATION_PLANE.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("No public claim without a repo source.", text)
        for phrase in (
            "README/status docs",
            "source inventory",
            "route inventory",
            "eval/audit outputs",
            "manual baseline records",
            "static site manifest",
            "publication inventory",
        ):
            self.assertIn(phrase, text)

    def test_action_policy_records_policy_only_posture(self) -> None:
        payload = load_json("action_policy.json")

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["status"], "policy_only")
        self.assertTrue(payload["no_install_automation_implemented"])
        self.assertTrue(payload["no_download_surface_implemented"])
        self.assertTrue(payload["no_malware_scanning_claim"])
        self.assertTrue(payload["no_rights_clearance_claim"])
        self.assertIn("download", payload["future_gated_actions"])
        self.assertIn("install_handoff", payload["future_gated_actions"])
        self.assertIn("package_manager_handoff", payload["future_gated_actions"])
        self.assertIn("execute", payload["future_gated_actions"])
        self.assertIn("silent_install", payload["prohibited_until_policy"])
        self.assertIn("auto_execute", payload["prohibited_until_policy"])
        self.assertIn("privileged_install", payload["prohibited_until_policy"])
        for defaults_name in ("public_alpha_defaults", "static_site_defaults"):
            defaults = payload[defaults_name]
            self.assertFalse(defaults["downloads_enabled"])
            self.assertFalse(defaults["install_handoff_enabled"])
            self.assertFalse(defaults["package_manager_handoff_enabled"])
            self.assertFalse(defaults["execute_enabled"])
            self.assertFalse(defaults["malware_scanning_enabled"])
            self.assertFalse(defaults["rights_clearance_claimed"])

    def test_local_cache_privacy_policy_records_policy_only_posture(self) -> None:
        payload = load_json("local_cache_privacy_policy.json")

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["policy_id"], "eureka-native-local-cache-privacy-policy")
        self.assertEqual(payload["status"], "policy_only")
        self.assertTrue(payload["no_cache_runtime_implemented"])
        self.assertTrue(payload["no_private_ingestion_implemented"])
        self.assertTrue(payload["no_telemetry_implemented"])
        self.assertTrue(payload["no_accounts_implemented"])
        self.assertTrue(payload["no_cloud_sync_implemented"])
        self.assertEqual(payload["privacy_default"], "local_private_off_by_default")
        for behavior in (
            "automatic_local_archive_scan",
            "private_file_ingestion_by_default",
            "private_uploads",
            "telemetry_by_default",
            "analytics_by_default",
            "cloud_sync_by_default",
            "public_path_leakage",
            "credential_export",
            "old_client_private_relay",
        ):
            self.assertIn(behavior, payload["prohibited_behaviors"])
        self.assertFalse(payload["private_cache_policy"]["enabled_by_default"])
        self.assertFalse(payload["telemetry_policy"]["implemented"])
        self.assertFalse(payload["telemetry_policy"]["default_enabled"])
        self.assertFalse(payload["telemetry_policy"]["analytics_enabled"])
        self.assertFalse(payload["telemetry_policy"]["external_uploads_enabled"])

    def test_no_provider_config_or_custom_domain_is_added(self) -> None:
        forbidden_paths = [
            "vercel.json",
            "netlify.toml",
            "fly.toml",
            "render.yaml",
            "wrangler.toml",
            "CNAME",
            "public_site/CNAME",
        ]
        for relative in forbidden_paths:
            with self.subTest(relative=relative):
                self.assertFalse((REPO_ROOT / relative).exists())

    def test_new_publication_docs_do_not_claim_public_deployment(self) -> None:
        paths = [
            REPO_ROOT / "docs" / "architecture" / "PUBLICATION_PLANE.md",
            REPO_ROOT / "docs" / "reference" / "PUBLIC_ROUTE_CONTRACT.md",
            REPO_ROOT / "docs" / "reference" / "PUBLIC_DATA_CONTRACT.md",
            PUBLICATION_DIR / "README.md",
        ]
        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("production ready", text)
                self.assertNotIn("eureka is deployed", text)
                self.assertNotIn("live internet archive search", text)


if __name__ == "__main__":
    unittest.main()
