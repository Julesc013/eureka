from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = REPO_ROOT / "site/dist"
SOURCE_DIR = REPO_ROOT / "control" / "inventory" / "sources"
REQUIRED_PAGES = {
    "index.html",
    "status.html",
    "sources.html",
    "evals.html",
    "demo-queries.html",
    "limitations.html",
    "roadmap.html",
    "local-quickstart.html",
}
PLACEHOLDERS = {
    "internet-archive-placeholder",
    "wayback-memento-placeholder",
    "software-heritage-placeholder",
    "local-files-placeholder",
}


class _ScriptCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.script_count += 1


class PublicStaticSitePackTest(unittest.TestCase):
    def test_site_dist_directory_and_manifest_exist(self) -> None:
        self.assertTrue(SITE_DIR.is_dir())
        manifest = json.loads((SITE_DIR / "site_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["site_pack_id"], "eureka_static_site_dist_v0")
        self.assertTrue(manifest["no_network_required"])
        self.assertTrue(manifest["no_deployment_performed"])
        self.assertEqual(set(manifest["pages"]), REQUIRED_PAGES)

    def test_required_pages_exist_and_do_not_require_javascript(self) -> None:
        for page in REQUIRED_PAGES:
            with self.subTest(page=page):
                path = SITE_DIR / page
                self.assertTrue(path.exists())
                parser = _ScriptCounter()
                parser.feed(path.read_text(encoding="utf-8"))
                self.assertEqual(parser.script_count, 0)

    def test_source_matrix_mentions_current_source_ids_and_placeholders(self) -> None:
        sources_html = (SITE_DIR / "sources.html").read_text(encoding="utf-8")
        source_ids = []
        for path in SOURCE_DIR.glob("*.source.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            source_ids.append(payload["source_id"])

        for source_id in source_ids:
            with self.subTest(source_id=source_id):
                self.assertIn(source_id, sources_html)
        for placeholder in PLACEHOLDERS:
            with self.subTest(placeholder=placeholder):
                start = sources_html.index(placeholder)
                nearby = sources_html[start : start + 400].casefold()
                self.assertIn("placeholder", nearby)

    def test_public_claims_are_honest(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in SITE_DIR.glob("*.html")
        )
        for required in (
            "Python reference backend prototype",
            "not production",
            "no scraping",
            "external baselines pending/manual",
            "placeholders remain placeholders",
        ):
            self.assertIn(required, combined)
        for prohibited in (
            "production ready",
            "live Google search",
            "live Internet Archive search",
            "native app available",
            "Rust production backend",
            "app store",
            "installer automation available",
        ):
            self.assertNotIn(prohibited, combined)

    def test_limitations_include_public_alpha_caveats(self) -> None:
        limitations = (SITE_DIR / "limitations.html").read_text(encoding="utf-8")
        for phrase in (
            "No production hosting",
            "No live crawling",
            "No scraping",
            "No arbitrary local path access",
            "No auth",
            "No production Rust backend",
            "No native GUI apps",
            "No installer automation",
            "No universal compatibility oracle",
            "Fixture-backed evidence is not global truth",
        ):
            self.assertIn(phrase, limitations)


if __name__ == "__main__":
    unittest.main()
