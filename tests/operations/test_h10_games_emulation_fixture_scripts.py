from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts import validate_h10_games_emulation_fixture_runtime as validator

REPO_ROOT = Path(__file__).resolve().parents[2]


class H10GamesEmulationFixtureScriptTests(unittest.TestCase):
    def test_validator_passes_current_repo(self) -> None:
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_normalizer_writes_no_files_by_default(self) -> None:
        before = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h10_games_emulation/normalized").glob("*.json")}
        result = subprocess.run([sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h10_games_emulation/normalized").glob("*.json")}
        self.assertEqual(before, after)

    def test_normalizer_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "normalized.json"
            game = Path(tmp) / "game.json"
            action = Path(tmp) / "action.json"
            result = subprocess.run([sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", str(output), "--game-output", str(game), "--action-output", str(action)], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_id"], "mobygames")
            self.assertIn("candidate_id", json.loads(game.read_text(encoding="utf-8")))
            self.assertEqual(json.loads(action.read_text(encoding="utf-8"))["action_status_current"], "blocked_current")

    def test_replay_writes_no_files_by_default_and_temp_when_explicit(self) -> None:
        result = subprocess.run([sys.executable, "scripts/replay_h10_games_emulation_fixtures.py", "--check"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, "scripts/replay_h10_games_emulation_fixtures.py", "--source-id", "mobygames", "--output-dir", tmp], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(list(Path(tmp).glob("*.json")))

    def test_scripts_refuse_forbidden_roots(self) -> None:
        commands = [
            [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "site/dist/h10.json"],
            [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "site/dist/data/public_index/h10.json"],
            [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "roms/h10.json"],
            [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "bios/h10.json"],
            [sys.executable, "scripts/normalize_h10_games_emulation_fixture.py", "--source-id", "mobygames", "--input", "examples/connectors/h10_games_emulation/fixtures/mobygames/game_identity_record.json", "--output", "emulators/h10.json"],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0, command)
            self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_summary_check(self) -> None:
        result = subprocess.run([sys.executable, "scripts/summarize_h10_games_emulation_fixture_outputs.py", "--input", "examples/connectors/h10_games_emulation", "--check", "--json"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_count"], 14)

    def test_validator_does_not_create_private_roots(self) -> None:
        validator.validate_repo(REPO_ROOT)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka", "roms", "isos", "disc_images", "chd", "bios", "firmware", "game_binaries", "emulators", "installers", "patches", "game_installs", "launchers", "hash_submissions", "storefront_accounts", "restricted_sources"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
