from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_service import LocalServiceApp
from runtime.search_hunt import build_replay_fixture_from_hunt, run_hunt_replay
from scripts.eureka_hunt_workflow_smoke import run_workflow_smoke


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class HuntReplayUiTests(unittest.TestCase):
    def test_hunt_page_renders_replay_state_without_future_action_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                workflow = run_workflow_smoke(runtime, query="sampleproject", missing_query="definitely-not-present-hunt-10")
                hunt_id = workflow["hunt_id"]
                fixture = build_replay_fixture_from_hunt(runtime, hunt_id)
                run_hunt_replay(runtime, fixture, operator_context={"authorized": True, "operator_label": "ui"}, mode="replay_local")
                html = LocalServiceApp(runtime).handle("GET", f"/hunt/{hunt_id}").body.lower()

                self.assertIn("deterministic hunt replay", html)
                self.assertIn("replay is not truth", html)
                self.assertIn("artifact acquisition", html)
                self.assertNotIn("download artifact", html)
                self.assertNotIn("install or execute artifact", html)
                self.assertNotIn("call model provider", html)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
