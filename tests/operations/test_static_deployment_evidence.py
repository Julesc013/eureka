from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "static-deployment-evidence-v0"
REPORT_PATH = AUDIT_ROOT / "static_deployment_evidence_report.json"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"
PAGES_DOC = REPO_ROOT / "docs" / "operations" / "GITHUB_PAGES_DEPLOYMENT.md"
LEGACY_STATIC_ROOT = "public" + "_site"


class StaticDeploymentEvidencePackTest(unittest.TestCase):
    def test_audit_pack_files_exist(self) -> None:
        required = {
            "README.md",
            "DEPLOYMENT_SUMMARY.md",
            "WORKFLOW_REVIEW.md",
            "STATIC_ARTIFACT_REVIEW.md",
            "GITHUB_PAGES_STATUS.md",
            "OPERATOR_STEPS.md",
            "DEPLOYMENT_EVIDENCE.md",
            "DEPLOYMENT_VERIFICATION.md",
            "FAILURE_OR_UNVERIFIED_STATUS.md",
            "PUBLIC_CLAIM_REVIEW.md",
            "REMAINING_BLOCKERS.md",
            "NEXT_STEPS.md",
            "COMMAND_RESULTS.md",
            "static_deployment_evidence_report.json",
        }
        self.assertTrue(AUDIT_ROOT.is_dir())
        present = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
        self.assertEqual(required - present, set())

    def test_report_records_unverified_static_deployment(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["artifact_root"], "site/dist")
        self.assertEqual(report["workflow_path"], ".github/workflows/pages.yml")
        self.assertFalse(report["deployment_verified"])
        self.assertFalse(report["deployment_success_claimed"])
        self.assertTrue(report["operator_action_required"])
        self.assertFalse(report["hosted_backend_claimed"])
        self.assertFalse(report["live_search_claimed"])
        self.assertFalse(report["live_probes_claimed"])
        self.assertFalse(report["dynamic_backend_deployed"])
        self.assertIn("workflow_configured", report["github_pages_status"])
        self.assertIn("deployment_unverified", report["github_pages_status"])
        self.assertIn("gh_unavailable", report["github_pages_status"])

    def test_workflow_uploads_site_dist_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: site/dist", text)
        self.assertIn("actions/upload-pages-artifact@v3", text)
        self.assertNotIn("path: " + LEGACY_STATIC_ROOT, text)

    def test_operator_steps_present_when_unverified(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertFalse(report["deployment_verified"])
        self.assertGreaterEqual(len(report["operator_steps"]), 5)
        steps_text = "\n".join(report["operator_steps"]).casefold()
        self.assertIn("settings -> pages", steps_text)
        self.assertIn("github actions", steps_text)
        self.assertIn("deployment url", steps_text)

    def test_public_claim_review_is_static_only(self) -> None:
        text = (AUDIT_ROOT / "PUBLIC_CLAIM_REVIEW.md").read_text(encoding="utf-8").casefold()
        self.assertIn("static-only", text)
        self.assertIn("no hosted backend", text)
        self.assertIn("no live probes", text)
        self.assertNotIn("github pages deployment succeeded", text)

    def test_github_pages_docs_present(self) -> None:
        self.assertTrue(PAGES_DOC.exists())
        text = PAGES_DOC.read_text(encoding="utf-8").casefold()
        self.assertIn("source", text)
        self.assertIn("github actions", text)
        self.assertIn("site/dist", text)


if __name__ == "__main__":
    unittest.main()
