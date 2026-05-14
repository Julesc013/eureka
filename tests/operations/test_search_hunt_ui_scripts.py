from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
SMOKE = ROOT / "scripts" / "eureka_search_hunt_ui_smoke.py"
VALIDATOR = ROOT / "scripts" / "validate_search_hunt_ui.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class SearchHuntUiScriptTests(unittest.TestCase):
    def test_smoke_refuses_non_localhost_url(self) -> None:
        completed = run_cmd(str(SMOKE), "--base-url", "http://example.com:8765", "--json")
        self.assertEqual(2, completed.returncode)
        self.assertEqual("fail", json.loads(completed.stdout)["status"])

    def test_smoke_script_passes_against_local_server(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            run_cmd("scripts/eureka_search_hunt.py", "--instance", str(instance), "create", "--query", "sampleproject", "--idempotency-key", "ui-script", "--json")
            process = subprocess.Popen(
                ["python", "scripts/eureka_local_server.py", "--instance", str(instance), "--host", "127.0.0.1", "--port", "0", "--json-startup"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                startup_line = process.stdout.readline() if process.stdout is not None else ""
                self.assertTrue(startup_line)
                base_url = json.loads(startup_line)["base_url"]
                completed = run_cmd(str(SMOKE), "--base-url", base_url, "--json")
                self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertEqual("pass", payload["status"])
                self.assertFalse(payload["mutation_controls_found"])
                self.assertFalse(payload["external_assets_found"])
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
