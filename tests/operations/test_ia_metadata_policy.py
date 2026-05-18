import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class IAMetadataPolicyTests(unittest.TestCase):
    def test_connector_policy_runtime_disabled(self):
        policy = load_json("control/policies/ia_metadata_connector_policy.json")
        self.assertEqual("policy_approved_runtime_disabled", policy["connector_status"])
        for key in (
            "live_calls_enabled",
            "source_probe_execution_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "write_apis_enabled",
            "account_auth_enabled",
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

    def test_allowed_endpoint_matrix_validates_required_rows(self):
        matrix = load_json("control/inventory/ia_metadata_allowed_endpoint_matrix.json")
        rows = {item["endpoint_class"]: item for item in matrix["rows"]}
        for endpoint_class in (
            "metadata_search_small",
            "item_metadata_read",
            "item_file_list_metadata_read",
        ):
            self.assertIn(endpoint_class, rows)
            row = rows[endpoint_class]
            self.assertEqual("future_allowed_after_IA_01_and_operator_approval", row["future_status"])
            self.assertTrue(row["cache_required"])
            self.assertTrue(row["review_required"])
            self.assertTrue(row["forbidden_side_effects"])

    def test_forbidden_action_matrix_validates_required_rows(self):
        matrix = load_json("control/inventory/ia_metadata_forbidden_action_matrix.json")
        rows = {item["action_id"]: item for item in matrix["rows"]}
        for action_id in (
            "downloads",
            "uploads",
            "write_apis",
            "s3_apis",
            "authenticated_account_apis",
            "reviews_write_apis",
            "tasks_write_apis",
            "item_file_fetch",
            "broad_collection_crawl",
            "unbounded_paging",
            "public_query_fanout",
            "arbitrary_url_fetch",
            "wayback_content_replay",
            "page_scraping_outside_metadata_api_posture",
            "source_cache_write_in_IA_00",
            "evidence_ledger_write_in_IA_00",
            "candidate_index_mutation_in_IA_00",
            "reviewed_index_mutation_in_IA_00",
            "master_index_mutation",
            "production_deployment",
        ):
            self.assertIn(action_id, rows)
            self.assertEqual("forbidden", rows[action_id]["status"])
            self.assertTrue(rows[action_id]["validator_assertion"])

    def test_policy_decision_keeps_live_and_writes_disabled(self):
        decision = load_json("control/inventory/ia_metadata_policy_decision.json")
        self.assertEqual("approve_metadata_only_local_pilot_policy_runtime_disabled", decision["decision"])
        self.assertEqual("IA-01", decision["future_live_probe_allowed_after"])
        self.assertTrue(decision["operator_approval_required_for_IA_02"])
        for key in (
            "live_calls_enabled_now",
            "source_cache_writes_enabled_now",
            "evidence_writes_enabled_now",
            "candidate_index_mutation_enabled_now",
            "reviewed_index_mutation_enabled_now",
            "downloads_enabled",
            "uploads_enabled",
            "public_search_fanout_enabled",
        ):
            self.assertFalse(decision[key], key)

    def test_runtime_gate_requires_ia_01_before_ia_02(self):
        matrix = load_json("control/inventory/ia_metadata_runtime_gate_matrix.json")
        gates = {item["gate_id"]: item for item in matrix["gates"]}
        self.assertIn("IA-01", gates)
        self.assertIn("IA-02", gates)
        self.assertIn("IA-01", gates["IA-02"]["enables"])
        self.assertIn("IA-03", gates["IA-02"]["next_task"])


if __name__ == "__main__":
    unittest.main()
