from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WorkbenchLiveRunScriptsTests(unittest.TestCase):
    def test_cli_dry_run_outputs_packet(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_workbench_live_run.py",
                "--query",
                "sampleproject",
                "--projection",
                "operator_workbench",
                "--dry-run",
                "--from-fixtures",
                "--include-ia-hunt-dry-run",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("workbench_live_run_packet.v0", payload["schema_version"])
        self.assertGreater(payload["workunit_count"], 0)
        self.assertFalse(payload["boundary_report"]["live_ia_call_performed"])


if __name__ == "__main__":
    unittest.main()
