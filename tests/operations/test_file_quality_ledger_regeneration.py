from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class FileQualityLedgerRegenerationTests(unittest.TestCase):
    def test_quality_validate_accepts_sharded_current_ledger(self) -> None:
        result = subprocess.run(
            [sys.executable, ".aide/scripts/aide_lite.py", "quality", "validate"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("result: PASS", result.stdout)

    def test_quality_status_accepts_sharded_current_ledger(self) -> None:
        result = subprocess.run(
            [sys.executable, ".aide/scripts/aide_lite.py", "quality", "status"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("result: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
