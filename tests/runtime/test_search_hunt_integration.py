from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


class SearchHuntIntegrationTests(unittest.TestCase):
    def test_instance_manifest_opens_search_hunt_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                self.assertIsNotNone(runtime.search_hunt)
                self.assertIn("search_hunt", runtime.store_manifest.stores)
                self.assertEqual("db/search_hunt.sqlite", runtime.store_manifest.stores["search_hunt"].relative_path)
                status = runtime.status().to_dict()
                self.assertIn("search_hunt", status["stores"])
                self.assertEqual("db/search_hunt.sqlite", status["search_hunt"]["relative_path"])
                self.assertIs(status["search_hunt"]["workunit_creation_enabled"], False)
            finally:
                close_local_appliance(runtime)

    def test_search_hunt_sessions_do_not_mutate_workunit_or_public_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            runtime = open_local_appliance(instance)
            try:
                before_work = runtime.workunit_queue.summarize().to_dict()
                before_public = runtime.public_index.summarize().to_dict()
                runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                self.assertEqual(before_work, runtime.workunit_queue.summarize().to_dict())
                self.assertEqual(before_public, runtime.public_index.summarize().to_dict())
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
