from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]


class EurekaE2EEvalScriptsTests(unittest.TestCase):
    def test_list_and_explain_commands_emit_json(self) -> None:
        listed = self._run("list", "--json")
        payload = json.loads(listed.stdout)
        self.assertEqual(36, payload["case_count"])
        self.assertEqual("pass", payload["validation"]["status"])

        explained = self._run("explain", "--case", "boundary_privacy_canaries", "--json")
        case = json.loads(explained.stdout)["case"]
        self.assertEqual("critical", case["criticality"])
        self.assertIn("authority_proof", case["proof_levels"])

    def test_run_validate_status_and_compare(self) -> None:
        run = self._run(
            "run",
            "--case",
            "boundary_privacy_canaries",
            "--out",
            ".eureka/e2e-reference/eval/test-cli",
            "--json",
        )
        summary = json.loads(run.stdout)
        self.assertEqual("PASS", summary["overall_gate_status"])

        run_dir = f".eureka/e2e-reference/eval/test-cli/{summary['execution_id']}"
        validated = self._run("validate", "--run-dir", run_dir, "--strict", "--json")
        self.assertEqual("pass", json.loads(validated.stdout)["status"])

        status = self._run("status", "--run-dir", run_dir, "--json")
        self.assertEqual("PASS", json.loads(status.stdout)["overall_gate_status"])

        compared = self._run(
            "compare",
            "--left",
            "evals/e2e_reference/oracle/baselines/reference_v0.json",
            "--right",
            run_dir,
            "--json",
        )
        comparison = json.loads(compared.stdout)
        self.assertEqual("PASS", comparison["right_status"])
        self.assertIn("boundary_privacy_canaries", comparison["changed_cases"])

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, "scripts/eureka_e2e_eval.py", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        return completed


if __name__ == "__main__":
    unittest.main()
