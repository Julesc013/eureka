from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator.auth import build_cli_operator_auth_state
from runtime.local_service import LocalServiceApp


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


class NeedWorkUnitRouteTests(unittest.TestCase):
    def test_plan_create_and_list_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="route")
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))

                plan = app.handle("POST", f"/api/v1/need/{need.id}/workunits/plan", body="operator_token=route-token")
                before = app.handle("GET", f"/api/v1/need/{need.id}/workunits")
                created = app.handle("POST", f"/api/v1/need/{need.id}/workunits", body="operator_token=route-token")
                after = app.handle("GET", f"/api/v1/need/{need.id}/workunits")
                hunt_work = app.handle("GET", f"/api/v1/hunt/{hunt.id}/workunits")

                self.assertEqual(200, plan.status_code)
                self.assertEqual(0, before.payload["workunit_count"])
                self.assertEqual(200, created.status_code)
                self.assertGreater(after.payload["workunit_count"], 0)
                self.assertEqual(after.payload["workunit_count"], hunt_work.payload["workunit_count"])
                self.assertFalse(created.payload["workunit_execution_performed"])
                self.assertFalse(created.payload["source_probe_executed"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
