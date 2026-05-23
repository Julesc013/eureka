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


class SearchHuntApiIntegrationTests(unittest.TestCase):
    def test_integrated_json_routes_return_linked_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                result = run_workflow_smoke(runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("token"))
                routes = [
                    "/api/v1/status",
                    "/api/v1/hunts",
                    f"/api/v1/hunt/{result['hunt_id']}",
                    f"/api/v1/hunt/{result['hunt_id']}/exhaustion",
                    f"/api/v1/hunt/{result['hunt_id']}/needs",
                    f"/api/v1/need/{result['search_need_id']}",
                    f"/api/v1/need/{result['search_need_id']}/workunits",
                    f"/api/v1/hunt/{result['hunt_id']}/runner",
                ]
                responses = [app.handle("GET", route) for route in routes]
            finally:
                close_local_appliance(runtime)
        self.assertTrue(all(response.status_code == 200 for response in responses))
        self.assertTrue(responses[4].payload["needs"])
        self.assertTrue(responses[6].payload["workunits"])
        self.assertEqual("pass", responses[7].payload["status"])


if __name__ == "__main__":
    unittest.main()
