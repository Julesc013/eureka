from __future__ import annotations

import unittest

from control.prototypes.legacy_runtime.connectors.h12_retro_community.fixture_loader import load_h12_retro_community_fixture
from control.prototypes.legacy_runtime.connectors.h12_retro_community import winworld_metadata
from scripts import validate_h12_retro_community_fixture_runtime as validator


class H12RightsSafetyMappingTests(unittest.TestCase):
    def test_rights_safety_candidate_does_not_clear_rights_or_safety(self) -> None:
        fixture = load_h12_retro_community_fixture(validator.REPO_ROOT / "examples/connectors/h12_retro_community/fixtures/winworld_metadata/rights_safety_record.json")
        candidate = winworld_metadata.normalize(fixture)["retro_rights_safety_candidate"]
        boundary = candidate["truth_boundary"]
        self.assertFalse(boundary["retro_rights_safety_candidate_is_rights_or_safety_truth"])
        self.assertFalse(boundary["rights_clearance_claimed"])
        self.assertFalse(boundary["legal_acquisition_claimed"])
        self.assertFalse(boundary["malware_safety_claimed"])
        self.assertFalse(boundary["content_safety_claimed"])
        self.assertFalse(boundary["privacy_safety_claimed"])
        self.assertFalse(candidate["acquisition_permission_current"])


if __name__ == "__main__":
    unittest.main()
