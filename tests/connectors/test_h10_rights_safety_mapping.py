from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.steam_game_metadata_policy_limited import normalize

REPO_ROOT = Path(__file__).resolve().parents[2]


class H10RightsSafetyMappingTests(unittest.TestCase):
    def test_rights_safety_candidate_does_not_clear_rights_or_safety(self) -> None:
        record = normalize(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/steam_game_metadata_policy_limited/rights_safety_record.json"))
        candidate = record["games_rights_safety_candidate"]
        self.assertFalse(candidate["truth_boundary"]["rights_safety_candidate_is_rights_or_safety_truth"])
        self.assertFalse(candidate["truth_boundary"]["rights_clearance_claimed"])
        self.assertFalse(candidate["truth_boundary"]["legal_acquisition_claimed"])
        self.assertFalse(candidate["truth_boundary"]["malware_safety_claimed"])
        self.assertFalse(candidate["truth_boundary"]["content_safety_claimed"])
        self.assertFalse(candidate["truth_boundary"]["privacy_safety_claimed"])


if __name__ == "__main__":
    unittest.main()
