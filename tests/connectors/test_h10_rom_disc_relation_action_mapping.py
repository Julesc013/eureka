from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture
from control.prototypes.legacy_runtime.connectors.h10_games_emulation.mame_software_lists import normalize

REPO_ROOT = Path(__file__).resolve().parents[2]


class H10RomDiscRelationActionMappingTests(unittest.TestCase):
    def test_media_candidate_is_not_media_truth_or_download_permission(self) -> None:
        record = normalize(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mame_software_lists/rom_disc_media_identity_record.json"))
        candidate = record["rom_disc_media_identity_candidate"]
        self.assertFalse(candidate["truth_boundary"]["rom_disc_media_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_rom_disc_media_truth"])
        self.assertFalse(candidate["truth_boundary"]["media_identity_grants_download_permission"])

    def test_relation_candidate_is_not_relation_truth(self) -> None:
        record = normalize(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mame_software_lists/game_relation_record.json"))
        candidate = record["game_relation_candidate"][0]
        self.assertFalse(candidate["truth_boundary"]["game_relation_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_game_relation_truth"])

    def test_action_candidate_is_blocked_only(self) -> None:
        record = normalize(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mame_software_lists/emulator_action_blocked_record.json"))
        candidate = record["emulator_action_candidate"]
        self.assertEqual(candidate["action_status_current"], "blocked_current")
        self.assertFalse(candidate["truth_boundary"]["emulator_action_candidate_is_action_permission"])
        self.assertFalse(candidate["truth_boundary"]["execution_permission_granted"])
        self.assertFalse(candidate["truth_boundary"]["acquisition_permission_granted"])


if __name__ == "__main__":
    unittest.main()
