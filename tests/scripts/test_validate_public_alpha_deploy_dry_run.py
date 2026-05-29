from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidatePublicAlphaDeployDryRunScriptTests(unittest.TestCase):
    def test_validator_passes_plain_and_json_in_passing_state(self) -> None:
        plain = subprocess.run(
            [sys.executable, "scripts/validate_public_alpha_deploy_dry_run.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(plain.returncode, 0, plain.stdout + plain.stderr)
        self.assertIn("pass", plain.stdout)

        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_alpha_deploy_dry_run.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["errors"], [])
        self.assertTrue(payload["deploy_dry_run_rehearsal_passed"])
        self.assertTrue(payload["deploy_smoke_passed"])
        self.assertTrue(payload["rollback_rehearsal_passed"])
        self.assertFalse(payload["deployment_performed"])
        self.assertFalse(payload["public_launch_performed"])


if __name__ == "__main__":
    unittest.main()
