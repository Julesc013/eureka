import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "result_merge" / "minimal_exact_duplicate_group_v0" / "DEDUPLICATION_ASSESSMENT.json"


class DeduplicationAssessmentValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_deduplication_assessment.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_deduplication_assessment.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_hard_booleans_are_safe(self) -> None:
        assessment = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "runtime_deduplication_implemented",
            "deduplication_applied_to_live_search",
            "records_merged",
            "results_suppressed",
            "results_hidden_without_explanation",
            "destructive_merge_performed",
            "ranking_changed",
            "candidate_promotion_performed",
            "master_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "live_source_called",
            "external_calls_performed",
            "telemetry_exported",
        ):
            self.assertFalse(assessment[key], key)
        self.assertGreaterEqual(len(assessment["assessed_results"]), 2)
        self.assertFalse(assessment["grouping_decision"]["grouping_applied_now"])
        self.assertTrue(assessment["grouping_decision"]["decision_not_truth"])
        self.assertFalse(assessment["display_decision"]["canonical_record_claimed_as_truth"])
        self.assertTrue(assessment["display_decision"]["alternative_results_preserved"])
        self.assertTrue(assessment["review"]["destructive_merge_forbidden"])
        self.assertTrue(assessment["review"]["ranking_change_forbidden"])

    def test_negative_assessment_failures(self) -> None:
        for path, value in (
            (("deduplication_applied_to_live_search",), True),
            (("results_suppressed",), True),
            (("results_hidden_without_explanation",), True),
            (("ranking_changed",), True),
            (("master_index_mutated",), True),
            (("records_merged",), True),
        ):
            with self.subTest(path=path):
                self._assert_invalid(path, value)

    def test_negative_private_path_fails(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\dedup.txt")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        assessment = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = assessment
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "DEDUPLICATION_ASSESSMENT.json"
            path.write_text(json.dumps(assessment), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_deduplication_assessment.py", "--assessment", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
