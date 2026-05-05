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
    / "EVIDENCE_WEIGHTED_RANKING_ASSESSMENT.json"
)


class EvidenceWeightedRankingAssessmentValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_evidence_weighted_ranking_assessment.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_evidence_weighted_ranking_assessment.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_hard_booleans_are_safe(self) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "runtime_ranking_implemented",
            "ranking_applied_to_live_search",
            "public_search_order_changed",
            "result_suppressed",
            "hidden_suppression_performed",
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
            "popularity_signal_used",
            "user_profile_signal_used",
            "ad_signal_used",
            "model_call_performed",
        ):
            self.assertFalse(page[key], key)
        self.assertGreaterEqual(len(page["ranked_items"]), 2)
        self.assertTrue(all(not item["rank_changed_now"] for item in page["ranked_items"]))
        self.assertTrue(all(not factor["score_applied_now"] for factor in page["ranking_factors"]))
        self.assertTrue(page["evidence_strength"]["evidence_strength_not_truth"])
        self.assertTrue(page["provenance_strength"]["provenance_not_truth"])
        self.assertFalse(page["source_posture"]["source_trust_claimed"])
        self.assertFalse(page["conflicts_and_uncertainty"]["conflict_hidden"])
        self.assertFalse(page["conflicts_and_uncertainty"]["conflict_suppresses_result_now"])
        self.assertTrue(page["conflicts_and_uncertainty"]["uncertainty_explanation_required"])
        self.assertTrue(page["candidate_status"]["candidate_confidence_not_truth"])
        self.assertFalse(page["absence_and_gaps"]["global_absence_claimed"])
        self.assertTrue(page["absence_and_gaps"]["gap_transparency_required"])
        self.assertFalse(page["action_safety"]["downloads_enabled"])
        self.assertFalse(page["action_safety"]["installs_enabled"])
        self.assertFalse(page["action_safety"]["execution_enabled"])
        self.assertFalse(page["rights_risk"]["rights_clearance_claimed"])
        self.assertFalse(page["rights_risk"]["malware_safety_claimed"])
        self.assertFalse(page["tie_breaks"]["random_tie_break_allowed"])
        self.assertFalse(page["tie_breaks"]["tie_break_applied_now"])

    def test_negative_assessment_failures(self) -> None:
        for path, value in (
            (("runtime_ranking_implemented",), True),
            (("ranking_applied_to_live_search",), True),
            (("public_search_order_changed",), True),
            (("result_suppressed",), True),
            (("hidden_suppression_performed",), True),
            (("popularity_signal_used",), True),
            (("user_profile_signal_used",), True),
            (("ad_signal_used",), True),
            (("candidate_promotion_performed",), True),
            (("master_index_mutated",), True),
            (("source_cache_mutated",), True),
            (("evidence_ledger_mutated",), True),
        ):
            with self.subTest(path=path):
                self._assert_invalid(path, value)

    def test_negative_private_path_fails(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\ranking.txt")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = page
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EVIDENCE_WEIGHTED_RANKING_ASSESSMENT.json"
            path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_evidence_weighted_ranking_assessment.py", "--assessment", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
