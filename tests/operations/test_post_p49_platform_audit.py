import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "post-p49-platform-audit-v0"
REPORT = AUDIT / "post_p49_platform_audit_report.json"


class PostP49PlatformAuditTests(unittest.TestCase):
    def test_audit_pack_exists_with_required_files(self) -> None:
        required = [
            "README.md",
            "EXECUTIVE_SUMMARY.md",
            "MILESTONE_STATUS.md",
            "REPOSITORY_SHAPE_STATUS.md",
            "STATIC_PUBLICATION_STATUS.md",
            "PUBLIC_SEARCH_STATUS.md",
            "SEARCH_USEFULNESS_STATUS.md",
            "SOURCE_COVERAGE_STATUS.md",
            "EXTERNAL_BASELINE_STATUS.md",
            "PACK_AND_HIVE_MIND_STATUS.md",
            "PACK_IMPORT_AND_STAGING_STATUS.md",
            "AI_ASSISTANCE_STATUS.md",
            "QUERY_INTELLIGENCE_GAP_STATUS.md",
            "LIVE_BACKEND_AND_HOSTING_STATUS.md",
            "LIVE_PROBE_AND_CONNECTOR_STATUS.md",
            "NATIVE_RELAY_SNAPSHOT_STATUS.md",
            "RUST_STATUS.md",
            "SECURITY_PRIVACY_RIGHTS_OPS_STATUS.md",
            "LANGUAGE_AND_RUNTIME_STRATEGY.md",
            "COMMAND_RESULTS.md",
            "RISK_REGISTER.md",
            "BLOCKERS.md",
            "HUMAN_OPERATED_WORK.md",
            "APPROVAL_GATED_WORK.md",
            "OPERATOR_GATED_WORK.md",
            "DO_NOT_DO_NEXT.md",
            "NEXT_20_MILESTONES.md",
            "post_p49_platform_audit_report.json",
        ]
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((AUDIT / name).exists())

    def test_json_report_shape(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["audit_id"], "post_p49_platform_audit_v0")
        self.assertIn("command_results", report)
        self.assertIn("subsystem_status", report)
        self.assertIn("next_20_milestones", report)
        self.assertEqual(len(report["next_20_milestones"]), 20)
        self.assertEqual(report["recommended_next_branch"], "p51-post-p50-remediation-pack-v0")

    def test_core_absence_and_gap_facts_recorded(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["external_baseline_summary"]["global_observed_slots"], 0)
        self.assertFalse(report["public_search_status"]["hosted_public_search"])
        self.assertFalse(report["ai_status"]["model_calls_performed"])
        self.assertFalse(report["ai_status"]["provider_runtime_implemented"])
        self.assertFalse(report["query_intelligence_gap_status"]["public_query_learning_runtime"])
        self.assertIn("language_runtime_strategy", report)

    def test_classifications_are_valid(self) -> None:
        allowed = {
            "implemented_runtime",
            "implemented_local_prototype",
            "implemented_static_artifact",
            "contract_only",
            "planning_only",
            "fixture_only",
            "manual_pending",
            "approval_gated",
            "operator_gated",
            "deferred",
            "blocked",
        }
        report = json.loads(REPORT.read_text(encoding="utf-8"))

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "classification" or key.endswith("_classification"):
                        self.assertIn(child, allowed)
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(report)

    def test_audit_does_not_claim_forbidden_success(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in AUDIT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}
        )
        self.assertNotIn("eureka is production ready", text)
        self.assertNotIn("github pages deployment succeeded", text)
        self.assertNotIn("external baselines were observed", text)
        self.assertNotIn("live probes are enabled", text)


if __name__ == "__main__":
    unittest.main()
