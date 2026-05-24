from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class WorkbenchLocalLoopScriptTests(unittest.TestCase):
    def test_cli_dry_run_passes(self) -> None:
        payload = self.run_json(
            [
                "scripts/eureka_local_loop_closeout.py",
                "--query",
                "sampleproject",
                "--projection",
                "operator_workbench",
                "--dry-run",
                "--json",
            ]
        )

        self.assertEqual(payload["status"], "dry_run")
        self.assertTrue(payload["dry_run_loop_passed"])

    def test_cli_temp_apply_passes(self) -> None:
        payload = self.run_json(
            [
                "scripts/eureka_local_loop_closeout.py",
                "--query",
                "sampleproject",
                "--projection",
                "operator_workbench",
                "--use-temp-instance",
                "--apply-to-temp",
                "--operator-token",
                "local-dev-token",
                "--confirm",
                "APPLY_TO_LOCAL_INSTANCE",
                "--json",
            ]
        )

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["search_after_apply_passed"])
        self.assertTrue(payload["search_after_rollback_passed"])

    def run_json(self, args: list[str]) -> dict[str, object]:
        completed = subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            self.fail(completed.stderr or completed.stdout)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
