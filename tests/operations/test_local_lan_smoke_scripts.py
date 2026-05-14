from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


class LocalLanSmokeScriptTests(unittest.TestCase):
    def test_read_only_probe_refuses_public_host(self) -> None:
        completed = run_cmd("scripts/eureka_lan_read_only_probe.py", "--base-url", "http://example.com:8765", "--json")
        self.assertNotEqual(0, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("fail", payload["status"])
        self.assertFalse(payload["external_internet_used"])

    def test_lan_smoke_script_runs_same_machine_bind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = run_cmd(
                "scripts/eureka_lan_smoke.py",
                "--instance",
                str(Path(tmp) / "eureka-instance"),
                "--host",
                "0.0.0.0",
                "--port",
                "0",
                "--bind-lan",
                "--read-only",
                "--json",
                timeout=240,
            )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(payload["same_machine_lan_bind_smoke_passed"])
        self.assertFalse(payload["external_client_smoke_performed"])

    def test_validator_passes(self) -> None:
        completed = run_cmd("scripts/validate_local_lan_smoke.py", "--json", timeout=600)
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(payload["same_machine_lan_bind_smoke_passed"])
        self.assertFalse(payload["source_probe_executed"])


if __name__ == "__main__":
    unittest.main()
