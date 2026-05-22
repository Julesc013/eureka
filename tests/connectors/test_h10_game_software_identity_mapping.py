from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.mobygames import normalize

REPO_ROOT = Path(__file__).resolve().parents[2]


class H10GameSoftwareIdentityMappingTests(unittest.TestCase):
    def test_game_identity_candidate_is_not_truth(self) -> None:
        record = normalize(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json"))
        candidate = record["game_software_identity_candidate"]
        self.assertEqual(candidate["schema_version"], "h10_game_software_identity_candidate.v0")
        self.assertFalse(candidate["truth_boundary"]["game_software_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_game_identity_truth"])
        self.assertFalse(candidate["truth_boundary"]["storefront_metadata_grants_acquisition_permission"])

    def test_source_cache_and_evidence_are_previews_only(self) -> None:
        record = normalize(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json"))
        self.assertFalse(record["source_cache_candidate_preview"]["accepted_source"])
        self.assertFalse(record["evidence_candidate_preview"]["accepted_evidence"])


if __name__ == "__main__":
    unittest.main()
