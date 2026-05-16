import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = ROOT / "control/inventory/hunt_warning_zero_boundary_audit.json"
RESULT = ROOT / "control/inventory/hunt_warning_zero_result.json"
NEXT_TASK = ROOT / "control/inventory/hunt_warning_zero_next_task_decision.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class HuntWarningZeroGateTests(unittest.TestCase):
    def test_boundary_audit_rejects_forbidden_side_effects(self):
        payload = load_json(BOUNDARY)
        for key in (
            "source_probe_executed",
            "extraction_executed",
            "model_provider_used",
            "agent_research_executed",
            "external_internet_search_used",
            "download_install_execute_performed",
            "source_sync_performed",
            "master_index_mutated",
            "site_dist_mutated",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "force_push_performed",
            "history_rewrite_performed",
        ):
            self.assertFalse(payload[key], key)

    def test_green_result_requires_no_warnings(self):
        payload = load_json(RESULT)
        if payload["status"] == "pass":
            self.assertEqual(0, payload["warnings_remaining"])
            self.assertEqual(0, payload["hard_blockers_remaining"])
            self.assertTrue(payload["full_unittest_discovery_pass"])

    def test_next_task_decision_is_explicit(self):
        payload = load_json(NEXT_TASK)
        self.assertEqual("hunt_warning_zero_next_task_decision.v0", payload["schema_version"])
        self.assertEqual("HUNT-TO-MAIN-PROMOTION-REVIEW", payload["recommended_next_task"])
        self.assertTrue(payload["syn_can_start"])
        self.assertTrue(payload["f0_can_resume"])
        self.assertFalse(payload["f0_recommended_now"])
        self.assertTrue(payload["main_promotion_review_required"])

    def test_production_and_public_launch_claims_are_rejected(self):
        for rel in (
            "control/inventory/hunt_warning_zero_result.json",
            "control/audits/hunt-warning-zero-01-v0/hunt_warning_zero_report.json",
        ):
            payload = load_json(ROOT / rel)
            self.assertFalse(payload["production_readiness_claimed"], rel)
            self.assertFalse(payload["public_launch_readiness_claimed"], rel)


if __name__ == "__main__":
    unittest.main()
