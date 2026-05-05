import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "control" / "audits" / "public-hosted-deployment-evidence-v0"
REPORT_PATH = AUDIT_DIR / "public_hosted_deployment_evidence_report.json"


class PublicHostedDeploymentEvidenceAuditTests(unittest.TestCase):
    def test_required_audit_files_exist(self) -> None:
        required = {
            "README.md",
            "DEPLOYMENT_SUMMARY.md",
            "STATIC_SITE_EVIDENCE.md",
            "HOSTED_BACKEND_EVIDENCE.md",
            "ROUTE_VERIFICATION_RESULTS.md",
            "SAFE_QUERY_VERIFICATION.md",
            "BLOCKED_REQUEST_VERIFICATION.md",
            "STATUS_AND_HEALTH_VERIFICATION.md",
            "STATIC_TO_DYNAMIC_HANDOFF_VERIFICATION.md",
            "PUBLIC_INDEX_VERIFICATION.md",
            "TLS_CORS_CACHE_HEADER_REVIEW.md",
            "RATE_LIMIT_AND_EDGE_EVIDENCE.md",
            "PRIVACY_LOGGING_AND_TELEMETRY_REVIEW.md",
            "PUBLIC_CLAIM_REVIEW.md",
            "OPERATOR_ACTIONS_REQUIRED.md",
            "FAILURE_OR_UNVERIFIED_STATUS.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "COMMAND_RESULTS.md",
            "public_hosted_deployment_evidence_report.json",
        }
        existing = {path.name for path in AUDIT_DIR.iterdir() if path.is_file()}
        self.assertTrue(required.issubset(existing))

    def test_report_is_honest_about_unverified_backend(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "public_hosted_deployment_evidence_v0")
        self.assertEqual(report["hosted_backend_status"], "not_configured")
        self.assertIsNone(report["backend_url"])
        self.assertFalse(report["deployment_verified"])
        self.assertFalse(report["production_ready_claimed"])
        self.assertFalse(report["backend_deployment_verified"])
        self.assertFalse(report["hosted_public_search_live"])
        self.assertFalse(report["live_probes_enabled"])
        self.assertFalse(report["source_connectors_enabled"])
        self.assertFalse(report["downloads_enabled"])
        self.assertFalse(report["uploads_enabled"])
        self.assertFalse(report["accounts_enabled"])
        self.assertFalse(report["telemetry_enabled"])
        self.assertFalse(report["master_index_mutation_enabled"])
        self.assertTrue(report["operator_actions_required"])
        self.assertTrue(report["public_claim_review"])

    def test_docs_record_no_runtime_or_mutation_claim(self) -> None:
        text = (ROOT / "docs" / "operations" / "PUBLIC_HOSTED_DEPLOYMENT_EVIDENCE.md").read_text(encoding="utf-8").casefold()
        for phrase in (
            "no deployment",
            "no production claim",
            "live connectors remain disabled",
            "must not mutate indexes",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
