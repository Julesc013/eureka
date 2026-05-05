import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "pack-import-runtime-planning-v0"


class PackImportRuntimePlanOperationTests(unittest.TestCase):
    def test_report_and_inventory_parse(self):
        report = json.loads((AUDIT / "pack_import_runtime_planning_report.json").read_text(encoding="utf-8"))
        inventory = json.loads((ROOT / "control" / "inventory" / "packs" / "pack_import_runtime_plan.json").read_text(encoding="utf-8"))
        self.assertIn(
            report["readiness_decision"],
            {
                "ready_for_local_dry_run_runtime_after_operator_approval",
                "ready_for_local_quarantine_runtime_after_operator_approval",
                "blocked_source_pack_contract_missing",
                "blocked_evidence_pack_contract_missing",
                "blocked_index_pack_contract_missing",
                "blocked_contribution_pack_contract_missing",
                "blocked_pack_set_validator_missing",
                "blocked_validate_only_import_missing",
                "blocked_import_report_contract_missing",
                "blocked_quarantine_staging_model_missing",
                "blocked_staged_pack_inspector_missing",
                "blocked_review_queue_contract_missing",
                "blocked_privacy_path_secret_policy_missing",
                "blocked_executable_payload_policy_missing",
                "blocked_mutation_boundary_incomplete",
                "blocked_other",
            },
        )
        self.assertEqual(inventory["status"], "planning_only")

    def test_hard_booleans_false(self):
        report = json.loads((AUDIT / "pack_import_runtime_planning_report.json").read_text(encoding="utf-8"))
        for key in (
            "pack_import_runtime_implemented",
            "validate_only_runtime_implemented",
            "quarantine_runtime_implemented",
            "staging_runtime_implemented",
            "promotion_runtime_implemented",
            "public_contribution_intake_enabled",
            "upload_endpoint_enabled",
            "admin_endpoint_enabled",
            "pack_content_execution_enabled",
            "pack_url_fetching_enabled",
            "arbitrary_local_path_enabled",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "promotion_decision_created",
            "accepted_record_created",
            "external_calls_performed",
            "live_source_called",
            "telemetry_enabled",
            "accounts_enabled",
        ):
            self.assertFalse(report[key], key)

    def test_gate_docs_present(self):
        for name in (
            "PACK_CONTRACT_GATE_REVIEW.md",
            "VALIDATE_ONLY_IMPORT_GATE_REVIEW.md",
            "QUARANTINE_AND_STAGING_GATE_REVIEW.md",
            "REVIEW_QUEUE_AND_PROMOTION_GATE_REVIEW.md",
            "PRIVACY_PATH_TRAVERSAL_AND_SECRET_POLICY.md",
            "EXECUTABLE_PAYLOAD_AND_CONTENT_SAFETY_POLICY.md",
            "MUTATION_AND_PROMOTION_BOUNDARY.md",
            "ACCEPTANCE_CRITERIA.md",
            "DO_NOT_IMPLEMENT_YET.md",
        ):
            self.assertTrue((AUDIT / name).exists(), name)

    def test_report_gates_present(self):
        report = json.loads((AUDIT / "pack_import_runtime_planning_report.json").read_text(encoding="utf-8"))
        gate = report["pack_contract_gate_review"]
        self.assertTrue(gate["source_pack_contract_valid"])
        self.assertTrue(gate["evidence_pack_contract_valid"])
        self.assertTrue(gate["index_pack_contract_valid"])
        self.assertTrue(gate["contribution_pack_contract_valid"])
        self.assertTrue(gate["pack_set_validator_valid"])
        self.assertTrue(report["validate_only_import_gate_review"]["validate_only_import_tool_valid"])
        self.assertTrue(report["quarantine_staging_gate_review"]["staged_pack_inspector_valid"])
        self.assertTrue(report["review_queue_promotion_gate_review"]["master_index_review_queue_contract_valid"])
        self.assertFalse(report["review_queue_promotion_gate_review"]["runtime_implementation_present"])

    def test_do_not_implement_file(self):
        do_not = (AUDIT / "DO_NOT_IMPLEMENT_YET.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "no pack import runtime",
            "no real pack staging",
            "no source cache writes",
            "no evidence ledger writes",
            "no candidate index writes",
            "no public/local/master index mutation",
            "no promotion decisions",
            "no upload endpoint",
            "no pack content execution",
            "no url fetching from packs",
            "no telemetry/accounts",
        ):
            self.assertIn(phrase, do_not)


if __name__ == "__main__":
    unittest.main()
