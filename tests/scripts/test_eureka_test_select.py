from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "eureka_test_select.py"


class EurekaTestSelectScriptTests(unittest.TestCase):
    def run_selector(self, *args: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)

    def test_failed_first_prioritizes_failure_ledger(self) -> None:
        payload = self.run_selector("--failed-first")
        self.assertIn("python -m unittest tests.operations.test_search_hunt_closeout", payload["failed_first_commands"])
        self.assertIn("L1_focused_unit", payload["selected_lanes"])

    def test_promotion_includes_full_discovery_and_refuses_active_blockers(self) -> None:
        payload = self.run_selector("--promotion")
        commands = {item["command"] for item in payload["selected_commands"]}
        self.assertIn("python -m unittest discover -s tests -t .", commands)
        self.assertTrue(payload["full_discovery_required"])
        self.assertFalse(payload["promotion_allowed"])
        self.assertIn("L4_promotion_release", payload["selected_lanes"])

    def test_task_mode_selects_workbench_result_lane_tests(self) -> None:
        payload = self.run_selector("--task", "WORKBENCH-RESULT-LANES-01")
        commands = {item["command"] for item in payload["selected_commands"]}
        self.assertIn("python scripts/validate_workbench_result_lanes.py", commands)
        self.assertTrue(payload["skip_reasons"])


if __name__ == "__main__":
    unittest.main()

