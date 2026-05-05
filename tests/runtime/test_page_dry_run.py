import json
import tempfile
import unittest
from pathlib import Path

from runtime.pages.dry_run import classify_page, run_page_dry_run
from runtime.pages.render import render_page_html, render_page_json, render_page_text


def page(**overrides):
    payload = {
        "schema_version": "page_runtime_dry_run.v0",
        "page_id": "temp-page-preview",
        "page_kind": "object_page",
        "page_status": "synthetic_example",
        "lane": "demo",
        "title": "Temporary Page Preview",
        "summary": "Temporary public-safe page preview.",
        "privacy_status": "public_safe",
        "public_safety_status": "public_safe",
        "action_status": "risky_actions_disabled",
        "allowed_actions": ["inspect_metadata", "compare", "cite"],
        "disabled_actions": ["download", "upload", "install", "execute"],
        "conflicts": [],
        "gaps": ["Temporary test gap."],
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "installs_enabled": False,
        "execution_enabled": False,
    }
    payload.update(overrides)
    return payload


class PageDryRunRuntimeTests(unittest.TestCase):
    def test_run_page_dry_run_over_synthetic_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, kind in (
                ("object", "object_page"),
                ("source", "source_page"),
                ("comparison", "comparison_page"),
            ):
                bundle = root / name
                bundle.mkdir()
                (bundle / "PAGE_RECORD.json").write_text(
                    json.dumps(page(page_id=f"temp-{name}", page_kind=kind), indent=2),
                    encoding="utf-8",
                )
            report = run_page_dry_run([root], strict=True, render=True)
        payload = report.to_dict()
        self.assertEqual(payload["mode"], "local_dry_run")
        self.assertEqual(payload["pages_seen"], 3)
        self.assertEqual(payload["pages_valid"], 3)
        self.assertEqual(payload["page_kinds"], {"comparison_page": 1, "object_page": 1, "source_page": 1})
        self.assertEqual(len(payload["preview_outputs"]), 3)
        self.assertTrue(payload["hard_booleans"]["local_dry_run"])
        for key, value in payload["hard_booleans"].items():
            if key != "local_dry_run":
                self.assertFalse(value, key)

    def test_classifies_page_fields(self) -> None:
        summary = classify_page(page(page_kind="source_page", page_status="review_required", lane="community"))
        self.assertEqual(summary.page_kind, "source_page")
        self.assertEqual(summary.page_status, "review_required")
        self.assertEqual(summary.lane, "community")
        self.assertEqual(summary.action_status, "risky_actions_disabled")
        self.assertTrue(summary.valid)

    def test_renders_text_html_and_json_preview(self) -> None:
        summary = classify_page(page(title="<Unsafe Title>"))
        text = render_page_text(summary)
        html = render_page_html(summary)
        payload = render_page_json(summary)
        self.assertIn("Unsafe Title", text)
        self.assertIn("&lt;Unsafe Title&gt;", html)
        self.assertEqual(payload["page_kind"], "object_page")
        self.assertFalse(payload["hard_booleans"]["external_calls_performed"])

    def test_rejects_private_absolute_path(self) -> None:
        summary = classify_page(page(summary="Synthetic C:\\Users\\Alice\\private cache"))
        self.assertFalse(summary.valid)
        self.assertTrue(any("private" in error for error in summary.errors))

    def test_rejects_url_and_live_source_fields(self) -> None:
        summary = classify_page(page(source_url="synthetic-source-url", live_source="source-selector"))
        self.assertFalse(summary.valid)
        self.assertTrue(any("forbidden field" in error for error in summary.errors))

    def test_detects_secret_like_keys(self) -> None:
        summary = classify_page(page(api_key="redacted-test-key"))
        self.assertFalse(summary.valid)
        self.assertTrue(any("secret-like field" in error for error in summary.errors))

    def test_detects_raw_payload_fields(self) -> None:
        summary = classify_page(page(raw_payload="payload"))
        self.assertFalse(summary.valid)
        self.assertTrue(any("raw payload" in error for error in summary.errors))

    def test_detects_unsafe_action_claims(self) -> None:
        summary = classify_page(page(allowed_actions=["download"]))
        self.assertFalse(summary.valid)
        self.assertEqual(summary.action_status, "unsafe_action_claim_detected")

    def test_report_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PAGE_RECORD.json"
            path.write_text(json.dumps(page(), indent=2), encoding="utf-8")
            first = run_page_dry_run([Path(tmp)], strict=True, render=True).to_dict()
            second = run_page_dry_run([Path(tmp)], strict=True, render=True).to_dict()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
