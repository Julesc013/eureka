from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)


class DeepExtractionTestMixin:
    maxDiff = None

    def load(self, rel: str):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class DeepExtractionContractOperationTests(DeepExtractionTestMixin, unittest.TestCase):
    def test_required_audit_pack_files_exist(self):
        audit = ROOT / "control/audits/deep-extraction-contract-v0"
        required = [
            "README.md",
            "CONTRACT_SUMMARY.md",
            "DEEP_EXTRACTION_REQUEST_SCHEMA.md",
            "EXTRACTION_RESULT_SUMMARY_SCHEMA.md",
            "EXTRACTION_POLICY_SCHEMA.md",
            "EXTRACTION_TIER_TAXONOMY.md",
            "CONTAINER_AND_MEMBER_MODEL.md",
            "MANIFEST_AND_METADATA_EXTRACTION_MODEL.md",
            "SELECTIVE_TEXT_EXTRACTION_MODEL.md",
            "OCR_AND_TRANSCRIPTION_HOOK_MODEL.md",
            "PACKAGE_ARCHIVE_ISO_WARC_WACZ_SOURCE_BUNDLE_MODEL.md",
            "NESTED_RECURSION_AND_DEPTH_LIMIT_MODEL.md",
            "SANDBOX_AND_RESOURCE_LIMIT_MODEL.md",
            "PRIVACY_PATH_AND_SECRET_POLICY.md",
            "EXECUTABLE_PAYLOAD_RISK_POLICY.md",
            "RIGHTS_RISK_AND_PROVENANCE_POLICY.md",
            "SYNTHETIC_RECORD_GENERATION_BOUNDARY.md",
            "SOURCE_CACHE_EVIDENCE_CANDIDATE_RELATIONSHIP.md",
            "PUBLIC_SEARCH_OBJECT_PAGE_RESULT_EXPLANATION_RELATIONSHIP.md",
            "NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
            "EXAMPLE_DEEP_EXTRACTION_REVIEW.md",
            "FUTURE_RUNTIME_PATH.md",
            "COMMAND_RESULTS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "deep_extraction_contract_report.json",
        ]
        for name in required:
            self.assertTrue((audit / name).exists(), name)

    def test_docs_say_contract_only_no_runtime_no_mutation(self):
        docs = [
            ROOT / "docs/reference/DEEP_EXTRACTION_CONTRACT.md",
            ROOT / "control/audits/deep-extraction-contract-v0/NO_RUNTIME_AND_NO_MUTATION_POLICY.md",
            ROOT / "control/audits/deep-extraction-contract-v0/SANDBOX_AND_RESOURCE_LIMIT_MODEL.md",
            ROOT / "control/audits/deep-extraction-contract-v0/EXECUTABLE_PAYLOAD_RISK_POLICY.md",
        ]
        phrases = [
            "contract-only",
            "no extraction runtime",
            "no OCR",
            "no transcription",
            "no execution",
            "no mutation",
        ]
        lowered = "\n".join(doc.read_text(encoding="utf-8").lower() for doc in docs)
        for phrase in phrases:
            self.assertIn(phrase.lower(), lowered, phrase)

    def test_report_hard_booleans_false(self):
        report = self.load("control/audits/deep-extraction-contract-v0/deep_extraction_contract_report.json")
        for key, value in report.items():
            if key.endswith("_implemented") or key.endswith("_executed") or key.endswith("_mutated") or key in {
                "extraction_executed",
                "files_opened",
                "archive_unpacked",
                "payload_executed",
                "installer_executed",
                "package_manager_invoked",
                "emulator_vm_launched",
                "OCR_performed",
                "transcription_performed",
                "live_source_called",
                "external_calls_performed",
                "URL_fetched",
                "accepted_as_truth",
                "rights_clearance_claimed",
                "malware_safety_claimed",
                "telemetry_enabled",
            }:
                self.assertIs(value, False, key)

    def test_policy_requires_sandbox_and_resource_limits(self):
        policy = self.load("control/inventory/extraction/deep_extraction_policy.json")
        self.assertEqual(policy["status"], "contract_only")
        self.assertIs(policy["sandbox_required_before_runtime"], True)
        self.assertIs(policy["resource_limits_required_before_runtime"], True)
        self.assertIs(policy["operator_approval_required"], True)
        self.assertIs(policy["runtime_extraction_implemented"], False)


if __name__ == "__main__":
    unittest.main()
