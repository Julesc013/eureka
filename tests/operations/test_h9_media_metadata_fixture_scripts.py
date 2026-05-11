from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts import validate_h9_media_metadata_fixture_runtime as validator

REPO_ROOT = Path(__file__).resolve().parents[2]


class H9MediaMetadataFixtureScriptTests(unittest.TestCase):
    def test_validator_passes_current_repo(self) -> None:
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_normalizer_writes_no_files_by_default(self) -> None:
        before = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h9_media_metadata/normalized").glob("*.json")}
        result = subprocess.run([sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h9_media_metadata/normalized").glob("*.json")}
        self.assertEqual(before, after)

    def test_normalizer_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "normalized.json"
            media = Path(tmp) / "media.json"
            result = subprocess.run([sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", str(output), "--media-output", str(media)], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_id"], "musicbrainz")
            self.assertIn("candidate_id", json.loads(media.read_text(encoding="utf-8")))

    def test_replay_writes_no_files_by_default_and_temp_when_explicit(self) -> None:
        result = subprocess.run([sys.executable, "scripts/replay_h9_media_metadata_fixtures.py", "--check"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, "scripts/replay_h9_media_metadata_fixtures.py", "--source-id", "musicbrainz", "--output-dir", tmp], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(list(Path(tmp).glob("*.json")))

    def test_scripts_refuse_forbidden_roots(self) -> None:
        commands = [
            [sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", "site/dist/h9.json"],
            [sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", "data/public_index/h9.json"],
            [sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", "media_downloads/h9.json"],
            [sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", "media_uploads/h9.json"],
            [sys.executable, "scripts/normalize_h9_media_metadata_fixture.py", "--source-id", "musicbrainz", "--input", "examples/connectors/h9_media_metadata/fixtures/musicbrainz/music_identity_record.json", "--output", "fingerprint_cache/h9.json"],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0, command)
            self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_summary_check(self) -> None:
        result = subprocess.run([sys.executable, "scripts/summarize_h9_media_metadata_fixture_outputs.py", "--input", "examples/connectors/h9_media_metadata", "--check", "--json"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_count"], 20)

    def test_validator_does_not_create_private_roots(self) -> None:
        validator.validate_repo(REPO_ROOT)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka", "media_downloads", "media_uploads", "fingerprint_cache", "fingerprint_uploads", "image_cache", "video_cache", "audio_cache", "map_downloads", "score_downloads", "restricted_sources"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
