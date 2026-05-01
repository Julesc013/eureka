import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "search-need-record-v0"
REPORT_PATH = AUDIT_DIR / "search_need_record_report.json"
POLICY_PATH = ROOT / "control" / "inventory" / "query_intelligence" / "search_need_record_policy.json"
EXAMPLE_ROOT = ROOT / "examples" / "search_needs"
REQUIRED_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "SEARCH_NEED_RECORD_SCHEMA.md",
    "NEED_IDENTITY_AND_FINGERPRINT_MODEL.md",
    "NEED_LIFECYCLE_MODEL.md",
    "NEED_AGGREGATION_MODEL.md",
    "TARGET_OBJECT_MODEL.md",
    "SOURCE_AND_CAPABILITY_GAP_MODEL.md",
    "INPUT_REFERENCE_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "SCOPED_ABSENCE_POLICY.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_NEED_RECORD_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "search_need_record_report.json",
}


class SearchNeedRecordContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.examples = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(EXAMPLE_ROOT.glob("*/SEARCH_NEED_RECORD.json"))
        ]

    def test_required_audit_files_exist(self) -> None:
        self.assertTrue(AUDIT_DIR.is_dir())
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertFalse(REQUIRED_FILES - existing)

    def test_report_shape_and_hard_booleans(self) -> None:
        self.assertEqual(self.report["report_id"], "search_need_record_v0")
        self.assertEqual(self.report["contract_file"], "contracts/query/search_need_record.v0.json")
        for key, value in self.report["hard_no_mutation_guarantees"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.report["runtime_status"]["runtime_need_store_implemented"])
        self.assertFalse(self.report["runtime_status"]["persistent_need_store_implemented"])
        self.assertFalse(self.report["runtime_status"]["telemetry_implemented"])
        self.assertFalse(self.report["runtime_status"]["public_query_logging_enabled"])
        self.assertFalse(self.report["runtime_status"]["demand_counts_runtime_implemented"])

    def test_policy_contract_only(self) -> None:
        self.assertEqual(self.policy["status"], "contract_only")
        self.assertEqual(self.policy["raw_query_retention_default"], "none")
        self.assertTrue(self.policy["scoped_absence_required"])
        self.assertFalse(self.policy["runtime_need_store_implemented"])
        self.assertFalse(self.policy["persistent_need_store_implemented"])
        self.assertFalse(self.policy["telemetry_implemented"])
        self.assertFalse(self.policy["master_index_mutation_allowed"])
        self.assertFalse(self.policy["candidate_index_mutation_allowed"])
        self.assertFalse(self.policy["probe_enqueue_allowed"])

    def test_examples_privacy_scope_and_no_mutation(self) -> None:
        self.assertEqual(len(self.examples), 2)
        object_kinds = {entry["target_object"]["object_kind"] for entry in self.examples}
        self.assertIn("software_version", object_kinds)
        self.assertIn("compatibility_evidence", object_kinds)
        for entry in self.examples:
            self.assertFalse(entry["priority"]["demand_count_claimed"])
            self.assertTrue(entry["checked_scope"]["checked_indexes"])
            self.assertTrue(entry["not_checked_scope"]["reasons_not_checked"])
            self.assertFalse(entry["checked_scope"]["live_probes_attempted"])
            self.assertFalse(entry["privacy"]["contains_private_path"])
            self.assertFalse(entry["privacy"]["contains_secret"])
            self.assertTrue(entry["source_and_capability_gaps"])
            self.assertFalse(entry["need_identity"]["need_fingerprint"]["reversible"])
            for step in entry["suggested_next_steps"]:
                self.assertTrue(step["future_only"])
            for key, value in entry["no_mutation_guarantees"].items():
                self.assertFalse(value, key)

    def test_docs_state_contract_only(self) -> None:
        doc_paths = [
            ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
            ROOT / "docs" / "reference" / "SEARCH_NEED_RECORD_CONTRACT.md",
            ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
            ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8").casefold() for path in doc_paths)
        self.assertIn("contract-only", text)
        self.assertIn("no runtime need store", text)
        self.assertIn("not telemetry", text)
        self.assertIn("scoped", text)
        self.assertIn("search need", text)
        self.assertIn("probe", text)
        self.assertIn("master-index mutation", text)

    def test_contract_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_search_need_record_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
