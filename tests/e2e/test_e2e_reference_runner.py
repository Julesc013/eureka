from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class E2EReferenceRunnerCliTests(unittest.TestCase):
    def test_cli_synthetic_validate_and_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_resolution_run.py",
                    "run",
                    "--mode",
                    "synthetic",
                    "--query",
                    "old blue FTP client for XP",
                    "--out",
                    temp_dir,
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, run_completed.returncode, run_completed.stderr)
            payload = json.loads(run_completed.stdout)
            run_dir = payload["run_dir"]
            validate_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_resolution_run.py",
                    "validate",
                    "--run-dir",
                    run_dir,
                    "--strict",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            replay_completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_resolution_run.py",
                    "replay",
                    "--run-dir",
                    run_dir,
                    "--strict",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(0, validate_completed.returncode, validate_completed.stderr)
        self.assertEqual("valid", json.loads(validate_completed.stdout)["status"])
        self.assertEqual(0, replay_completed.returncode, replay_completed.stderr)
        self.assertEqual("replay_verified", json.loads(replay_completed.stdout)["status"])

    def test_cli_live_shadow_is_policy_blocked(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_resolution_run.py",
                "run",
                "--mode",
                "live-shadow",
                "--query",
                "old blue FTP client for XP",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(2, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("policy_blocked", payload["run"]["state"])
        self.assertFalse(payload["boundaries"]["network_provider_calls"])


if __name__ == "__main__":
    unittest.main()
