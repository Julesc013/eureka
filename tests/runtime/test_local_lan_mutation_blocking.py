from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.service import LocalServiceApp


ROOT = Path(__file__).resolve().parents[2]


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise AssertionError(completed.stderr or completed.stdout)
    return instance


class LocalLanMutationBlockingTests(unittest.TestCase):
    def test_lan_review_rebuild_worker_and_probe_mutations_are_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                app = LocalServiceApp(runtime)
                self.assertEqual(403, app.handle("POST", "/rebuild", client_host="192.168.1.50").status_code)
                self.assertEqual(403, app.handle("POST", "/review/item/decision", client_host="192.168.1.50").status_code)
                self.assertEqual(403, app.handle("POST", "/workers/run", client_host="192.168.1.50").status_code)
                self.assertEqual(403, app.handle("GET", "/api/v1/source-probe", client_host="192.168.1.50").status_code)
            finally:
                close_local_appliance(runtime)

    def test_loopback_operator_mutation_remains_token_gated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                self.assertEqual(401, LocalServiceApp(runtime).handle("POST", "/rebuild", client_host="127.0.0.1").status_code)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
