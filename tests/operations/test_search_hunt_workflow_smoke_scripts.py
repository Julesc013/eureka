import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SearchHuntWorkflowSmokeScriptsTests(unittest.TestCase):
    def test_workflow_smoke_and_demo_scripts_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            run("scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
            run("scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")
            workflow = run("scripts/eureka_hunt_workflow_smoke.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")
            demo = run("scripts/demo_search_hunt_workflow.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")
        self.assertEqual("pass", json.loads(workflow.stdout)["status"])
        self.assertEqual("pass", json.loads(demo.stdout)["status"])


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True, timeout=90)


if __name__ == "__main__":
    unittest.main()
