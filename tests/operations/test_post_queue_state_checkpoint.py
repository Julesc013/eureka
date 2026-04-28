import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT = ROOT / "control" / "audits" / "post-queue-state-checkpoint-v0"


class PostQueueStateCheckpointTests(unittest.TestCase):
    def test_checkpoint_pack_exists_with_required_files(self) -> None:
        required = [
            "README.md",
            "CURRENT_STATE.md",
            "MILESTONE_STATUS.md",
            "VERIFICATION_RESULTS.md",
            "PUBLICATION_PLANE_STATUS.md",
            "PUBLIC_ALPHA_STATUS.md",
            "STATIC_SITE_STATUS.md",
            "EXTERNAL_BASELINE_STATUS.md",
            "EVAL_AND_AUDIT_STATUS.md",
            "RUST_PARITY_STATUS.md",
            "SOURCE_AND_RETRIEVAL_STATUS.md",
            "COMPATIBILITY_SURFACE_STATUS.md",
            "SNAPSHOT_AND_RELAY_STATUS.md",
            "RISK_REGISTER.md",
            "NEXT_MILESTONE_PLAN.md",
            "DEFERRED_AND_BLOCKED_WORK.md",
            "COMMAND_RESULTS.md",
            "checkpoint_report.json",
        ]
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((CHECKPOINT / name).exists())

    def test_checkpoint_report_shape_and_posture(self) -> None:
        report = json.loads((CHECKPOINT / "checkpoint_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "post_queue_state_checkpoint_v0")
        self.assertIn("git_status", report)
        self.assertIn("command_results", report)
        self.assertGreaterEqual(len(report["command_results"]), 50)
        self.assertIn("Manual Observation Batch 0", " ".join(report["human_operated_work"]))
        self.assertIn("No Google scraping", " ".join(report["explicit_deferrals"]))
        self.assertIn("Relay Surface Design v0", report["final_recommendation"])
        self.assertEqual(
            report["eval_status"]["external_baselines"]["global_observed_count"],
            0,
        )

    def test_checkpoint_does_not_claim_production_or_observed_baselines(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in CHECKPOINT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}
        )
        self.assertNotIn("eureka is production-ready", text)
        self.assertNotIn("github pages deployment succeeded", text)
        self.assertNotIn("external baselines were observed", text)


if __name__ == "__main__":
    unittest.main()
