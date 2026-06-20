from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runtime.local.synthetic_truth_path import DEFAULT_OUTPUT_ROOT


REPO_ROOT = Path(__file__).resolve().parents[2]


class SyntheticTruthPathScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.out = REPO_ROOT / DEFAULT_OUTPUT_ROOT / "script-test"
        if self.out.exists():
            shutil.rmtree(self.out)

    def tearDown(self) -> None:
        if self.out.exists():
            shutil.rmtree(self.out)

    def test_cli_run_validate_status_rollback_and_snapshot(self) -> None:
        run = _run(
            "scripts/eureka_synthetic_truth_path.py",
            "run",
            "--scenario",
            "minimal-success",
            "--out",
            str(DEFAULT_OUTPUT_ROOT / "script-test"),
            "--json",
        )
        payload = json.loads(run.stdout)
        scenario_dir = payload["scenario_dir"]

        validate = _run("scripts/eureka_synthetic_truth_path.py", "validate", "--scenario-dir", scenario_dir, "--strict", "--json")
        status = _run("scripts/eureka_synthetic_truth_path.py", "status", "--scenario-dir", scenario_dir, "--json")
        snapshot = _run("scripts/eureka_synthetic_truth_path.py", "verify-snapshot", "--scenario-dir", scenario_dir, "--json")
        rollback = _run("scripts/eureka_synthetic_truth_path.py", "rollback", "--scenario-dir", scenario_dir, "--json")

        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(json.loads(validate.stdout)["status"], "pass")
        self.assertEqual(json.loads(status.stdout)["rollback_verified"], True)
        self.assertEqual(json.loads(snapshot.stdout)["verification_status"], "verified_local")
        self.assertEqual(json.loads(rollback.stdout)["index"]["baseline_result_restored"], True)

    def test_cli_rejects_output_outside_test_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_synthetic_truth_path.py",
                    "run",
                    "--scenario",
                    "minimal-success",
                    "--out",
                    temp_dir,
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("output must remain under", result.stderr)


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(f"{' '.join(args)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


if __name__ == "__main__":
    unittest.main()
