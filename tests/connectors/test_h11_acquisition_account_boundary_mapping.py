from __future__ import annotations

import importlib
import unittest

from control.prototypes.legacy_runtime.connectors.h11_storefront.fixture_loader import load_h11_storefront_fixture
from scripts import validate_h11_storefront_fixture_runtime as validator


class H11AcquisitionAccountBoundaryMappingTests(unittest.TestCase):
    def test_acquisition_and_account_candidates_are_blocked(self) -> None:
        module = importlib.import_module("control.prototypes.legacy_runtime.connectors.h11_storefront.gog_store_metadata")
        acquisition = module.normalize(load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures/gog_store_metadata/acquisition_path_blocked_record.json"))["acquisition_path_candidate"]
        account = module.normalize(load_h11_storefront_fixture(validator.REPO_ROOT / "examples/connectors/h11_storefront/fixtures/gog_store_metadata/account_entitlement_boundary_record.json"))["account_entitlement_boundary_candidate"]
        self.assertEqual(acquisition["action_status_current"], "blocked_current")
        self.assertTrue(acquisition["j_track_required"])
        self.assertFalse(acquisition["truth_boundary"]["acquisition_path_candidate_is_action_permission"])
        self.assertEqual(account["account_access_current"], "blocked_current")
        self.assertFalse(account["truth_boundary"]["account_entitlement_boundary_candidate_is_license_truth"])
