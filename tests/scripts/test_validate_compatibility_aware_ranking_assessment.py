import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "compatibility_aware_ranking" / "minimal_os_compatibility_ranking_v0" / "COMPATIBILITY_AWARE_RANKING_ASSESSMENT.json"


class CompatibilityAwareRankingAssessmentValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self):
        completed = subprocess.run([sys.executable, "scripts/validate_compatibility_aware_ranking_assessment.py", "--all-examples"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 6", completed.stdout)

    def test_validator_json_parses(self):
        completed = subprocess.run([sys.executable, "scripts/validate_compatibility_aware_ranking_assessment.py", "--all-examples", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 6)

    def test_hard_booleans_are_safe(self):
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in ("runtime_compatibility_ranking_implemented", "compatibility_ranking_applied_to_live_search", "public_search_order_changed", "result_suppressed", "hidden_suppression_performed", "candidate_promotion_performed", "installability_claimed", "compatibility_truth_claimed", "dependency_safety_claimed", "emulator_vm_launch_enabled", "package_manager_invoked", "executable_inspected", "downloads_enabled", "installs_enabled", "execution_enabled", "master_index_mutated", "public_index_mutated", "local_index_mutated", "source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated", "live_source_called", "external_calls_performed", "telemetry_exported", "popularity_signal_used", "user_profile_signal_used", "ad_signal_used", "model_call_performed"):
            self.assertFalse(page[key], key)
        self.assertGreaterEqual(len(page["ranked_items"]), 2)
        self.assertTrue(all(not item["rank_changed_now"] for item in page["ranked_items"]))
        self.assertTrue(all(not factor["score_applied_now"] for factor in page["compatibility_factors"]))
        self.assertTrue(page["platform_os_version_matching"]["platform_match_not_truth"])
        self.assertFalse(page["runtime_dependency_requirements"]["dependency_resolution_performed"])
        self.assertTrue(page["compatibility_evidence_strength"]["compatibility_evidence_not_truth"])
        self.assertTrue(page["incompatibility_and_unknown_gaps"]["absence_of_evidence_is_not_incompatibility"])
        self.assertFalse(page["source_provenance_candidate_caution"]["source_trust_claimed"])
        self.assertTrue(page["source_provenance_candidate_caution"]["candidate_confidence_not_truth"])
        self.assertTrue(page["source_provenance_candidate_caution"]["provenance_not_truth"])
        self.assertTrue(page["action_safety_installability_caution"]["installability_evidence_required"])
        self.assertFalse(page["rights_risk"]["rights_clearance_claimed"])
        self.assertFalse(page["rights_risk"]["malware_safety_claimed"])
        self.assertFalse(page["tie_breaks"]["random_tie_break_allowed"])
        self.assertFalse(page["tie_breaks"]["tie_break_applied_now"])

    def test_negative_assessment_failures(self):
        for key_path, value in (
            (("runtime_compatibility_ranking_implemented",), True),
            (("compatibility_ranking_applied_to_live_search",), True),
            (("public_search_order_changed",), True),
            (("result_suppressed",), True),
            (("installability_claimed",), True),
            (("dependency_safety_claimed",), True),
            (("emulator_vm_launch_enabled",), True),
            (("package_manager_invoked",), True),
            (("execution_enabled",), True),
            (("master_index_mutated",), True),
            (("source_cache_mutated",), True),
            (("evidence_ledger_mutated",), True),
        ):
            with self.subTest(key_path=key_path):
                self._assert_invalid(key_path, value)

    def test_negative_private_path_fails(self):
        self._assert_invalid(("notes", 0), "C:\\Users\\Example\\compat.txt")

    def _assert_invalid(self, key_path, value):
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = page
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "COMPATIBILITY_AWARE_RANKING_ASSESSMENT.json"
            path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/validate_compatibility_aware_ranking_assessment.py", "--assessment", str(path), "--json"], cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
