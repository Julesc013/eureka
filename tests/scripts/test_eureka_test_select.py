from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
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
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_selector_inputs(root)
            write_failure_ledger(
                root,
                [
                    {
                        "failure_id": "test-fixed-pending",
                        "status": "fixed_pending_full",
                        "blocking_level": "promotion_blocker",
                        "rerun_command": "python -m unittest tests.operations.test_contract_taxonomy_plan",
                    }
                ],
            )

            payload = self.run_selector("--repo-root", str(root), "--failed-first")

        self.assertEqual(
            ["python -m unittest tests.operations.test_contract_taxonomy_plan"],
            payload["failed_first_commands"],
        )
        self.assertIn("L1_focused_unit", payload["selected_lanes"])

    def test_promotion_includes_full_discovery_and_refuses_active_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copy_selector_inputs(root)
            write_failure_ledger(
                root,
                [
                    {
                        "failure_id": "test-reproduced",
                        "status": "reproduced",
                        "blocking_level": "promotion_blocker",
                        "rerun_command": "python -m unittest tests.operations.test_contract_taxonomy_plan",
                    }
                ],
            )

            payload = self.run_selector("--repo-root", str(root), "--promotion")

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

def copy_selector_inputs(root: Path) -> None:
    for rel in (
        "control/policies/test_lane_policy.json",
        "control/inventory/test_impact_map.json",
        "control/inventory/test_failure_ledger.json",
    ):
        source = REPO_ROOT / rel
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def write_failure_ledger(root: Path, failures: list[dict[str, str]]) -> None:
    path = root / "control/inventory/test_failure_ledger.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["failures"] = failures
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
