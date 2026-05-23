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


class SearchHuntCommandAuthTests(unittest.TestCase):
    def test_operator_token_is_required_for_mutating_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("token"))
                self.assertEqual(401, app.handle("POST", f"/hunt/{hunt.id}/cancel", body="reason=test").status_code)
                self.assertEqual(401, app.handle("POST", f"/hunt/{hunt.id}/cancel", body="operator_token=wrong&reason=test").status_code)
                self.assertEqual(200, app.handle("POST", f"/hunt/{hunt.id}/cancel", body="operator_token=token&reason=test").status_code)
            finally:
                close_local_appliance(runtime)

    def test_read_only_runtime_blocks_direct_command_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
            finally:
                close_local_appliance(runtime)

            runtime = open_local_appliance(instance, read_only=True)
            try:
                with self.assertRaises(Exception):
                    runtime.search_hunt.apply_command(hunt.id, "pause", reason="blocked")
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
