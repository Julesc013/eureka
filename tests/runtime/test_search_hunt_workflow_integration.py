import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from scripts.eureka_hunt_workflow_smoke import run_workflow_smoke


ROOT = Path(__file__).resolve().parents[2]


class SearchHuntWorkflowIntegrationTests(unittest.TestCase):
    def test_integrated_workflow_creates_and_runs_safe_local_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                result = run_workflow_smoke(runtime)
            finally:
                close_local_appliance(runtime)
        self.assertEqual("pass", result["status"])
        for key in (
            "create_hunt_stage_passed",
            "command_steering_stage_passed",
            "exhaustion_stage_passed",
            "search_need_stage_passed",
            "workunit_creation_stage_passed",
            "safe_worker_stage_passed",
            "policy_blocked_workunits_remained_blocked",
        ):
            self.assertTrue(result[key], key)
        self.assertFalse(result["source_probe_executed"])
        self.assertFalse(result["extraction_executed"])
        self.assertFalse(result["model_provider_used"])


if __name__ == "__main__":
    unittest.main()
