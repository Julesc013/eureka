from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.fixture_loader import load_h8_manuals_docs_fixture
from archive.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.normalizer_common import H8_FIXTURE_KINDS, H8_SOURCE_IDS

REPO_ROOT = Path(__file__).resolve().parents[2]


class H8ManualsDocsFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_all_fixture_kinds(self) -> None:
        for source_id in H8_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.{source_id}")
            for kind in H8_FIXTURE_KINDS:
                filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
                fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(normalized["source_id"], source_id)
                self.assertEqual(normalized["schema_version"], "h8_manuals_docs_normalized_record.v0")
                self.assertFalse(normalized["truth_boundary"]["normalized_record_is_public_truth"])
                self.assertFalse(normalized["product_boundary"]["enabled_downloads"])
                self.assertIn("source_cache_candidate_preview", normalized)
                self.assertIn("evidence_candidate_preview", normalized)

    def test_missing_optional_fields_produce_limitations(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/minimal_record.json")
        normalized = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.bitsavers_docs").normalize(fixture)
        self.assertTrue(any("optional field absent or unknown" in item for item in normalized["source_limitations"]))
        self.assertEqual(normalized["document_title"], "unknown")

    def test_examples_are_valid_json(self) -> None:
        for path in (REPO_ROOT / "examples/connectors/h8_manuals_docs_standards").rglob("*.json"):
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
