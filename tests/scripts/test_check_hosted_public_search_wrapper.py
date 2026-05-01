from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check_hosted_public_search_wrapper.py"


class CheckHostedPublicSearchWrapperScriptTest(unittest.TestCase):
    def test_plain_check_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn("status: passed", completed.stdout)
        self.assertIn("checks: 14/14", completed.stdout)

    def test_json_check_passes_and_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["failed_checks"], 0)
        self.assertEqual(payload["passed_checks"], 14)
        for key, value in payload["hard_booleans"].items():
            with self.subTest(key=key):
                self.assertIs(value, False)


if __name__ == "__main__":
    unittest.main()
