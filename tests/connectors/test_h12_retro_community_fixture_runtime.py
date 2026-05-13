from __future__ import annotations

import importlib
import unittest

from control.prototypes.legacy_runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture
from control.prototypes.legacy_runtime.connectors.h12_retro_community.normalizer_common import H12_SOURCE_IDS, detect_h12_product_boundary_violations, detect_h12_truth_boundary_violations
from scripts import validate_h12_retro_community_fixture_runtime as validator


class H12RetroCommunityFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_minimal_and_policy_blocked(self) -> None:
        for source_id in H12_SOURCE_IDS:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h12_retro_community.{source_id}")
            for filename in ("minimal_record.json", "policy_blocked_record.json"):
                fixture = load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures" / source_id / filename)
                record = module.normalize(fixture)
                self.assertEqual(record["source_id"], source_id)
                self.assertFalse(detect_h12_truth_boundary_violations(record))
                self.assertFalse(detect_h12_product_boundary_violations(record))

    def test_all_fixture_kinds_normalize(self) -> None:
        files = validator.FIXTURE_FILES.values()
        for source_id in H12_SOURCE_IDS:
            module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h12_retro_community.{source_id}")
            for filename in files:
                fixture = load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures" / source_id / filename)
                record = module.normalize(fixture)
                self.assertIn("retro_software_identity_candidate", record)
                self.assertIn("retro_rights_safety_candidate", record)

    def test_validator_passes_current_repo(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_missing_optional_fields_are_limited_not_fabricated(self) -> None:
        fixture = load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/minimal_record.json")
        record = importlib.import_module("control.prototypes.legacy_runtime.connectors.h12_retro_community.winworld_metadata").normalize(fixture)
        self.assertEqual(record["version_candidate"], "unknown")
        self.assertTrue(record["source_limitations"])


if __name__ == "__main__":
    unittest.main()
