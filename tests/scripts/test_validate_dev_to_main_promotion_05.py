from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateDevToMainPromotion05ScriptTests(unittest.TestCase):
    def test_validator_passes_plain_and_json_in_current_state(self) -> None:
        plain = subprocess.run(
            [sys.executable, "scripts/validate_dev_to_main_promotion_05.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(plain.returncode, 0, plain.stdout + plain.stderr)
        self.assertRegex(plain.stdout, r"(waiting_for_external_full_discovery|pass)")

        completed = subprocess.run(
            [sys.executable, "scripts/validate_dev_to_main_promotion_05.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"waiting_for_external_full_discovery", "pass"})
        self.assertEqual(payload["errors"], [])
        if payload["status"] == "waiting_for_external_full_discovery":
            self.assertFalse(payload["external_full_discovery_summary_received"])
            self.assertFalse(payload["promotion_performed"])
        else:
            self.assertTrue(payload["external_full_discovery_summary_received"])
            self.assertTrue(payload["full_unittest_discovery_passed"])
            self.assertTrue(payload["promotion_ready"])


if __name__ == "__main__":
    unittest.main()
