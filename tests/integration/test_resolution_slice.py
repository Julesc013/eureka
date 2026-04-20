from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO_SCRIPT = REPO_ROOT / "scripts" / "demo_resolution_slice.py"


class ResolutionSliceIntegrationTestCase(unittest.TestCase):
    def test_demo_command_exercises_connector_to_gateway_path_for_known_and_unknown_targets(self) -> None:
        with self.subTest(target_ref="fixture:software/synthetic-demo-app@1.0.0"):
            payload = self._run_demo("fixture:software/synthetic-demo-app@1.0.0")
            self.assertEqual(payload["status"], "completed")
            self.assertEqual(payload["result"]["primary_object"]["id"], "obj.synthetic-demo-app")

        with self.subTest(target_ref="fixture:software/missing-demo-app@0.0.1"):
            payload = self._run_demo("fixture:software/missing-demo-app@0.0.1")
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["notices"][0]["code"], "fixture_target_not_found")

    def _run_demo(self, target_ref: str) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, str(DEMO_SCRIPT), target_ref],
            capture_output=True,
            check=True,
            cwd=REPO_ROOT,
            text=True,
        )
        return json.loads(completed.stdout)
