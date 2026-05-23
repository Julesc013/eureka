from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.service import LocalServiceApp


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise AssertionError(completed.stderr or completed.stdout)
    return instance


class LocalServiceLanGateTests(unittest.TestCase):
    def test_lan_client_can_read_status_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                app = LocalServiceApp(runtime)
                response = app.handle("GET", "/api/v1/status", client_host="192.168.1.20")
                health = app.handle("GET", "/api/v1/health", client_host="192.168.1.20")
                self.assertEqual(200, response.status_code)
                self.assertEqual(200, health.status_code)
            finally:
                close_local_appliance(runtime)

    def test_lan_client_is_blocked_from_operator_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                app = LocalServiceApp(runtime)
                self.assertEqual(403, app.handle("GET", "/review", client_host="192.168.1.20").status_code)
                self.assertEqual(403, app.handle("GET", "/rebuild", client_host="192.168.1.20").status_code)
                self.assertEqual(403, app.handle("POST", "/rebuild", client_host="192.168.1.20").status_code)
                self.assertEqual(403, app.handle("POST", "/review/item/decision", client_host="192.168.1.20").status_code)
            finally:
                close_local_appliance(runtime)

    def test_lan_client_is_blocked_from_future_unsafe_classes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                app = LocalServiceApp(runtime)
                self.assertEqual(403, app.handle("GET", "/api/v1/source-probe", client_host="192.168.1.20").status_code)
                self.assertEqual(403, app.handle("POST", "/workers/run", client_host="192.168.1.20").status_code)
            finally:
                close_local_appliance(runtime)

    def test_loopback_rebuild_stays_token_gated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                response = LocalServiceApp(runtime).handle("POST", "/rebuild", client_host="127.0.0.1")
                self.assertEqual(401, response.status_code)
            finally:
                close_local_appliance(runtime)

    def test_workbench_shows_default_and_explicit_lan_posture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                app = LocalServiceApp(runtime)
                home = app.handle("GET", "/", client_host="127.0.0.1")
                self.assertIn("LAN binding is disabled by default", home.body)
                setattr(runtime, "lan_enabled", True)
                setattr(runtime, "bind_lan", True)
                setattr(runtime, "lan_read_only", True)
                status = app.handle("GET", "/status", client_host="127.0.0.1")
                self.assertIn("Explicit LAN binding is read-only", status.body)
                self.assertIn("lan_mutations_enabled", status.body)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
