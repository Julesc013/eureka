import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runtime.engine.ranking.dry_run import run_public_search_ranking_dry_run


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_public_search_ranking_dry_run_report.py"


class ValidatePublicSearchRankingDryRunReportScriptTests(unittest.TestCase):
    def run_validator(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_validates_audit_report(self):
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: valid", result.stdout)

    def test_json_output_parses(self):
        result = self.run_validator("--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")

    def test_negative_hard_boolean_reports_fail(self):
        false_keys = [
            "public_search_order_changed",
            "public_search_response_changed",
            "hidden_scores_enabled",
            "result_suppression_enabled",
            "model_call_performed",
            "telemetry_signal_used",
            "source_cache_read",
            "evidence_ledger_read",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "master_index_mutated",
        ]
        base = run_public_search_ranking_dry_run([Path("examples/public_search_ranking_dry_run")]).to_dict()
        with tempfile.TemporaryDirectory() as temp_dir:
            for key in false_keys:
                payload = json.loads(json.dumps(base))
                payload["hard_booleans"][key] = True
                report = Path(temp_dir) / f"{key}.json"
                report.write_text(json.dumps(payload), encoding="utf-8")
                with self.subTest(key=key):
                    result = self.run_validator("--report", str(report))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(f"{key} must be false", result.stdout)


if __name__ == "__main__":
    unittest.main()
