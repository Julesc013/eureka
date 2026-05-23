from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp
from runtime.search.need import create_workunits_from_need


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


class BackgroundHuntRunnerUiTests(unittest.TestCase):
    def test_hunt_page_shows_runner_state_without_future_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="ui")
                create_workunits_from_need(runtime, need.id, operator_label="ui")
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("ui-token"))
                page = app.handle("GET", f"/hunt/{hunt.id}")

                self.assertEqual(200, page.status_code)
                self.assertIn("Background hunt runner", page.body)
                self.assertIn("Runnable WorkUnits", page.body)
                self.assertIn("Policy-blocked WorkUnits", page.body)
                self.assertIn("Run next safe worker", page.body)
                self.assertNotIn("Run source probe", page.body)
                self.assertNotIn("call model provider", page.body.lower())
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
