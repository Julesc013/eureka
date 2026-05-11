from __future__ import annotations

import importlib
import unittest

from runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture
from scripts import validate_h11_storefront_fixture_runtime as validator


class H11VersionPriceAvailabilityMappingTests(unittest.TestCase):
    def test_version_and_price_candidates_do_not_claim_truth(self) -> None:
        module = importlib.import_module("runtime.connectors.h11_storefront.steam_store_metadata")
        version = module.normalize(load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures/steam_store_metadata/version_release_channel_record.json"))["version_release_channel_candidate"]
        price = module.normalize(load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures/steam_store_metadata/price_availability_region_record.json"))["price_availability_region_candidate"]
        self.assertFalse(version["truth_boundary"]["version_release_channel_candidate_is_truth"])
        self.assertFalse(price["truth_boundary"]["price_availability_region_candidate_is_truth"])
        self.assertFalse(price["truth_boundary"]["price_metadata_is_current_price_truth"])
        self.assertFalse(price["truth_boundary"]["availability_metadata_is_current_availability_truth"])
