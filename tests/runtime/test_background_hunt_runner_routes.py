from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator.auth import build_cli_operator_auth_state
from runtime.local_service import LocalServiceApp
from runtime.search_need import create_workunits_from_need


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


class BackgroundHuntRunnerRouteTests(unittest.TestCase):
    def test_runner_routes_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="route")
                create_workunits_from_need(runtime, need.id, operator_label="route")
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))

                plan = app.handle("POST", f"/api/v1/hunt/{hunt.id}/runner/plan")
                get = app.handle("GET", f"/api/v1/hunt/{hunt.id}/runner")
                run = app.handle("POST", f"/api/v1/hunt/{hunt.id}/runner/run-next", body="operator_token=route-token")
                workunits = app.handle("GET", f"/api/v1/hunt/{hunt.id}/workunits")

                self.assertEqual(200, plan.status_code)
                self.assertEqual(200, get.status_code)
                self.assertEqual(200, run.status_code)
                self.assertEqual(200, workunits.status_code)
                self.assertFalse(run.payload["source_probe_executed"])
                self.assertEqual("complete", run.payload["run"]["status"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
