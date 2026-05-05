import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "identity_resolution" / "minimal_exact_identifier_match_v0" / "IDENTITY_RESOLUTION_ASSESSMENT.json"


class IdentityResolutionAssessmentValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_identity_resolution_assessment.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_identity_resolution_assessment.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_hard_booleans_and_identity_cautions_are_safe(self) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "runtime_identity_resolution_implemented",
            "persistent_identity_store_implemented",
            "identity_cluster_created",
            "records_merged",
            "destructive_merge_performed",
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
            self.assertFalse(page[key], key)
        self.assertGreaterEqual(len(page["subjects"]), 2)
        self.assertTrue(page["asserted_relation"]["relation_claim_not_truth"])
        self.assertFalse(page["asserted_relation"]["global_merge_allowed"])
        self.assertTrue(page["confidence"]["confidence_not_truth"])
        self.assertFalse(page["confidence"]["confidence_sufficient_for_merge_now"])
        self.assertTrue(page["review"]["promotion_policy_required"])
        self.assertTrue(page["review"]["destructive_merge_forbidden"])
        self.assertTrue(page["alias_name_evidence"]["name_match_not_sufficient_alone"])
        self.assertFalse(page["conflicts"]["destructive_merge_allowed"])
        self.assertFalse(page["representation_member_evidence"]["payload_included"])
        self.assertFalse(page["representation_member_evidence"]["downloads_enabled"])

    def test_exact_same_object_has_strong_identifier(self) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(page["asserted_relation"]["relation_type"], "exact_same_object")
        strong = [
            item
            for item in page["identifier_evidence"]
            if item["identifier_status"] == "exact_match" and item["strength"] in {"intrinsic_strong", "strong"}
        ]
        self.assertTrue(strong)

    def test_negative_mutations_and_merge_fail(self) -> None:
        for path, value in (
            (("runtime_identity_resolution_implemented",), True),
            (("records_merged",), True),
            (("destructive_merge_performed",), True),
            (("candidate_promotion_performed",), True),
            (("master_index_mutated",), True),
            (("confidence", "confidence_not_truth"), False),
            (("asserted_relation", "global_merge_allowed"), True),
        ):
            with self.subTest(path=path):
                self._assert_invalid(path, value)

    def test_negative_exact_same_object_without_strong_identifier_fails(self) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        page["identifier_evidence"] = []
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "IDENTITY_RESOLUTION_ASSESSMENT.json"
            tmp_path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_identity_resolution_assessment.py", "--assessment", str(tmp_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")

    def test_negative_private_path_and_secret_fail(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\identity.txt")
        self._assert_invalid(("notes", 0), "api_key=example-value")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = page
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "IDENTITY_RESOLUTION_ASSESSMENT.json"
            tmp_path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_identity_resolution_assessment.py", "--assessment", str(tmp_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
