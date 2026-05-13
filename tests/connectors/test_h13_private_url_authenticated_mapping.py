from __future__ import annotations

import unittest

from control.prototypes.legacy_runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture
from control.prototypes.legacy_runtime.connectors.h13_local_private import private_nas_metadata_boundary, user_supplied_url_metadata_boundary, user_owned_authenticated_source_boundary
from scripts import validate_h13_local_private_fixture_runtime as validator


class H13PrivateUrlAuthenticatedMappingTests(unittest.TestCase):
    def test_private_boundary_does_not_grant_access(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/private_nas_metadata_boundary/private_source_boundary_record.json")
        candidate = private_nas_metadata_boundary.normalize(fixture)["private_source_boundary_candidate"]
        self.assertFalse(candidate["truth_boundary"]["private_source_boundary_candidate_is_access_permission"])

    def test_user_url_does_not_grant_fetch(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/user_supplied_url_metadata_boundary/user_supplied_url_boundary_record.json")
        candidate = user_supplied_url_metadata_boundary.normalize(fixture)["user_supplied_url_boundary_candidate"]
        self.assertFalse(candidate["truth_boundary"]["user_supplied_url_boundary_candidate_is_fetch_permission"])

    def test_authenticated_boundary_does_not_grant_account_access(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/user_owned_authenticated_source_boundary/authenticated_source_boundary_record.json")
        candidate = user_owned_authenticated_source_boundary.normalize(fixture)["authenticated_source_boundary_candidate"]
        self.assertFalse(candidate["truth_boundary"]["authenticated_source_boundary_candidate_is_account_permission"])


if __name__ == "__main__":
    unittest.main()
