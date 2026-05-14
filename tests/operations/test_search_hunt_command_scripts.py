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
COMMAND = ROOT / "scripts" / "eureka_search_hunt_command.py"
DEMO = ROOT / "scripts" / "demo_search_hunt_commands.py"
VALIDATOR = ROOT / "scripts" / "validate_search_hunt_commands.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class SearchHuntCommandScriptTests(unittest.TestCase):
    def test_cli_requires_operator_token_for_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            created = run_cmd(str(HUNT), "--instance", str(instance), "create", "--query", "sampleproject", "--json")
            self.assertEqual(0, created.returncode, created.stderr)
            hunt_id = json.loads(created.stdout)["session"]["id"]

            missing = run_cmd(str(COMMAND), "--instance", str(instance), "pause", "--id", hunt_id, "--reason", "test", "--json")
            self.assertEqual(2, missing.returncode)
            self.assertEqual("fail", json.loads(missing.stdout)["status"])

    def test_cli_commands_and_demo_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            self.assertEqual(0, run_cmd(str(SET_TOKEN), "--instance", str(instance), "--token", "local-token", "--json").returncode)
            created = run_cmd(str(HUNT), "--instance", str(instance), "create", "--query", "sampleproject", "--json")
            self.assertEqual(0, created.returncode, created.stderr)
            hunt_id = json.loads(created.stdout)["session"]["id"]
            pause = run_cmd(str(COMMAND), "--instance", str(instance), "--operator-token", "local-token", "pause", "--id", hunt_id, "--reason", "test", "--json")
            resume = run_cmd(str(COMMAND), "--instance", str(instance), "--operator-token", "local-token", "resume", "--id", hunt_id, "--reason", "test", "--json")
            steer = run_cmd(str(COMMAND), "--instance", str(instance), "--operator-token", "local-token", "steer", "--id", hunt_id, "--type", "metadata_only", "--json")
            listing = run_cmd(str(COMMAND), "--instance", str(instance), "commands", "--id", hunt_id, "--json")
            demo = run_cmd(str(DEMO), "--instance", str(instance), "--operator-token", "local-token", "--json")

            for completed in (pause, resume, steer, listing, demo):
                self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
                self.assertEqual("pass", json.loads(completed.stdout)["status"])

    def test_validator_passes(self) -> None:
        completed = run_cmd(str(VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
