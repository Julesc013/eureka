import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_hunt_remediation_continue import validate, validate_continue_payload


class HuntRemediationContinueTests(unittest.TestCase):
    def test_continuation_validator_passes(self):
        result = validate(Path.cwd())
        self.assertEqual(result["status"], "pass", result["errors"])

    def test_continuation_fails_if_previous_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = validate(Path(tmp))
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("missing JSON file" in error for error in result["errors"]))

    def test_continuation_fails_if_hard_blockers_remain(self):
        errors = []
        payload = passing_payload()
        payload["hard_blockers_remaining"] = 1
        validate_continue_payload(payload, errors)
        self.assertTrue(any("hard blockers" in error for error in errors))

    def test_continuation_fails_if_full_discovery_fails(self):
        errors = []
        payload = passing_payload()
        payload["full_unittest_discovery_pass"] = False
        validate_continue_payload(payload, errors)
        self.assertTrue(any("full_unittest_discovery_pass" in error for error in errors))

    def test_script_entrypoint_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_hunt_remediation_continue.py", "--json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)


def passing_payload():
    return {
        "status": "pass",
        "all_remaining_issues_reviewed": True,
        "safe_repairs_applied": 0,
        "missing_outputs_backfilled": 0,
        "child_tasks_created": 0,
        "hard_blockers_remaining": 0,
        "warnings_remaining": 0,
        "all_hunt_validators_pass": True,
        "all_local_dependency_validators_pass": True,
        "hunt_workflow_smoke_pass": True,
        "full_unittest_discovery_pass": True,
        "generated_artifact_cleanliness_pass": True,
        "architecture_boundaries_pass": True,
        "runtime_leakage_gate_pass": True,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "syn_can_start": True,
        "f0_can_resume": True,
        "f0_recommended_now": False,
        "recommended_next_task": "SYN-00 - Synthetic Query Foundry planning over Local Appliance",
    }


if __name__ == "__main__":
    unittest.main()
