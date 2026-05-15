from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
SET_TOKEN = ROOT / "scripts" / "eureka_set_operator_token.py"
HUNT = ROOT / "scripts" / "eureka_search_hunt.py"
HUNT_TO_NEED = ROOT / "scripts" / "eureka_hunt_to_search_need.py"
NEED_TO_WORK = ROOT / "scripts" / "eureka_need_to_workunits.py"
NEED = ROOT / "scripts" / "eureka_search_need.py"
DEMO = ROOT / "scripts" / "demo_hunt_to_workunits.py"
VALIDATOR = ROOT / "scripts" / "validate_hunt_to_workunits.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class NeedToWorkUnitScriptTests(unittest.TestCase):
    def test_cli_plan_create_list_and_demo_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            self.assertEqual(0, run_cmd(str(SET_TOKEN), "--instance", str(instance), "--token", "local-token", "--json").returncode)
            hunt_payload = json.loads(run_cmd(str(HUNT), "--instance", str(instance), "create", "--query", "sampleproject", "--json").stdout)
            hunt_id = hunt_payload["session"]["id"]
            need_payload = json.loads(
                run_cmd(str(HUNT_TO_NEED), "--instance", str(instance), "--operator-token", "local-token", "--hunt-id", hunt_id, "--json").stdout
            )
            need_id = need_payload["need"]["id"]

            plan = run_cmd(str(NEED_TO_WORK), "--instance", str(instance), "--need-id", need_id, "--plan-only", "--json")
            missing = run_cmd(str(NEED_TO_WORK), "--instance", str(instance), "--need-id", need_id, "--create", "--json")
            created = run_cmd(str(NEED_TO_WORK), "--instance", str(instance), "--need-id", need_id, "--operator-token", "local-token", "--create", "--json")
            listed = run_cmd(str(NEED), "--instance", str(instance), "workunits", "--id", need_id, "--json")
            demo = run_cmd(str(DEMO), "--instance", str(instance), "--operator-token", "local-token", "--json")

            self.assertEqual(0, plan.returncode, plan.stdout + plan.stderr)
            self.assertEqual(2, missing.returncode)
            for completed in (created, listed, demo):
                self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
                self.assertEqual("pass", json.loads(completed.stdout)["status"])

    def test_validator_passes(self) -> None:
        completed = run_cmd(str(VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
