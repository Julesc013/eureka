from __future__ import annotations

import importlib
import unittest

from archive.prototypes.legacy_runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture
from archive.prototypes.legacy_runtime.connectors.h13_local_private.normalizer_common import H13_SOURCE_IDS, detect_h13_product_boundary_violations, detect_h13_truth_boundary_violations
from scripts import validate_h13_local_private_fixture_runtime as validator


class H13LocalPrivateFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_minimal_and_policy_blocked(self) -> None:
        for source_id in H13_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h13_local_private.{source_id}")
            for filename in ("minimal_record.json", "policy_blocked_record.json"):
                fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures" / source_id / filename)
                record = module.normalize(fixture)
                self.assertEqual(record["source_id"], source_id)
                self.assertFalse(detect_h13_truth_boundary_violations(record))
                self.assertFalse(detect_h13_product_boundary_violations(record))

    def test_all_fixture_kinds_normalize(self) -> None:
        for source_id in H13_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h13_local_private.{source_id}")
            for filename in validator.FIXTURE_FILES.values():
                fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures" / source_id / filename)
                record = module.normalize(fixture)
                self.assertIn("local_source_identity_candidate", record)
                self.assertIn("local_private_rights_safety_candidate", record)

    def test_validator_passes_current_repo(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_missing_optional_fields_are_limited_not_fabricated(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/local_folder_metadata/minimal_record.json")
        record = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h13_local_private.local_folder_metadata").normalize(fixture)
        self.assertEqual(record["private_source_ref"], "unknown")
        self.assertTrue(record["source_limitations"])


if __name__ == "__main__":
    unittest.main()
