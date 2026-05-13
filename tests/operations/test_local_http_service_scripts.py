from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
SERVER = ROOT / "scripts" / "eureka_local_server.py"
SMOKE = ROOT / "scripts" / "eureka_local_service_smoke.py"
VALIDATOR = ROOT / "scripts" / "validate_local_http_service.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def payload(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout)


class LocalHTTPServiceScriptTests(unittest.TestCase):
    def test_server_script_requires_instance(self) -> None:
        completed = run_cmd(str(SERVER), "--json-startup")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("missing_instance", payload(completed)["error"])

    def test_server_script_refuses_write_mode(self) -> None:
        completed = run_cmd(str(SERVER), "--instance", "unused", "--write-mode", "--json-startup")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("write_mode_forbidden", payload(completed)["error"])

    def test_smoke_script_refuses_non_localhost_url(self) -> None:
        completed = run_cmd(str(SMOKE), "--base-url", "http://192.168.1.10:8765", "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("base_url_rejected", payload(completed)["error"])

    def test_smoke_script_passes_against_loopback_server(self) -> None:
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
                self.assertEqual("pass", startup["status"])
                completed = run_cmd(str(SMOKE), "--base-url", startup["base_url"], "--json")
                self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
                data = payload(completed)
                self.assertEqual("pass", data["status"])
                self.assertIs(data["status_route_passed"], True)
                self.assertIs(data["search_route_passed"], True)
                self.assertIs(data["absence_route_passed"], True)
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
