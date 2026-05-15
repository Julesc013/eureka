import unittest

from scripts.validate_hunt_remediation_continue import validate_supporting_payloads


class HuntRemediationContinueGateTests(unittest.TestCase):
    def test_warning_disposition_required(self):
        errors = []
        payloads = supporting_payloads()
        payloads["control/inventory/hunt_remediation_continue_issue_register.json"]["warnings_remaining"] = 1
        validate_supporting_payloads(payloads, errors)
        self.assertTrue(any("warnings" in error for error in errors))

    def test_missing_hunt_validator_blocks_claimed_capability(self):
        errors = []
        payloads = supporting_payloads()
        payloads["control/inventory/hunt_remediation_continue_validation_matrix.json"]["all_hunt_validators_pass"] = False
        validate_supporting_payloads(payloads, errors)
        self.assertTrue(any("all_hunt_validators_pass" in error for error in errors))

    def test_forbidden_side_effects_fail_closed(self):
        for key in ("source_probe_executed", "extraction_executed", "model_provider_used"):
            errors = []
            payloads = supporting_payloads()
            payloads["control/inventory/hunt_remediation_continue_boundary_audit.json"][key] = True
            validate_supporting_payloads(payloads, errors)
            self.assertTrue(any(key in error for error in errors))

    def test_f0_not_recommended_by_default(self):
        errors = []
        payloads = supporting_payloads()
        payloads["control/inventory/hunt_remediation_continue_next_task_decision.json"]["f0_recommended_now"] = True
        validate_supporting_payloads(payloads, errors)
        self.assertTrue(any("F0" in error for error in errors))


def supporting_payloads():
    return {
        "control/inventory/hunt_remediation_continue_input_state.json": {
            "previous_remediation_found": True,
            "previous_status": "pass",
            "previous_hard_blockers": 0,
            "previous_warnings": 0,
            "state_reconstructed": False,
        },
        "control/inventory/hunt_remediation_continue_issue_register.json": {
            "all_remaining_issues_reviewed": True,
            "hard_blockers_remaining": 0,
            "warnings_remaining": 0,
            "issues": [],
        },
        "control/inventory/hunt_remediation_continue_repair_result.json": {
            "issues_remaining": [],
            "child_tasks_created": [],
            "unsafe_repairs_deferred": [],
            "policy_weakened": False,
            "forbidden_side_effects_introduced": False,
        },
        "control/inventory/hunt_remediation_continue_validation_matrix.json": {
            "all_hunt_validators_pass": True,
            "all_local_dependency_validators_pass": True,
            "hunt_workflow_smoke_pass": True,
            "full_unittest_discovery_pass": True,
            "generated_artifact_cleanliness_pass": True,
            "architecture_boundaries_pass": True,
            "runtime_leakage_gate_pass": True,
        },
        "control/inventory/hunt_remediation_continue_smoke_result.json": {
            "hunt_workflow_smoke_pass": True,
            "demo_search_hunt_workflow_pass": True,
            "background_hunt_runner_demo_pass": True,
            "hunt_replay_demo_pass": True,
            "ai_escalation_demo_pass": True,
            "hunt_workbench_smoke_pass": True,
            "api_smoke_pass": True,
            "local_auto_test_pass": True,
        },
        "control/inventory/hunt_remediation_continue_boundary_audit.json": {
            "source_probe_executed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "agent_research_executed": False,
            "external_internet_search_used": False,
            "download_install_execute_performed": False,
            "source_sync_performed": False,
            "master_index_mutated": False,
            "site_dist_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
        "control/inventory/hunt_remediation_continue_next_task_decision.json": {
            "recommended_next_task": "SYN-00 - Synthetic Query Foundry planning over Local Appliance",
            "f0_can_resume": True,
            "f0_recommended_now": False,
            "main_promotion_review_required": True,
        },
    }


if __name__ == "__main__":
    unittest.main()
