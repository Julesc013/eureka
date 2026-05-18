import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class IAFixtureReplayScriptTests(unittest.TestCase):
    def test_replay_cli_directory_json(self):
        completed = run_script(
            "scripts/eureka_ia_fixture_replay.py",
            "--fixture-dir",
            "examples/internet_archive_metadata",
            "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["all_fixtures_replay"])
        self.assertEqual(8, payload["fixture_count"])
        self.assertFalse(payload["forbidden_network_imports_detected"])

    def test_replay_cli_single_fixture_json(self):
        completed = run_script(
            "scripts/eureka_ia_fixture_replay.py",
            "--fixture",
            "examples/internet_archive_metadata/retry_after_429.fixture.json",
            "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(1, payload["fixture_count"])
        self.assertEqual("retry_after_429", payload["fixture_ids"][0])
        self.assertEqual("retry_after", payload["normalized_records"][0]["observation_kind"])

    def test_validator_passes(self):
        completed = run_script("scripts/validate_ia_fixture_replay.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertTrue(payload["all_fixtures_replay"])
        self.assertTrue(payload["expected_records_match"])
        self.assertTrue(payload["no_download_proof_passed"])

    def test_no_forbidden_network_imports_in_ia_replay_modules(self):
        forbidden = ("requests", "httpx", "aiohttp", "urllib.request", "selenium", "playwright", "openai")
        for relative in (
            "runtime/source_observation/internet_archive_metadata.py",
            "runtime/source_observation/internet_archive_normalization.py",
            "runtime/source_observation/internet_archive_validation.py",
            "runtime/source_observation/internet_archive_fixture_replay.py",
            "scripts/eureka_ia_fixture_replay.py",
            "scripts/validate_ia_fixture_replay.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            for name in forbidden:
                self.assertNotIn(f"import {name}", text)
                self.assertNotIn(f"from {name}", text)


if __name__ == "__main__":
    unittest.main()
