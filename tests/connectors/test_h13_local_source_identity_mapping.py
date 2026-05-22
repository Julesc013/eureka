from __future__ import annotations

import unittest

from archive.prototypes.legacy_runtime.connectors.h13_local_private.fixture_loader import load_h13_local_private_fixture
from archive.prototypes.legacy_runtime.connectors.h13_local_private import local_folder_metadata
from scripts import validate_h13_local_private_fixture_runtime as validator


class H13LocalSourceIdentityMappingTests(unittest.TestCase):
    def test_identity_candidate_is_not_truth(self) -> None:
        fixture = load_h13_local_private_fixture(validator.REPO_ROOT / "examples/connectors/h13_local_private/fixtures/local_folder_metadata/local_source_identity_record.json")
        candidate = local_folder_metadata.normalize(fixture)["local_source_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["local_source_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["declared_ownership_is_rights_clearance"])

    def test_public_master_index_claims_rejected(self) -> None:
        errors: list[str] = []
        validator._scan_json_boundaries({"truth_boundary": {"public_index_mutated": True, "master_index_mutated": True}}, "mutated", errors)
        self.assertGreaterEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
