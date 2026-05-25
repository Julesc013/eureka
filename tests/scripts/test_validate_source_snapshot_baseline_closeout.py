from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateSourceSnapshotBaselineCloseoutScriptTests(unittest.TestCase):
    def test_validator_script_json_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_source_snapshot_baseline_closeout.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass", payload["errors"])


if __name__ == "__main__":
    unittest.main()
