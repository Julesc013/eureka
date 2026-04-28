from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "public_site"
REQUIRED_JSON_FILES = {
    "publication_contract.json",
    "page_registry.json",
    "client_profiles.json",
    "deployment_targets.json",
    "public_data_contract.json",
    "redirects.json",
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
    "/lite/",
    "/text/",
    "/files/",
    "/data/",
    "/api/",
    "/snapshots/",
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
    "/files/index.txt",
    "/files/SHA256SUMS",
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

    def test_client_profiles_include_required_profiles(self) -> None:
        payload = load_json("client_profiles.json")
        profiles = {profile["id"]: profile for profile in payload["profiles"]}

        self.assertTrue(REQUIRED_CLIENT_PROFILES.issubset(profiles))
        self.assertEqual(
            profiles["standard_web"]["current_support_level"],
            "current public_site static pages",
        )
        self.assertIn("/data/", profiles["api_client"]["intended_path_prefixes"])
        self.assertNotEqual(profiles["native_client"]["status"], "implemented")

    def test_deployment_targets_record_project_pages_and_custom_domain_contracts(self) -> None:
        payload = load_json("deployment_targets.json")
        targets = {target["id"]: target for target in payload["targets"]}

        project = targets["github_pages_project"]
        self.assertEqual(project["kind"], "static")
        self.assertEqual(project["status"], "planned")
        self.assertEqual(project["artifact_root"], "public_site")
        self.assertEqual(project["base_path"], "/eureka/")
        self.assertEqual(project["canonical_base_url"], "https://julesc013.github.io/eureka/")
        self.assertTrue(project["requires_base_path_safe_links"])
        self.assertTrue(project["no_backend"])
        self.assertTrue(project["no_live_probes"])
        self.assertTrue(project["no_secrets"])

        custom = targets["custom_domain_static"]
        self.assertEqual(custom["status"], "future")
        self.assertEqual(custom["base_path"], "/")
        self.assertTrue(custom["requires_domain_verification"])
        self.assertTrue(custom["no_backend"])

        backend = targets["hosted_public_alpha_backend"]
        self.assertEqual(backend["status"], "future")
        self.assertTrue(backend["no_live_probes_by_default"])

    def test_public_data_contract_includes_required_future_files(self) -> None:
        payload = load_json("public_data_contract.json")
        entries = {entry["path"]: entry for entry in payload["entries"]}

        self.assertTrue(REQUIRED_PUBLIC_DATA_PATHS.issubset(entries))
        for path in REQUIRED_PUBLIC_DATA_PATHS:
            with self.subTest(path=path):
                entry = entries[path]
                self.assertNotEqual(entry["status"], "implemented")
                self.assertFalse(entry["contains_live_data"])
                self.assertFalse(entry["contains_external_observations"])
                self.assertTrue(entry["safe_for_static_hosting"])

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

    def test_no_deployment_workflow_or_provider_config_is_added(self) -> None:
        forbidden_paths = [
            ".github/workflows/pages.yml",
            "vercel.json",
            "netlify.toml",
            "fly.toml",
            "render.yaml",
            "wrangler.toml",
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

