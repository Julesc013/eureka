from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class LocalWorkerScriptTests(unittest.TestCase):
    def test_worker_runner_requires_instance(self) -> None:
        completed = run_cmd("scripts/eureka_worker_runner.py", "list-workers", "--json")
        self.assertNotEqual(0, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("missing_instance", payload["error"])

    def test_worker_runner_cli_and_demo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            create = run_cmd(
                "scripts/eureka_workunit_queue.py",
                "--instance",
                str(instance),
                "create",
                "--kind",
                "regression_test",
                "--title",
                "Script worker sample",
                "--payload-json",
                "{\"worker_kind\":\"noop_worker\"}",
                "--json",
            )
            self.assertEqual(0, create.returncode, create.stderr)
            listing = run_cmd("scripts/eureka_worker_runner.py", "--instance", str(instance), "list-workers", "--json")
            self.assertEqual(0, listing.returncode, listing.stderr)
            self.assertIn("source_probe_worker", listing.stdout)
            run_next = run_cmd("scripts/eureka_worker_runner.py", "--instance", str(instance), "run-next", "--kind", "noop_worker", "--json")
            self.assertEqual(0, run_next.returncode, run_next.stderr)
            payload = json.loads(run_next.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertEqual("complete", payload["worker_results"][0]["status"])
            disabled = run_cmd("scripts/eureka_worker_runner.py", "--instance", str(instance), "run-next", "--kind", "source_probe_worker", "--json")
            self.assertNotEqual(0, disabled.returncode)
            disabled_payload = json.loads(disabled.stdout)
            self.assertEqual("disabled_worker_kind", disabled_payload["error"])
            demo = run_cmd("scripts/demo_local_worker_runner.py", "--instance", str(instance), "--json")
            self.assertEqual(0, demo.returncode, demo.stderr)
            demo_payload = json.loads(demo.stdout)
            self.assertTrue(demo_payload["blocked_disabled_worker_kind"])

    def test_validator_passes(self) -> None:
        completed = run_cmd("scripts/validate_local_worker_runner.py", "--json")
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(payload["noop_worker_passed"])
        self.assertTrue(payload["source_probe_worker_blocked"])


if __name__ == "__main__":
    unittest.main()
