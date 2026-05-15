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
NEED = ROOT / "scripts" / "eureka_search_need.py"
DEMO = ROOT / "scripts" / "demo_hunt_to_search_need.py"
VALIDATOR = ROOT / "scripts" / "validate_hunt_to_search_need.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class SearchNeedScriptTests(unittest.TestCase):
    def test_cli_requires_operator_token_for_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            created = run_cmd(str(HUNT), "--instance", str(instance), "create", "--query", "sampleproject", "--json")
            self.assertEqual(0, created.returncode, created.stderr)
            hunt_id = json.loads(created.stdout)["session"]["id"]
            missing = run_cmd(str(HUNT_TO_NEED), "--instance", str(instance), "--hunt-id", hunt_id, "--json")

            self.assertEqual(2, missing.returncode)
            self.assertEqual("fail", json.loads(missing.stdout)["status"])

    def test_cli_create_list_show_transition_and_demo_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            self.assertEqual(0, run_cmd(str(SET_TOKEN), "--instance", str(instance), "--token", "local-token", "--json").returncode)
            created = run_cmd(str(HUNT), "--instance", str(instance), "create", "--query", "sampleproject", "--json")
            self.assertEqual(0, created.returncode, created.stderr)
            hunt_id = json.loads(created.stdout)["session"]["id"]
            made = run_cmd(str(HUNT_TO_NEED), "--instance", str(instance), "--operator-token", "local-token", "--hunt-id", hunt_id, "--json")
            self.assertEqual(0, made.returncode, made.stdout + made.stderr)
            need_id = json.loads(made.stdout)["need"]["id"]
            listed = run_cmd(str(NEED), "--instance", str(instance), "list", "--json")
            shown = run_cmd(str(NEED), "--instance", str(instance), "show", "--id", need_id, "--with-transitions", "--json")
            transitioned = run_cmd(str(NEED), "--instance", str(instance), "transition", "--id", need_id, "--state", "open", "--operator-token", "local-token", "--json")
            demo = run_cmd(str(DEMO), "--instance", str(instance), "--operator-token", "local-token", "--json")

            for completed in (listed, shown, transitioned, demo):
                self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
                self.assertEqual("pass", json.loads(completed.stdout)["status"])

    def test_validator_passes(self) -> None:
        completed = run_cmd(str(VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
