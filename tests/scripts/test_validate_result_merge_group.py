import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "result_merge" / "minimal_exact_duplicate_group_v0" / "RESULT_MERGE_GROUP.json"


class ResultMergeGroupValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_result_merge_group.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_result_merge_group.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_hard_booleans_and_transparency_are_safe(self) -> None:
        group = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "runtime_result_merge_implemented",
            "persistent_merge_group_store_implemented",
            "public_search_runtime_grouping_enabled",
            "public_search_ranking_changed",
            "records_merged",
            "duplicates_deleted",
            "results_hidden_without_explanation",
            "destructive_merge_performed",
            "canonical_record_claimed_as_truth",
            "candidate_promotion_performed",
            "master_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "live_source_called",
            "external_calls_performed",
            "downloads_enabled",
            "installs_enabled",
            "execution_enabled",
            "telemetry_exported",
        ):
            self.assertFalse(group[key], key)
        self.assertGreaterEqual(len(group["grouped_results"]), 2)
        self.assertTrue(group["group_relation"]["relation_claim_not_truth"])
        self.assertFalse(group["group_relation"]["destructive_merge_allowed"])
        self.assertTrue(group["merge_group_identity"]["group_label_not_truth"])
        self.assertFalse(group["canonical_display_record"]["canonical_record_claimed_as_truth"])
        self.assertTrue(group["canonical_display_record"]["alternative_results_preserved"])
        self.assertFalse(group["collapsed_results"]["hidden_without_explanation"])
        self.assertTrue(group["collapsed_results"]["conflict_results_must_not_be_hidden"])

    def test_exact_duplicate_has_strong_evidence(self) -> None:
        group = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(group["group_relation"]["relation_type"], "exact_duplicate_result")
        strong = [item for item in group["grouping_criteria"] if item["strength"] == "strong" and item["passed"]]
        self.assertTrue(strong)

    def test_negative_group_failures(self) -> None:
        for path, value in (
            (("runtime_result_merge_implemented",), True),
            (("records_merged",), True),
            (("duplicates_deleted",), True),
            (("destructive_merge_performed",), True),
            (("collapsed_results", "hidden_without_explanation"), True),
            (("canonical_display_record", "canonical_record_claimed_as_truth"), True),
            (("public_search_ranking_changed",), True),
            (("master_index_mutated",), True),
        ):
            with self.subTest(path=path):
                self._assert_invalid(path, value)

    def test_negative_exact_duplicate_without_strong_evidence_fails(self) -> None:
        group = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        group["grouping_criteria"] = [
            {
                "criterion_id": "weak-title",
                "criterion_type": "normalized_title_match",
                "strength": "weak",
                "passed": True,
                "evidence_refs": [],
                "limitations": [],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RESULT_MERGE_GROUP.json"
            path.write_text(json.dumps(group), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_result_merge_group.py", "--group", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")

    def test_negative_private_path_and_secret_fail(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\merge.txt")
        self._assert_invalid(("notes", 0), "api_key=example-value")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        group = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = group
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RESULT_MERGE_GROUP.json"
            path.write_text(json.dumps(group), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_result_merge_group.py", "--group", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
