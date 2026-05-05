import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_page_dry_run_report.py"
AUDIT_REPORT = REPO_ROOT / "control" / "audits" / "object-source-comparison-page-local-dry-run-runtime-v0" / "page_local_dry_run_runtime_report.json"


class ValidatePageDryRunReportTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_validates_audit_report(self) -> None:
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_json_parses(self) -> None:
        result = self.run_script("--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")

    def test_negative_hard_booleans_fail(self) -> None:
        base = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        for field in (
            "hosted_runtime_enabled",
            "public_routes_added",
            "public_search_runtime_mutated",
            "live_source_called",
            "source_cache_read",
            "evidence_ledger_read",
            "master_index_mutated",
            "downloads_enabled",
        ):
            with self.subTest(field=field):
                mutated = copy.deepcopy(base)
                mutated[field] = True
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "bad.json"
                    path.write_text(json.dumps(mutated), encoding="utf-8")
                    result = self.run_script("--report", str(path))
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
