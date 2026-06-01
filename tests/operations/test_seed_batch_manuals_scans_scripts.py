from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class SeedBatchManualsScansScriptTests(unittest.TestCase):
    def test_seed_batch_scripts_help(self) -> None:
        for script in (
            "scripts/eureka_seed_batch_manuals_scans.py",
            "scripts/eureka_seed_batch_run.py",
            "scripts/eureka_seed_batch_report.py",
            "scripts/validate_seed_batch_manuals_scans.py",
        ):
            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / script), "--help"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, msg=completed.stderr)


if __name__ == "__main__":
    unittest.main()
