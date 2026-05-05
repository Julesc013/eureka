import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "connector-approval-runtime-planning-audit-v0"
REPORT = AUDIT / "connector_approval_runtime_planning_audit_report.json"
INVENTORY = ROOT / "control" / "inventory" / "connectors" / "connector_approval_runtime_planning_status.json"
DOC = ROOT / "docs" / "operations" / "CONNECTOR_APPROVAL_RUNTIME_PLANNING_AUDIT.md"

CONNECTORS = {
    "internet_archive_metadata",
    "wayback_cdx_memento",
    "github_releases",
    "pypi_metadata",
    "npm_metadata",
    "software_heritage",
}

VALID_CLASSIFICATIONS = {
    "approval_pack_missing",
    "approval_pack_present",
    "approval_pending",
    "approval_complete_future",
    "contract_only",
    "planning_only",
    "runtime_plan_missing",
    "runtime_plan_present",
    "local_dry_run_ready_after_operator_approval",
    "source_sync_worker_ready_after_operator_approval",
    "operator_gated",
    "approval_gated",
    "policy_gated",
    "dependency_gated",
    "blocked",
    "disabled",
    "implemented_local_dry_run",
    "implemented_runtime",
    "unexpected_runtime_or_live_integration",
}

REQUIRED_FILES = {
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "CONNECTOR_STATUS_MATRIX.md",
    "APPROVAL_PACK_STATUS.md",
    "RUNTIME_PLANNING_STATUS.md",
    "SOURCE_POLICY_GATE_STATUS.md",
    "USER_AGENT_CONTACT_RATE_LIMIT_STATUS.md",
    "TOKEN_AUTH_GATE_STATUS.md",
    "IDENTITY_PRIVACY_GATE_STATUS.md",
    "SOURCE_CACHE_EVIDENCE_LEDGER_DEPENDENCY_STATUS.md",
    "PUBLIC_SEARCH_BOUNDARY_STATUS.md",
    "RUNTIME_IMPLEMENTATION_STATUS.md",
    "MUTATION_BOUNDARY_STATUS.md",
    "CONNECTOR_BY_CONNECTOR_REVIEW.md",
    "INTERNET_ARCHIVE_METADATA_REVIEW.md",
    "WAYBACK_CDX_MEMENTO_REVIEW.md",
    "GITHUB_RELEASES_REVIEW.md",
    "PYPI_METADATA_REVIEW.md",
    "NPM_METADATA_REVIEW.md",
    "SOFTWARE_HERITAGE_REVIEW.md",
    "OPERATOR_ACTIONS_REQUIRED.md",
    "APPROVAL_GATED_ACTIONS.md",
    "DO_NOT_IMPLEMENT_YET.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "connector_approval_runtime_planning_audit_report.json",
}


class ConnectorApprovalRuntimePlanningAuditOperationTests(unittest.TestCase):
    def test_audit_pack_inventory_and_docs_exist(self):
        self.assertTrue(AUDIT.exists())
        for name in REQUIRED_FILES:
            self.assertTrue((AUDIT / name).is_file(), name)
        self.assertTrue(INVENTORY.is_file())
        self.assertTrue(DOC.is_file())

    def test_report_and_inventory_parse(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "connector_approval_runtime_planning_audit_v0")
        self.assertEqual(inventory["status"], "audited")

    def test_all_six_connectors_present_and_classified(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        matrix = report["connector_status_matrix"]
        self.assertEqual(set(matrix.keys()), CONNECTORS)
        for connector_id, row in matrix.items():
            self.assertEqual(row["connector_id"], connector_id)
            for key in (
                "approval_pack_status",
                "connector_contract_status",
                "connector_inventory_status",
                "runtime_planning_status",
                "readiness_decision",
                "source_policy_gate",
                "public_search_boundary",
                "mutation_status",
            ):
                self.assertIn(row[key], VALID_CLASSIFICATIONS)
            self.assertEqual(row["approval_pack_status"], "approval_pack_present")
            self.assertEqual(row["runtime_planning_status"], "runtime_plan_present")
            self.assertEqual(row["readiness_decision"], "approval_gated")
            self.assertFalse(row["live_calls_enabled"])
            self.assertFalse(row["downloads_enabled"])
            self.assertFalse(row["install_execute_enabled"])

    def test_boundaries_documented_and_hard_booleans_false(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["audit_only"])
        for key in (
            "connector_runtime_implemented_by_this_milestone",
            "live_connector_runtime_enabled",
            "public_search_connector_fanout_enabled",
            "external_calls_performed",
            "live_source_called",
            "credentials_configured",
            "tokens_enabled",
            "downloads_enabled",
            "installs_enabled",
            "execution_enabled",
            "source_cache_mutated",
            "evidence_ledger_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "deployment_performed",
            "telemetry_enabled",
            "accounts_enabled",
        ):
            self.assertFalse(report[key], key)
        self.assertTrue((AUDIT / "OPERATOR_ACTIONS_REQUIRED.md").is_file())
        self.assertTrue((AUDIT / "APPROVAL_GATED_ACTIONS.md").is_file())
        self.assertTrue((AUDIT / "DO_NOT_IMPLEMENT_YET.md").is_file())
        self.assertIn("must not call connectors live", (AUDIT / "PUBLIC_SEARCH_BOUNDARY_STATUS.md").read_text(encoding="utf-8"))
        self.assertIn("master_index_mutated", (AUDIT / "MUTATION_BOUNDARY_STATUS.md").read_text(encoding="utf-8"))

    def test_command_matrix_and_docs_reference_validator(self):
        matrix_text = (ROOT / "control" / "inventory" / "tests" / "command_matrix.json").read_text(encoding="utf-8")
        registry_text = (ROOT / "control" / "inventory" / "tests" / "test_registry.json").read_text(encoding="utf-8")
        scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        for text in (matrix_text, registry_text, scripts_readme):
            self.assertIn("validate_connector_approval_runtime_planning_audit.py", text)
            self.assertIn("report_connector_approval_runtime_status.py --json", text)
        doc_text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "connector set",
            "approval packs are not runtime",
            "public search must not call connectors live",
            "mutation remains disabled",
        ):
            self.assertIn(phrase, doc_text)


if __name__ == "__main__":
    unittest.main()
