from __future__ import annotations

import subprocess
from pathlib import Path
import tempfile
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator.auth import build_cli_operator_auth_state
from runtime.local.service import LocalServiceApp
from tests.runtime.test_e2e_hunt_exploration_view_models import _build_preview


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


class E2EHuntExplorationUITests(unittest.TestCase):
    def test_explore_routes_are_private_preview_and_runner_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            preview = _build_preview(root)
            instance = root / "instance"
            subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                runtime.e2e_explore_preview_index_path = Path(preview["current_path"])
                runtime.e2e_explore_runs_root = root / "runs"
                app = LocalServiceApp(runtime, operator_auth_state=build_cli_operator_auth_state("route-token"))

                html = app.handle("GET", "/explore?q=WinFTP%20XP%20client")
                api = app.handle("GET", "/api/v1/explore?q=WinFTP%20XP%20client")
                lan = app.handle("GET", "/explore?q=WinFTP%20XP%20client", client_host="192.168.1.24")
                get_start = app.handle("GET", "/explore/run/start")
                missing_token = app.handle("POST", "/api/v1/explore/run/start", body="q=WinFTP%20XP%20client")
                start = app.handle("POST", "/api/v1/explore/run/start", body="operator_token=route-token&q=WinFTP%20XP%20client")
                run_id = start.payload["run_id"]
                detail = app.handle("GET", f"/api/v1/explore/run/{run_id}")
                detail_html = app.handle("GET", f"/explore/run/{run_id}")
                runs = app.handle("GET", "/api/v1/explore/runs")
                replay = app.handle("POST", f"/api/v1/explore/run/{run_id}/replay", body="operator_token=route-token")
                pause = app.handle("POST", f"/api/v1/explore/run/{run_id}/pause", body="operator_token=route-token")
                compare = app.handle("GET", f"/api/v1/explore/compare?left={run_id}&right={run_id}")

                self.assertEqual(200, html.status_code)
                self.assertIn("Result Lanes", html.body)
                self.assertEqual(200, api.status_code)
                self.assertEqual("pass", api.payload["preview_index"]["status"])
                self.assertEqual(403, lan.status_code)
                self.assertEqual(404, get_start.status_code)
                self.assertEqual(401, missing_token.status_code)
                self.assertEqual(200, start.status_code)
                self.assertFalse(start.payload["network_provider_calls"])
                self.assertFalse(start.payload["accepted_truth_created"])
                self.assertEqual(200, detail.status_code)
                self.assertEqual("completed", detail.payload["run"]["state"])
                self.assertEqual(200, detail_html.status_code)
                self.assertIn("Run Controls", detail_html.body)
                self.assertEqual(200, runs.status_code)
                self.assertEqual(1, runs.payload["run_count"])
                self.assertEqual(200, replay.status_code)
                self.assertEqual("replay_verified", replay.payload["replay_report"]["status"])
                self.assertEqual(409, pause.status_code)
                self.assertEqual("blocked", pause.payload["status"])
                self.assertEqual(200, compare.status_code)
                self.assertFalse(compare.payload["diff"]["event_count_delta"])
                self.assertFalse(detail.payload["reviewed_master_mutation"])
                self.assertFalse(detail.payload["public_index_mutation"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
