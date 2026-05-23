from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.service import LocalServiceApp, create_local_http_server, validate_host_allowed
from runtime.local.service.errors import LocalServiceHostError


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class LocalServiceReadOnlyTests(unittest.TestCase):
    def test_write_methods_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                app = LocalServiceApp(runtime)
                for method in ("POST", "PUT", "PATCH", "DELETE"):
                    response = app.handle(method, "/api/v1/search", "q=demo")
                    self.assertEqual(405, response.status_code)
                    self.assertEqual("fail", response.payload["status"])
            finally:
                close_local_appliance(runtime)

    def test_lan_and_wildcard_hosts_are_rejected(self) -> None:
        for host in ("0.0.0.0", "::", "192.168.1.10"):
            with self.assertRaises(LocalServiceHostError):
                validate_host_allowed(host)

    def test_server_creation_rejects_non_localhost(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LocalServiceHostError):
                create_local_http_server(init_instance(tmp), host="0.0.0.0", port=0)

    def test_app_requests_do_not_mutate_instance_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            before = tree_digest(instance)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                app = LocalServiceApp(runtime)
                app.handle("GET", "/status")
                app.handle("GET", "/api/v1/search", "q=demo")
                app.handle("GET", "/api/v1/absence", "q=missing")
            finally:
                close_local_appliance(runtime)
            self.assertEqual(before, tree_digest(instance))

    def test_status_reports_no_disabled_execution_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp), read_only=True)
            try:
                payload = LocalServiceApp(runtime).handle("GET", "/api/v1/status").payload
                service = payload["service"]
                self.assertIs(service["source_probe_execution_enabled"], False)
                self.assertIs(service["workunit_execution_enabled"], False)
                self.assertIs(service["review_decision_mutation_enabled"], False)
                self.assertIs(service["index_rebuild_enabled"], False)
                self.assertIs(service["deployment_performed"], False)
            finally:
                close_local_appliance(runtime)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name.endswith("-journal") or path.name.endswith("-wal") or path.name.endswith("-shm"):
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
