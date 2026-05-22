from __future__ import annotations

import importlib
import unittest

from archive.prototypes.legacy_runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture
from archive.prototypes.legacy_runtime.connectors.h11_storefront.normalizer_common import H11_SOURCE_IDS, detect_h11_product_boundary_violations, detect_h11_truth_boundary_violations
from scripts import validate_h11_storefront_fixture_runtime as validator


class H11StorefrontFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_minimal_and_policy_blocked(self) -> None:
        for source_id in H11_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h11_storefront.{source_id}")
            for filename in ("minimal_record.json", "policy_blocked_record.json"):
                fixture = load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures" / source_id / filename)
                record = module.normalize(fixture)
                self.assertEqual(record["source_id"], source_id)
                self.assertFalse(detect_h11_truth_boundary_violations(record))
                self.assertFalse(detect_h11_product_boundary_violations(record))

    def test_validator_passes_current_repo(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_missing_optional_fields_are_limited_not_fabricated(self) -> None:
        fixture = load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures/fdroid_metadata/minimal_record.json")
        record = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h11_storefront.fdroid_metadata").normalize(fixture)
        self.assertEqual(record["version_candidate"], "unknown")
        self.assertTrue(record["source_limitations"])
