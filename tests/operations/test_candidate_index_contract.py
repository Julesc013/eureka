import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "candidate-index-v0"
REPORT_PATH = AUDIT_DIR / "candidate_index_report.json"
POLICY_PATH = ROOT / "control" / "inventory" / "query_intelligence" / "candidate_index_policy.json"
EXAMPLE_ROOT = ROOT / "examples" / "candidate_index"
REQUIRED_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "CANDIDATE_INDEX_RECORD_SCHEMA.md",
    "CANDIDATE_TYPE_TAXONOMY.md",
    "CANDIDATE_LIFECYCLE_MODEL.md",
    "CONFIDENCE_AND_REVIEW_MODEL.md",
    "PROVENANCE_AND_INPUT_REF_MODEL.md",
    "CONFLICT_AND_DUPLICATE_MODEL.md",
    "SOURCE_EVIDENCE_AND_RIGHTS_POLICY.md",
    "PRIVACY_AND_REDACTION_POLICY.md",
    "NO_TRUTH_AND_NO_MUTATION_POLICY.md",
    "PUBLIC_VISIBILITY_POLICY.md",
    "INTEGRATION_BOUNDARIES.md",
    "EXAMPLE_CANDIDATE_RECORD_REVIEW.md",
    "FUTURE_RUNTIME_PATH.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "candidate_index_report.json",
}


class CandidateIndexContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.examples = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(EXAMPLE_ROOT.glob("*/CANDIDATE_INDEX_RECORD.json"))
        ]

    def test_required_audit_files_exist(self) -> None:
        self.assertTrue(AUDIT_DIR.is_dir())
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertFalse(REQUIRED_FILES - existing)

    def test_report_shape_and_hard_booleans(self) -> None:
        self.assertEqual(self.report["report_id"], "candidate_index_v0")
        self.assertEqual(self.report["contract_file"], "contracts/query/candidate_index_record.v0.json")
        for key, value in self.report["no_truth_no_mutation_guarantees"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.report["runtime_status"]["runtime_candidate_index_implemented"])
        self.assertFalse(self.report["runtime_status"]["persistent_candidate_index_implemented"])
        self.assertFalse(self.report["runtime_status"]["candidate_promotion_runtime_implemented"])
        self.assertFalse(self.report["runtime_status"]["telemetry_implemented"])

    def test_policy_contract_only(self) -> None:
        self.assertEqual(self.policy["status"], "contract_only")
        self.assertEqual(self.policy["raw_query_retention_default"], "none")
        self.assertTrue(self.policy["promotion_policy_required"])
        self.assertFalse(self.policy["runtime_candidate_index_implemented"])
        self.assertFalse(self.policy["persistent_candidate_index_implemented"])
        self.assertFalse(self.policy["telemetry_implemented"])
        self.assertFalse(self.policy["candidate_promotion_runtime_implemented"])
        self.assertFalse(self.policy["public_search_candidate_injection_allowed"])
        self.assertFalse(self.policy["source_cache_mutation_allowed"])
        self.assertFalse(self.policy["evidence_ledger_mutation_allowed"])
        self.assertFalse(self.policy["master_index_mutation_allowed"])

    def test_examples_privacy_review_and_no_mutation(self) -> None:
        self.assertEqual(len(self.examples), 4)
        candidate_types = {entry["candidate_type"]["type"] for entry in self.examples}
        self.assertIn("software_version_candidate", candidate_types)
        self.assertIn("compatibility_claim_candidate", candidate_types)
        self.assertIn("absence_candidate", candidate_types)
        self.assertIn("identity_match_candidate", candidate_types)
        for entry in self.examples:
            self.assertFalse(entry["no_truth_guarantees"]["accepted_as_truth"])
            self.assertFalse(entry["no_truth_guarantees"]["promoted_to_master_index"])
            self.assertFalse(entry["review"]["promotion_allowed_now"])
            self.assertTrue(entry["review"]["promotion_policy_required"])
            self.assertTrue(entry["confidence"]["confidence_not_truth"])
            self.assertFalse(entry["source_policy"]["live_source_called"])
            self.assertFalse(entry["source_policy"]["live_probe_enabled"])
            self.assertFalse(entry["privacy"]["contains_private_path"])
            self.assertFalse(entry["privacy"]["contains_secret"])
            self.assertFalse(entry["rights_and_risk"]["downloads_enabled"])
            self.assertFalse(entry["rights_and_risk"]["installs_enabled"])
            self.assertFalse(entry["rights_and_risk"]["execution_enabled"])
            self.assertFalse(entry["rights_and_risk"]["rights_clearance_claimed"])
            self.assertFalse(entry["rights_and_risk"]["malware_safety_claimed"])
            self.assertFalse(entry["candidate_identity"]["candidate_fingerprint"]["reversible"])
            for key, value in entry["no_mutation_guarantees"].items():
                self.assertFalse(value, key)
            self.assertIn(entry["conflicts"]["preservation_policy"], {"preserve_conflict", "review_required", "not_applicable"})

    def test_docs_state_contract_only(self) -> None:
        doc_paths = [
            ROOT / "docs" / "architecture" / "QUERY_INTELLIGENCE_PLANE.md",
            ROOT / "docs" / "reference" / "CANDIDATE_INDEX_CONTRACT.md",
            ROOT / "docs" / "reference" / "QUERY_PRIVACY_AND_REDACTION_POLICY.md",
            ROOT / "docs" / "operations" / "QUERY_INTELLIGENCE_PRIVACY.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8").casefold() for path in doc_paths)
        self.assertIn("contract-only", text)
        self.assertIn("candidate is not truth", text)
        self.assertIn("no runtime candidate index", text)
        self.assertIn("candidate promotion is not implemented", text)
        self.assertIn("confidence-not-truth", text)
        self.assertIn("master-index mutation", text)

    def test_contract_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_candidate_index_contract.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
