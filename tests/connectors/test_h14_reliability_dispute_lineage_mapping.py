from __future__ import annotations

import copy
import unittest

from runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture
from runtime.connectors.h14_source_discovery.source_dispute_revocation_source import normalize as normalize_dispute
from runtime.connectors.h14_source_discovery.source_lineage_provenance_source import normalize as normalize_lineage
from runtime.connectors.h14_source_discovery.source_reliability_freshness_source import normalize as normalize_reliability
from runtime.connectors.h14_source_discovery.normalizer_common import detect_h14_truth_boundary_violations
from scripts import validate_h14_source_discovery_fixture_runtime as validator


class H14ReliabilityDisputeLineageMappingTests(unittest.TestCase):
    def test_reliability_and_freshness_are_not_truth(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_reliability_freshness/reliability_freshness_record.json")
        normalized = normalize_reliability(fixture)
        self.assertFalse(normalized["source_reliability_freshness_candidate"]["truth_boundary"]["source_reliability_freshness_candidate_is_truth"])
        self.assertFalse(normalized["truth_boundary"]["freshness_score_is_currentness_truth"])

    def test_dispute_revocation_is_not_accepted_truth_or_deletion(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_dispute_revocation/dispute_revocation_record.json")
        normalized = normalize_dispute(fixture)
        self.assertFalse(normalized["source_dispute_revocation_candidate"]["truth_boundary"]["source_dispute_revocation_candidate_is_accepted_truth"])
        self.assertFalse(normalized["truth_boundary"]["dispute_revocation_candidate_is_automatic_deletion"])

    def test_lineage_is_not_truth_or_auto_merge(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_lineage_provenance/lineage_provenance_record.json")
        normalized = normalize_lineage(fixture)
        self.assertFalse(normalized["source_lineage_provenance_candidate"]["truth_boundary"]["source_lineage_provenance_candidate_is_lineage_truth"])
        self.assertFalse(normalized["truth_boundary"]["lineage_auto_merges_sources"])

    def test_source_cache_and_evidence_previews_are_not_acceptance(self) -> None:
        fixture = load_h14_source_discovery_fixture(validator.REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures/source_reliability_freshness/minimal_record.json")
        normalized = normalize_reliability(fixture)
        self.assertFalse(normalized["source_cache_candidate_preview"]["accepted_source"])
        self.assertFalse(normalized["evidence_candidate_preview"]["accepted_evidence"])
        mutated = copy.deepcopy(normalized)
        mutated["truth_boundary"]["accepted_evidence_truth"] = True
        self.assertTrue(detect_h14_truth_boundary_violations(mutated))


if __name__ == "__main__":
    unittest.main()
