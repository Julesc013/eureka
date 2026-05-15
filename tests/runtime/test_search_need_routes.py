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


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class SearchNeedRouteTests(unittest.TestCase):
    def test_api_routes_create_list_show_and_transition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))
                created = app.handle("POST", f"/api/v1/hunt/{hunt.id}/search-need", body="operator_token=route-token&operator_label=route")
                need_id = created.payload["need"]["id"]
                listed = app.handle("GET", "/api/v1/needs")
                detail = app.handle("GET", f"/api/v1/need/{need_id}")
                hunt_needs = app.handle("GET", f"/api/v1/hunt/{hunt.id}/needs")
                transitioned = app.handle("POST", f"/api/v1/need/{need_id}/state", body="operator_token=route-token&state=open&reason=route")

                self.assertEqual(200, created.status_code)
                self.assertEqual(1, listed.payload["need_count"])
                self.assertEqual(200, detail.status_code)
                self.assertEqual(1, hunt_needs.payload["need_count"])
                self.assertEqual("open", transitioned.payload["need"]["state"])
                self.assertFalse(created.payload["workunit_creation_performed"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
