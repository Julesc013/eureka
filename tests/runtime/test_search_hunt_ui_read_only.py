from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_service import LocalServiceApp


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


class SearchHuntUiReadOnlyTests(unittest.TestCase):
    def test_hunt_ui_routes_do_not_mutate_hunts_or_workunits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(0, init.returncode, init.stderr)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime, idempotency_key="readonly-test")
                before_hunts = runtime.search_hunt.summarize()["total"]
                before_workunits = runtime.workunit_queue.summarize().total
            finally:
                close_local_appliance(runtime)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                app = LocalServiceApp(runtime)
                for path in ("/hunts", f"/hunt/{hunt.id}", "/api/v1/hunts", f"/api/v1/hunt/{hunt.id}"):
                    response = app.handle("GET", path)
                    self.assertEqual(200, response.status_code)
                post = app.handle("POST", f"/hunt/{hunt.id}")
                self.assertNotEqual(200, post.status_code)
                self.assertEqual(before_hunts, runtime.search_hunt.summarize()["total"])
                self.assertEqual(before_workunits, runtime.workunit_queue.summarize().total)
            finally:
                close_local_appliance(runtime)

    def test_hunt_ui_pages_have_no_mutation_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(0, init.returncode, init.stderr)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime, idempotency_key="readonly-page-test")
            finally:
                close_local_appliance(runtime)
            runtime = open_local_appliance(instance, read_only=True)
            try:
                app = LocalServiceApp(runtime)
                html = app.handle("GET", f"/hunt/{hunt.id}").body.lower()
                self.assertNotIn("method=\"post\"", html)
                self.assertNotIn("create hunt", html)
                self.assertNotIn("transition hunt", html)
                self.assertNotIn("create workunit", html)
                self.assertNotIn("source probe controls", html)
                self.assertNotIn("ai escalation controls", html)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
