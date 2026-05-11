from __future__ import annotations

import unittest

from runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture
from runtime.connectors.h12_retro_community import winworld_metadata
from scripts import validate_h12_retro_community_fixture_runtime as validator


class H12PlatformArchiveMemberMappingTests(unittest.TestCase):
    def test_platform_and_archive_candidates_do_not_grant_truth_or_download(self) -> None:
        platform = winworld_metadata.normalize(load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/platform_version_edition_record.json"))["platform_version_edition_candidate"]
        archive = winworld_metadata.normalize(load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/archive_item_member_record.json"))["archive_item_member_candidate"]
        self.assertFalse(platform["truth_boundary"]["platform_version_edition_candidate_is_truth"])
        self.assertFalse(archive["truth_boundary"]["archive_item_member_candidate_is_truth"])
        self.assertEqual(archive["download_permission_current"], "blocked_current")
        self.assertEqual(archive["extraction_permission_current"], "blocked_current")


if __name__ == "__main__":
    unittest.main()
