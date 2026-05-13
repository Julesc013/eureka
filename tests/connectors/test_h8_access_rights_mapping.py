from __future__ import annotations

import copy
from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.fixture_loader import load_h8_manuals_docs_fixture
from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards import bitsavers_docs
from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.normalizer_common import detect_h8_product_boundary_violations, detect_h8_truth_boundary_violations

REPO_ROOT = Path(__file__).resolve().parents[2]


class H8AccessRightsMappingTests(unittest.TestCase):
    def test_access_rights_do_not_grant_download_or_rights_clearance(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/access_rights_record.json")
        candidate = bitsavers_docs.normalize(fixture)["access_rights_candidate"]
        self.assertFalse(candidate["truth_boundary"]["access_metadata_is_rights_truth"])
        self.assertFalse(candidate["truth_boundary"]["open_access_metadata_is_rights_clearance"])
        self.assertFalse(candidate["truth_boundary"]["document_metadata_grants_download_permission"])

    def test_master_index_and_fetch_claims_are_rejected(self) -> None:
        fixture = load_h8_manuals_docs_fixture(REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json")
        normalized = bitsavers_docs.normalize(fixture)
        truth_mutated = copy.deepcopy(normalized)
        truth_mutated["truth_boundary"]["master_index_mutated"] = True
        self.assertTrue(any("master_index_mutated" in error for error in detect_h8_truth_boundary_violations(truth_mutated)))
        product_mutated = copy.deepcopy(normalized)
        product_mutated["product_boundary"]["document_download_used"] = True
        self.assertTrue(any("document_download_used" in error for error in detect_h8_product_boundary_violations(product_mutated)))


if __name__ == "__main__":
    unittest.main()
