import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "probe-queue-v0"
REPORT_PATH = AUDIT_DIR / "probe_queue_report.json"
POLICY_PATH = ROOT / "control" / "inventory" / "query_intelligence" / "probe_queue_policy.json"
EXAMPLE_ROOT = ROOT / "examples" / "probe_queue"
REQUIRED_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "PROBE_QUEUE_ITEM_SCHEMA.md",
    "PROBE_KIND_TAXONOMY.md",
    "QUEUE_LIFECYCLE_MODEL.md",
    "PRIORITY_AND_SCHEDULING_MODEL.md",
    "SOURCE_POLICY_AND_APPROVAL_MODEL.md",
    "INPUT_REFERENCE_MODEL.md",
    "EXPECTED_OUTPUT_MODEL.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_EXECUTION_AND_NO_MUTATION_POLICY.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_PROBE_ITEM_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "probe_queue_report.json",
}


class ProbeQueueContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.examples = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(EXAMPLE_ROOT.glob("*/PROBE_QUEUE_ITEM.json"))
        ]

    def test_required_audit_files_exist(self) -> None:
        self.assertTrue(AUDIT_DIR.is_dir())
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertFalse(REQUIRED_FILES - existing)

    def test_report_shape_and_hard_booleans(self) -> None:
        self.assertEqual(self.report["report_id"], "probe_queue_v0")
        self.assertEqual(self.report["contract_file"], "contracts/query/probe_queue_item.v0.json")
        for key, value in self.report["no_execution_no_mutation_guarantees"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.report["runtime_status"]["runtime_probe_queue_implemented"])
        self.assertFalse(self.report["runtime_status"]["persistent_probe_queue_implemented"])
        self.assertFalse(self.report["runtime_status"]["telemetry_implemented"])
        self.assertFalse(self.report["runtime_status"]["public_query_logging_enabled"])

    def test_policy_contract_only(self) -> None:
        self.assertEqual(self.policy["status"], "contract_only")
        self.assertEqual(self.policy["raw_query_retention_default"], "none")
        self.assertTrue(self.policy["approval_required_for_live_network_probe"])
        self.assertTrue(self.policy["operator_required_for_worker_runtime"])
        self.assertFalse(self.policy["runtime_probe_queue_implemented"])
        self.assertFalse(self.policy["persistent_probe_queue_implemented"])
        self.assertFalse(self.policy["telemetry_implemented"])
        self.assertFalse(self.policy["live_probe_execution_allowed"])
        self.assertFalse(self.policy["source_cache_mutation_allowed"])
        self.assertFalse(self.policy["evidence_ledger_mutation_allowed"])
        self.assertFalse(self.policy["candidate_index_mutation_allowed"])
        self.assertFalse(self.policy["master_index_mutation_allowed"])

    def test_examples_privacy_safety_and_no_mutation(self) -> None:
        self.assertEqual(len(self.examples), 3)
        kinds = {entry["probe_kind"]["kind"] for entry in self.examples}
        self.assertIn("manual_observation", kinds)
        self.assertIn("source_metadata_probe", kinds)
        self.assertIn("deep_container_extraction", kinds)
        for entry in self.examples:
            self.assertFalse(entry["source_policy"]["live_probe_enabled"])
            self.assertFalse(entry["priority"]["demand_count_claimed"])
            self.assertTrue(entry["input_refs"]["search_need_refs"])
            self.assertFalse(entry["privacy"]["contains_private_path"])
            self.assertFalse(entry["privacy"]["contains_secret"])
            self.assertFalse(entry["probe_identity"]["probe_fingerprint"]["reversible"])
            for key in (
                "no_downloads",
                "no_installs",
                "no_execution",
                "no_uploads",
                "no_private_paths",
                "no_credentials",
                "no_arbitrary_url_fetch",
            ):
                self.assertTrue(entry["safety_requirements"][key], key)
            for key, value in entry["no_execution_guarantees"].items():
                self.assertFalse(value, key)
            for key, value in entry["no_mutation_guarantees"].items():
                self.assertFalse(value, key)
            if entry["probe_kind"]["live_network_required_future"]:
                self.assertTrue(entry["probe_kind"]["approval_required"])
                self.assertTrue(entry["safety_requirements"]["rate_limit_required_future"])
                self.assertTrue(entry["safety_requirements"]["circuit_breaker_required_future"])

    def test_docs_state_contract_only(self) -> None:
        doc_paths = [
            ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
            ROOT / "docs" / "reference" / "PROBE_QUEUE_CONTRACT.md",
            ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
            ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8").casefold() for path in doc_paths)
        self.assertIn("contract-only", text)
        self.assertIn("no runtime probe queue", text)
        self.assertIn("not telemetry", text)
        self.assertIn("source policy", text)
        self.assertIn("approval", text)
        self.assertIn("no execution", text)
        self.assertIn("master-index mutation", text)

    def test_contract_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_probe_queue_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
