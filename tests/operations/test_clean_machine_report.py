from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_SAMPLE = ROOT / "control" / "audits" / "local-13-clean-machine-bootstrap-v0" / "generated" / "sample_clean_machine_bootstrap_result.json"
SMOKE_SAMPLE = ROOT / "control" / "audits" / "local-13-clean-machine-bootstrap-v0" / "generated" / "sample_clean_machine_smoke_result.json"


def run_cmd(*args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)


class CleanMachineReportScriptTests(unittest.TestCase):
    def test_report_records_external_proof_not_performed_honestly(self) -> None:
        completed = run_cmd(
            "scripts/eureka_clean_machine_report.py",
            "--bootstrap-result",
            str(BOOTSTRAP_SAMPLE),
            "--smoke-result",
            str(SMOKE_SAMPLE),
            "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass_with_warnings", payload["status"])
        self.assertFalse(payload["actual_second_machine_proof_performed"])
        self.assertFalse(payload["deployment_performed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])

    def test_report_writes_markdown_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.md"
            completed = run_cmd(
                "scripts/eureka_clean_machine_report.py",
                "--bootstrap-result",
                str(BOOTSTRAP_SAMPLE),
                "--smoke-result",
                str(SMOKE_SAMPLE),
                "--output",
                str(output),
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("Clean-Machine Bootstrap Summary", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
