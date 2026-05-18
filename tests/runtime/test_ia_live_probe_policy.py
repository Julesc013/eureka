import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "control/policies/ia_live_probe_policy.json"


class IALiveProbePolicyTests(unittest.TestCase):
    def test_policy_is_fail_closed_except_approved_probe(self):
        policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual("ia_live_probe_policy.v0", policy["schema_version"])
        self.assertTrue(policy["live_calls_allowed_in_IA_02"])
        self.assertTrue(policy["live_calls_require_approve_live_flag"])
        self.assertEqual(["archive.org"], policy["allowed_domains"])
        self.assertEqual(1, policy["metadata_search_rows_max"])
        self.assertEqual(2, policy["total_http_requests_max"])
        for key in (
            "downloads_enabled",
            "uploads_enabled",
            "write_apis_enabled",
            "public_search_fanout_enabled",
            "source_cache_writes_enabled",
            "evidence_ledger_writes_enabled",
            "candidate_index_mutation_enabled",
            "reviewed_index_mutation_enabled",
            "master_index_mutation_enabled",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(policy[key], key)


if __name__ == "__main__":
    unittest.main()
