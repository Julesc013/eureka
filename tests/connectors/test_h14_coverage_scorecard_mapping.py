from __future__ import annotations

import copy
import unittest

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.coverage_manifest_source import normalize as normalize_coverage
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.connector_scorecard_source import normalize as normalize_scorecard
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import detect_h14_truth_boundary_violations
from scripts import validate_h14_source_discovery_fixture_runtime as validator


class H14CoverageScorecardMappingTests(unittest.TestCase):
    def test_coverage_manifest_is_not_exhaustive_or_completeness(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/coverage_manifest/coverage_manifest_record.json")
        normalized = normalize_coverage(fixture)
        self.assertFalse(normalized["coverage_manifest_candidate"]["truth_boundary"]["coverage_manifest_candidate_is_exhaustive"])
        self.assertFalse(normalized["truth_boundary"]["source_completeness_claimed"])

    def test_connector_scorecard_is_not_connector_approval_or_production_readiness(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/connector_scorecard/connector_scorecard_record.json")
        normalized = normalize_scorecard(fixture)
        self.assertFalse(normalized["connector_scorecard_candidate"]["truth_boundary"]["connector_scorecard_candidate_is_connector_approval"])
        self.assertFalse(normalized["truth_boundary"]["production_readiness_claimed"])

    def test_overclaims_fail(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/coverage_manifest/coverage_manifest_record.json")
        normalized = normalize_coverage(fixture)
        for key in ("coverage_manifest_candidate_is_exhaustive", "source_completeness_claimed", "production_readiness_claimed"):
            mutated = copy.deepcopy(normalized)
            mutated["truth_boundary"][key] = True
            self.assertTrue(detect_h14_truth_boundary_violations(mutated), key)


if __name__ == "__main__":
    unittest.main()
