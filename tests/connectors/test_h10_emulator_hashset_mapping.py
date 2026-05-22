from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.scummvm_compatibility import normalize as normalize_scummvm
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.redump_hash_sets import normalize as normalize_redump

REPO_ROOT = Path(__file__).resolve().parents[2]


class H10EmulatorHashsetMappingTests(unittest.TestCase):
    def test_compatibility_candidate_is_not_playability_or_correctness_truth(self) -> None:
        record = normalize_scummvm(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/scummvm_compatibility/emulator_compatibility_record.json"))
        candidate = record["emulator_compatibility_candidate"]
        self.assertFalse(candidate["truth_boundary"]["emulator_compatibility_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_emulator_compatibility_truth"])
        self.assertFalse(candidate["truth_boundary"]["compatibility_metadata_proves_playability"])

    def test_hashset_candidate_is_not_hashset_truth_or_authenticity_proof(self) -> None:
        record = normalize_redump(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/redump_hash_sets/preservation_hashset_record.json"))
        candidate = record["preservation_hashset_candidate"]
        self.assertFalse(candidate["truth_boundary"]["preservation_hashset_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_hashset_truth"])
        self.assertFalse(candidate["truth_boundary"]["hash_metadata_proves_authenticity"])


if __name__ == "__main__":
    unittest.main()
