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


class BackgroundHuntRunnerAuthTests(unittest.TestCase):
    def test_run_routes_require_token_and_loopback_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="auth")
                create_workunits_from_need(runtime, need.id, operator_label="auth")
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("auth-token"))

                plan = app.handle("POST", f"/hunt/{hunt.id}/runner/plan")
                missing = app.handle("POST", f"/hunt/{hunt.id}/runner/run-next")
                invalid = app.handle("POST", f"/hunt/{hunt.id}/runner/run-next", body="operator_token=bad")
                lan = app.handle("POST", f"/hunt/{hunt.id}/runner/run-next", client_host="192.168.1.20", body="operator_token=auth-token")

                self.assertEqual(200, plan.status_code)
                self.assertEqual(401, missing.status_code)
                self.assertEqual(401, invalid.status_code)
                self.assertEqual(403, lan.status_code)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
