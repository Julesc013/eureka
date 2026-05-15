import unittest

from scripts.validate_hunt_remediation import validate_supporting_payloads


class HuntRemediationGateTests(unittest.TestCase):
    def test_warning_disposition_required(self):
        errors = []
        payloads = supporting_payloads()
        payloads["control/inventory/hunt_remediation_warning_disposition.json"]["warnings_remaining"] = 1
        validate_supporting_payloads(payloads, errors)
        self.assertTrue(any("warnings" in error for error in errors))

    def test_boundary_rejects_master_index_mutation(self):
        errors = []
        payloads = supporting_payloads()
        payloads["control/inventory/hunt_remediation_boundary_audit.json"]["master_index_mutated"] = True
        validate_supporting_payloads(payloads, errors)
        self.assertTrue(any("master_index_mutated" in error for error in errors))

    def test_validation_matrix_requires_architecture_and_leakage(self):
        for key in ("architecture_boundaries_pass", "runtime_leakage_gate_pass"):
            errors = []
            payloads = supporting_payloads()
            payloads["control/inventory/hunt_remediation_validation_matrix.json"][key] = False
            validate_supporting_payloads(payloads, errors)
            self.assertTrue(any(key in error for error in errors))


def supporting_payloads():
    return {
        "control/inventory/hunt_remediation_state_diagnosis.json": {
            "tasks": [{"task_id": f"HUNT-{index:02d}", "classification": "pass"} for index in range(13)]
        },
        "control/inventory/hunt_remediation_blocker_register.json": {
            "hard_blockers_remaining": 0,
            "blockers": [],
        },
        "control/inventory/hunt_remediation_warning_disposition.json": {
            "warnings_remaining": 0,
            "all_warnings_disposed": True,
        },
        "control/inventory/hunt_remediation_validation_matrix.json": {
            "all_hunt_validators_pass": True,
            "hunt_workflow_smoke_pass": True,
            "full_unittest_discovery_pass": True,
            "generated_artifact_cleanliness_pass": True,
            "architecture_boundaries_pass": True,
            "runtime_leakage_gate_pass": True,
        },
        "control/inventory/hunt_remediation_boundary_audit.json": {
            "source_probe_executed": False,
            "extraction_executed": False,
            "model_provider_used": False,
            "download_install_execute_performed": False,
            "master_index_mutated": False,
            "site_dist_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
        "control/inventory/hunt_remediation_next_task_decision.json": {
            "recommended_next_task": "SYN-00 — Synthetic Query Foundry planning over Local Appliance",
            "f0_recommended_now": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
