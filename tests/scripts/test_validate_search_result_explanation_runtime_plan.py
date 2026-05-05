from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_search_result_explanation_runtime_plan.py"
REPORT = (
    REPO_ROOT
    / "control"
    / "audits"
    / "search-result-explanation-runtime-planning-v0"
    / "search_result_explanation_runtime_planning_report.json"
)


class ValidateSearchResultExplanationRuntimePlanTest(unittest.TestCase):
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

    def test_negative_runtime_explanation_implemented_fails(self) -> None:
        self.assert_report_toggle_fails("runtime_explanation_implemented")

    def test_negative_public_search_response_changed_fails(self) -> None:
        self.assert_report_toggle_fails("public_search_response_changed")

    def test_negative_public_search_routes_changed_fails(self) -> None:
        self.assert_report_toggle_fails("public_search_routes_changed")

    def test_negative_explanation_api_routes_enabled_fails(self) -> None:
        self.assert_report_toggle_fails("explanation_api_routes_enabled")

    def test_negative_model_call_performed_fails(self) -> None:
        self.assert_report_toggle_fails("model_call_performed")

    def test_negative_hidden_score_used_fails(self) -> None:
        self.assert_report_toggle_fails("hidden_score_used")

    def test_negative_result_suppressed_fails(self) -> None:
        self.assert_report_toggle_fails("result_suppressed")

    def test_negative_source_cache_read_fails(self) -> None:
        self.assert_report_toggle_fails("source_cache_read")

    def test_negative_evidence_ledger_read_fails(self) -> None:
        self.assert_report_toggle_fails("evidence_ledger_read")

    def test_negative_source_cache_mutated_fails(self) -> None:
        self.assert_report_toggle_fails("source_cache_mutated")

    def test_negative_evidence_ledger_mutated_fails(self) -> None:
        self.assert_report_toggle_fails("evidence_ledger_mutated")

    def test_negative_master_index_mutated_fails(self) -> None:
        self.assert_report_toggle_fails("master_index_mutated")


if __name__ == "__main__":
    unittest.main()

