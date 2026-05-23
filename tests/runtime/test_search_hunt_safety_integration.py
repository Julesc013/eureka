import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp
from scripts.eureka_hunt_workflow_smoke import run_workflow_smoke


ROOT = Path(__file__).resolve().parents[2]


class SearchHuntSafetyIntegrationTests(unittest.TestCase):
    def test_tokens_lan_and_policy_blocked_workers_stay_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                result = run_workflow_smoke(runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("token"))
                missing = app.handle("POST", f"/hunt/{result['hunt_id']}/exhaustion")
                invalid = app.handle("POST", f"/hunt/{result['hunt_id']}/exhaustion", body="operator_token=bad")
                lan = app.handle("POST", f"/hunt/{result['hunt_id']}/pause", client_host="192.168.1.20", body="operator_token=token")
                workunits = runtime.workunit_queue.list_workunits(limit=500)
            finally:
                close_local_appliance(runtime)
        self.assertEqual(401, missing.status_code)
        self.assertEqual(401, invalid.status_code)
        self.assertEqual(403, lan.status_code)
        blocked_payloads = [dict(item.payload) for item in workunits if item.state.value == "blocked"]
        self.assertTrue(any(item.get("worker_kind") == "extraction_worker" for item in blocked_payloads))
        self.assertTrue(any(item.get("worker_kind") == "ai_model_worker" for item in blocked_payloads))
        self.assertTrue(any(item.get("source_probe_execution_enabled") is False for item in blocked_payloads))


if __name__ == "__main__":
    unittest.main()
