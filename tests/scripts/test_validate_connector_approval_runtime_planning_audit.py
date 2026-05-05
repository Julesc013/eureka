import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "connector-approval-runtime-planning-audit-v0"
REPORT = AUDIT / "connector_approval_runtime_planning_audit_report.json"
INVENTORY = ROOT / "control" / "inventory" / "connectors" / "connector_approval_runtime_planning_status.json"
DOC = ROOT / "docs" / "operations" / "CONNECTOR_APPROVAL_RUNTIME_PLANNING_AUDIT.md"


class ConnectorApprovalRuntimePlanningAuditValidatorTests(unittest.TestCase):
    def test_validator_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_connector_approval_runtime_planning_audit.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_validator_json_parses(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_connector_approval_runtime_planning_audit.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")

    def test_negative_hard_booleans_fail(self):
        cases = (
            "external_calls_performed",
            "public_search_connector_fanout_enabled",
            "live_connector_runtime_enabled",
            "credentials_configured",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "master_index_mutated",
        )
        for field in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                report_path = Path(tmp) / "report.json"
                payload = json.loads(REPORT.read_text(encoding="utf-8"))
                payload[field] = True
                report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                completed = subprocess.run(
                    [
                        sys.executable,
                        "scripts/validate_connector_approval_runtime_planning_audit.py",
                        "--audit-dir",
                        str(AUDIT),
                        "--report",
                        str(report_path),
                        "--inventory",
                        str(INVENTORY),
                        "--doc",
                        str(DOC),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(field, completed.stdout)


if __name__ == "__main__":
    unittest.main()
