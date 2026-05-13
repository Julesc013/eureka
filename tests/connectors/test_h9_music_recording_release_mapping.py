from __future__ import annotations

from pathlib import Path
import unittest

from control.prototypes.legacy_runtime.connectors.h9_media_metadata.fixture_loader import load_h9_media_metadata_fixture
from control.prototypes.legacy_runtime.connectors.h9_media_metadata.music_work_recording_release import build_h9_music_work_recording_release_candidate
from control.prototypes.legacy_runtime.connectors.h9_media_metadata.normalizer_common import detect_h9_truth_boundary_violations, normalize_h9_media_metadata_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


class H9MusicRecordingReleaseMappingTests(unittest.TestCase):
    def test_music_candidate_is_not_music_or_audio_truth(self) -> None:
        fixture = load_h9_media_metadata_fixture(REPO_ROOT / "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json")
        normalized = normalize_h9_media_metadata_fixture(fixture, "musicbrainz")
        candidate = build_h9_music_work_recording_release_candidate(normalized)
        self.assertFalse(candidate["truth_boundary"]["music_identity_candidate_is_truth"])
        self.assertFalse(candidate["truth_boundary"]["fingerprint_match_candidate_is_truth"])
        self.assertFalse(detect_h9_truth_boundary_violations(candidate))


if __name__ == "__main__":
    unittest.main()
