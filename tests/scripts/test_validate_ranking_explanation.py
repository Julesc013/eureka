import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = (
    ROOT
    / "examples"
    / "evidence_weighted_ranking"
    / "minimal_strong_evidence_ranking_v0"
    / "RANKING_EXPLANATION.json"
)


class RankingExplanationValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_ranking_explanation.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_ranking_explanation.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_hard_booleans_and_text_are_safe(self) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "explanation_generated_by_runtime",
            "explanation_applied_to_live_search",
            "result_suppressed",
            "hidden_suppression_performed",
            "ranking_applied_to_live_search",
        ):
            self.assertFalse(page[key], key)
        self.assertTrue(page["item_explanations"])
        self.assertTrue(page["factor_explanations"])
        self.assertIn("not truth", page["public_user_text"].lower())
        self.assertIn("not applied to live search", page["public_user_text"].lower())

    def test_negative_explanation_applied_to_live_search_fails(self) -> None:
        self._assert_invalid(("explanation_applied_to_live_search",), True)

    def test_negative_private_path_fails(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\explanation.txt")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = page
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RANKING_EXPLANATION.json"
            path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_ranking_explanation.py", "--explanation", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
