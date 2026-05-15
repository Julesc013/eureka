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


class SearchHuntExhaustionRouteTests(unittest.TestCase):
    def test_get_and_post_exhaustion_routes_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))
                missing_report = app.handle("GET", f"/api/v1/hunt/{hunt.id}/exhaustion")
                generated = app.handle("POST", f"/hunt/{hunt.id}/exhaustion", body="operator_token=route-token&operator_label=route")
                shown = app.handle("GET", f"/api/v1/hunt/{hunt.id}/exhaustion")
                generated_api = app.handle("POST", f"/api/v1/hunt/{hunt.id}/exhaustion", body="operator_token=route-token")

                self.assertEqual(200, missing_report.status_code)
                self.assertEqual("not_found", missing_report.payload["status"])
                self.assertEqual(200, generated.status_code)
                self.assertTrue(generated.payload["exhaustion_report"]["checked_layers"])
                self.assertEqual(200, shown.status_code)
                self.assertEqual("pass", shown.payload["status"])
                self.assertEqual(200, generated_api.status_code)
            finally:
                close_local_appliance(runtime)

    def test_unknown_hunt_returns_404(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))
                response = app.handle("GET", "/api/v1/hunt/not-present/exhaustion")
                self.assertEqual(404, response.status_code)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
