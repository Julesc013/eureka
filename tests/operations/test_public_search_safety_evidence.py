from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-search-safety-evidence-v0"
REPORT = AUDIT_DIR / "public_search_safety_evidence_report.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_public_search_safety_evidence.py"


class PublicSearchSafetyEvidenceOperationTest(unittest.TestCase):
    def test_audit_pack_and_report_exist(self) -> None:
        required = {
            "README.md",
            "SAFETY_SUMMARY.md",
            "SAFE_QUERY_EVIDENCE.md",
            "BLOCKED_REQUEST_EVIDENCE.md",
            "LIMIT_AND_TIMEOUT_EVIDENCE.md",
            "STATUS_ENDPOINT_EVIDENCE.md",
            "STATIC_HANDOFF_SAFETY_REVIEW.md",
            "PUBLIC_INDEX_SAFETY_REVIEW.md",
            "HOSTED_WRAPPER_SAFETY_REVIEW.md",
            "RATE_LIMIT_AND_EDGE_STATUS.md",
            "PRIVACY_AND_REDACTION_REVIEW.md",
            "PUBLIC_CLAIM_REVIEW.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "COMMAND_RESULTS.md",
            "public_search_safety_evidence_report.json",
        }
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((AUDIT_DIR / name).is_file())
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["report_id"], "public_search_safety_evidence_v0")
        self.assertEqual(payload["next_recommended_branch"], "P58 Hosted Public Search Rehearsal v0")

    def test_report_records_safety_evidence(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(payload["route_evidence"]), 9)
        self.assertEqual(len(payload["safe_query_evidence"]), 4)
        self.assertEqual(len(payload["blocked_request_evidence"]), 32)
        self.assertEqual(payload["forbidden_parameter_coverage"]["missing_categories"], [])
        self.assertEqual(payload["limit_and_timeout_evidence"][-1]["expected_behavior"], "contract_only")
        self.assertEqual(payload["rate_limit_and_edge_status"]["edge_rate_limit_status"], "operator_gated")

    def test_hard_booleans_and_claims_are_false(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        for mapping_name in ("hard_booleans", "public_claim_review"):
            for key, value in payload[mapping_name].items():
                with self.subTest(mapping_name=mapping_name, key=key):
                    self.assertIs(value, False)

    def test_static_handoff_and_public_index_are_checked(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        static = payload["static_handoff_review"]
        self.assertEqual(static["status"], "passed")
        self.assertFalse(static["hosted_backend_verified"])
        self.assertFalse(static["search_form_enabled"])
        index = payload["public_index_safety_review"]
        self.assertEqual(index["document_count"], 584)
        self.assertFalse(index["contains_live_data"])
        self.assertFalse(index["contains_private_data"])
        self.assertFalse(index["contains_executables"])

    def test_no_private_paths_or_secret_values_in_report(self) -> None:
        text = REPORT.read_text(encoding="utf-8").casefold()
        for marker in ("d:\\", "c:\\", "/users/", "/home/", "/tmp/", "/var/", "secret-value"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, text)

    def test_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)


if __name__ == "__main__":
    unittest.main()
