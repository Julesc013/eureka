from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_action_policy.py"


class ActionPolicyValidatorTestCase(unittest.TestCase):
    def test_validator_json_output_parses(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["created_by"], "action_policy_validator_v0")
        self.assertEqual(payload["action_counts"]["current_safe"], 9)
        self.assertEqual(payload["action_counts"]["current_bounded"], 4)
        self.assertEqual(payload["action_counts"]["future_gated"], 15)
        self.assertEqual(payload["action_counts"]["prohibited"], 9)
        self.assertEqual(payload["public_alpha_risky_actions_enabled"], [])
        self.assertEqual(payload["static_site_risky_actions_enabled"], [])


if __name__ == "__main__":
    unittest.main()
