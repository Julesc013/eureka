from __future__ import annotations

import copy
import unittest

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.source_candidate_registry import normalize as normalize_candidate
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.source_discovery_policy import normalize as normalize_discovery
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import detect_h14_product_boundary_violations, detect_h14_truth_boundary_violations
from scripts import validate_h14_source_discovery_fixture_runtime as validator


class H14SourceCandidateDiscoveryMappingTests(unittest.TestCase):
    def test_source_candidate_is_not_source_truth(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_candidate_registry/source_candidate_record.json")
        normalized = normalize_candidate(fixture)
        self.assertFalse(normalized["source_candidate_candidate"]["truth_boundary"]["source_candidate_candidate_is_source_truth"])

    def test_discovery_candidate_is_not_registry_mutation_or_live_runtime(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_discovery_policy/source_discovery_candidate_record.json")
        normalized = normalize_discovery(fixture)
        self.assertFalse(normalized["source_discovery_candidate"]["truth_boundary"]["source_discovery_candidate_is_registry_mutation"])
        self.assertFalse(normalized["product_boundary"]["enabled_source_discovery"])

    def test_registry_and_live_claims_are_rejected(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_discovery_policy/source_discovery_candidate_record.json")
        normalized = normalize_discovery(fixture)
        mutated = copy.deepcopy(normalized)
        mutated["truth_boundary"]["source_discovery_candidate_is_registry_mutation"] = True
        self.assertTrue(detect_h14_truth_boundary_violations(mutated))
        mutated = copy.deepcopy(normalized)
        mutated["product_boundary"]["enabled_source_discovery"] = True
        self.assertTrue(detect_h14_product_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
