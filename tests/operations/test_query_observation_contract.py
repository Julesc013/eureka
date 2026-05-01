import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "query-observation-contract-v0"
REPORT_PATH = AUDIT_DIR / "query_observation_contract_report.json"
POLICY_PATH = ROOT / "control" / "inventory" / "query_intelligence" / "query_observation_policy.json"
EXAMPLE_PATH = ROOT / "examples" / "query_observations" / "minimal_query_observation_v0" / "QUERY_OBSERVATION.json"
REQUIRED_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "QUERY_OBSERVATION_SCHEMA.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "FINGERPRINT_AND_NORMALIZATION_MODEL.md",
    "INTENT_ENTITY_DESTINATION_MODEL.md",
    "RESULT_SUMMARY_MODEL.md",
    "PUBLIC_AGGREGATE_POLICY.md",
    "PROHIBITED_DATA_REVIEW.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_OBSERVATION_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "query_observation_contract_report.json",
}


class QueryObservationContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_required_audit_files_exist(self) -> None:
        self.assertTrue(AUDIT_DIR.is_dir())
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertFalse(REQUIRED_FILES - existing)

    def test_report_shape_and_hard_booleans(self) -> None:
        self.assertEqual(self.report["report_id"], "query_observation_contract_v0")
        self.assertEqual(self.report["contract_file"], "contracts/query/query_observation.v0.json")
        for key, value in self.report["hard_no_mutation_guarantees"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.report["runtime_status"]["runtime_persistence_implemented"])
        self.assertFalse(self.report["runtime_status"]["telemetry_implemented"])
        self.assertFalse(self.report["runtime_status"]["public_query_logging_enabled"])

    def test_policy_contract_only(self) -> None:
        self.assertEqual(self.policy["status"], "contract_only")
        self.assertEqual(self.policy["raw_query_retention_default"], "none")
        self.assertFalse(self.policy["runtime_persistence_implemented"])
        self.assertFalse(self.policy["telemetry_implemented"])
        self.assertFalse(self.policy["master_index_mutation_allowed"])
        self.assertFalse(self.policy["probe_enqueue_allowed"])

    def test_example_privacy_and_no_mutation(self) -> None:
        self.assertFalse(self.example["raw_query_policy"]["raw_query_retained"])
        self.assertFalse(self.example["raw_query_policy"]["safe_to_publish_raw_query"])
        self.assertFalse(self.example["privacy"]["private_path_detected"])
        self.assertFalse(self.example["privacy"]["credential_detected"])
        self.assertFalse(self.example["probe_policy"]["probe_enqueue_allowed"])
        for key, value in self.example["no_mutation_guarantees"].items():
            self.assertFalse(value, key)

    def test_docs_state_contract_only(self) -> None:
        doc_paths = [
            ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
            ROOT / "docs" / "reference" / "QUERY_OBSERVATION_CONTRACT.md",
            ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
            ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8").casefold() for path in doc_paths)
        self.assertIn("contract-only", text)
        self.assertIn("no telemetry", text)
        self.assertIn("no runtime persistence", text)
        self.assertIn("no persistent query logging", text)
        self.assertIn("master-index mutation", text)

    def test_contract_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_query_observation_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
