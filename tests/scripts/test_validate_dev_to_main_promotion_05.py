from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateDevToMainPromotion05ScriptTests(unittest.TestCase):
    def test_validator_passes_plain_and_json_in_waiting_state(self) -> None:
        plain = subprocess.run(
            [sys.executable, "scripts/validate_dev_to_main_promotion_05.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(plain.returncode, 0, plain.stdout + plain.stderr)
        self.assertIn("waiting_for_external_full_discovery", plain.stdout)

        completed = subprocess.run(
            [sys.executable, "scripts/validate_dev_to_main_promotion_05.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "waiting_for_external_full_discovery")
        self.assertEqual(payload["errors"], [])
        self.assertFalse(payload["external_full_discovery_summary_received"])
        self.assertFalse(payload["promotion_performed"])


if __name__ == "__main__":
    unittest.main()
