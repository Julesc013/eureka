from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str, timeout: int = 240) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


class CleanMachineBootstrapScriptTests(unittest.TestCase):
    def test_bootstrap_creates_temp_checkout_and_validates_instance(self) -> None:
        completed = run_cmd("scripts/eureka_clean_machine_bootstrap.py", "--repo", ".", "--json")
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(payload["temp_checkout_created"])
        self.assertTrue(payload["instance_initialized"])
        self.assertTrue(payload["instance_validated"])
        self.assertTrue(payload["runtime_status_passed"])
        self.assertFalse(payload["hidden_state_copied"])

    def test_bootstrap_refuses_to_copy_forbidden_state_names(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        from eureka_clean_machine_bootstrap import ignore_forbidden_state

        ignored = ignore_forbidden_state("repo", ["eureka-instance", ".env", ".aide.local", "runtime"])
        self.assertIn("eureka-instance", ignored)
        self.assertIn(".env", ignored)
        self.assertIn(".aide.local", ignored)
        self.assertNotIn("runtime", ignored)

    def test_no_repo_root_instance_state_is_tracked(self) -> None:
        completed = subprocess.run(["git", "ls-files", "--", "eureka-instance"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual("", completed.stdout.strip())


if __name__ == "__main__":
    unittest.main()
