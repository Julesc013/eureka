from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ResolutionRunScriptsTests(unittest.TestCase):
    def test_resolution_run_cli_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_resolution_run.py",
                "--query",
                "sampleproject",
                "--projection",
                "operator_workbench",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("completed", payload["run"]["state"])
        self.assertGreater(payload["workunit_schedule"]["workunit_count"], 0)

    def test_validator_cli_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_resolution_run_kernel.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)


if __name__ == "__main__":
    unittest.main()
