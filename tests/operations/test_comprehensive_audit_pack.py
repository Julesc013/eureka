import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = (
    ROOT
    / "control"
    / "audits"
    / "2026-04-25-comprehensive-test-eval-audit"
)
FINDING_REQUIRED_FIELDS = {
    "finding_id",
    "title",
    "severity",
    "category",
    "area",
    "status",
    "evidence",
    "impact",
    "recommended_next_test",
    "recommended_next_work",
    "suggested_milestone",
    "blocked_by",
    "do_not_do",
    "owner_hint",
    "created_by_audit",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class TestComprehensiveAuditPack(unittest.TestCase):
    def test_audit_pack_required_files_exist(self):
        required_files = {
            "README.md",
            "BASELINE.md",
            "commands-run.txt",
            "git-status.txt",
            "STRUCTURE_AUDIT.md",
            "STRUCTURE_FINDINGS.json",
            "CONTENT_COVERAGE_AUDIT.md",
            "SOURCE_GAP_MATRIX.md",
            "RESOURCE_BACKLOG.json",
            "BEHAVIOR_AUDIT.md",
            "FEATURE_MATRIX.md",
            "TEST_GAP_AUDIT.md",
            "HARD_TEST_PROPOSALS.md",
            "TEST_BACKLOG.json",
            "AUDIT_SUMMARY.md",
            "NEXT_MILESTONE_RECOMMENDATIONS.md",
            "findings.json",
        }
        for name in required_files:
            self.assertTrue((AUDIT_DIR / name).exists(), name)

    def test_findings_json_validates_required_fields(self):
        payload = load_json(AUDIT_DIR / "findings.json")
        self.assertEqual(payload["created_by_audit"], "comprehensive_test_eval_audit_v0")
        self.assertGreaterEqual(len(payload["findings"]), 10)
        for finding in payload["findings"]:
            self.assertTrue(FINDING_REQUIRED_FIELDS.issubset(finding), finding)
            self.assertIn(
                finding["severity"], {"critical", "high", "medium", "low", "info"}
            )
            self.assertIsInstance(finding["evidence"], list)
            self.assertIsInstance(finding["blocked_by"], list)
            self.assertIsInstance(finding["do_not_do"], list)

    def test_other_structured_backlogs_parse(self):
        for name in [
            "STRUCTURE_FINDINGS.json",
            "RESOURCE_BACKLOG.json",
            "TEST_BACKLOG.json",
        ]:
            payload = load_json(AUDIT_DIR / name)
            self.assertTrue(payload)

    def test_next_milestones_contains_at_least_eight_recommendations(self):
        text = (AUDIT_DIR / "NEXT_MILESTONE_RECOMMENDATIONS.md").read_text(
            encoding="utf-8"
        )
        recommendation_count = len(re.findall(r"^## \d+\.", text, re.MULTILINE))
        self.assertGreaterEqual(recommendation_count, 8)
        self.assertIn("Hard Test Pack v0", text)
        self.assertIn("Rust Query Planner Parity Candidate v0", text)

    def test_audit_docs_do_not_make_positive_production_claims(self):
        forbidden_positive_claims = [
            "is production-ready",
            "is production ready",
            "approved for open internet",
            "open-internet approved",
            "production deployment packet",
        ]
        for path in AUDIT_DIR.glob("*.md"):
            text = path.read_text(encoding="utf-8").lower()
            for claim in forbidden_positive_claims:
                self.assertNotIn(claim, text, path)

    def test_external_baselines_are_not_claimed_observed(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in AUDIT_DIR.glob("*.md")
        )
        self.assertIn("pending manual", combined)
        self.assertNotIn("google baseline observed", combined)
        self.assertNotIn("internet archive baseline observed", combined)

    def test_hard_eval_weakening_is_rejected_not_recommended(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in AUDIT_DIR.glob("*.md")
        )
        self.assertIn("do not weaken", combined)
        self.assertIn("do not rewrite hard fixtures", combined)
        self.assertNotIn("weaken hard evals", combined.replace("do not weaken hard evals", ""))

    def test_test_registry_and_command_matrix_still_parse(self):
        load_json(ROOT / "control" / "inventory" / "tests" / "test_registry.json")
        load_json(ROOT / "control" / "inventory" / "tests" / "command_matrix.json")


if __name__ == "__main__":
    unittest.main()
