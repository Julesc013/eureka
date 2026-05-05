import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "public-search-runtime-integration-audit-v0"
REPORT = AUDIT / "public_search_runtime_integration_audit_report.json"
INVENTORY = ROOT / "control" / "inventory" / "publication" / "public_search_runtime_integration_status.json"
DOC = ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RUNTIME_INTEGRATION_AUDIT.md"


class PublicSearchRuntimeIntegrationAuditValidatorTests(unittest.TestCase):
    def test_validator_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_search_runtime_integration_audit.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_validator_json_parses(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_search_runtime_integration_audit.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")

    def test_negative_hard_booleans_fail(self):
        cases = (
            "public_search_runtime_mutated",
            "source_cache_dry_run_integrated_with_public_search",
            "connector_runtime_integrated_with_public_search",
            "public_search_live_source_fanout_enabled",
            "public_search_order_changed",
            "telemetry_enabled",
            "downloads_enabled",
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
                        "scripts/validate_public_search_runtime_integration_audit.py",
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

    def test_negative_missing_audit_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit_copy = Path(tmp) / "audit"
            shutil.copytree(AUDIT, audit_copy)
            (audit_copy / "MUTATION_BOUNDARY_STATUS.md").unlink()
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_public_search_runtime_integration_audit.py",
                    "--audit-dir",
                    str(audit_copy),
                    "--report",
                    str(REPORT),
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
            self.assertIn("MUTATION_BOUNDARY_STATUS.md", completed.stdout)


if __name__ == "__main__":
    unittest.main()
