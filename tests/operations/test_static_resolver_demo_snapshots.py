from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_SITE = REPO_ROOT / "public_site"
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
DEMO_ROOT = PUBLIC_SITE / "demo"
REQUIRED_DEMO_PAGES = {
    "index.html",
    "query-plan-windows-7-apps.html",
    "result-member-driver-inside-support-cd.html",
    "result-firefox-xp.html",
    "result-article-scan.html",
    "absence-example.html",
    "comparison-example.html",
    "source-example.html",
    "eval-summary.html",
}


class _LinkAndScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.script_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.script_count += 1
        for key, value in attrs:
            if key.lower() in {"href", "src"} and value:
                self.links.append(value)


class StaticResolverDemoSnapshotsTest(unittest.TestCase):
    def test_demo_data_exists_and_is_static_only(self) -> None:
        data = json.loads((DEMO_ROOT / "data" / "demo_snapshots.json").read_text(encoding="utf-8"))

        self.assertEqual(data["generated_by"], "scripts/generate_static_resolver_demos.py")
        self.assertGreaterEqual(data["demo_count"], 8)
        self.assertTrue(data["no_live_backend"])
        self.assertTrue(data["no_external_observations"])
        self.assertTrue(data["no_deployment_claim"])
        self.assertFalse(data["contains_live_data"])
        self.assertFalse(data["contains_live_probes"])
        for demo in data["demos"]:
            self.assertEqual(demo["status"], "static_demo")
            self.assertFalse(demo["live_backend_required"])
            self.assertFalse(demo["external_observation_required"])
            self.assertTrue(demo["fixture_backed"])

    def test_required_demo_pages_exist_with_limitations_and_relative_links(self) -> None:
        for page in REQUIRED_DEMO_PAGES:
            path = DEMO_ROOT / page
            with self.subTest(page=page):
                self.assertTrue(path.exists())
                text = path.read_text(encoding="utf-8")
                lowered = text.casefold()
                for phrase in (
                    "static demo snapshot",
                    "fixture-backed",
                    "not live search",
                    "not production",
                ):
                    self.assertIn(phrase, lowered)
                parser = _LinkAndScriptParser()
                parser.feed(text)
                self.assertEqual(parser.script_count, 0)
                for link in parser.links:
                    self.assertFalse(link.startswith("/"), link)
                    self.assertFalse(link.startswith("https://julesc013.github.io/"), link)

    def test_member_demo_includes_member_lineage_lane_and_user_cost(self) -> None:
        text = (DEMO_ROOT / "result-member-driver-inside-support-cd.html").read_text(encoding="utf-8")
        for phrase in (
            "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
            "member:sha256:",
            "Parent target ref",
            "local-bundle-fixtures",
            "inside_bundles",
            "User cost",
            "compatibility",
        ):
            self.assertIn(phrase, text)

    def test_article_demo_includes_parent_page_and_ocr_limitations(self) -> None:
        text = (DEMO_ROOT / "result-article-scan.html").read_text(encoding="utf-8")
        for phrase in (
            "PC Magazine",
            "pages-123-128.ocr.txt",
            "page",
            "OCR-like synthetic fixture text",
            "No real scan parsing",
            "article-scan-recorded-fixtures",
        ):
            self.assertIn(phrase, text)

    def test_source_demo_distinguishes_placeholders_from_active_fixtures(self) -> None:
        text = (DEMO_ROOT / "source-example.html").read_text(encoding="utf-8")
        self.assertIn("local-bundle-fixtures", text)
        self.assertIn("article-scan-recorded-fixtures", text)
        self.assertIn("internet-archive-placeholder", text)
        self.assertIn("placeholder", text.casefold())
        self.assertIn("False", text)

    def test_eval_demo_keeps_external_baselines_pending(self) -> None:
        text = (DEMO_ROOT / "eval-summary.html").read_text(encoding="utf-8")
        self.assertIn("Archive hard eval tasks", text)
        self.assertIn("satisfied", text)
        self.assertIn("Manual baseline pending", text)
        self.assertIn("Manual baseline observed", text)
        self.assertIn("192", text)
        self.assertIn("0", text)

    def test_publication_inventory_covers_demo_routes_and_data(self) -> None:
        registry = json.loads((PUBLICATION_DIR / "page_registry.json").read_text(encoding="utf-8"))
        routes = {route["path"]: route for route in registry["routes"]}
        for route in (
            "/demo/",
            "/demo/query-plan-windows-7-apps.html",
            "/demo/result-member-driver-inside-support-cd.html",
            "/demo/result-firefox-xp.html",
            "/demo/result-article-scan.html",
            "/demo/absence-example.html",
            "/demo/comparison-example.html",
            "/demo/source-example.html",
            "/demo/eval-summary.html",
        ):
            with self.subTest(route=route):
                self.assertEqual(routes[route]["status"], "static_demo")
                self.assertFalse(routes[route]["requires_javascript"])
                self.assertFalse(routes[route]["live_backend_required"])
                self.assertFalse(routes[route]["external_observation_required"])
                self.assertTrue((REPO_ROOT / routes[route]["source_file"]).exists())

        contract = json.loads((PUBLICATION_DIR / "public_data_contract.json").read_text(encoding="utf-8"))
        entries = {entry["path"]: entry for entry in contract["entries"]}
        self.assertEqual(entries["/demo/data/demo_snapshots.json"]["status"], "static_demo")
        self.assertEqual(
            entries["/demo/data/demo_snapshots.json"]["generated_by"],
            "scripts/generate_static_resolver_demos.py",
        )


if __name__ == "__main__":
    unittest.main()
