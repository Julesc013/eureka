import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunCandidateIndexRecordTests(unittest.TestCase):
    def test_dry_run_stdout_only_public_safe(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_candidate_index_record.py",
                "--label",
                "Firefox ESR Windows XP compatibility candidate",
                "--candidate-type",
                "compatibility_claim_candidate",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertEqual(payload["candidate_kind"], "candidate_index_record")
        self.assertEqual(payload["candidate_type"]["type"], "compatibility_claim_candidate")
        self.assertFalse(payload["no_truth_guarantees"]["accepted_as_truth"])
        self.assertFalse(payload["no_truth_guarantees"]["promoted_to_master_index"])
        self.assertFalse(payload["review"]["promotion_allowed_now"])
        self.assertTrue(payload["review"]["promotion_policy_required"])
        self.assertTrue(payload["confidence"]["confidence_not_truth"])
        self.assertFalse(payload["source_policy"]["live_source_called"])
        self.assertFalse(payload["source_policy"]["live_probe_enabled"])
        self.assertFalse(payload["rights_and_risk"]["downloads_enabled"])
        self.assertFalse(payload["rights_and_risk"]["installs_enabled"])
        self.assertFalse(payload["rights_and_risk"]["execution_enabled"])
        self.assertFalse(payload["no_mutation_guarantees"]["source_cache_mutated"])
        self.assertFalse(payload["no_mutation_guarantees"]["evidence_ledger_mutated"])
        self.assertFalse(payload["no_mutation_guarantees"]["master_index_mutated"])

    def test_dry_run_rejects_sensitive_label(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_candidate_index_record.py",
                "--label",
                "C:\\Users\\Alice\\private.txt api_key=abc",
                "--candidate-type",
                "compatibility_claim_candidate",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_future")
        self.assertEqual(payload["candidate_identity"]["canonical_candidate_label"], "<redacted>")
        self.assertTrue(payload["privacy"]["contains_private_path"])
        self.assertTrue(payload["privacy"]["contains_secret"])
        self.assertFalse(payload["privacy"]["public_aggregate_allowed"])


if __name__ == "__main__":
    unittest.main()
