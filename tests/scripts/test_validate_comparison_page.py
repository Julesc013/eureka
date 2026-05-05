import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "comparison_pages" / "minimal_object_comparison_page_v0" / "COMPARISON_PAGE.json"


class ComparisonPageValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_comparison_page.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_comparison_page.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_hard_booleans_and_no_winner_are_safe(self) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "runtime_comparison_page_implemented",
            "persistent_comparison_page_store_implemented",
            "comparison_page_generated_from_live_source",
            "comparison_winner_claimed",
            "live_source_called",
            "external_calls_performed",
            "source_sync_worker_executed",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "candidate_promotion_performed",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "execution_enabled",
            "arbitrary_url_fetch_enabled",
            "rights_clearance_claimed",
            "malware_safety_claimed",
            "source_trust_claimed",
        ):
            self.assertFalse(page[key], key)
        self.assertGreaterEqual(len(page["subjects"]), 2)
        self.assertFalse(page["comparison_type"]["winner_allowed"])
        self.assertFalse(page["comparison_matrix"]["scoring_used_now"])
        self.assertFalse(page["comparison_matrix"]["ranking_used_now"])
        self.assertFalse(page["comparison_matrix"]["winner_selected_now"])
        self.assertFalse(page["identity_comparison"]["destructive_merge_allowed"])
        self.assertFalse(page["absence_near_miss_gap_comparison"]["global_absence_claimed"])
        self.assertFalse(page["representation_member_comparison"]["payload_included"])
        for cell in page["comparison_matrix"]["cells"]:
            self.assertTrue(cell["confidence_not_truth"])

    def test_negative_mutations_actions_and_winner_fail(self) -> None:
        for path, value in (
            (("runtime_comparison_page_implemented",), True),
            (("comparison_winner_claimed",), True),
            (("comparison_matrix", "winner_selected_now"), True),
            (("live_source_called",), True),
            (("downloads_enabled",), True),
            (("installs_enabled",), True),
            (("execution_enabled",), True),
            (("source_cache_mutated",), True),
            (("evidence_ledger_mutated",), True),
            (("master_index_mutated",), True),
            (("rights_clearance_claimed",), True),
            (("malware_safety_claimed",), True),
            (("source_trust_claimed",), True),
        ):
            with self.subTest(path=path):
                self._assert_invalid(path, value)

    def test_negative_private_path_fails(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\compare.txt")

    def test_negative_credential_like_value_fails(self) -> None:
        self._assert_invalid(("notes", 0), "api_key=example-value")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = page
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "COMPARISON_PAGE.json"
            tmp_path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_comparison_page.py", "--page", str(tmp_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
