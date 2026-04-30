from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACK = REPO_ROOT / "control" / "audits" / "static-artifact-promotion-review-v0"
REPORT = PACK / "static_artifact_promotion_report.json"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"
EXTERNAL = REPO_ROOT / "external"


class StaticArtifactPromotionReviewTest(unittest.TestCase):
    def test_audit_pack_exists(self) -> None:
        required = {
            "README.md",
            "CURRENT_STATIC_ARTIFACT.md",
            "PROMOTION_DECISION.md",
            "VALIDATION_EVIDENCE.md",
            "WORKFLOW_REVIEW.md",
            "GENERATED_ARTIFACT_REVIEW.md",
            "STATIC_SAFETY_REVIEW.md",
            "BASE_PATH_REVIEW.md",
            "PUBLIC_DATA_SURFACE_REVIEW.md",
            "STALE_REFERENCE_REVIEW.md",
            "RISK_REGISTER.md",
            "BLOCKERS_AND_DEFERRED_WORK.md",
            "NEXT_STEPS.md",
            "static_artifact_promotion_report.json",
        }
        self.assertTrue(PACK.is_dir())
        self.assertEqual(required, {path.name for path in PACK.iterdir() if path.is_file()})

    def test_json_report_records_conditional_promotion(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["decision"], "conditionally_promoted_pending_github_actions_evidence")
        self.assertEqual(payload["active_static_artifact"], "site/dist")
        self.assertEqual(payload["workflow_upload_path"], "site/dist")
        self.assertFalse(payload[("public" + "_site") + "_exists"])
        self.assertTrue(payload["external_exists"])
        self.assertFalse(payload[("third" + "_party") + "_exists"])
        self.assertEqual(payload["github_actions_status"], "unverified")
        self.assertFalse(payload["deployment_success_claimed"])

    def test_workflow_uploads_site_dist(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: site/dist", text)
        self.assertIn("python scripts/check_generated_artifact_drift.py --artifact static_site_dist", text)
        self.assertNotIn("path: " + ("public" + "_site"), text)

    def test_retired_artifact_absent_and_external_exists(self) -> None:
        self.assertFalse((REPO_ROOT / ("public" + "_site")).exists())
        self.assertFalse((REPO_ROOT / ("third" + "_party")).exists())
        self.assertTrue(EXTERNAL.is_dir())
        self.assertTrue((EXTERNAL / "README.md").is_file())

    def test_stale_reference_review_exists(self) -> None:
        text = (PACK / "STALE_REFERENCE_REVIEW.md").read_text(encoding="utf-8")
        self.assertIn("Active current references | Allowed historical references", text)
        self.assertIn("0 | yes", text)

    def test_no_deployment_success_claim_without_evidence(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PACK.glob("*.md")
            if path.is_file()
        ).casefold()
        self.assertEqual(payload["github_actions_status"], "unverified")
        self.assertFalse(payload["deployment_success_claimed"])
        for phrase in (
            "github pages deployment succeeded",
            "deployment success: verified",
            "production ready",
            "production-ready",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_next_milestone_is_actions_evidence_then_public_search(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        next_steps = (PACK / "NEXT_STEPS.md").read_text(encoding="utf-8")
        self.assertEqual(payload["next_recommended_milestone"], "GitHub Pages Run Evidence Review v0")
        self.assertIn("GitHub Pages Run Evidence Review v0", next_steps)
        self.assertIn("Public Search API Contract v0", next_steps)


if __name__ == "__main__":
    unittest.main()
