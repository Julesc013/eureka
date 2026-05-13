from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.fixture_loader import load_h6_web_archive_fixture
from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import H6_FIXTURE_KINDS, H6_SOURCE_IDS

REPO_ROOT = Path(__file__).resolve().parents[2]


class H6WebArchiveFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_all_fixture_kinds(self) -> None:
        for source_id in H6_SOURCE_IDS:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.{source_id}")
            for kind in H6_FIXTURE_KINDS:
                filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
                fixture = load_h6_web_archive_fixture(REPO_ROOT / "examples/connectors/h6_web_archive_news_event/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(normalized["source_id"], source_id)
                self.assertEqual(normalized["schema_version"], "h6_web_archive_normalized_record.v0")
                self.assertFalse(normalized["truth_boundary"]["normalized_record_is_public_truth"])
                self.assertFalse(normalized["product_boundary"]["enabled_fetching"])
                self.assertIn("source_cache_candidate_preview", normalized)
                self.assertIn("evidence_candidate_preview", normalized)

    def test_missing_optional_fields_produce_limitations(self) -> None:
        fixture = load_h6_web_archive_fixture(REPO_ROOT / "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/minimal_record.json")
        normalized = importlib.import_module("control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.wayback_cdx_memento").normalize(fixture)
        self.assertTrue(any("optional field absent or unknown" in item for item in normalized["source_limitations"]))
        self.assertEqual(normalized["capture_timestamp"], "unknown")

    def test_examples_are_valid_json(self) -> None:
        for path in (REPO_ROOT / "examples/connectors/h6_web_archive_news_event").rglob("*.json"):
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
