from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFF = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_handoff.json"
SAFETY = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_safety.json"
SITE_DIST = REPO_ROOT / "site" / "dist"


class _InputParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0
        self.q_maxlengths: list[int] = []
        self.form_actions: list[str] = []
        self.disabled_buttons = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.casefold(): value for name, value in attrs}
        folded_tag = tag.casefold()
        if folded_tag == "script":
            self.script_count += 1
        if folded_tag == "form":
            self.form_actions.append(attr.get("action") or "")
        if folded_tag == "input" and attr.get("name") == "q":
            self.q_maxlengths.append(int(attr.get("maxlength") or "0"))
        if folded_tag == "button" and "disabled" in attr:
            self.disabled_buttons += 1


class PublicSearchStaticHandoffOperationTest(unittest.TestCase):
    def test_handoff_inventory_records_unconfigured_hosted_backend(self) -> None:
        payload = _load_json(HANDOFF)

        self.assertEqual(payload["status"], "implemented_static_handoff")
        self.assertEqual(payload["static_artifact"], "site/dist")
        self.assertEqual(payload["runtime_dependency"], "local_public_search_runtime_v0")
        self.assertEqual(payload["hosted_backend_status"], "unavailable")
        self.assertEqual(payload["default_backend_mode"], "not_configured")
        self.assertTrue(payload["no_js_required"])
        self.assertIsNone(payload["backend_url_policy"]["hosted_backend_url"])
        self.assertFalse(payload["backend_url_policy"]["hosted_backend_url_configured"])
        self.assertFalse(payload["backend_url_policy"]["hosted_backend_url_verified"])
        self.assertFalse(payload["form_policy"]["hosted_form_enabled"])

    def test_static_search_outputs_exist_and_are_no_js(self) -> None:
        for relative in (
            "search.html",
            "lite/search.html",
            "text/search.txt",
            "files/search.README.txt",
            "data/search_handoff.json",
        ):
            with self.subTest(relative=relative):
                path = SITE_DIST / relative
                self.assertTrue(path.exists())
                if path.suffix in {".html", ".txt"}:
                    self.assertNotIn("<script", path.read_text(encoding="utf-8").casefold())

    def test_search_page_form_is_disabled_and_safety_limited(self) -> None:
        handoff = _load_json(HANDOFF)
        safety = _load_json(SAFETY)
        text = (SITE_DIST / "search.html").read_text(encoding="utf-8")
        parser = _InputParser()
        parser.feed(text)

        self.assertEqual(parser.script_count, 0)
        self.assertEqual(parser.form_actions, [""])
        self.assertTrue(parser.disabled_buttons)
        self.assertEqual(parser.q_maxlengths, [safety["request_limits"]["max_query_length"]])
        self.assertEqual(
            handoff["form_policy"]["query_maxlength"],
            safety["request_limits"]["max_query_length"],
        )

    def test_static_pages_are_honest_about_disabled_hosted_search(self) -> None:
        combined = "\n".join(
            (SITE_DIST / relative).read_text(encoding="utf-8").casefold()
            for relative in (
                "search.html",
                "lite/search.html",
                "text/search.txt",
                "files/search.README.txt",
            )
        )

        for phrase in (
            "hosted public search is not configured",
            "local_index_only",
            "no live probes",
            "downloads",
            "installs",
            "uploads",
            "local path search",
            "windows 7 apps",
            "pc magazine ray tracing",
        ):
            self.assertIn(phrase, combined)
        for prohibited in (
            "hosted public search is live",
            "github pages runs python",
            "live probes are enabled",
            "downloads are enabled",
            "production-ready public search",
        ):
            self.assertNotIn(prohibited, combined)

    def test_public_data_summary_matches_handoff_posture(self) -> None:
        payload = _load_json(SITE_DIST / "data" / "search_handoff.json")

        self.assertEqual(payload["search_handoff_status"], "implemented_static_handoff")
        self.assertEqual(payload["hosted_backend_status"], "unavailable")
        self.assertEqual(payload["default_backend_mode"], "not_configured")
        self.assertIsNone(payload["backend_url"])
        self.assertTrue(payload["local_runtime_available"])
        self.assertEqual(payload["first_mode"], "local_index_only")
        self.assertFalse(payload["contains_live_backend"])
        self.assertFalse(payload["contains_live_probes"])
        self.assertFalse(payload["deployment_performed"])
        self.assertTrue(payload["no_hosted_search_claim"])
        self.assertFalse(payload["disabled_behaviors"]["live_probes_enabled"])
        self.assertFalse(payload["disabled_behaviors"]["downloads_enabled"])
        self.assertFalse(payload["disabled_behaviors"]["local_path_search_enabled"])


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
