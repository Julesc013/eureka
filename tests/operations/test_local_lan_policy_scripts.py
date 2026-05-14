from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


class LocalLanPolicyScriptTests(unittest.TestCase):
    def test_lan_policy_check_reports_default_and_explicit_hosts(self) -> None:
        localhost = run_cmd("scripts/eureka_lan_policy_check.py", "--host", "127.0.0.1", "--json")
        rejected = run_cmd("scripts/eureka_lan_policy_check.py", "--host", "0.0.0.0", "--json")
        accepted = run_cmd("scripts/eureka_lan_policy_check.py", "--host", "0.0.0.0", "--bind-lan", "--json")
        self.assertEqual(0, localhost.returncode)
        self.assertEqual(0, rejected.returncode)
        self.assertEqual(0, accepted.returncode)
        self.assertTrue(json.loads(localhost.stdout)["host_allowed"])
        self.assertFalse(json.loads(rejected.stdout)["host_allowed"])
        self.assertTrue(json.loads(accepted.stdout)["host_allowed"])

    def test_validator_passes(self) -> None:
        completed = run_cmd("scripts/validate_local_lan_safety_gate.py", "--json", timeout=480)
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(payload["lan_mutations_blocked"])
        self.assertFalse(payload["actual_lan_smoke_performed"])


if __name__ == "__main__":
    unittest.main()
