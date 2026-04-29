import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "full-project-state-audit-v0"


class FullProjectStateAuditTests(unittest.TestCase):
    def test_audit_pack_exists_with_required_files(self) -> None:
        required = [
            "README.md",
            "EXECUTIVE_SUMMARY.md",
            "CURRENT_STATE.md",
            "MILESTONE_INVENTORY.md",
            "VERIFICATION_MATRIX.md",
            "EVAL_AND_SEARCH_USEFULNESS_STATUS.md",
            "EXTERNAL_BASELINE_STATUS.md",
            "SOURCE_AND_RETRIEVAL_STATUS.md",
            "PUBLICATION_AND_STATIC_SITE_STATUS.md",
            "PUBLIC_ALPHA_AND_HOSTING_STATUS.md",
            "LIVE_BACKEND_AND_PROBE_STATUS.md",
            "SNAPSHOT_RELAY_AND_COMPATIBILITY_STATUS.md",
            "NATIVE_CLIENT_STATUS.md",
            "RUST_PARITY_STATUS.md",
            "PRIVACY_SECURITY_ACTION_POLICY_STATUS.md",
            "RISK_REGISTER.md",
            "BLOCKERS.md",
            "NEXT_20_MILESTONES.md",
            "HUMAN_OPERATED_WORK.md",
            "DO_NOT_DO_NEXT.md",
            "PROMPT_QUEUE_RECOMMENDATIONS.md",
            "COMMAND_RESULTS.md",
            "full_project_audit_report.json",
        ]
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((AUDIT / name).exists())

    def test_report_shape_and_recommendations(self) -> None:
        report = json.loads((AUDIT / "full_project_audit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "full_project_state_audit_v0")
        self.assertIn("milestone_counts", report)
        self.assertIn("verification_summary", report)
        self.assertIn("command_results", report)
        self.assertIn("Public Data Contract Stability Review v0", report["immediate_next_codex_prompt"])
        self.assertIn("Manual Observation Batch 0", " ".join(report["human_operated_parallel_work"]))
        self.assertGreaterEqual(report["verification_summary"]["passed_count"], 70)
        self.assertEqual(report["verification_summary"]["failed_count"], 0)
        self.assertEqual(report["external_baseline_status"]["global_observed_slots"], 0)
        self.assertFalse(report["search_usefulness_status"]["comparison_report_eligible"])

    def test_report_includes_deferrals_and_cargo_status(self) -> None:
        report = json.loads((AUDIT / "full_project_audit_report.json").read_text(encoding="utf-8"))
        deferrals = " ".join(report["explicit_deferrals"]).lower()
        self.assertIn("no relay runtime", deferrals)
        self.assertIn("no downloads", deferrals)
        self.assertIn("no live probes", deferrals)
        self.assertFalse(report["rust_status"]["cargo_available"])
        self.assertEqual(report["rust_status"]["cargo_check_status"], "unavailable")

    def test_audit_does_not_claim_forbidden_success(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in AUDIT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}
        )
        self.assertNotIn("eureka is production ready", text)
        self.assertNotIn("github pages deployment succeeded", text)
        self.assertNotIn("external baselines were observed", text)


if __name__ == "__main__":
    unittest.main()
