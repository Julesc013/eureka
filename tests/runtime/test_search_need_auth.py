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


class SearchNeedAuthTests(unittest.TestCase):
    def test_missing_invalid_token_and_lan_creation_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("auth-token"))
                missing = app.handle("POST", f"/hunt/{hunt.id}/search-need")
                invalid = app.handle("POST", f"/hunt/{hunt.id}/search-need", body="operator_token=bad")
                lan = app.handle("POST", f"/hunt/{hunt.id}/search-need", client_host="192.168.1.10", body="operator_token=auth-token")

                self.assertEqual(401, missing.status_code)
                self.assertEqual(401, invalid.status_code)
                self.assertEqual(403, lan.status_code)
                self.assertEqual([], runtime.search_need.list_needs())
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
