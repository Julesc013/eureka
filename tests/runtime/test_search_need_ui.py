from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class SearchNeedUITests(unittest.TestCase):
    def test_search_need_pages_and_hunt_link_render(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("ui-token"))
                created = app.handle("POST", f"/hunt/{hunt.id}/search-need", body="operator_token=ui-token&operator_label=ui")
                need_id = created.payload["need"]["id"]
                hunt_page = app.handle("GET", f"/hunt/{hunt.id}")
                list_page = app.handle("GET", "/needs")
                detail_page = app.handle("GET", f"/need/{need_id}")

                self.assertEqual(200, hunt_page.status_code)
                self.assertIn("Linked SearchNeeds", hunt_page.body)
                self.assertIn("Create SearchNeed", hunt_page.body)
                self.assertIn(need_id, hunt_page.body)
                self.assertEqual(200, list_page.status_code)
                self.assertIn("SearchNeeds", list_page.body)
                self.assertEqual(200, detail_page.status_code)
                self.assertIn("Recommended future work categories", detail_page.body)
                self.assertIn("Unavailable future actions", detail_page.body)
                self.assertNotIn("create WorkUnit", detail_page.body)
                self.assertNotIn("call model provider", detail_page.body)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
