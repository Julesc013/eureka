import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "control/inventory/hunt_perfect_closeout_result.json"
CAPABILITY_MATRIX = ROOT / "control/inventory/hunt_perfect_capability_matrix.json"
REPORT = ROOT / "control/audits/hunt-perfect-closeout-01-v0/hunt_perfect_closeout_report.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class HuntPerfectCloseoutTests(unittest.TestCase):
    def test_perfect_closeout_result_is_green(self):
        payload = load_json(RESULT)
        self.assertEqual("hunt_perfect_closeout_result.v0", payload["schema_version"])
        self.assertEqual("pass", payload["status"])
        for key in (
            "hunt_track_complete",
            "all_required_capabilities_implemented",
            "all_required_capabilities_tested",
            "aide_updated_baseline_integrated",
            "aide_eval_green",
            "aide_report_size_clean",
            "all_hunt_validators_pass",
            "all_local_dependency_validators_pass",
            "hunt_workflow_smoke_pass",
            "hunt_api_smoke_pass",
            "hunt_workbench_smoke_pass",
            "deterministic_replay_pass",
            "ai_escalation_gate_disabled",
            "full_unittest_discovery_pass",
            "generated_artifact_cleanliness_pass",
            "architecture_boundaries_pass",
            "runtime_leakage_gate_pass",
            "syn_can_start",
            "f0_can_resume",
            "main_promotion_review_required",
        ):
            self.assertTrue(payload[key], key)
        self.assertEqual(0, payload["warnings_remaining"])
        self.assertEqual(0, payload["hard_blockers_remaining"])
        self.assertFalse(payload["f0_recommended_now"])
        self.assertEqual("HUNT-TO-MAIN-PROMOTION-REVIEW", payload["recommended_next_task"])

    def test_every_required_capability_is_classified(self):
        payload = load_json(CAPABILITY_MATRIX)
        capabilities = {row["capability_id"]: row for row in payload["capabilities"]}
        required = {
            "hunt_00_track_plan",
            "hunt_01_search_hunt_session_runtime",
            "hunt_02_local_workbench_hunt_ui_state",
            "hunt_03_pause_resume_cancel_steer_commands",
            "hunt_04_exhaustion_reports",
            "hunt_05_searchneed_runtime_and_hunt_to_need_pipeline",
            "hunt_06_hunt_to_workunit_pipeline",
            "hunt_07_background_hunt_runner",
            "hunt_08_workbench_api_cli_workflow_smoke",
            "hunt_09_agent_research_task_contract_provider_disabled",
            "hunt_10_deterministic_replay_harness",
            "hunt_11_ai_escalation_gate_disabled_by_default",
            "hunt_12_closeout_and_syn_f0_handoff",
            "hunt_remediation_state",
            "aide_updated_baseline_compatibility",
            "local_appliance_dependency_compatibility",
        }
        self.assertEqual(set(), required - set(capabilities))
        for row in capabilities.values():
            self.assertTrue(row["implemented"], row["capability_id"])
            self.assertTrue(row["tested"], row["capability_id"])
            self.assertIn(row["proof_level"], {"scaffold", "runtime", "integration", "operational"})

    def test_report_matches_result_boundaries(self):
        result = load_json(RESULT)
        report = load_json(REPORT)
        self.assertEqual("hunt_perfect_closeout_report.v0", report["schema_version"])
        self.assertEqual(result["status"], report["status"])
        for key in (
            "source_probe_executed",
            "extraction_executed",
            "model_provider_used",
            "download_install_execute_performed",
            "master_index_mutated",
            "site_dist_mutated",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(result[key], key)
            self.assertFalse(report[key], key)


if __name__ == "__main__":
    unittest.main()
