from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_deep_extraction_runtime_plan.py"
REPORT = (
    REPO_ROOT
    / "control"
    / "audits"
    / "deep-extraction-runtime-planning-v0"
    / "deep_extraction_runtime_planning_report.json"
)


class ValidateDeepExtractionRuntimePlanTest(unittest.TestCase):
    def run_validator(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def test_validator_passes(self) -> None:
        completed = self.run_validator()
        self.assertIn("status: valid", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = self.run_validator("--json")
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])

    def assert_report_toggle_fails(self, key: str) -> None:
        data = json.loads(REPORT.read_text(encoding="utf-8"))
        data[key] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
            completed = self.run_validator("--report", str(path), "--json", check=False)
        self.assertNotEqual(completed.returncode, 0, key)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(any(key in error for error in payload["errors"]))

    def test_negative_runtime_extraction_implemented_fails(self) -> None:
        self.assert_report_toggle_fails("runtime_extraction_implemented")

    def test_negative_extraction_executed_fails(self) -> None:
        self.assert_report_toggle_fails("extraction_executed")

    def test_negative_files_opened_fails(self) -> None:
        self.assert_report_toggle_fails("files_opened")

    def test_negative_archive_unpacked_fails(self) -> None:
        self.assert_report_toggle_fails("archive_unpacked")

    def test_negative_arbitrary_local_path_enabled_fails(self) -> None:
        self.assert_report_toggle_fails("arbitrary_local_path_enabled")

    def test_negative_url_fetched_fails(self) -> None:
        self.assert_report_toggle_fails("URL_fetched")

    def test_negative_payload_executed_fails(self) -> None:
        self.assert_report_toggle_fails("payload_executed")

    def test_negative_ocr_performed_fails(self) -> None:
        self.assert_report_toggle_fails("OCR_performed")

    def test_negative_source_cache_mutated_fails(self) -> None:
        self.assert_report_toggle_fails("source_cache_mutated")

    def test_negative_evidence_ledger_mutated_fails(self) -> None:
        self.assert_report_toggle_fails("evidence_ledger_mutated")

    def test_negative_master_index_mutated_fails(self) -> None:
        self.assert_report_toggle_fails("master_index_mutated")


if __name__ == "__main__":
    unittest.main()

