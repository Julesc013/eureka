import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "hosted-public-search-rehearsal-v0"
REPORT_PATH = AUDIT_DIR / "hosted_public_search_rehearsal_report.json"
REQUIRED_FILES = {
    "README.md",
    "REHEARSAL_SUMMARY.md",
    "HOSTED_MODE_CONFIGURATION.md",
    "STARTUP_AND_HEALTH_EVIDENCE.md",
    "ROUTE_REHEARSAL_RESULTS.md",
    "SAFE_QUERY_REHEARSAL.md",
    "BLOCKED_REQUEST_REHEARSAL.md",
    "STATIC_HANDOFF_COMPATIBILITY.md",
    "PUBLIC_INDEX_COMPATIBILITY.md",
    "SAFETY_AND_PRIVACY_REVIEW.md",
    "DEPLOYMENT_TEMPLATE_REVIEW.md",
    "OPERATOR_DEPLOYMENT_READINESS.md",
    "RATE_LIMIT_AND_EDGE_GAPS.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "hosted_public_search_rehearsal_report.json",
}


class HostedPublicSearchRehearsalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    def test_required_files_exist(self) -> None:
        self.assertTrue(AUDIT_DIR.is_dir())
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertFalse(REQUIRED_FILES - existing)

    def test_report_shape(self) -> None:
        self.assertEqual(self.report["report_id"], "hosted_public_search_rehearsal_v0")
        self.assertEqual(self.report["rehearsal_mode"], "hosted_local_rehearsal")
        self.assertTrue(self.report["server_started"])
        self.assertTrue(str(self.report["base_url"]).startswith("http://127.0.0.1:"))
        self.assertEqual(len(self.report["route_results"]), 9)
        self.assertEqual(len(self.report["safe_query_results"]), 5)
        self.assertEqual(len(self.report["blocked_request_results"]), 34)

    def test_no_product_expansion_claims(self) -> None:
        for key, value in self.report["hard_booleans"].items():
            self.assertFalse(value, key)
        for key, value in self.report["public_claim_review"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.report["hosted_deployment_performed"])
        self.assertFalse(self.report["hosted_deployment_verified"])

    def test_static_and_index_compatibility_recorded(self) -> None:
        self.assertTrue(all(item["passed"] for item in self.report["static_handoff_compatibility"]))
        self.assertTrue(all(item["passed"] for item in self.report["public_index_compatibility"]))
        self.assertEqual(self.report["public_index_compatibility"][0]["document_count"], 584)

    def test_rate_limit_edge_gaps_recorded(self) -> None:
        gaps = self.report["rate_limit_and_edge_gaps"]
        self.assertEqual(gaps["edge_rate_limit_status"], "operator_gated")
        self.assertFalse(gaps["cloudflare_or_edge_claimed"])

    def test_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_hosted_public_search_rehearsal.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
