from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACK = REPO_ROOT / "control" / "audits" / "github-pages-run-evidence-v0"
REPORT = PACK / "github_pages_run_evidence_report.json"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"
LEGACY_STATIC_ROOT = "public" + "_site"


class GitHubPagesRunEvidenceReviewTest(unittest.TestCase):
    def test_audit_pack_exists(self) -> None:
        required = {
            "README.md",
            "WORKFLOW_CONFIGURATION.md",
            "RUN_EVIDENCE.md",
            "ARTIFACT_EVIDENCE.md",
            "DEPLOYMENT_EVIDENCE.md",
            "LOCAL_VALIDATION_EVIDENCE.md",
            "GAPS_AND_OPERATOR_ACTIONS.md",
            "PROMOTION_IMPLICATIONS.md",
            "github_pages_run_evidence_report.json",
        }
        self.assertTrue(PACK.is_dir())
        self.assertEqual(required, {path.name for path in PACK.iterdir() if path.is_file()})

    def test_report_json_records_failed_current_head_run(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["report_id"], "github_pages_run_evidence_v0")
        self.assertEqual(payload["workflow_upload_path"], "site/dist")
        self.assertTrue(payload["workflow_static_only"])
        self.assertFalse(payload["workflow_runs_backend_or_live_probes"])
        self.assertEqual(payload["local_validation_status"], "passed")
        self.assertEqual(payload["overall_decision"], "failed")
        self.assertEqual(payload["latest_pages_run"]["conclusion"], "failure")
        self.assertTrue(payload["latest_pages_run"]["matches_current_head"])

    def test_workflow_uploads_site_dist(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: site/dist", text)
        self.assertIn("actions/upload-pages-artifact@v3", text)
        self.assertNotIn("path: " + LEGACY_STATIC_ROOT, text)

    def test_artifact_and_deployment_evidence_do_not_claim_success(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertFalse(payload["artifact_evidence"]["available"])
        self.assertFalse(payload["artifact_evidence"]["downloaded"])
        self.assertFalse(payload["artifact_evidence"]["verified_contents"])
        self.assertEqual(payload["deployment_evidence"]["deployment_state"], "failure")
        self.assertIsNone(payload["deployment_evidence"]["page_url"])
        self.assertFalse(payload["deployment_evidence"]["success_claim_allowed"])

    def test_operator_actions_exist_for_failed_evidence(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["overall_decision"], "failed")
        self.assertTrue(payload["operator_actions"])
        self.assertEqual(payload["next_recommended_milestone"], "GitHub Pages Workflow Repair v0")

    def test_no_production_backend_or_live_search_claim(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PACK.glob("*.md")
            if path.is_file()
        ).casefold()
        for phrase in (
            "production backend is deployed",
            "live search is deployed",
            "deployment success is verified",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
