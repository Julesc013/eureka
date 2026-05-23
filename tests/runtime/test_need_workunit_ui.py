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


class NeedWorkUnitUiTests(unittest.TestCase):
    def test_need_and_hunt_pages_show_plans_and_linked_workunits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id, operator_label="ui")
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("ui-token"))
                need_page_before = app.handle("GET", f"/need/{need.id}")
                create_workunits_from_need(runtime, need.id, operator_label="ui")
                need_page_after = app.handle("GET", f"/need/{need.id}")
                hunt_page = app.handle("GET", f"/hunt/{hunt.id}")

                self.assertEqual(200, need_page_before.status_code)
                self.assertIn("WorkUnit plan preview", need_page_before.body)
                self.assertIn("Persist planned WorkUnits", need_page_before.body)
                self.assertEqual(200, need_page_after.status_code)
                self.assertIn("Linked WorkUnits", need_page_after.body)
                self.assertIn("blocked_by_policy", need_page_after.body)
                self.assertEqual(200, hunt_page.status_code)
                self.assertIn("Linked WorkUnits", hunt_page.body)
                self.assertNotIn("Run source probe", need_page_after.body)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
