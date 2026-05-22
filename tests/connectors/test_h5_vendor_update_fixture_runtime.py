from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.fixture_loader import load_h5_vendor_update_fixture
from archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.normalizer_common import H5_FIXTURE_KINDS, H5_SOURCE_IDS

REPO_ROOT = Path(__file__).resolve().parents[2]


class H5VendorUpdateFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_all_fixture_kinds(self) -> None:
        for source_id in H5_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.{source_id}")
            for kind in H5_FIXTURE_KINDS:
                filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
                fixture = load_h5_vendor_update_fixture(REPO_ROOT / "examples/connectors/h5_vendor_update_driver/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(normalized["source_id"], source_id)
                self.assertEqual(normalized["schema_version"], "h5_vendor_update_normalized_record.v0")
                self.assertFalse(normalized["truth_boundary"]["normalized_record_is_public_truth"])
                self.assertFalse(normalized["product_boundary"]["enabled_catalog_fetch"])
                self.assertIn("vendor_identity_candidate", normalized)
                self.assertIn("payload_metadata_candidate_preview", normalized)

    def test_missing_optional_fields_produce_limitations(self) -> None:
        fixture = load_h5_vendor_update_fixture(REPO_ROOT / "examples/connectors/h5_vendor_update_driver/fixtures/microsoft_download_center/minimal_record.json")
        normalized = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h5_vendor_update_driver.microsoft_download_center").normalize(fixture)
        self.assertTrue(any("optional field absent or unknown" in item for item in normalized["source_limitations"]))
        self.assertEqual(normalized["vendor_version"], "unknown")

    def test_examples_are_valid_json(self) -> None:
        for path in (REPO_ROOT / "examples/connectors/h5_vendor_update_driver").rglob("*.json"):
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
