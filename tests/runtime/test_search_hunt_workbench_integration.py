import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator.auth import build_cli_operator_auth_state
from runtime.local_service import LocalServiceApp
from scripts.eureka_hunt_workflow_smoke import run_workflow_smoke


ROOT = Path(__file__).resolve().parents[2]


class SearchHuntWorkbenchIntegrationTests(unittest.TestCase):
    def test_integrated_pages_show_links_and_disabled_future_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                result = run_workflow_smoke(runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("token"))
                hunt_page = app.handle("GET", f"/hunt/{result['hunt_id']}")
                need_page = app.handle("GET", f"/need/{result['search_need_id']}")
                home = app.handle("GET", "/")
            finally:
                close_local_appliance(runtime)
        self.assertEqual(200, hunt_page.status_code)
        self.assertEqual(200, need_page.status_code)
        self.assertIn("Background hunt runner", hunt_page.body)
        self.assertIn("Linked WorkUnits", hunt_page.body)
        self.assertIn("WorkUnit plan preview", need_page.body)
        self.assertIn("Policy-gated WorkUnits stay blocked", need_page.body)
        self.assertIn("Auto-test/search", home.body)
        self.assertIn("WorkUnits", home.body)
        self.assertNotIn("Run source probe", hunt_page.body + need_page.body)


if __name__ == "__main__":
    unittest.main()
