from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_service import LocalServiceApp


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


def create_hunt(instance: Path) -> str:
    runtime = open_local_appliance(instance, read_only=False)
    try:
        session = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime, idempotency_key="route-test")
        return session.id
    finally:
        close_local_appliance(runtime)


class SearchHuntUiRouteTests(unittest.TestCase):
    def test_json_hunt_list_and_detail_routes_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            hunt_id = create_hunt(instance)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                app = LocalServiceApp(runtime)
                listing = app.handle("GET", "/api/v1/hunts")
                detail = app.handle("GET", f"/api/v1/hunt/{hunt_id}")
                self.assertEqual(200, listing.status_code)
                self.assertEqual("search_hunt_ui_hunts_response.v0", listing.payload["schema_version"])
                self.assertEqual(1, listing.payload["hunt_count"])
                self.assertEqual(200, detail.status_code)
                self.assertEqual("search_hunt_ui_hunt_response.v0", detail.payload["schema_version"])
                self.assertEqual(hunt_id, detail.payload["hunt"]["id"])
                self.assertTrue(detail.payload["transitions"])
            finally:
                close_local_appliance(runtime)

    def test_html_hunt_list_detail_and_missing_routes_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            hunt_id = create_hunt(instance)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                app = LocalServiceApp(runtime)
                listing = app.handle("GET", "/hunts")
                detail = app.handle("GET", f"/hunt/{hunt_id}")
                missing = app.handle("GET", "/hunt/not-present")
                api_missing = app.handle("GET", "/api/v1/hunt/not-present")
                self.assertEqual(200, listing.status_code)
                self.assertIn("Search Hunts", listing.body)
                self.assertEqual(200, detail.status_code)
                self.assertIn("Transition history", detail.body)
                self.assertEqual(404, missing.status_code)
                self.assertIn("Search Hunt not found", missing.body)
                self.assertEqual(404, api_missing.status_code)
                self.assertIsNone(api_missing.payload["hunt"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
