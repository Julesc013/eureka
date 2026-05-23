from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp
from scripts.eureka_hunt_workflow_smoke import run_workflow_smoke


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class HuntReplayRoutesTests(unittest.TestCase):
    def test_replay_routes_plan_run_auth_and_lan_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                workflow = run_workflow_smoke(runtime, query="sampleproject", missing_query="definitely-not-present-hunt-10")
                hunt_id = workflow["hunt_id"]
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))

                get = app.handle("GET", f"/api/v1/hunt/{hunt_id}/replay")
                plan = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/plan")
                missing = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run")
                invalid = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run", body="operator_token=bad")
                lan = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run", client_host="192.168.1.20", body="operator_token=route-token")
                run = app.handle("POST", f"/api/v1/hunt/{hunt_id}/replay/run", body="operator_token=route-token")

                self.assertEqual(200, get.status_code)
                self.assertEqual(200, plan.status_code)
                self.assertEqual(401, missing.status_code)
                self.assertEqual(401, invalid.status_code)
                self.assertEqual(403, lan.status_code)
                self.assertEqual(200, run.status_code)
                self.assertFalse(run.payload["source_probe_executed"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
