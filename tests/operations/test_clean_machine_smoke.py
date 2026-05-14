from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


class CleanMachineSmokeScriptTests(unittest.TestCase):
    def test_smoke_runs_service_workbench_auto_test_and_auto_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(
                "scripts/eureka_clean_machine_smoke.py",
                "--repo",
                ".",
                "--instance",
                str(instance),
                "--port",
                "0",
                "--json",
            )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertTrue(payload["localhost_server_started"])
        self.assertTrue(payload["service_smoke_passed"])
        self.assertTrue(payload["workbench_smoke_passed"])
        self.assertTrue(payload["auto_test_passed"])
        self.assertTrue(payload["auto_search_passed"])
        self.assertTrue(payload["server_shutdown_clean"])
        self.assertFalse(payload["site_dist_mutated"])
        self.assertFalse(payload["master_index_mutated"])

    def test_validator_passes_with_known_warning(self) -> None:
        completed = run_cmd("scripts/validate_clean_machine_bootstrap.py", "--json", timeout=600)
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(payload["temp_checkout_created"])
        self.assertTrue(payload["auto_test_passed"])
        self.assertFalse(payload["deployment_performed"])


if __name__ == "__main__":
    unittest.main()
