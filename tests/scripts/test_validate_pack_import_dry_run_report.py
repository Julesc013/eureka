import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_pack_import_dry_run_report.py"
AUDIT_REPORT = (
    REPO_ROOT
    / "control"
    / "audits"
    / "pack-import-local-dry-run-runtime-v0"
    / "pack_import_local_dry_run_runtime_report.json"
)


class ValidatePackImportDryRunReportTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_validates_audit_report(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_json_output_parses(self):
        result = self.run_cli("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")

    def test_negative_reports_fail(self):
        base = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        fields = [
            "authoritative_pack_import_runtime_implemented",
            "real_pack_staging_performed",
            "pack_content_executed",
            "pack_urls_followed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "master_index_mutated",
            "upload_endpoint_enabled",
            "promotion_decision_created",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for field in fields:
                candidate = dict(base)
                candidate[field] = True
                path = Path(tmp) / f"{field}.json"
                path.write_text(json.dumps(candidate), encoding="utf-8")
                result = self.run_cli("--report", str(path))
                self.assertNotEqual(result.returncode, 0, field)


if __name__ == "__main__":
    unittest.main()
