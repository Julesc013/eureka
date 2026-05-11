from __future__ import annotations

import importlib
import unittest

from runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture
from runtime.connectors.h14_source_discovery.normalizer_common import H14_FIXTURE_FILES, H14_SOURCE_IDS
from scripts import validate_h14_source_discovery_fixture_runtime as validator


class H14SourceDiscoveryFixtureRuntimeTests(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = validator.validate_repo()
        self.assertEqual("valid", result["status"], result["errors"])

    def test_all_normalizers_handle_minimal_and_policy_blocked_fixtures(self) -> None:
        for source_id in H14_SOURCE_IDS:
            module_name = validator.SOURCE_MODULES[source_id]
            module = importlib.import_module(f"runtime.connectors.h14_source_discovery.{module_name}")
            for filename in ("minimal_record.json", "policy_blocked_record.json"):
                fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(source_id, normalized["source_id"])
                self.assertFalse(normalized["truth_boundary"]["normalized_record_is_public_truth"])
                self.assertFalse(normalized["product_boundary"]["enabled_source_discovery"])

    def test_all_fixture_kinds_normalize_for_source_need_registry(self) -> None:
        module = importlib.import_module("runtime.connectors.h14_source_discovery.source_need_registry")
        for filename in H14_FIXTURE_FILES.values():
            fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_need_registry" / filename)
            normalized = module.normalize(fixture)
            self.assertIn("source_cache_candidate_preview", normalized)
            self.assertIn("evidence_candidate_preview", normalized)


if __name__ == "__main__":
    unittest.main()
