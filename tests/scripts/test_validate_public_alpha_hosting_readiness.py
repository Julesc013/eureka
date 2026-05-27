from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidatePublicAlphaHostingReadinessScriptTests(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, "scripts/validate_public_alpha_hosting_readiness.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(plain.returncode, 0, plain.stdout + plain.stderr)
        self.assertIn("validation: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_alpha_hosting_readiness.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["contracts_checked"], 9)
        self.assertEqual(payload["policies_checked"], 7)
        self.assertIn("static_snapshot_site", payload["hosting_modes_defined"])
        self.assertIs(payload["deployment_performed"], False)
        self.assertIs(payload["public_launch_readiness_claimed"], False)


if __name__ == "__main__":
    unittest.main()
