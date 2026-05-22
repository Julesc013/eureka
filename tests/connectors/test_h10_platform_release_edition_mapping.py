from __future__ import annotations

from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.fixture_loader import load_h10_games_emulation_fixture
from archive.prototypes.legacy_runtime.connectors.h10_games_emulation.mobygames import normalize

REPO_ROOT = Path(__file__).resolve().parents[2]


class H10PlatformReleaseEditionMappingTests(unittest.TestCase):
    def test_release_candidate_is_not_release_or_platform_truth(self) -> None:
        record = normalize(load_h10_games_emulation_fixture(REPO_ROOT / "examples/connectors/h10_games_emulation/fixtures/mobygames/platform_release_edition_record.json"))
        candidate = record["platform_release_edition_candidate"]
        self.assertFalse(candidate["truth_boundary"]["platform_release_edition_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_release_truth"])
        self.assertFalse(candidate["truth_boundary"]["accepted_platform_truth"])
        self.assertFalse(candidate["truth_boundary"]["compatibility_metadata_proves_playability"])


if __name__ == "__main__":
    unittest.main()
