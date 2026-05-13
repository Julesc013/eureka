from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
SERVER = ROOT / "scripts" / "eureka_local_server.py"
WORKBENCH_SMOKE = ROOT / "scripts" / "eureka_local_workbench_smoke.py"
SERVICE_SMOKE = ROOT / "scripts" / "eureka_local_service_smoke.py"
VALIDATOR = ROOT / "scripts" / "validate_local_html_workbench.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def payload(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout)


class LocalWorkbenchScriptTests(unittest.TestCase):
    def test_workbench_smoke_refuses_non_localhost_url(self) -> None:
        completed = run_cmd(str(WORKBENCH_SMOKE), "--base-url", "http://192.168.1.10:8765", "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("base_url_rejected", payload(completed)["error"])

    def test_workbench_smoke_passes_against_loopback_server(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            process = subprocess.Popen(
                [
                    "python",
                    str(SERVER),
                    "--instance",
                    str(instance),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "0",
                    "--json-startup",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                startup_line = process.stdout.readline() if process.stdout is not None else ""
                if not startup_line:
                    self.fail(process.stderr.read() if process.stderr is not None else "server did not report startup")
                startup = json.loads(startup_line)
                workbench = run_cmd(str(WORKBENCH_SMOKE), "--base-url", startup["base_url"], "--json")
                service = run_cmd(str(SERVICE_SMOKE), "--base-url", startup["base_url"], "--json")
                self.assertEqual(0, workbench.returncode, workbench.stdout + workbench.stderr)
                self.assertEqual(0, service.returncode, service.stdout + service.stderr)
                data = payload(workbench)
                self.assertEqual("pass", data["status"])
                self.assertIs(data["home_page_passed"], True)
                self.assertIs(data["json_api_still_passed"], True)
                self.assertIs(data["mutation_controls_found"], False)
                self.assertIs(data["external_assets_found"], False)
            finally:
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

    def test_validator_passes(self) -> None:
        completed = run_cmd(str(VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
