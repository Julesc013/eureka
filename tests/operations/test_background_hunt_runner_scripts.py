from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
SET_TOKEN = ROOT / "scripts" / "eureka_set_operator_token.py"
DEMO_WORKUNITS = ROOT / "scripts" / "demo_hunt_to_workunits.py"
RUNNER = ROOT / "scripts" / "eureka_hunt_runner.py"
DEMO_RUNNER = ROOT / "scripts" / "demo_background_hunt_runner.py"
VALIDATOR = ROOT / "scripts" / "validate_background_hunt_runner.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class BackgroundHuntRunnerScriptTests(unittest.TestCase):
    def test_cli_plan_run_summary_and_demo_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            self.assertEqual(0, run_cmd(str(SET_TOKEN), "--instance", str(instance), "--token", "local-token", "--json").returncode)
            demo = run_cmd(str(DEMO_WORKUNITS), "--instance", str(instance), "--operator-token", "local-token", "--json")
            self.assertEqual(0, demo.returncode, demo.stdout + demo.stderr)
            demo_payload = json.loads(demo.stdout)
            hunt_id = demo_payload.get("hunt_id") or demo_payload["hunt"]["id"]

            plan = run_cmd(str(RUNNER), "--instance", str(instance), "--hunt-id", hunt_id, "plan", "--json")
            missing = run_cmd(str(RUNNER), "--instance", str(instance), "--hunt-id", hunt_id, "run-next", "--json")
            run_next = run_cmd(str(RUNNER), "--instance", str(instance), "--hunt-id", hunt_id, "--operator-token", "local-token", "run-next", "--json")
            summary = run_cmd(str(RUNNER), "--instance", str(instance), "--hunt-id", hunt_id, "summary", "--json")
            runner_demo = run_cmd(str(DEMO_RUNNER), "--instance", str(instance), "--operator-token", "local-token", "--json")

            self.assertEqual(0, plan.returncode, plan.stdout + plan.stderr)
            self.assertNotEqual(0, missing.returncode)
            for completed in (run_next, summary, runner_demo):
                self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
                self.assertEqual("pass", json.loads(completed.stdout)["status"])

    def test_validator_passes(self) -> None:
        completed = run_cmd(str(VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
