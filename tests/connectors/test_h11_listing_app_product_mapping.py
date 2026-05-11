from __future__ import annotations

import importlib
import unittest

from runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture
from scripts import validate_h11_storefront_fixture_runtime as validator


class H11ListingAppProductMappingTests(unittest.TestCase):
    def test_listing_and_app_product_candidates_are_not_truth(self) -> None:
        for source_id in ("microsoft_store_metadata", "google_play_metadata", "fdroid_metadata"):
            module = importlib.import_module(f"runtime.connectors.h11_storefront.{source_id}")
            for filename, key in (("listing_identity_record.json", "storefront_listing_identity_candidate"), ("app_product_identity_record.json", "app_product_identity_candidate")):
                fixture = load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures" / source_id / filename)
                candidate = module.normalize(fixture)[key]
                self.assertFalse(candidate["truth_boundary"]["storefront_listing_identity_candidate_is_truth"])
                self.assertFalse(candidate["truth_boundary"]["app_product_identity_candidate_is_truth"])
                self.assertFalse(candidate["product_boundary"]["mutated_public_index"])
