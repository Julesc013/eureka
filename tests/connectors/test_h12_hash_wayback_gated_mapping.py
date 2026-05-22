from __future__ import annotations

import unittest

from archive.prototypes.legacy_runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture
from archive.prototypes.legacy_runtime.connectors.h12_retro_community import winworld_metadata
from scripts import validate_h12_retro_community_fixture_runtime as validator


class H12HashWaybackGatedMappingTests(unittest.TestCase):
    def test_hash_wayback_and_gated_candidates_do_not_overclaim(self) -> None:
        hash_candidate = winworld_metadata.normalize(load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/hash_checksum_record.json"))["hash_checksum_candidate"]
        wayback = winworld_metadata.normalize(load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/ia_wayback_corroboration_record.json"))["ia_wayback_corroboration_candidate"]
        gated = winworld_metadata.normalize(load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/gated_source_boundary_record.json"))["gated_source_boundary_candidate"]
        self.assertFalse(hash_candidate["truth_boundary"]["hash_checksum_candidate_is_truth"])
        self.assertFalse(hash_candidate["truth_boundary"]["checksum_correctness_claimed"])
        self.assertFalse(wayback["truth_boundary"]["ia_wayback_corroboration_candidate_is_truth"])
        self.assertEqual(gated["access_permission_current"], "blocked_current")
        self.assertFalse(gated["truth_boundary"]["gated_source_boundary_candidate_grants_access_permission"])


if __name__ == "__main__":
    unittest.main()
