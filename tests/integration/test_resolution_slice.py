from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO_SCRIPT = REPO_ROOT / "scripts" / "demo_resolution_slice.py"


class ResolutionSliceIntegrationTestCase(unittest.TestCase):
    def test_demo_command_exercises_connector_to_gateway_to_workbench_path_for_known_and_unknown_targets(self) -> None:
        with self.subTest(target_ref="fixture:software/synthetic-demo-app@1.0.0"):
            payload = self._run_demo("fixture:software/synthetic-demo-app@1.0.0", include_workbench_session=True)
            self.assertEqual(payload["submit_response"]["status_code"], 202)
            self.assertEqual(payload["submit_response"]["body"]["status"], "accepted")
            self.assertEqual(
                payload["submit_response"]["body"]["resolved_resource_id"],
                "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
            )
            self.assertEqual(payload["read_response"]["status_code"], 200)
            self.assertEqual(payload["read_response"]["body"]["status"], "completed")
            self.assertEqual(
                payload["read_response"]["body"]["resolved_resource_id"],
                "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
            )
            self.assertEqual(
                payload["read_response"]["body"]["result"]["primary_object"]["id"],
                "obj.synthetic-demo-app",
            )
            self.assertEqual(
                payload["read_response"]["body"]["result"]["resolved_resource_id"],
                "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
            )
            self.assertEqual(
                payload["workbench_session"]["selected_object"]["id"],
                "obj.synthetic-demo-app",
            )
            self.assertEqual(
                payload["workbench_session"]["resolved_resource_id"],
                "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
            )
            self.assertEqual(payload["workbench_session"]["active_job"]["status"], "completed")

        with self.subTest(target_ref="fixture:software/missing-demo-app@0.0.1"):
            payload = self._run_demo("fixture:software/missing-demo-app@0.0.1", include_workbench_session=True)
            self.assertEqual(payload["submit_response"]["status_code"], 202)
            self.assertEqual(payload["submit_response"]["body"]["status"], "accepted")
            self.assertEqual(payload["read_response"]["status_code"], 200)
            self.assertEqual(payload["read_response"]["body"]["status"], "blocked")
            self.assertEqual(
                payload["read_response"]["body"]["notices"][0]["code"],
                "fixture_target_not_found",
            )
            self.assertEqual(payload["workbench_session"]["active_job"]["status"], "blocked")
            self.assertEqual(
                payload["workbench_session"]["notices"][0]["code"],
                "fixture_target_not_found",
            )

    def _run_demo(self, target_ref: str, *, include_workbench_session: bool = False) -> dict[str, object]:
        command = [sys.executable, str(DEMO_SCRIPT), target_ref]
        if include_workbench_session:
            command.append("--include-workbench-session")

        completed = subprocess.run(
            command,
            capture_output=True,
            check=True,
            cwd=REPO_ROOT,
            text=True,
        )
        return json.loads(completed.stdout)
