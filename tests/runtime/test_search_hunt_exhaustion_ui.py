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


class SearchHuntExhaustionUITests(unittest.TestCase):
    def test_hunt_detail_page_includes_exhaustion_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("ui-token"))
                app.handle("POST", f"/hunt/{hunt.id}/exhaustion", body="operator_token=ui-token&operator_label=ui")
                response = app.handle("GET", f"/hunt/{hunt.id}")

                self.assertEqual(200, response.status_code)
                self.assertIn("Exhaustion report", response.body)
                self.assertIn("Exhaustion checked layers", response.body)
                self.assertIn("Exhaustion deferred layers", response.body)
                self.assertIn("Blocked-by-policy entries", response.body)
                self.assertIn("Recommended future action categories", response.body)
                self.assertIn("Exhaustion non-claims", response.body)
                self.assertIn("Generate local exhaustion report", response.body)
                self.assertIn("operator_token", response.body)
                self.assertNotIn("create WorkUnit", response.body)
                self.assertNotIn("call model provider", response.body)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
