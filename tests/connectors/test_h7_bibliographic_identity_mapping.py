from __future__ import annotations

import copy
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h7_library_research.fixture_loader import load_h7_library_research_fixture
from archive.prototypes.legacy_runtime.connectors.h7_library_research.worldcat_library_catalog import normalize
from archive.prototypes.legacy_runtime.connectors.h7_library_research.normalizer_common import detect_h7_truth_boundary_violations

REPO_ROOT = Path(__file__).resolve().parents[2]


class H7BibliographicIdentityMappingTests(unittest.TestCase):
    def test_bibliographic_candidate_is_not_truth(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/worldcat_library_catalog/identity_record.json")
        candidate = normalize(fixture)["bibliographic_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["bibliographic_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_bibliographic_truth"])
        self.assertIn("title", candidate["supporting_fields"])

    def test_source_cache_and_evidence_are_previews_only(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/worldcat_library_catalog/identity_record.json")
        normalized = normalize(fixture)
        self.assertFalse(normalized["source_cache_candidate_preview"]["persistence_allowed_current"])
        self.assertFalse(normalized["evidence_candidate_preview"]["evidence_ledger_write_allowed_current"])

    def test_public_index_mutation_claim_is_rejected(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/worldcat_library_catalog/identity_record.json")
        normalized = normalize(fixture)
        mutated = copy.deepcopy(normalized)
        mutated["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(any("public_index_mutated" in error for error in detect_h7_truth_boundary_violations(mutated)))


if __name__ == "__main__":
    unittest.main()
