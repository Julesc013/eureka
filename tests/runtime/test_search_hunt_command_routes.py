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


class SearchHuntCommandRouteTests(unittest.TestCase):
    def test_command_json_routes_work_with_operator_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))
                pause = app.handle("POST", f"/hunt/{hunt.id}/pause", body="operator_token=route-token&reason=route")
                resume = app.handle("POST", f"/hunt/{hunt.id}/resume", body="operator_token=route-token&reason=route")
                steer = app.handle("POST", f"/hunt/{hunt.id}/steer", body="operator_token=route-token&type=metadata_only&reason=route")
                commands = app.handle("GET", f"/api/v1/hunt/{hunt.id}/commands")
                steering = app.handle("GET", f"/api/v1/hunt/{hunt.id}/steering")

                self.assertEqual(200, pause.status_code)
                self.assertEqual("paused", pause.payload["command"]["resulting_state"])
                self.assertEqual(200, resume.status_code)
                self.assertEqual("running", resume.payload["command"]["resulting_state"])
                self.assertEqual(200, steer.status_code)
                self.assertEqual("metadata_only", steer.payload["steering_preference"]["command_type"])
                self.assertEqual(200, commands.status_code)
                self.assertEqual(3, commands.payload["command_count"])
                self.assertEqual(200, steering.status_code)
                self.assertEqual(1, steering.payload["steering_count"])
            finally:
                close_local_appliance(runtime)

    def test_missing_invalid_lan_and_unknown_mutations_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))
                missing = app.handle("POST", f"/hunt/{hunt.id}/pause", body="reason=missing")
                invalid = app.handle("POST", f"/hunt/{hunt.id}/pause", body="operator_token=wrong&reason=invalid")
                lan = app.handle("POST", f"/hunt/{hunt.id}/pause", client_host="192.168.1.25", body="operator_token=route-token&reason=lan")
                unknown = app.handle("POST", "/hunt/not-present/pause", body="operator_token=route-token&reason=missing")

                self.assertEqual(401, missing.status_code)
                self.assertEqual(401, invalid.status_code)
                self.assertEqual(403, lan.status_code)
                self.assertEqual(404, unknown.status_code)
                self.assertEqual(0, len(runtime.search_hunt.list_commands(hunt.id)))
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
