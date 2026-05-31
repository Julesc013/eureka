from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class SnapshotRefreshScriptTests(unittest.TestCase):
    def test_snapshot_refresh_scripts_help(self) -> None:
        for script in (
            "scripts/eureka_snapshot_refresh.py",
            "scripts/eureka_snapshot_refresh_report.py",
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
