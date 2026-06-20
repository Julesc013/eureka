from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = REPO_ROOT / "scripts" / "eureka.py"


class PortableEurekaCleanMachineTests(unittest.TestCase):
    def run_cli(self, instance: Path, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, str(CLI), "--instance", str(instance), *args, "--json"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def test_clean_machine_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "clean machine instance"
            self.assertFalse(instance.exists())

            bootstrap = self.run_cli(instance, "bootstrap")
            self.assertEqual(bootstrap["status"], "pass")
            self.assertTrue(instance.is_dir())

            second_bootstrap = self.run_cli(instance, "bootstrap")
            self.assertIn(second_bootstrap["status"], {"pass", "pass_with_warnings"})

            doctor = self.run_cli(instance, "doctor", "--strict")
            self.assertIn(doctor["status"], {"pass", "pass_with_warnings"})

            oracle = self.run_cli(instance, "test", "--suite", "core")
            self.assertEqual(oracle["status"], "pass")

            hunt = self.run_cli(instance, "hunt", "old blue FTP client for XP")
            self.assertEqual(hunt["status"], "pass")
            self.assertTrue(hunt["run_id"])

            replay = self.run_cli(instance, "replay", str(hunt["run_id"]), "--strict")
            self.assertEqual(replay["status"], "pass")

            status = self.run_cli(instance, "status")
            self.assertEqual(status["status"], "pass")
            self.assertFalse(status["provider_network_calls"])
            self.assertFalse(status["public_exposure"])

            smoke = self.run_cli(instance, "serve", "--mode", "exploration", "--host", "127.0.0.1", "--port", "0", "--smoke")
            self.assertEqual(smoke["status"], "pass")
            self.assertFalse((instance / "run" / "eureka-portable-server.lock").exists())

            for child in Path(tmp).iterdir():
                self.assertEqual(child.resolve(), instance.resolve())


if __name__ == "__main__":
    unittest.main()
