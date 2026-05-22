from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h7_library_research.fixture_loader import load_h7_library_research_fixture
from archive.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import H7_FIXTURE_KINDS, H7_SOURCE_IDS

REPO_ROOT = Path(__file__).resolve().parents[2]


class H7LibraryResearchFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_all_fixture_kinds(self) -> None:
        for source_id in H7_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h7_library_research.{source_id}")
            for kind in H7_FIXTURE_KINDS:
                filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
                fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(normalized["source_id"], source_id)
                self.assertEqual(normalized["schema_version"], "h7_library_research_normalized_record.v0")
                self.assertFalse(normalized["truth_boundary"]["normalized_record_is_public_truth"])
                self.assertFalse(normalized["product_boundary"]["enabled_harvesting"])
                self.assertIn("source_cache_candidate_preview", normalized)
                self.assertIn("evidence_candidate_preview", normalized)

    def test_missing_optional_fields_produce_limitations(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/openalex/minimal_record.json")
        normalized = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h7_library_research.openalex").normalize(fixture)
        self.assertTrue(any("optional field absent or unknown" in item for item in normalized["source_limitations"]))
        self.assertEqual(normalized["doi_candidate"], "unknown")

    def test_examples_are_valid_json(self) -> None:
        for path in (REPO_ROOT / "examples/connectors/h7_library_research").rglob("*.json"):
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
