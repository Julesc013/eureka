from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidatePublicAlphaLaunchCandidateScriptTests(unittest.TestCase):
    def test_validator_passes_plain_and_json_in_passing_state(self) -> None:
        plain = subprocess.run(
            [sys.executable, "scripts/validate_public_alpha_launch_candidate.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(plain.returncode, 0, plain.stdout + plain.stderr)
        self.assertIn("pass", plain.stdout)

        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_alpha_launch_candidate.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["errors"], [])
        self.assertTrue(payload["external_full_discovery_verified"])
        self.assertEqual(payload["external_full_discovery_tests_run"], 5057)
        self.assertTrue(payload["launch_candidate_ready"])


if __name__ == "__main__":
    unittest.main()
