from __future__ import annotations

import unittest

from control.prototypes.legacy_runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture
from control.prototypes.legacy_runtime.connectors.h12_retro_community import winworld_metadata
from scripts import validate_h12_retro_community_fixture_runtime as validator


class H12RetroSoftwareIdentityMappingTests(unittest.TestCase):
    def test_identity_candidate_is_not_truth(self) -> None:
        fixture = load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/retro_software_identity_record.json")
        candidate = winworld_metadata.normalize(fixture)["retro_software_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["retro_software_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["community_download_metadata_grants_acquisition_permission"])

    def test_public_master_index_claims_rejected(self) -> None:
        errors: list[str] = []
        validator._scan_json_boundaries({"truth_boundary": {"public_index_mutated": True, "master_index_mutated": True}}, "mutated", errors)
        self.assertGreaterEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
