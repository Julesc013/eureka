from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_SITE = REPO_ROOT / "site/dist"
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


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


class LiteTextFilesSurfacesTest(unittest.TestCase):
    def test_lite_surface_exists_without_scripts_or_root_relative_links(self) -> None:
        for relative in (
            "lite/index.html",
            "lite/sources.html",
            "lite/evals.html",
            "lite/demo-queries.html",
            "lite/search.html",
            "lite/limitations.html",
        ):
            path = PUBLIC_SITE / relative
            with self.subTest(relative=relative):
                self.assertTrue(path.exists())
                parser = _LinkAndScriptParser()
                parser.feed(path.read_text(encoding="utf-8"))
                self.assertEqual(parser.script_count, 0)
                for link in parser.links:
                    self.assertFalse(link.startswith("/"), link)
                    self.assertFalse(link.startswith("https://julesc013.github.io/"), link)
                self.assertIn("No JavaScript", path.read_text(encoding="utf-8"))

    def test_text_surface_contains_status_and_limitations(self) -> None:
        index = (PUBLIC_SITE / "text" / "index.txt").read_text(encoding="utf-8")
        limitations = (PUBLIC_SITE / "text" / "limitations.txt").read_text(encoding="utf-8")

        self.assertIn("Python reference backend prototype", index)
        self.assertIn("not production", index)
        self.assertIn("not live search", index)
        self.assertIn("no executable downloads or mirrors", limitations)
        self.assertIn("no public /snapshots/ route", limitations)
        self.assertIn("production signed snapshots yet", limitations)

    def test_files_surface_manifest_and_checksums_are_static_only(self) -> None:
        manifest = json.loads((PUBLIC_SITE / "files" / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["status"], "static_demo")
        self.assertFalse(manifest["contains_live_backend"])
        self.assertFalse(manifest["contains_live_probes"])
        self.assertFalse(manifest["contains_live_data"])
        self.assertFalse(manifest["contains_external_observations"])
        self.assertFalse(manifest["contains_executable_downloads"])
        self.assertFalse(manifest["downloads_available"])
        self.assertTrue((PUBLIC_SITE / "files" / "SHA256SUMS").exists())

    def test_surfaces_reference_public_data_summaries(self) -> None:
        combined = "\n".join(
            [
                (PUBLIC_SITE / "lite" / "index.html").read_text(encoding="utf-8"),
                (PUBLIC_SITE / "text" / "index.txt").read_text(encoding="utf-8"),
                (PUBLIC_SITE / "files" / "index.txt").read_text(encoding="utf-8"),
            ]
        )
        for relative in (
            "data/source_summary.json",
            "data/eval_summary.json",
            "data/route_summary.json",
            "data/search_handoff.json",
            "data/search_config.json",
            "data/public_index_summary.json",
        ):
            with self.subTest(relative=relative):
                self.assertIn(relative, combined)

    def test_no_real_binaries_or_executable_downloads_are_present(self) -> None:
        forbidden_suffixes = {".exe", ".msi", ".dmg", ".pkg", ".zip", ".tar", ".gz", ".7z"}
        for path in (PUBLIC_SITE / "lite").rglob("*"):
            self.assertNotIn(path.suffix.casefold(), forbidden_suffixes)
        for path in (PUBLIC_SITE / "text").rglob("*"):
            self.assertNotIn(path.suffix.casefold(), forbidden_suffixes)
        for path in (PUBLIC_SITE / "files").rglob("*"):
            self.assertNotIn(path.suffix.casefold(), forbidden_suffixes)

    def test_publication_inventory_marks_seed_surfaces_only(self) -> None:
        registry = json.loads((PUBLICATION_DIR / "page_registry.json").read_text(encoding="utf-8"))
        routes = {route["path"]: route for route in registry["routes"]}

        for route in ("/lite/", "/text/", "/files/"):
            with self.subTest(route=route):
                self.assertEqual(routes[route]["status"], "static_demo")
                self.assertEqual(routes[route]["stability"], "stable_draft")
                self.assertTrue((REPO_ROOT / routes[route]["source_file"]).exists())

        self.assertNotEqual(routes["/snapshots/"]["status"], "static_demo")
        self.assertNotEqual(routes["/api/"]["status"], "static_demo")
        self.assertFalse((PUBLIC_SITE / "snapshots").exists())

    def test_client_profiles_seed_only_current_support(self) -> None:
        profiles = {
            profile["id"]: profile
            for profile in json.loads((PUBLICATION_DIR / "client_profiles.json").read_text(encoding="utf-8"))["profiles"]
        }

        self.assertEqual(profiles["lite_html"]["status"], "static_demo")
        self.assertEqual(profiles["text"]["status"], "static_demo")
        self.assertEqual(profiles["file_tree"]["status"], "static_demo")
        self.assertNotEqual(profiles["snapshot"]["status"], "static_demo")
        self.assertNotEqual(profiles["native_client"]["status"], "static_demo")
        self.assertNotEqual(profiles["relay"]["status"], "static_demo")


if __name__ == "__main__":
    unittest.main()
