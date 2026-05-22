from __future__ import annotations

import importlib
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.normalizer_common import H10_FIXTURE_KINDS, H10_SOURCE_IDS, detect_h10_product_boundary_violations, detect_h10_truth_boundary_violations

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_FILES = {
    "minimal": "minimal_record.json",
    "game_identity": "game_identity_record.json",
    "platform_release_edition": "platform_release_edition_record.json",
    "emulator_compatibility": "emulator_compatibility_record.json",
    "preservation_hashset": "preservation_hashset_record.json",
    "rom_disc_media_identity": "rom_disc_media_identity_record.json",
    "game_relation": "game_relation_record.json",
    "emulator_action_blocked": "emulator_action_blocked_record.json",
    "rights_safety": "rights_safety_record.json",
    "policy_blocked": "policy_blocked_record.json",
}


class H10GamesEmulationFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_all_fixture_kinds(self) -> None:
        self.assertEqual(set(H10_FIXTURE_KINDS), set(FIXTURE_FILES))
        for source_id in H10_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h10_games_emulation.{source_id}")
            for kind, filename in FIXTURE_FILES.items():
                fixture = load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(normalized["source_id"], source_id)
                self.assertEqual(normalized["schema_version"], "h10_games_emulation_normalized_record.v0")
                self.assertFalse(detect_h10_truth_boundary_violations(normalized))
                self.assertFalse(detect_h10_product_boundary_violations(normalized))

    def test_missing_optional_fields_produce_limitations(self) -> None:
        fixture = load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mobygames/minimal_record.json")
        normalized = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h10_games_emulation.mobygames").normalize(fixture)
        self.assertIn("optional field platform is absent or unknown in committed fixture", normalized["source_limitations"])
        self.assertEqual(normalized["platform"], "unknown")

    def test_public_and_master_index_mutation_claims_are_rejected(self) -> None:
        fixture = load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json")
        normalized = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h10_games_emulation.mobygames").normalize(fixture)
        bad = dict(normalized)
        bad["truth_boundary"] = dict(normalized["truth_boundary"], public_index_mutated=True)
        self.assertTrue(detect_h10_truth_boundary_violations(bad))
        bad = dict(normalized)
        bad["product_boundary"] = dict(normalized["product_boundary"], mutated_master_index=True)
        self.assertTrue(detect_h10_product_boundary_violations(bad))


if __name__ == "__main__":
    unittest.main()
