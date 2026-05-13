from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
CLI = ROOT / "scripts" / "eureka_workunit_queue.py"
DEMO = ROOT / "scripts" / "demo_workunit_queue.py"
VALIDATOR = ROOT / "scripts" / "validate_workunit_queue.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class WorkUnitQueueScriptTests(unittest.TestCase):
    def test_cli_requires_instance(self) -> None:
        completed = run_cmd(str(CLI), "list", "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("missing_instance", json.loads(completed.stdout)["error"])

    def test_cli_create_list_show_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            create = run_cmd(str(CLI), "--instance", str(instance), "create", "--kind", "search_need", "--title", "Sample local search need", "--json")
            self.assertEqual(0, create.returncode, create.stderr)
            workunit_id = json.loads(create.stdout)["workunit"]["id"]
            listing = run_cmd(str(CLI), "--instance", str(instance), "list", "--json")
            self.assertEqual(0, listing.returncode, listing.stderr)
            self.assertEqual(1, json.loads(listing.stdout)["count"])
            show = run_cmd(str(CLI), "--instance", str(instance), "show", "--id", workunit_id, "--with-transitions", "--json")
            self.assertEqual(0, show.returncode, show.stderr)
            self.assertTrue(json.loads(show.stdout)["transitions"])
            summary = run_cmd(str(CLI), "--instance", str(instance), "summary", "--json")
            self.assertEqual(0, summary.returncode, summary.stderr)
            self.assertEqual(1, json.loads(summary.stdout)["summary"]["total"])

    def test_demo_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            demo = run_cmd(str(DEMO), "--instance", str(instance), "--json")
            self.assertEqual(0, demo.returncode, demo.stderr)
            payload = json.loads(demo.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertTrue(payload["invalid_transition_rejected"])
            self.assertIs(payload["work_execution_performed"], False)

    def test_validator_passes(self) -> None:
        completed = run_cmd(str(VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
