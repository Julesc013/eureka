import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_REPORT = ROOT / "control/audits/evidence-ledger-local-dry-run-runtime-v0/evidence_ledger_local_dry_run_runtime_report.json"


class ValidateEvidenceLedgerDryRunReportTests(unittest.TestCase):
    def test_validates_audit_report(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_evidence_ledger_dry_run_report.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_json_output_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_evidence_ledger_dry_run_report.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")

    def test_negative_hard_boolean_reports_fail(self) -> None:
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))["dry_run_results"]
        for key in (
            "live_source_called",
            "evidence_ledger_mutated",
            "source_cache_mutated",
            "public_index_mutated",
            "credentials_used",
            "claim_accepted_as_truth",
            "promotion_decision_created",
        ):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as tmp:
                mutated = json.loads(json.dumps(report))
                mutated["hard_booleans"][key] = True
                path = Path(tmp) / "report.json"
                path.write_text(json.dumps(mutated, indent=2), encoding="utf-8")
                completed = subprocess.run(
                    [sys.executable, "scripts/validate_evidence_ledger_dry_run_report.py", "--report", str(path)],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(key, completed.stdout)


if __name__ == "__main__":
    unittest.main()
