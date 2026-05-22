from __future__ import annotations

import unittest

from archive.prototypes.legacy_runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture
from archive.prototypes.legacy_runtime.connectors.h12_retro_community import winworld_metadata
from scripts import validate_h12_retro_community_fixture_runtime as validator


class H12CompatibilityCommunityMappingTests(unittest.TestCase):
    def test_compatibility_and_community_candidates_remain_observations(self) -> None:
        compatibility = winworld_metadata.normalize(load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/compatibility_install_note_record.json"))["compatibility_install_note_candidate"]
        community = winworld_metadata.normalize(load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/community_review_comment_record.json"))["community_review_comment_candidate"]
        self.assertFalse(compatibility["truth_boundary"]["compatibility_install_note_candidate_is_truth"])
        self.assertEqual(compatibility["execution_permission_current"], "blocked_current")
        self.assertFalse(community["truth_boundary"]["community_review_comment_candidate_is_truth"])
        self.assertFalse(community["truth_boundary"]["community_reputation_claimed"])


if __name__ == "__main__":
    unittest.main()
