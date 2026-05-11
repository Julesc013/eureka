from __future__ import annotations

import copy
import unittest

from runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture
from runtime.connectors.h14_source_discovery.source_need_registry import normalize
from runtime.connectors.h14_source_discovery.normalizer_common import detect_h14_truth_boundary_violations
from scripts import validate_h14_source_discovery_fixture_runtime as validator


class H14SourceNeedCandidateMappingTests(unittest.TestCase):
    def test_source_need_candidate_is_not_approval(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_need_registry/source_need_record.json")
        normalized = normalize(fixture)
        candidate = normalized["source_need_candidate"]
        self.assertFalse(candidate["truth_boundary"]["source_need_candidate_is_source_approval"])
        self.assertFalse(candidate["truth_boundary"]["public_index_mutation_allowed"])

    def test_missing_optional_fields_become_limitations(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json")
        normalized = normalize(fixture)
        self.assertTrue(any("Missing optional H14 fixture fields" in item for item in normalized["source_limitations"]))

    def test_source_need_truth_claim_is_rejected(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_need_registry/source_need_record.json")
        normalized = normalize(fixture)
        mutated = copy.deepcopy(normalized)
        mutated["source_need_candidate"]["truth_boundary"]["source_need_candidate_is_source_approval"] = True
        self.assertTrue(detect_h14_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
