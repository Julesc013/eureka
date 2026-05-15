import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SearchHuntWorkbenchSmokeScriptsTests(unittest.TestCase):
    def test_workbench_and_api_smoke_scripts_pass(self) -> None:
        process: subprocess.Popen[str] | None = None
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            run("scripts/eureka_init_instance.py", "--instance", str(instance), "--json")
            run("scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json")
            run("scripts/eureka_hunt_workflow_smoke.py", "--instance", str(instance), "--operator-token", "validator-token", "--json")
            try:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "scripts/eureka_local_server.py",
                        "--instance",
                        str(instance),
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "0",
                        "--operator-token",
                        "validator-token",
                        "--json-startup",
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                startup = json.loads(process.stdout.readline())
                base_url = startup["base_url"]
                workbench = run("scripts/eureka_hunt_workbench_smoke.py", "--base-url", base_url, "--instance", str(instance), "--operator-token", "validator-token", "--json")
                api = run("scripts/eureka_hunt_api_smoke.py", "--base-url", base_url, "--json")
            finally:
                if process is not None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                    if process.stdout is not None:
                        process.stdout.close()
                    if process.stderr is not None:
                        process.stderr.close()
        self.assertEqual("pass", json.loads(workbench.stdout)["status"])
        self.assertEqual("pass", json.loads(api.stdout)["status"])


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True, timeout=90)


if __name__ == "__main__":
    unittest.main()
