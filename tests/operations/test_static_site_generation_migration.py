from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "site"
PUBLIC_SITE = REPO_ROOT / "site/dist"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"
SOURCE_DIR = REPO_ROOT / "control" / "inventory" / "sources"


class _ScriptCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.script_count += 1
        for key, value in attrs:
            if key.lower() in {"href", "src"} and value:
                self.links.append(value)


class StaticSiteGenerationMigrationTest(unittest.TestCase):
    def test_site_tree_exists_with_expected_structure(self) -> None:
        required = [
            "README.md",
            "build.py",
            "validate.py",
            "templates/base.html",
            "templates/page.html",
            "data/README.md",
            "assets/site.css",
            "dist/site_manifest.json",
        ]
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((SITE_ROOT / relative).exists())

    def test_required_page_sources_exist(self) -> None:
        for slug in (
            "index",
            "status",
            "sources",
            "evals",
            "demo-queries",
            "limitations",
            "roadmap",
            "local-quickstart",
        ):
            path = SITE_ROOT / "pages" / f"{slug}.json"
            with self.subTest(path=path):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["slug"], slug)
                self.assertEqual(payload["status"], "implemented")
                self.assertIn("sections", payload)
                self.assertIn("required_claims", payload)

    def test_committed_generated_dist_is_no_js_and_relative_linked(self) -> None:
        for path in sorted((SITE_ROOT / "dist").glob("*.html")):
            parser = _ScriptCounter()
            parser.feed(path.read_text(encoding="utf-8"))
            with self.subTest(path=path):
                self.assertEqual(parser.script_count, 0)
                for link in parser.links:
                    self.assertFalse(link.startswith("/"), link)
                    self.assertFalse(link.startswith("https://julesc013.github.io/"), link)

    def test_generated_sources_page_mentions_current_source_ids(self) -> None:
        sources = (SITE_ROOT / "dist" / "sources.html").read_text(encoding="utf-8")
        for source_path in SOURCE_DIR.glob("*.source.json"):
            source_id = json.loads(source_path.read_text(encoding="utf-8"))["source_id"]
            with self.subTest(source_id=source_id):
                self.assertIn(source_id, sources)

    def test_generated_manifest_preserves_static_only_posture(self) -> None:
        manifest = json.loads((SITE_ROOT / "dist" / "site_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["generated_by"], "site/build.py")
        self.assertEqual(manifest["source_root"], "site")
        self.assertEqual(manifest["artifact_root"], "site/dist")
        self.assertEqual(manifest["deploy_artifact_current"], "site/dist")
        self.assertFalse(manifest["generated_output_deployed"])
        self.assertTrue(manifest["no_deployment_performed"])
        self.assertTrue(manifest["no_network_required"])
        self.assertTrue(manifest["no_live_backend"])
        self.assertTrue(manifest["no_live_probes"])
        self.assertIn("/eureka/", manifest["base_path_targets"])
        self.assertIn("/", manifest["base_path_targets"])

    def test_site_dist_remains_deployment_artifact(self) -> None:
        self.assertTrue(PUBLIC_SITE.exists())
        self.assertTrue((PUBLIC_SITE / "site_manifest.json").exists())
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: site/dist", workflow)

    def test_no_node_or_frontend_build_chain_was_added(self) -> None:
        forbidden = [
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "vite.config.js",
            "next.config.js",
            "tailwind.config.js",
        ]
        for relative in forbidden:
            with self.subTest(relative=relative):
                self.assertFalse((REPO_ROOT / relative).exists())


if __name__ == "__main__":
    unittest.main()
