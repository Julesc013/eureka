from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp
from runtime.index.public import PublicIndexStore
from runtime.search.observability import DiscoveryEventStore
from tests.runtime.test_public_index_store import make_record


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


def app_for(instance: Path) -> tuple[LocalServiceApp, object]:
    runtime = open_local_appliance(instance, read_only=True)
    return LocalServiceApp(runtime), runtime


class LocalServiceRouteTests(unittest.TestCase):
    def test_status_routes_return_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app, runtime = app_for(init_instance(tmp))
            try:
                status = app.handle("GET", "/status")
                api_status = app.handle("GET", "/api/v1/status")
                self.assertEqual(200, status.status_code)
                self.assertEqual(200, api_status.status_code)
                self.assertEqual("local_http_status_response.v0", status.payload["schema_version"])
                self.assertIs(status.payload["service"]["lan_enabled"], False)
            finally:
                close_local_appliance(runtime)

    def test_search_and_absence_routes_return_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            with PublicIndexStore.open(instance / "db" / "public_index.sqlite") as store:
                store.write_record(make_record())
            app, runtime = app_for(instance)
            try:
                search = app.handle("GET", "/api/v1/search", "q=demo")
                absence = app.handle("GET", "/api/v1/absence", "q=missing")
                self.assertEqual(200, search.status_code)
                self.assertEqual(1, search.payload["result_count"])
                self.assertEqual(200, absence.status_code)
                self.assertEqual("local_http_absence_response.v0", absence.payload["schema_version"])
            finally:
                close_local_appliance(runtime)

    def test_object_and_source_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            with PublicIndexStore.open(instance / "db" / "public_index.sqlite") as store:
                store.write_record(make_record())
            app, runtime = app_for(instance)
            try:
                found = app.handle("GET", "/api/v1/object/pir_0123456789abcdef")
                missing = app.handle("GET", "/api/v1/object/not-present")
                source = app.handle("GET", "/api/v1/source/source.example.metadata")
                empty_source = app.handle("GET", "/api/v1/source/not-present")
                self.assertEqual(200, found.status_code)
                self.assertEqual(404, missing.status_code)
                self.assertEqual(1, source.payload["result_count"])
                self.assertEqual(0, empty_source.payload["result_count"])
            finally:
                close_local_appliance(runtime)

    def test_root_and_health_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app, runtime = app_for(init_instance(tmp))
            try:
                root = app.handle("GET", "/")
                health = app.handle("GET", "/api/v1/health")
                self.assertEqual(302, root.status_code)
                self.assertEqual("/explore", root.headers.get("Location"))
                self.assertEqual(200, health.status_code)
                self.assertIs(health.payload["localhost_only"], True)
            finally:
                close_local_appliance(runtime)

    def test_metrics_and_diagnostics_routes_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            app, runtime = app_for(instance)
            try:
                event_path = Path(tmp) / "events.jsonl"
                setattr(runtime, "eureka_discovery_events_path", event_path)
                store = DiscoveryEventStore(event_path)
                store.record("search_started", run_id="r1", query="private operator query", provider="brave")
                store.append({"event_type": "document_indexed", "run_id": "r1", "url": "https://provider.example/item", "snippet": "restricted"})

                metrics = app.handle("GET", "/api/v1/metrics")
                diagnostics = app.handle("GET", "/api/v1/diagnostics", "run_id=r1")

                self.assertEqual(200, metrics.status_code)
                self.assertEqual(1, metrics.payload["search_count"])
                self.assertEqual(1, metrics.payload["preview_index_upserts"])
                self.assertEqual(200, diagnostics.status_code)
                encoded = diagnostics.body
                self.assertNotIn("private operator query", encoded)
                self.assertNotIn("provider.example", encoded)
                self.assertNotIn("restricted", encoded)
                self.assertFalse(diagnostics.payload["provider_payload_included"])
            finally:
                close_local_appliance(runtime)

    def test_foundry_operator_routes_are_local_and_token_gated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                setattr(runtime, "eureka_foundry_plans_root", Path(tmp) / "foundry" / "plans")
                setattr(runtime, "eureka_foundry_runs_root", Path(tmp) / "foundry" / "runs")
                setattr(runtime, "eureka_discovery_events_path", Path(tmp) / "events.jsonl")
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))

                home = app.handle("GET", "/api/v1/foundry/plan", "seed=manual&max_queries=1&max_fetches=0")
                self.assertEqual(200, home.status_code)
                self.assertFalse(home.payload["plan_preview_makes_network_calls"])
                self.assertFalse(home.payload["run_started"])

                invalid = app.handle("POST", "/api/v1/foundry/runs", body="operator_token=bad&seed=manual")
                lan = app.handle("POST", "/api/v1/foundry/runs", client_host="192.168.1.20", body="operator_token=route-token&seed=manual")
                started = app.handle("POST", "/api/v1/foundry/runs", body="operator_token=route-token&seed=manual&max_queries=1&max_fetches=0")

                self.assertEqual(401, invalid.status_code)
                self.assertEqual(403, lan.status_code)
                self.assertEqual(200, started.status_code)
                self.assertEqual("disabled", started.payload["result"]["status"])
                self.assertFalse(started.payload["network_calls_performed"])
                run_id = started.payload["result"]["run_id"]
                status = app.handle("GET", f"/api/v1/foundry/run/{run_id}")
                pause = app.handle("POST", f"/api/v1/foundry/run/{run_id}/pause", body="operator_token=route-token")
                resume = app.handle("POST", f"/api/v1/foundry/run/{run_id}/resume", body="operator_token=route-token")
                cancel = app.handle("POST", f"/api/v1/foundry/run/{run_id}/cancel", body="operator_token=route-token")

                self.assertEqual(200, status.status_code)
                self.assertEqual(200, pause.status_code)
                self.assertEqual("paused", pause.payload["status"])
                self.assertEqual("running", resume.payload["status"])
                self.assertEqual("cancelled", cancel.payload["status"])
                self.assertFalse(cancel.payload["public_index_mutation"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
