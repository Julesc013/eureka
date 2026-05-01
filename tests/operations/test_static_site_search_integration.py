from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "static-site-search-integration-v0"
SITE_DIST = REPO_ROOT / "site" / "dist"
REPORT = AUDIT_DIR / "static_site_search_integration_report.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_static_site_search_integration.py"


class _FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0
        self.form_actions: list[str] = []
        self.q_maxlengths: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.casefold(): value for name, value in attrs}
        if tag.casefold() == "script":
            self.script_count += 1
        if tag.casefold() == "form":
            self.form_actions.append(attr.get("action") or "")
        if tag.casefold() == "input" and attr.get("name") == "q":
            self.q_maxlengths.append(int(attr.get("maxlength") or "0"))


class StaticSiteSearchIntegrationOperationTest(unittest.TestCase):
    def test_audit_pack_and_report_exist(self) -> None:
        required = {
            "README.md",
            "INTEGRATION_SUMMARY.md",
            "SEARCH_PAGE_REVIEW.md",
            "LITE_TEXT_FILES_REVIEW.md",
            "SEARCH_CONFIG_REVIEW.md",
            "PUBLIC_INDEX_SUMMARY_REVIEW.md",
            "STATIC_TO_DYNAMIC_HANDOFF.md",
            "BACKEND_CONFIGURATION_STATUS.md",
            "NO_JS_AND_OLD_CLIENT_REVIEW.md",
            "PUBLIC_CLAIM_REVIEW.md",
            "GENERATED_ARTIFACT_REVIEW.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "static_site_search_integration_report.json",
        }
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((AUDIT_DIR / name).is_file())
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["report_id"], "static_site_search_integration_v0")
        self.assertFalse(payload["hosted_backend_verified"])
        self.assertFalse(payload["production_claimed"])

    def test_static_search_surfaces_exist_and_are_no_js(self) -> None:
        for relative in (
            "search.html",
            "lite/search.html",
            "text/search.txt",
            "files/search.README.txt",
            "data/search_config.json",
            "data/public_index_summary.json",
        ):
            with self.subTest(relative=relative):
                path = SITE_DIST / relative
                self.assertTrue(path.is_file())
                if path.suffix in {".html", ".txt"}:
                    self.assertNotIn("<script", path.read_text(encoding="utf-8").casefold())

    def test_backend_unconfigured_mode_is_honest(self) -> None:
        config = json.loads((SITE_DIST / "data" / "search_config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["hosted_backend_status"], "backend_unconfigured")
        self.assertIsNone(config["hosted_backend_url"])
        self.assertFalse(config["hosted_backend_verified"])
        self.assertFalse(config["search_form_enabled"])
        self.assertEqual(config["mode"], "local_index_only")
        for key in (
            "live_probes_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
        ):
            self.assertFalse(config[key], key)

    def test_search_page_form_policy(self) -> None:
        text = (SITE_DIST / "search.html").read_text(encoding="utf-8")
        parser = _FormParser()
        parser.feed(text)
        self.assertEqual(parser.script_count, 0)
        self.assertEqual(parser.form_actions, [""])
        self.assertEqual(parser.q_maxlengths, [160])
        lowered = text.casefold()
        self.assertIn("hosted public search is not configured", lowered)
        self.assertNotIn("hosted public search is live", lowered)
        self.assertIn("data/search_config.json", text)
        self.assertIn("data/public_index_summary.json", text)

    def test_public_index_summary_matches_index_stats(self) -> None:
        summary = json.loads((SITE_DIST / "data" / "public_index_summary.json").read_text(encoding="utf-8"))
        stats = json.loads((REPO_ROOT / "data" / "public_index" / "index_stats.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["document_count"], stats["document_count"])
        self.assertEqual(summary["source_family_counts"], stats["source_family_counts"])
        self.assertFalse(summary["contains_live_data"])
        self.assertFalse(summary["contains_private_data"])
        self.assertFalse(summary["contains_executables"])

    def test_no_private_paths_in_static_search_outputs(self) -> None:
        combined = "\n".join(
            (SITE_DIST / relative).read_text(encoding="utf-8")
            for relative in (
                "search.html",
                "lite/search.html",
                "text/search.txt",
                "files/search.README.txt",
                "data/search_config.json",
                "data/public_index_summary.json",
            )
        )
        for marker in ("D:\\", "C:\\", "/Users/", "/home/", "/tmp/", "/var/"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined)

    def test_validator_and_site_build_pass(self) -> None:
        for command in (
            [sys.executable, str(VALIDATOR)],
            [sys.executable, "site/build.py", "--check"],
            [sys.executable, "site/validate.py"],
        ):
            with self.subTest(command=" ".join(command)):
                completed = subprocess.run(
                    command,
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn("status: valid", completed.stdout)


if __name__ == "__main__":
    unittest.main()
