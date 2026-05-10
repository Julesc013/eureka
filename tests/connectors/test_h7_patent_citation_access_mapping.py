from __future__ import annotations

import copy
from pathlib import Path
import unittest

from runtime.connectors.h7_library_research.fixture_loader import load_h7_library_research_fixture
from runtime.connectors.h7_library_research import google_patents, openalex
from runtime.connectors.h7_library_research.normalizer_common import detect_h7_product_boundary_violations, detect_h7_truth_boundary_violations

REPO_ROOT = Path(__file__).resolve().parents[2]


class H7PatentCitationAccessMappingTests(unittest.TestCase):
    def test_patent_fields_do_not_become_legal_truth(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/google_patents/identity_record.json")
        candidate = google_patents.normalize(fixture)["patent_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["patent_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["patent_validity_verified"])

    def test_citation_relation_fields_do_not_become_citation_correctness(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/openalex/relation_record.json")
        candidate = openalex.normalize(fixture)["citation_relation_candidate"][0]
        self.assertFalse(candidate["truth_boundary"]["citation_relation_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["citation_correctness_verified"])

    def test_access_rights_do_not_grant_download_or_rights_clearance(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/openalex/access_rights_record.json")
        candidate = openalex.normalize(fixture)["access_rights_availability_candidate"]
        self.assertFalse(candidate["truth_boundary"]["access_metadata_is_rights_truth"])
        self.assertFalse(candidate["truth_boundary"]["open_access_metadata_is_rights_clearance"])
        self.assertFalse(candidate["truth_boundary"]["landing_page_grants_download_permission"])

    def test_master_index_and_fetch_claims_are_rejected(self) -> None:
        fixture = load_h7_library_research_fixture(REPO_ROOT / "examples/connectors/h7_library_research/fixtures/openalex/identity_record.json")
        normalized = openalex.normalize(fixture)
        truth_mutated = copy.deepcopy(normalized)
        truth_mutated["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(any("master_index_mutated" in error for error in detect_h7_truth_boundary_violations(truth_mutated)))
        product_mutated = copy.deepcopy(normalized)
        product_mutated["product_boundary"]["dataset_download_used"] = True
        self.assertTrue(any("dataset_download_used" in error for error in detect_h7_product_boundary_violations(product_mutated)))


if __name__ == "__main__":
    unittest.main()
