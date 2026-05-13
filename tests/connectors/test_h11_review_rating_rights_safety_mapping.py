from __future__ import annotations

import importlib
import unittest

from control.prototypes.legacy_runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture
from scripts import validate_h11_storefront_fixture_runtime as validator


class H11ReviewRatingRightsSafetyMappingTests(unittest.TestCase):
    def test_review_and_rights_candidates_do_not_overclaim(self) -> None:
        module = importlib.import_module("control.prototypes.legacy_runtime.connectors.h11_storefront.mozilla_addons_metadata")
        review = module.normalize(load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures/mozilla_addons_metadata/review_rating_metadata_record.json"))["review_rating_metadata_candidate"]
        rights = module.normalize(load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures/mozilla_addons_metadata/rights_safety_record.json"))["storefront_rights_safety_candidate"]
        self.assertFalse(review["truth_boundary"]["review_rating_metadata_candidate_is_quality_truth"])
        self.assertFalse(rights["truth_boundary"]["storefront_rights_safety_candidate_is_rights_or_safety_truth"])
        self.assertFalse(rights["truth_boundary"]["rights_clearance_claimed"])
        self.assertFalse(rights["truth_boundary"]["malware_safety_claimed"])
        self.assertFalse(rights["truth_boundary"]["privacy_safety_claimed"])
