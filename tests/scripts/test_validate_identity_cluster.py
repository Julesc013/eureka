import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "identity_resolution" / "minimal_exact_identifier_match_v0" / "IDENTITY_CLUSTER.json"


class IdentityClusterValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_identity_cluster.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 5", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_identity_cluster.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 5)

    def test_hard_booleans_and_review_are_safe(self) -> None:
        cluster = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in (
            "runtime_identity_cluster_implemented",
            "persistent_cluster_store_implemented",
            "cluster_accepted_as_truth",
            "records_merged",
            "destructive_merge_performed",
            "master_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "telemetry_exported",
        ):
            self.assertFalse(cluster[key], key)
        self.assertGreaterEqual(len(cluster["cluster_members"]), 2)
        self.assertTrue(cluster["cluster_relations"])
        self.assertFalse(cluster["canonicalization_policy"]["canonicalization_allowed_now"])
        self.assertTrue(cluster["canonicalization_policy"]["canonicalization_review_required"])
        self.assertFalse(cluster["conflicts"]["destructive_merge_allowed"])
        self.assertTrue(cluster["conflicts"]["disagreement_preserved"])
        self.assertTrue(cluster["confidence"]["confidence_not_truth"])
        self.assertFalse(cluster["confidence"]["confidence_sufficient_for_merge_now"])
        self.assertTrue(cluster["review"]["promotion_policy_required"])
        self.assertTrue(cluster["review"]["destructive_merge_forbidden"])

    def test_negative_mutations_cluster_truth_and_merge_fail(self) -> None:
        for path, value in (
            (("runtime_identity_cluster_implemented",), True),
            (("cluster_accepted_as_truth",), True),
            (("records_merged",), True),
            (("destructive_merge_performed",), True),
            (("master_index_mutated",), True),
            (("conflicts", "destructive_merge_allowed"), True),
            (("canonicalization_policy", "canonicalization_allowed_now"), True),
        ):
            with self.subTest(path=path):
                self._assert_invalid(path, value)

    def test_negative_private_path_fails(self) -> None:
        self._assert_invalid(("notes", 0), "C:\\\\Users\\\\Example\\\\cluster.txt")

    def _assert_invalid(self, key_path: tuple, value) -> None:
        cluster = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = cluster
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "IDENTITY_CLUSTER.json"
            tmp_path.write_text(json.dumps(cluster), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_identity_cluster.py", "--cluster", str(tmp_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
