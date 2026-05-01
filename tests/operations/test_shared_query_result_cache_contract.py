import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "shared-query-result-cache-v0"
REPORT_PATH = AUDIT_DIR / "shared_query_result_cache_report.json"
POLICY_PATH = ROOT / "control" / "inventory" / "query_intelligence" / "search_result_cache_policy.json"
EXAMPLE_ROOT = ROOT / "examples" / "query_result_cache"
REQUIRED_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "CACHE_ENTRY_SCHEMA.md",
    "CACHE_KEY_AND_FINGERPRINT_MODEL.md",
    "CACHED_RESULT_SUMMARY_MODEL.md",
    "ABSENCE_AND_GAP_CACHE_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "FRESHNESS_AND_INVALIDATION_POLICY.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_CACHE_ENTRY_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "shared_query_result_cache_report.json",
}


class SharedQueryResultCacheContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.examples = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(EXAMPLE_ROOT.glob("*/SEARCH_RESULT_CACHE_ENTRY.json"))
        ]

    def test_required_audit_files_exist(self) -> None:
        self.assertTrue(AUDIT_DIR.is_dir())
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertFalse(REQUIRED_FILES - existing)

    def test_report_shape_and_hard_booleans(self) -> None:
        self.assertEqual(self.report["report_id"], "shared_query_result_cache_v0")
        self.assertEqual(self.report["contract_file"], "contracts/query/search_result_cache_entry.v0.json")
        for key, value in self.report["hard_no_mutation_guarantees"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.report["runtime_status"]["runtime_cache_implemented"])
        self.assertFalse(self.report["runtime_status"]["persistent_cache_implemented"])
        self.assertFalse(self.report["runtime_status"]["telemetry_implemented"])
        self.assertFalse(self.report["runtime_status"]["public_query_logging_enabled"])

    def test_policy_contract_only(self) -> None:
        self.assertEqual(self.policy["status"], "contract_only")
        self.assertEqual(self.policy["raw_query_retention_default"], "none")
        self.assertFalse(self.policy["runtime_cache_implemented"])
        self.assertFalse(self.policy["persistent_cache_implemented"])
        self.assertFalse(self.policy["telemetry_implemented"])
        self.assertFalse(self.policy["master_index_mutation_allowed"])
        self.assertFalse(self.policy["probe_enqueue_allowed"])

    def test_examples_privacy_absence_and_no_mutation(self) -> None:
        self.assertGreaterEqual(len(self.examples), 2)
        statuses = {entry["absence_summary"]["absence_status"] for entry in self.examples}
        self.assertIn("scoped_absence", statuses)
        for entry in self.examples:
            self.assertFalse(entry["query_ref"]["raw_query_retained"])
            self.assertFalse(entry["privacy"]["contains_private_path"])
            self.assertFalse(entry["privacy"]["contains_secret"])
            self.assertFalse(entry["checked_scope"]["live_probes_attempted"])
            for key, value in entry["no_mutation_guarantees"].items():
                self.assertFalse(value, key)

    def test_docs_state_contract_only(self) -> None:
        doc_paths = [
            ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
            ROOT / "docs" / "reference" / "SEARCH_RESULT_CACHE_CONTRACT.md",
            ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
            ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8").casefold() for path in doc_paths)
        self.assertIn("contract-only", text)
        self.assertIn("no runtime cache writes", text)
        self.assertIn("no telemetry", text)
        self.assertIn("scoped absence", text)
        self.assertIn("master-index mutation", text)

    def test_contract_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_shared_query_result_cache_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
